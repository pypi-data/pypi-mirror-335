"""
dupdetsdk: A package for dataset duplication detection.

Modules:
    - FeatureDuplicationDetectionModel: Model for feature-based duplication detection.
    - RuleDuplicationDetectionModel: Model for rule-based duplication detection.
"""

from .feature_model import FeatureDuplicationDetectionModel
from .rule_model import RuleDuplicationDetectionModel

# 统一管理版本号
__version__ = "0.2.0"  # 确保与setup.py中的版本一致

# 定义可导出的内容
__all__ = [
    "FeatureDuplicationDetectionModel",
    "RuleDuplicationDetectionModel",
    "__version__",
]