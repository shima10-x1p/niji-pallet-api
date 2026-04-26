"""ライバー検索ユースケースを定義する。"""

from __future__ import annotations

from core.application.ports.outbound import LiverRepository
from core.domain.entities import LiverSummaryEntity


class SearchLiversUsecase:
    """検索語に一致するライバー一覧を取得する。"""

    def __init__(self, repository: LiverRepository) -> None:
        """依存する Repository を受け取る。"""

        self._repository = repository

    async def execute(
        self,
        *,
        query: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """検索結果の一覧と総件数を返す。"""

        return await self._repository.search(
            query=query,
            page=page,
            limit=limit,
        )