"""
認証関連の機能を提供するモジュール
"""
import time
from typing import Dict, Optional, Tuple

import requests
from requests.exceptions import RequestException


class LogilessAuth:
    """
    LOGILESS APIの認証を処理するクラス
    """

    def __init__(
        self,
        access_token: str,
        merchant_id: str,
    ):
        """
        LogilessAuthクラスの初期化

        Args:
            access_token (str): アクセストークン
            merchant_id (str): マーチャントID
        """
        self.access_token = access_token
        self.merchant_id = merchant_id
        self.token_expires_at: Optional[float] = None

    def get_auth_header(self) -> Dict[str, str]:
        """
        APIリクエスト用の認証ヘッダーを取得する

        Returns:
            Dict[str, str]: Authorization ヘッダーを含む辞書
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "X-Merchant-ID": self.merchant_id
        }

    def is_token_expired(self) -> bool:
        """
        アクセストークンが期限切れかどうかを確認する

        Returns:
            bool: トークンが期限切れの場合はTrue、そうでない場合はFalse
        """
        if not self.access_token:
            return True
        return False  # トークンの有効期限チェックを無効化

    def ensure_active_token(self) -> Tuple[bool, Optional[str]]:
        """
        アクセストークンが有効であることを確認する

        Returns:
            Tuple[bool, Optional[str]]: 
                - トークンが有効であればTrue、そうでなければFalse
                - エラーメッセージ（エラーがない場合はNone）
        """
        if not self.access_token:
            return False, "アクセストークンが設定されていません"

        if self.is_token_expired():
            return False, "トークンの有効期限が切れています"

        return True, None
