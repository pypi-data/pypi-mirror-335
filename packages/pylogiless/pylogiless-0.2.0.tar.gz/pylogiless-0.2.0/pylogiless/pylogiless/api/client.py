"""
LOGILESS APIのクライアントモジュール
"""
import json
from typing import Any, Dict, List, Optional, Type, Union

import requests
from requests.exceptions import RequestException

from .auth import LogilessAuth
from .errors import LogilessError, raise_for_error


class APIResource:
    """
    APIリソースの基底クラス
    個別のAPIエンドポイントに対応するリソースクラスの基底となるクラスです。
    """

    def __init__(self, client: "LogilessClient", resource_path: str):
        """
        APIResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
            resource_path (str): APIリソースのパス
        """
        self.client = client
        self.resource_path = resource_path

    def _make_url(self, path: Optional[str] = None) -> str:
        """
        APIリソースのURLを生成する

        Args:
            path (Optional[str], optional): 追加のパス

        Returns:
            str: 完全なAPIエンドポイントURL
        """
        url = f"{self.client.api_base_url}/{self.resource_path}"
        if path:
            url = f"{url}/{path}"
        return url

    def get(self, resource_id: str, **params) -> Dict[str, Any]:
        """
        リソースを取得する

        Args:
            resource_id (str): 取得するリソースのID
            **params: 追加のクエリパラメータ

        Returns:
            Dict[str, Any]: APIレスポンス
        """
        return self.client.request("GET", self._make_url(resource_id), params=params)

    def list(self, **params) -> Dict[str, Any]:
        """
        リソースのリストを取得する

        Args:
            **params: クエリパラメータ

        Returns:
            Dict[str, Any]: APIレスポンス
        """
        return self.client.request("GET", self._make_url(), params=params)

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        リソースを作成する

        Args:
            data (Dict[str, Any]): 作成するリソースのデータ

        Returns:
            Dict[str, Any]: APIレスポンス
        """
        return self.client.request("POST", self._make_url(), json=data)

    def update(self, resource_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        リソースを更新する

        Args:
            resource_id (str): 更新するリソースのID
            data (Dict[str, Any]): 更新データ

        Returns:
            Dict[str, Any]: APIレスポンス
        """
        return self.client.request("PUT", self._make_url(resource_id), json=data)

    def delete(self, resource_id: str) -> Dict[str, Any]:
        """
        リソースを削除する

        Args:
            resource_id (str): 削除するリソースのID

        Returns:
            Dict[str, Any]: APIレスポンス
        """
        return self.client.request("DELETE", self._make_url(resource_id))


class ArticleResource(APIResource):
    """
    商品情報に関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        ArticleResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/articles")


class ActualInventorySummaryResource(APIResource):
    """
    実在庫サマリ(ActualInventorySummary)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        ActualInventorySummaryResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/actual_inventory_summaries")


class LogicalInventorySummaryResource(APIResource):
    """
    論理在庫サマリ(LogicalInventorySummary)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        LogicalInventorySummaryResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/logical_inventory_summaries")


class OutboundDeliveryResource(APIResource):
    """
    出荷配送(OutboundDelivery)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        OutboundDeliveryResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/outbound_deliveries")


class InboundDeliveryResource(APIResource):
    """
    入荷配送(InboundDelivery)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        InboundDeliveryResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/inbound_deliveries")


class SalesOrderResource(APIResource):
    """
    受注(SalesOrder)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        SalesOrderResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/sales_orders")


class WarehouseResource(APIResource):
    """
    倉庫(Warehouse)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        WarehouseResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/warehouses")


class StoreResource(APIResource):
    """
    店舗(Store)リソースを扱うクラス
    """

    def __init__(self, client: "LogilessClient"):
        """
        StoreResourceクラスの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/stores")


class LocationResource(APIResource):
    """
    ロケーション情報に関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        LocationResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/locations")


class ReorderPointResource(APIResource):
    """
    再注文点に関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        ReorderPointResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/reorder_points")


