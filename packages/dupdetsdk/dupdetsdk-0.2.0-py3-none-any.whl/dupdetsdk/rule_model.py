import random
import time
import loguru
import sys
import chromadb
from .dataset_observer import DatabaseObserver
from .dataset_pacer import DRRatePacer
import json
from .utils import *
from dataloopsdk import DataLoopSDK
import uuid
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
# from __future__ import annotations
class RuleDuplicationDetectionModel():
    def __init__(
        self,
        verbose,
        meta_funcs,
        meta_filter_func,
        dataloop_client,
        ttl,
        delta_quantity_trigger,
        rate_stat_window,
        chromadb_path = f"rule_db_{uuid.uuid4()}",
        chromadb_collection_name = "rule_collection",
        sdk_retries = 3
    ):
        self.result_template = {"is_valid":None, "is_duplicated": None, "duplicate_fields":None}
        self.verbose = verbose
        self.meta_filter_func = meta_filter_func
        self.meta_funcs = meta_funcs
        self.dataloop_client = dataloop_client
        self.ttl = ttl
        self.delta_quantity_trigger = delta_quantity_trigger
        self.chroma_db_name = chromadb_collection_name
        self.chromadb_path = chromadb_path
        self.sdk_retries = sdk_retries
        self.rate_stat_window = rate_stat_window
        
        #  ↓ Lazy 初始化 策略，以便分到多个进程之后能够分别获得一个client ↓
        self.chromadb_client = None
        self.chromadb_collection = None
        self.dataset_observer = None 
        self.dr_rate_pacer = None
        self.logger = None
        # time.sleep(5)

    def laziely_configure_logger(self):
        logger = loguru.logger
        logger.remove()
        logger.add(sys.stdout, format="{time} {level} {message}")  
        # logger.add(
        # "feature_test.log",  
        # format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        # level="INFO",  
        # )      
        self.logger = logger
    
    def laziely_load_chromadb_related(self):
        if self.chromadb_client is None:
            if self.logger and self.verbose:
                self.logger.info(f"<RuleModel> Loading ChromaDB client from path {self.chroma_db_name}")
            # self.chromadb_client = chromadb.PersistentClient(path=self.chromadb_path)
            # print("ok")
            self.chromadb_client = chromadb.EphemeralClient(
                settings=Settings(),
                tenant=DEFAULT_TENANT,
                database=DEFAULT_DATABASE,
            )
            # print("ok2")
            assert self.chromadb_client is not None
            print(self.chromadb_client)
            self.chromadb_collection = self.chromadb_client.get_or_create_collection(self.chroma_db_name)
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
                self.logger.info(f"<RuleModel> ChromaDB collection loaded: {self.chroma_db_name}")
    
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
            return False
        
        count = len(results.get("ids", []))
        if count >= quantity_limit:
            if self.logger and self.verbose:
                self.logger.info(f"<MetaModel> [{uid}] Duplicated detected ({count}/{quantity_limit})")
            return True
        if self.logger and self.verbose:
            self.logger.info(f"<MetaModel [{uid}] No duplicates found ({count} pcs. < {quantity_limit} pcs.)")
        return False
    
    def detect_duplicate(self, uid, raw_meta=None):
        try:
            if raw_meta is None:
                raw_meta = self.uid_to_meta_downloader(uid)
            if not self.meta_filter_func(self.logger, self.verbose,raw_meta,uid):
                return {"is_valid":False, "is_duplicated": None, "duplicate_type":None}
            if not self.chromadb_client:
                self.laziely_configure_logger()
                self.laziely_load_chromadb_related()
            if self.logger and self.verbose:
                self.logger.info(f"<MetaModel> [{uid}] Analysis started.")
            
            extracted_meta = self.extract_meta(raw_meta, uid, meta_funcs=self.meta_funcs)
            duplicate_fields = []

            for meta_func in self.meta_funcs:
                target_field, restriction_dict, quantity_limit = meta_func(raw_meta)
                is_duplicate = self.query_db(uid, restriction_dict, quantity_limit)
                if is_duplicate:
                    duplicate_fields.append(target_field)

            if duplicate_fields:
                self.dr_rate_pacer.found_duplicated()
                return {"is_valid": True, "is_duplicated": True, "duplicate_fields": duplicate_fields}
            if self.logger and self.verbose:
                self.logger.info(f"<MetaModel> [{uid}] No duplicates found after all checks.")
            self.insert_to_db(uid, extracted_meta)
            self.dataset_observer.check_and_maintain_db()
            self.dr_rate_pacer.log_duplication_rate()
            self.dr_rate_pacer.found_not_duplicate()
            return {"is_valid": True, "is_duplicated": False, "duplicate_fields": []}
        except Exception as e:
            if self.logger:
                self.logger.error(f"<MetaModel> Error during detection: {e}", exc_info=True)
            raise
            # return {"is_valid": False, "is_duplicated": None, "duplicate_fields": []}
    
    def uid_to_meta_downloader(self, uid):
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
            raise RuntimeError(f"<SDKMetaFetch> No records found for UID: {uid}")
        return records[0]
     
    def insert_to_db(self, uid, extracted_meta, feature_vector=None):
        timestamp = int(time.time())
        try:
            self.chromadb_collection.add(
                ids=[uid],
                embeddings=[get_hash(uid) if not feature_vector else feature_vector],
                metadatas=[extracted_meta]
            )
        except Exception as e:
            if self.logger:
                self.logger.error(f"<InsertToDB> Error inserting record: {e}", exc_info=True)
            raise
        if self.logger and self.verbose:
            self.logger.info(f"<InsertToDB> Record inserted successfully: UID={uid}")
    
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
    
    
if __name__ == "__main__":
    
    # 最小测试demo ↓
    
    logger = loguru.logger  # Initialize loguru logger
    logger.remove()  
    logger.add(
        sys.stdout, 
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO"
    )
    logger.add(
        "rule_test.log",  # 输出到日志文件
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO"
    )
    
    def meta_filter(logger, verbose, raw_meta, uid):
        try:
            assert raw_meta["bg"] == "ap", "bg must be ap"
            assert raw_meta["sourceInfo"]["type"] == "trigger", "source must be trigger"
            assert raw_meta["type"] == "image", "must be image"
            assert raw_meta["extra"]["deviceSn"] is not None, "must have device sn"
            return True
        except Exception as e:
            if logger and verbose:
                logger.info(f"<MetaModel> [{uid}] Not a DR candidate, detail:{e}")
            return False
        
    def deviceSn_meta_extractor(raw_meta):
        target_field = "deviceSn"
        target_value = raw_meta["extra"]["deviceSn"]
        quantity_limit = 5
        return target_field, {target_field: target_value}, quantity_limit

    meta_funcs = [deviceSn_meta_extractor] 
    
    dataloop_client = DataLoopSDK(url="https://dataloop.anker-in.com")
    
    rule_detector = RuleDuplicationDetectionModel(
        # logger=logger,
        verbose=True,
        meta_funcs=meta_funcs,
        meta_filter_func=meta_filter,
        dataloop_client=dataloop_client,
        ttl=10,
        delta_quantity_trigger=100,
        rate_stat_window = 100,
    )

    result = rule_detector.detect_duplicate("63f68d7a72a0a1d6bc561c64bd7fc26c")
    print(result)