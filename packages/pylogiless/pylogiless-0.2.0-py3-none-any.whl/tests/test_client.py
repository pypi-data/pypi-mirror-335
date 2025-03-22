"""
クライアントモジュールのテスト
"""
import json
from unittest import mock

import pytest
import requests

from pylogiless import LogilessClient
from pylogiless.api.errors import (
    LogilessAuthError,
    LogilessError,
    LogilessRateLimitError,
    LogilessServerError,
    LogilessValidationError,
)


class TestLogilessClient:
    """
    LogilessClientクラスのテストケース
    """

    def setup_method(self):
        """
        テスト前の準備
        """
        self.access_token = "test_access_token"
        self.merchant_id = "test_merchant_id"
        self.client = LogilessClient(self.access_token, self.merchant_id)

    def test_initialization(self):
        """
        クライアントの初期化をテスト
        """
        assert self.client.api_base_url == LogilessClient.API_BASE_URL
        assert self.client.auth.access_token == self.access_token
        assert self.client.auth.merchant_id == self.merchant_id

        # リソースが正しく初期化されていることを確認
        assert self.client.article is not None
        assert self.client.actual_inventory_summary is not None
        assert self.client.logical_inventory_summary is not None
        assert self.client.outbound_delivery is not None
        assert self.client.inbound_delivery is not None
        assert self.client.sales_order is not None
        assert self.client.warehouse is not None
        assert self.client.store is not None
        assert self.client.location is not None

    def test_custom_api_base_url(self):
        """
        カスタムAPIベースURLを設定できることをテスト
        """
        custom_url = "https://staging.logiless.com/api"
        client = LogilessClient(
            self.access_token, self.merchant_id, api_base_url=custom_url
        )
        assert client.api_base_url == custom_url

    @mock.patch.object(LogilessClient, "request")
    def test_resource_get(self, mock_request):
        """
        リソースのget()メソッドをテスト
        """
        # モックの設定
        mock_request.return_value = {"id": "123", "name": "テスト商品"}

        # テスト対象の関数を呼び出し
        result = self.client.article.get("123")

        # 期待される結果を検証
        assert result == {"id": "123", "name": "テスト商品"}
        mock_request.assert_called_once_with(
            "GET", f"{self.client.api_base_url}/merchant/{self.client.auth.merchant_id}/articles/123", params={}
        )

    @mock.patch.object(LogilessClient, "request")
    def test_resource_list(self, mock_request):
        """
        リソースのlist()メソッドをテスト
        """
        # モックの設定
        mock_request.return_value = {
            "items": [{"id": "123", "name": "テスト商品1"}, {"id": "456", "name": "テスト商品2"}],
            "total": 2,
        }

        # テスト対象の関数を呼び出し
        result = self.client.article.list(limit=10, offset=0)

        # 期待される結果を検証
        assert result == {
            "items": [{"id": "123", "name": "テスト商品1"}, {"id": "456", "name": "テスト商品2"}],
            "total": 2,
        }
        mock_request.assert_called_once_with(
            "GET", f"{self.client.api_base_url}/merchant/{self.client.auth.merchant_id}/articles", params={"limit": 10, "offset": 0}
        )

    @mock.patch.object(LogilessClient, "request")
    def test_resource_create(self, mock_request):
        """
        リソースのcreate()メソッドをテスト
        """
        # モックの設定
        mock_request.return_value = {"id": "123", "name": "新商品"}

        # テスト対象の関数を呼び出し
        data = {"name": "新商品", "code": "NEW001"}
        result = self.client.article.create(data)

        # 期待される結果を検証
        assert result == {"id": "123", "name": "新商品"}
        mock_request.assert_called_once_with(
            "POST", f"{self.client.api_base_url}/merchant/{self.client.auth.merchant_id}/articles", json=data
        )

    @mock.patch.object(LogilessClient, "request")
    def test_resource_update(self, mock_request):
        """
        リソースのupdate()メソッドをテスト
        """
        # モックの設定
        mock_request.return_value = {"id": "123", "name": "更新商品"}

        # テスト対象の関数を呼び出し
        data = {"name": "更新商品"}
        result = self.client.article.update("123", data)

        # 期待される結果を検証
        assert result == {"id": "123", "name": "更新商品"}
        mock_request.assert_called_once_with(
            "PUT", f"{self.client.api_base_url}/merchant/{self.client.auth.merchant_id}/articles/123", json=data
        )

    @mock.patch.object(LogilessClient, "request")
    def test_resource_delete(self, mock_request):
        """
        リソースのdelete()メソッドをテスト
        """
        # モックの設定
        mock_request.return_value = {"success": True}

        # テスト対象の関数を呼び出し
        result = self.client.article.delete("123")

        # 期待される結果を検証
        assert result == {"success": True}
        mock_request.assert_called_once_with(
            "DELETE", f"{self.client.api_base_url}/merchant/{self.client.auth.merchant_id}/articles/123"
        )

    @mock.patch("requests.request")
    def test_request_success(self, mock_request):
        """
        requestメソッドの成功をテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(True, None))
        self.client.auth.ensure_active_token = mock_ensure_token

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"id": "123", "name": "テスト商品"}
        mock_request.return_value = mock_response

        # テスト対象の関数を呼び出し
        result = self.client.request("GET", "https://app2.logiless.com/api/article/123")

        # 期待される結果を検証
        assert result == {"id": "123", "name": "テスト商品"}
        mock_request.assert_called_once()
        assert mock_request.call_args[0][0] == "GET"
        assert mock_request.call_args[0][1] == "https://app2.logiless.com/api/article/123"

    @mock.patch("requests.request")
    def test_request_with_invalid_token(self, mock_request):
        """
        無効なトークンを使用した場合のrequestメソッドをテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(False, "トークンが無効です"))
        self.client.auth.ensure_active_token = mock_ensure_token

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(LogilessError, match="トークンが無効です"):
            self.client.request("GET", "https://app2.logiless.com/api/article/123")

        # requestが呼ばれていないことを確認
        mock_request.assert_not_called()

    @mock.patch("requests.request")
    def test_request_with_validation_error(self, mock_request):
        """
        バリデーションエラーが発生した場合のrequestメソッドをテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(True, None))
        self.client.auth.ensure_active_token = mock_ensure_token

        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "code": 400,
            "message": "Validation Failed",
            "errors": {"name": "必須項目です"},
        }
        mock_request.return_value = mock_response

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(LogilessValidationError):
            self.client.request("POST", "https://app2.logiless.com/api/article", json={"code": "TEST"})

    @mock.patch("requests.request")
    def test_request_with_auth_error(self, mock_request):
        """
        認証エラーが発生した場合のrequestメソッドをテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(True, None))
        self.client.auth.ensure_active_token = mock_ensure_token

        mock_response = mock.Mock()
        mock_response.status_code = 401
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "error": "invalid_token",
            "error_description": "トークンが無効です",
        }
        mock_request.return_value = mock_response

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(LogilessAuthError):
            self.client.request("GET", "https://app2.logiless.com/api/article/123")

    @mock.patch("requests.request")
    def test_request_with_rate_limit_error(self, mock_request):
        """
        レート制限エラーが発生した場合のrequestメソッドをテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(True, None))
        self.client.auth.ensure_active_token = mock_ensure_token

        mock_response = mock.Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "error": "rate_limit_exceeded",
            "error_description": "APIのリクエストレート制限を超えました",
        }
        mock_request.return_value = mock_response

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(LogilessRateLimitError):
            self.client.request("GET", "https://app2.logiless.com/api/article/123")

    @mock.patch("requests.request")
    def test_request_with_server_error(self, mock_request):
        """
        サーバーエラーが発生した場合のrequestメソッドをテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(True, None))
        self.client.auth.ensure_active_token = mock_ensure_token

        mock_response = mock.Mock()
        mock_response.status_code = 500
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "error": "internal_server_error",
            "error_description": "内部サーバーエラーが発生しました",
        }
        mock_request.return_value = mock_response

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(LogilessServerError):
            self.client.request("GET", "https://app2.logiless.com/api/article/123")

    @mock.patch("requests.request")
    def test_request_with_non_json_response(self, mock_request):
        """
        非JSONレスポンスの場合のrequestメソッドをテスト
        """
        # モックの設定
        mock_ensure_token = mock.Mock(return_value=(True, None))
        self.client.auth.ensure_active_token = mock_ensure_token

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.text = "プレーンテキストレスポンス"
        mock_request.return_value = mock_response

        # テスト対象の関数を呼び出し
        result = self.client.request("GET", "https://app2.logiless.com/api/article/123")

        # 期待される結果を検証
        assert result == {"text": "プレーンテキストレスポンス"}