class SupplierResource(APIResource):
    """
    サプライヤー情報に関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        SupplierResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/suppliers")


class ArticleMapResource(APIResource):
    """
    商品マッピングに関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        ArticleMapResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/article_maps")


class DailyInventorySummaryResource(APIResource):
    """
    日次在庫サマリに関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        DailyInventorySummaryResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/daily_inventory_summaries")


class TransactionLogResource(APIResource):
    """
    取引ログに関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        TransactionLogResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/transaction_logs")


class InterWarehouseTransferResource(APIResource):
    """
    倉庫間移動に関するリソースクラス
    """
    def __init__(self, client: "LogilessClient"):
        """
        InterWarehouseTransferResourceの初期化

        Args:
            client (LogilessClient): LogilessClientインスタンス
        """
        super().__init__(client, f"merchant/{client.auth.merchant_id}/inter_warehouse_transfers")


class LogilessClient:
    """
    LOGILESS APIのクライアントクラス
    """

    API_BASE_URL = "https://app2.logiless.com/api/v1"

    def __init__(
        self,
        access_token: str,
        merchant_id: str,
        api_base_url: Optional[str] = None,
    ):
        """
        LogilessClientクラスの初期化

        Args:
            access_token (str): アクセストークン
            merchant_id (str): マーチャントID
            api_base_url (Optional[str], optional): APIベースURL（テスト用など）
        """
        self.api_base_url = api_base_url or self.API_BASE_URL
        self.auth = LogilessAuth(access_token, merchant_id)

        # APIリソースを初期化
        self.article = ArticleResource(self)
        self.actual_inventory_summary = ActualInventorySummaryResource(self)
        self.logical_inventory_summary = LogicalInventorySummaryResource(self)
        self.outbound_delivery = OutboundDeliveryResource(self)
        self.inbound_delivery = InboundDeliveryResource(self)
        self.sales_order = SalesOrderResource(self)
        self.warehouse = WarehouseResource(self)
        self.store = StoreResource(self)
        self.location = LocationResource(self)
        # 追加のAPIリソース
        self.reorder_point = ReorderPointResource(self)
        self.supplier = SupplierResource(self)
        self.article_map = ArticleMapResource(self)
        self.daily_inventory_summary = DailyInventorySummaryResource(self)
        self.transaction_log = TransactionLogResource(self)
        self.inter_warehouse_transfer = InterWarehouseTransferResource(self)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        APIリクエストを実行する

        Args:
            method (str): HTTPメソッド
            url (str): リクエストURL
            params (Optional[Dict[str, Any]], optional): URLクエリパラメータ
            json (Optional[Dict[str, Any]], optional): JSONリクエストボディ
            headers (Optional[Dict[str, str]], optional): HTTPヘッダー
            files (Optional[Dict[str, Any]], optional): マルチパートファイル

        Returns:
            Union[Dict[str, Any], List[Dict[str, Any]]]: APIレスポンス

        Raises:
            LogilessError: APIエラーが発生した場合
        """
        # トークンが有効かチェック
        token_valid, error_message = self.auth.ensure_active_token()
        if not token_valid:
            raise LogilessError(error_message)

        # ヘッダーの準備
        request_headers = {
            "Content-Type": "application/json",
            **self.auth.get_auth_header(),
        }
        if headers:
            request_headers.update(headers)

        try:
            # リクエスト実行
            response = requests.request(
                method,
                url,
                params=params,
                json=json,
                headers=request_headers,
                files=files,
            )

            # 成功以外のステータスコードの場合、例外をスロー
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"error": "解析エラー", "error_description": response.text}
                raise_for_error(response.status_code, error_data)

            # レスポンスがJSONの場合はパース、そうでなければテキスト
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            return {"text": response.text}

        except RequestException as e:
            raise LogilessError(f"APIリクエストエラー: {str(e)}")
        except ValueError as e:
            raise LogilessError(f"JSONパースエラー: {str(e)}")
        except LogilessError:
            raise
        except Exception as e:
            raise LogilessError(f"不明なエラー: {str(e)}")
