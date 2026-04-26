"""ドメイン層とアプリケーション層で使う例外を定義する。"""

from __future__ import annotations


class DomainError(Exception):
    """ドメイン層の不変条件違反を表す。"""

    def __init__(self, message: str) -> None:
        """例外メッセージを保持する。"""

        self.message = message
        super().__init__(message)


class ApplicationError(Exception):
    """アプリケーション層の業務エラーを表す。"""

    def __init__(
        self,
        message: str,
        *,
        resource_id: str | None = None,
    ) -> None:
        """例外メッセージと関連リソース ID を保持する。"""

        self.message = message
        self.resource_id = resource_id
        super().__init__(message)


class NotFoundError(ApplicationError):
    """対象リソースが存在しないことを表す。"""

    def __init__(self, resource_id: str, message: str | None = None) -> None:
        """未発見リソース向けの既定メッセージを組み立てる。"""

        resolved_message = (
            message
            or f"指定されたリソースが見つかりません: {resource_id}"
        )
        super().__init__(resolved_message, resource_id=resource_id)


class ConflictError(ApplicationError):
    """対象リソースの競合を表す。"""

    def __init__(self, resource_id: str, message: str | None = None) -> None:
        """競合リソース向けの既定メッセージを組み立てる。"""

        resolved_message = (
            message
            or f"指定されたリソースはすでに存在します: {resource_id}"
        )
        super().__init__(resolved_message, resource_id=resource_id)