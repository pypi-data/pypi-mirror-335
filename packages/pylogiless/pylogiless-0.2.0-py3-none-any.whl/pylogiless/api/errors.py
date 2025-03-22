"""
LOGILESS APIのエラー処理モジュール
"""
from typing import Any, Dict, Optional


class LogilessError(Exception):
    """
    LOGILESS API関連のエラーの基底クラス
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None):
        """
        LogilessErrorクラスの初期化

        Args:
            message (str): エラーメッセージ
            status_code (Optional[int], optional): HTTPステータスコード
            response (Optional[Dict[str, Any]], optional): APIレスポンスの内容
        """
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)

    def __str__(self) -> str:
        """
        エラーメッセージの文字列表現を返す

        Returns:
            str: フォーマットされたエラーメッセージ
        """
        if self.status_code:
            return f"{self.status_code} - {self.message}"
        return self.message


class LogilessAuthError(LogilessError):
    """
    認証関連のエラーを表すクラス
    """
    pass


class LogilessValidationError(LogilessError):
    """
    バリデーションエラーを表すクラス
    """

    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict[str, Any]] = None, validation_errors: Optional[Dict[str, str]] = None):
        """
        LogilessValidationErrorクラスの初期化

        Args:
            message (str): エラーメッセージ
            status_code (Optional[int], optional): HTTPステータスコード
            response (Optional[Dict[str, Any]], optional): APIレスポンスの内容
            validation_errors (Optional[Dict[str, str]], optional): バリデーションエラーの詳細
        """
        super().__init__(message, status_code, response)
        self.validation_errors = validation_errors or {}

    def __str__(self) -> str:
        """
        エラーメッセージの文字列表現を返す

        Returns:
            str: フォーマットされたエラーメッセージとバリデーション詳細
        """
        base_message = super().__str__()
        if self.validation_errors:
            validation_details = ", ".join([f"{k}: {v}" for k, v in self.validation_errors.items()])
            return f"{base_message} - バリデーションエラー: {validation_details}"
        return base_message


class LogilessRateLimitError(LogilessError):
    """
    レート制限エラーを表すクラス
    """
    pass


class LogilessResourceLockedError(LogilessError):
    """
    リソースロックエラーを表すクラス（ステータスコード423）
    """
    pass


class LogilessServerError(LogilessError):
    """
    サーバーエラーを表すクラス
    """
    pass


def raise_for_error(status_code: int, response_body: Dict[str, Any]) -> None:
    """
    ステータスコードとレスポンスボディに基づいて適切な例外を発生させる

    Args:
        status_code (int): HTTPステータスコード
        response_body (Dict[str, Any]): APIレスポンスの内容

    Raises:
        LogilessAuthError: 認証エラー（401）の場合
        LogilessValidationError: バリデーションエラー（400）の場合
        LogilessRateLimitError: レート制限エラー（429）の場合
        LogilessResourceLockedError: リソースロックエラー（423）の場合
        LogilessServerError: サーバーエラー（500）の場合
        LogilessError: その他のエラーの場合
    """
    if status_code == 400:
        message = response_body.get("message", "バリデーションエラー")
        validation_errors = response_body.get("errors", {})
        raise LogilessValidationError(message, status_code, response_body, validation_errors)
    elif status_code == 401:
        error = response_body.get("error", "認証エラー")
        error_description = response_body.get("error_description", "認証に失敗しました")
        message = f"{error}: {error_description}"
        raise LogilessAuthError(message, status_code, response_body)
    elif status_code == 403:
        error = response_body.get("error", "アクセス拒否")
        error_description = response_body.get("error_description", "リクエストへのアクセスが拒否されました")
        message = f"{error}: {error_description}"
        raise LogilessAuthError(message, status_code, response_body)
    elif status_code == 423:
        error = response_body.get("error", "リソースロック")
        error_description = response_body.get("error_description", "リソースがロックされています")
        message = f"{error}: {error_description}"
        raise LogilessResourceLockedError(message, status_code, response_body)
    elif status_code == 429:
        error = response_body.get("error", "レート制限超過")
        error_description = response_body.get("error_description", "APIのリクエストレート制限を超えました")
        message = f"{error}: {error_description}"
        raise LogilessRateLimitError(message, status_code, response_body)
    elif status_code >= 500:
        error = response_body.get("error", "サーバーエラー")
        error_description = response_body.get("error_description", "内部サーバーエラーが発生しました")
        message = f"{error}: {error_description}"
        raise LogilessServerError(message, status_code, response_body)
    else:
        error = response_body.get("error", "未知のエラー")
        error_description = response_body.get("error_description", "エラーが発生しました")
        message = f"{error}: {error_description}"
        raise LogilessError(message, status_code, response_body)
