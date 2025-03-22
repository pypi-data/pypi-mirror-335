"""
pylogiless - LOGILESS API クライアントライブラリ

ロジレス（LOGILESS）APIにPythonからアクセスするためのクライアントライブラリです。
OAuth2認証と主要なAPIエンドポイントに対応しています。
"""

__version__ = "0.1.0"

from .auth import LogilessAuth
from .client import (
    LogilessClient,
    APIResource,
    ArticleResource,
    ActualInventorySummaryResource,
    LogicalInventorySummaryResource,
    OutboundDeliveryResource,
    InboundDeliveryResource,
    SalesOrderResource,
    WarehouseResource,
    StoreResource,
    LocationResource,
    ReorderPointResource,
    SupplierResource,
    ArticleMapResource,
    DailyInventorySummaryResource,
    TransactionLogResource,
    InterWarehouseTransferResource,
)
from .errors import (
    LogilessError,
    LogilessAuthError,
    LogilessValidationError,
    LogilessRateLimitError,
    LogilessResourceLockedError,
    LogilessServerError,
)

__all__ = [
    "LogilessClient",
    "LogilessAuth",
    "APIResource",
    "ArticleResource",
    "ActualInventorySummaryResource",
    "LogicalInventorySummaryResource",
    "OutboundDeliveryResource",
    "InboundDeliveryResource",
    "SalesOrderResource",
    "WarehouseResource",
    "StoreResource",
    "LocationResource",
    "ReorderPointResource",
    "SupplierResource", 
    "ArticleMapResource",
    "DailyInventorySummaryResource",
    "TransactionLogResource",
    "InterWarehouseTransferResource",
    "LogilessError",
    "LogilessAuthError",
    "LogilessValidationError",
    "LogilessRateLimitError",
    "LogilessResourceLockedError",
    "LogilessServerError",
]
