"""ライバーデータ保存先の抽象インターフェースを定義する。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.domain.entities import (
    BranchEnum,
    LiverColorEntity,
    LiverEntity,
    LiverStatusEnum,
    LiverSummaryEntity,
)


class LiverRepository(ABC):
    """ライバー情報を永続化層から取得するためのポート。"""

    @abstractmethod
    async def find_all(
        self,
        *,
        branch: BranchEnum | None = None,
        generation: str | None = None,
        status: LiverStatusEnum | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """条件に一致するライバー一覧と総件数を返す。"""

    @abstractmethod
    async def find_by_id(self, liver_id: UUID) -> LiverEntity | None:
        """ID に一致するライバー詳細を返す。"""

    @abstractmethod
    async def search(
        self,
        *,
        query: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """名前や別名に一致するライバー一覧と総件数を返す。"""

    @abstractmethod
    async def find_current_color(self, liver_id: UUID) -> LiverColorEntity | None:
        """ライバーの現在カラー情報を返す。"""
