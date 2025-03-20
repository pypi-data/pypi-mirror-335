import random
import time
import loguru
import sys
import chromadb
from dataloopsdk import DataLoopSDK
import json
from .utils import *
import logging
import torch
from torchvision import models, transforms
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
from .dataset_observer import DatabaseObserver
from .dataset_pacer import DRRatePacer
from PIL import Image
import numpy as np
import base64
import os
from io import BytesIO
import multiprocessing
import logging
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings

class FeatureDuplicationDetectionModel():
    def __init__(
        self,
        verbose,
        dataloop_client=None,
        ttl=3600,
        delta_quantity_trigger=100,
        rate_stat_window=100,
        meta_filter_func=None,
        pytorch_threads=4,
        threshold=0.1,
        is_filter_meta=False,
        chroma_db_name="feat_db",
        chromadb_collection_name="feat_collection",
        sdk_retries=3
    ):
        self.is_filter_meta = is_filter_meta
        self.verbose = verbose
        self.dataloop_client = dataloop_client
        self.ttl = ttl
        self.sdk_retries = sdk_retries
        self.meta_filter_func = meta_filter_func
        self.rate_stat_window = rate_stat_window
        self.pytorch_threads = pytorch_threads
        self.threshold = threshold
        self.delta_quantity_trigger = delta_quantity_trigger
        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.chroma_db_name = chroma_db_name
        self.chromadb_collection_name = chromadb_collection_name
            
        # Lazy initialization strategy to get separate client for each process
        self.chromadb_client = None
        self.chromadb_collection = None
        self.dataset_observer = None 
        self.dr_rate_pacer = None
        self.logger = None
    
    def detect_duplicate(self, uid, raw_meta=None, img_base64=None):
        try:
            
            if not self.chromadb_client:
                self.laziely_configure_logger()
                self.laziely_set_up_torch()
                self.laziely_load_chromadb_related()
            
            if self.is_filter_meta:
                if self.logger and self.verbose:
                    self.logger.info(f"<FeatureModel> [{uid}] Performing meta filter")
                if raw_meta is None:
                    raw_meta = self.uid_to_meta_downloader(uid)
                if not self.meta_filter_func(self.logger, self.verbose, raw_meta, uid):
                    return {"is_valid": False, "is_duplicated": None}
            else:
                if self.logger and self.verbose:
                    self.logger.info(f"<FeatureModel> [{uid}] Skipping meta filtering")
            
            extracted_meta = self.extract_meta(raw_meta, uid)
            
            # Check if we can get the image data
            if img_base64 is None:
                if self.dataloop_client is None:
                    raise ValueError("Either img_base64 must be provided or dataloop_client must be initialized")
                img_base64 = self.uid_to_media_b64_downloader(uid, self.dataloop_client) 

            if self.logger and self.verbose:
                self.logger.info(f"<FeatureModel> [{uid}] Feature Model Infering")     
            feature_vector = self._extract_feature(img_base64, uid)
            if self.logger and self.verbose:
                self.logger.info(f"<FeatureModel> [{uid}] Querying similar feature")
                
            results = self.chromadb_collection.query(
                query_embeddings=[feature_vector],  
                n_results=1,  
                include=["distances", "metadatas"],
            )
            
            try:
                target_distance = results['distances'][0][0] if results['distances'][0] else None
                related_uid = results['metadatas'][0][0]['uid'] if results['metadatas'][0][0]['uid'] else None
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"<FeatureModel> no result retrieved from db, db possibly empty")
                self.insert_to_db(uid, extracted_meta, feature_vector)
                self.dataset_observer.check_and_maintain_db()
                self.dr_rate_pacer.found_not_duplicate()
                return {"is_valid": True, "is_duplicated": False}
                
            if target_distance is not None and target_distance <= self.threshold:
                if self.logger and self.verbose:
                    self.logger.info(f"<FeatureModel> [{uid}] Found duplicate, distance: {target_distance:.4f}, threshold: {self.threshold:.4f}")
                self.dr_rate_pacer.found_duplicated()
                return {"is_valid": True, "is_duplicated": True}
            else:
                if self.logger and self.verbose:
                    self.logger.info(f"<FeatureModel> [{uid}] Not feature duplicate was found, distance: {target_distance:.4f}, threshold: {self.threshold:.4f}")
                self.insert_to_db(uid, extracted_meta, feature_vector)
                self.dr_rate_pacer.log_duplication_rate()
                self.dataset_observer.check_and_maintain_db()
                self.dr_rate_pacer.found_not_duplicate()
                return {"is_valid": True, "is_duplicated": False}
        except Exception as e:
            if self.logger:
                self.logger.error(f"<FeatureModel> [{uid}] Error occurred, detail:{e}", exc_info=True)
            raise

    def extract_meta(self, raw_metas, uid, meta_funcs=None):
        if meta_funcs is None:
            extracted = {"timestamp": int(time.time()), "uid": uid}
            return extracted
        else:
            extracted = {"timestamp": int(time.time()), "uid": uid}
            for func in meta_funcs:
                target_field, restriction, quantity = func(raw_metas)
                extracted[target_field] = restriction[target_field]
            if self.logger and self.verbose: 
                self.logger.info(f"<MetaExtractor> [{uid}] Extracted meta: {extracted}")
            return extracted
            
    def laziely_configure_logger(self):
        logger = loguru.logger
        logger.remove()
        logger.add(sys.stdout, format="{time} {level} {message}")  
        self.logger = logger
        logging.getLogger("requests").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger('azure').setLevel(logging.ERROR)
        logging.getLogger('azure.core.pipeline.policies').setLevel(logging.ERROR)
        
    def laziely_load_chromadb_related(self):
        if self.chromadb_client is None:
            if self.logger and self.verbose:
                self.logger.info(f"<FeatureModel> Loading ChromaDB client from collection: {self.chromadb_collection_name}")
            # self.chromadb_client = chromadb.PersistentClient(path=self.chroma_db_name)
            self.chromadb_client = chromadb.EphemeralClient(
                settings=Settings(),
                tenant=DEFAULT_TENANT,
                database=DEFAULT_DATABASE,
            )
            self.chromadb_collection = self.chromadb_client.get_or_create_collection(name=self.chromadb_collection_name, metadata={"hnsw:space": "cosine"})
            self.dataset_observer = DatabaseObserver(
                self.logger,
                self.verbose,
                self.chromadb_collection,
                self.ttl,
                self.delta_quantity_trigger)
            self.dr_rate_pacer = DRRatePacer(
                self.logger,
                self.verbose,
                self.rate_stat_window
            )
            if self.logger and self.verbose:
                self.logger.info(f"<FeatureModel> ChromaDB collection loaded: {self.chromadb_collection_name}")
    
    def laziely_set_up_torch(self):
        torch.backends.cudnn.enabled = False
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        torch.set_num_threads(self.pytorch_threads)
        self.model = self._load_model()
    
    def _extract_feature(self, base64, uid):
        """Extract feature vector from image"""
        if self.logger and self.verbose:
            self.logger.info(f"<FeatureModel> [{uid}] Extracting feature using mobilenet")
        img_tensor = self._preprocess_image_b64(uid, base64)
        try:
            # Convert numpy array to list before returning
            feature_vector = self.model(img_tensor).squeeze().detach().numpy().tolist()
        except Exception as e:
            self.logger.error(f"<DEBUG>, {e}")            
        
        if self.logger and self.verbose:
            self.logger.info(f"<FeatureModel> [{uid}] Extract feature successfully")
        return feature_vector
    
    def _load_model(self):
        """Load MobileNetV3 without classification layer, for feature extraction only"""
        weights = MobileNet_V3_Small_Weights.DEFAULT
        model = mobilenet_v3_small(weights=weights)
        model.classifier = torch.nn.Identity()  # Remove classification layer
        return model
    
    def _preprocess_image_b64(self, uid, base64_str):
        img_data = base64.b64decode(base64_str)
        img = Image.open(BytesIO(img_data)).convert('RGB')
        if self.logger and self.verbose: 
            self.logger.info(f"<FeatureModel> [{uid}] B64Image preprocessed")
        return self.preprocess(img).unsqueeze(0)
    
    def query_db(self, uid, restriction_dict, quantity_limit):
        query_filter = {
            "$and": [
                {"timestamp": {"$gte": int(time.time()) - self.ttl}},
                *[{k: v} for k, v in restriction_dict.items()]
            ]
        }
        if self.logger and self.verbose:
            self.logger.info(f"<MetaModel> [{uid}] Querying db with filter: {query_filter}")
        
        try:
            results = self.chromadb_collection.get(
                where=query_filter,
                include=["metadatas"]
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"<MetaModel> DB query error: {e}", exc_info=True)
            return {"is_valid": False, "is_duplicated": None}
        
        count = len(results.get("ids", []))
        if count >= quantity_limit:
            if self.logger and self.verbose:
                self.logger.info(f"<MetaModel> [{uid}] Duplicated detected ({count}/{quantity_limit})")
            return {"is_valid": True, "is_duplicated": True}
        if self.logger and self.verbose:
            self.logger.info(f"<MetaModel [{uid}] No duplicates found ({count} pcs. < {quantity_limit} pcs.)")
        return {"is_valid": True, "is_duplicated": False}
    
    def insert_to_db(self, uid, extracted_meta, feature_vector=None):
        timestamp = int(time.time())
        try:
            # Make sure the embedding is in list format
            embedding = get_hash(uid) if feature_vector is None else feature_vector
            # Convert to list if it's a numpy array
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
                
            self.chromadb_collection.add(
                ids=[uid],
                embeddings=[embedding],
                metadatas=[extracted_meta]
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"<InsertToDB> Error inserting record: {e}", exc_info=True)
            raise
        if self.logger and self.verbose:
            self.logger.info(f"<InsertToDB> Record inserted successfully: UID={uid}")
    
    def uid_to_meta_downloader(self, uid):
        if self.dataloop_client is None:
            raise ValueError("dataloop_client must be initialized to download metadata")
            
        attempt = 0
        while True:
            try:
                query = {"uid": uid}
                response = self.dataloop_client.query_origin_data(query)
                if self.logger and self.verbose:
                    self.logger.info(f"<SDKMetaFetch> [{uid}] SDK query succeeded")
                break
            except Exception as e:
                attempt += 1
                if attempt >= self.sdk_retries:
                    raise RuntimeError(f"SDK query failed after {self.sdk_retries} attempts") from e
                wait_time = min(2 ** attempt, 60)
                if self.logger and self.verbose:
                    self.logger.warning(
                        f"<SDKMetaFetch> [{uid}] Retrying SDK query in {wait_time}s (attempt {attempt}/{self.sdk_retries}): {e}"
                    )
                time.sleep(wait_time)
        
        records = response.get("records", [])
        if not records:
            raise RuntimeError(f"<SDKMetaFetch> [{uid}] No records found.")
        return records[0]
    
    def uid_to_media_b64_downloader(self, uid, dataloop_client):
        if dataloop_client is None:
            raise ValueError("dataloop_client must be provided to download media")
            
        # Retry mechanism for SDK requests
        attempt = 0
        while True:
            try:
                ret = dataloop_client.get_imagebase64_by_uid(uid)
                if self.logger and self.verbose:
                    self.logger.info(f"<SDKMediaB64Download> [{uid}] Media Downloaded Using SDK Successfully")
                break
            except Exception as e:
                if attempt >= self.sdk_retries - 1:
                    raise Exception(f"Retry limit reached when download_file using sdk, detail: {e}")
                wait_time = min(2 ** attempt, 60)
                if self.logger and self.verbose:
                    self.logger.warning(f"<SDKMediaB64Download> [{uid}] Exception occurred, retry download_file using sdk after {wait_time} seconds, ({attempt+1}/{self.sdk_retries}), detail: {e}")                
                time.sleep(wait_time)
                attempt += 1
                continue
        
        assert ret is not None, "<SDKMediaB64Download> SDK Response was none"
        if self.logger and self.verbose: 
            self.logger.info(f"<SDKMediaB64Download> [{uid}] Media Successfully Resolved After download")
        return ret