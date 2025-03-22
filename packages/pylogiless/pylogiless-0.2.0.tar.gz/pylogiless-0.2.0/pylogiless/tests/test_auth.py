"""
認証モジュールのテスト
"""
import json
import time
from unittest import mock

import pytest
import requests
from requests.exceptions import HTTPError

from pylogiless.api.auth import LogilessAuth


class TestLogilessAuth:
    """
    LogilessAuthクラスのテストケース
    """

    def setup_method(self):
        """
        テスト前の準備
        """
        self.client_id = "test_client_id"
        self.client_secret = "test_client_secret"
        self.redirect_uri = "https://example.com/callback"
        self.auth = LogilessAuth(self.client_id, self.client_secret, self.redirect_uri)

    def test_get_authorization_url(self):
        """
        認証URLの生成をテスト
        """
        expected_url = f"{self.auth.AUTH_URL}?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}"
        assert self.auth.get_authorization_url() == expected_url

    @mock.patch("requests.get")
    def test_fetch_token_success(self, mock_get):
        """
        トークン取得の成功をテスト
        """
        # モックレスポンスの設定
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer",
        }
        mock_get.return_value = mock_response

        # テスト対象の関数を呼び出し
        result = self.auth.fetch_token("test_code")

        # 期待される結果を検証
        assert result == mock_response.json.return_value
        assert self.auth.access_token == "test_access_token"
        assert self.auth.refresh_token == "test_refresh_token"
        assert self.auth.token_expires_at is not None

        # モックの呼び出しを検証
        mock_get.assert_called_once_with(
            self.auth.TOKEN_URL,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": "test_code",
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri,
            },
        )

    @mock.patch("requests.get")
    def test_fetch_token_error(self, mock_get):
        """
        トークン取得時のエラーをテスト
        """
        # モックレスポンスの設定
        mock_response = mock.Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_request",
            "error_description": "Missing required parameter",
        }
        # raise_for_statusメソッドがHTTPErrorを発生させるように設定
        http_error = HTTPError("400 Client Error")
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(ValueError):
            self.auth.fetch_token("invalid_code")

    @mock.patch("requests.get")
    def test_refresh_access_token_success(self, mock_get):
        """
        アクセストークンの更新成功をテスト
        """
        # 事前条件の設定
        self.auth.refresh_token = "test_refresh_token"

        # モックレスポンスの設定
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer",
        }
        mock_get.return_value = mock_response

        # テスト対象の関数を呼び出し
        result = self.auth.refresh_access_token()

        # 期待される結果を検証
        assert result == mock_response.json.return_value
        assert self.auth.access_token == "new_access_token"
        assert self.auth.refresh_token == "new_refresh_token"

        # モックの呼び出しを検証
        mock_get.assert_called_once_with(
            self.auth.TOKEN_URL,
            params={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": "test_refresh_token",
                "grant_type": "refresh_token",
            },
        )

    def test_refresh_access_token_no_token(self):
        """
        リフレッシュトークンが設定されていない場合のテスト
        """
        # リフレッシュトークンが設定されていないことを確認
        self.auth.refresh_token = None

        # テスト対象の関数を呼び出し、例外が発生することを検証
        with pytest.raises(ValueError, match="リフレッシュトークンが設定されていません"):
            self.auth.refresh_access_token()

    def test_set_token(self):
        """
        トークンの手動設定をテスト
        """
        # テスト対象の関数を呼び出し
        self.auth.set_token("test_access_token", "test_refresh_token", 3600)

        # 期待される結果を検証
        assert self.auth.access_token == "test_access_token"
        assert self.auth.refresh_token == "test_refresh_token"
        assert self.auth.token_expires_at is not None
        # 3600秒後に期限切れになることを検証（多少の誤差を許容）
        assert self.auth.token_expires_at - time.time() > 3590

    def test_get_auth_header(self):
        """
        認証ヘッダーの取得をテスト
        """
        # 事前条件の設定
        self.auth.access_token = "test_access_token"

        # テスト対象の関数を呼び出し
        header = self.auth.get_auth_header()

        # 期待される結果を検証
        assert header == {"Authorization": "Bearer test_access_token"}

    def test_is_token_expired_with_expired_token(self):
        """
        トークンが期限切れの場合のテスト
        """
        # 事前条件の設定（期限切れのトークン）
        self.auth.access_token = "test_access_token"
        self.auth.token_expires_at = time.time() - 100  # 100秒前に期限切れ

        # テスト対象の関数を呼び出し
        result = self.auth.is_token_expired()

        # 期待される結果を検証
        assert result is True

    def test_is_token_expired_with_valid_token(self):
        """
        トークンが有効な場合のテスト
        """
        # 事前条件の設定（有効なトークン）
        self.auth.access_token = "test_access_token"
        self.auth.token_expires_at = time.time() + 3600  # 1時間後に期限切れ

        # テスト対象の関数を呼び出し
        result = self.auth.is_token_expired()

        # 期待される結果を検証
        assert result is False

    def test_ensure_active_token_no_token(self):
        """
        アクセストークンが設定されていない場合のテスト
        """
        # 事前条件の設定
        self.auth.access_token = None

        # テスト対象の関数を呼び出し
        result, error = self.auth.ensure_active_token()

        # 期待される結果を検証
        assert result is False
        assert error == "アクセストークンが設定されていません"

    def test_ensure_active_token_expired_no_refresh(self):
        """
        トークンが期限切れだがリフレッシュトークンがない場合のテスト
        """
        # 事前条件の設定
        self.auth.access_token = "test_access_token"
        self.auth.token_expires_at = time.time() - 100  # 期限切れ
        self.auth.refresh_token = None

        # テスト対象の関数を呼び出し
        result, error = self.auth.ensure_active_token()

        # 期待される結果を検証
        assert result is False
        assert "トークンの有効期限が切れており" in error

    @mock.patch.object(LogilessAuth, "refresh_access_token")
    def test_ensure_active_token_expired_with_refresh(self, mock_refresh):
        """
        トークンが期限切れでリフレッシュできる場合のテスト
        """
        # 事前条件の設定
        self.auth.access_token = "test_access_token"
        self.auth.token_expires_at = time.time() - 100  # 期限切れ
        self.auth.refresh_token = "test_refresh_token"

        # モックの設定
        mock_refresh.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
        }

        # テスト対象の関数を呼び出し
        result, error = self.auth.ensure_active_token()

        # 期待される結果を検証
        assert result is True
        assert error is None
        mock_refresh.assert_called_once()

    def test_ensure_active_token_valid(self):
        """
        トークンが有効な場合のテスト
        """
        # 事前条件の設定
        self.auth.access_token = "test_access_token"
        self.auth.token_expires_at = time.time() + 3600  # 有効

        # テスト対象の関数を呼び出し
        result, error = self.auth.ensure_active_token()

        # 期待される結果を検証
        assert result is True
        assert error is None
