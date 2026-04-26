"""ライバー一覧取得ユースケースを定義する。"""

from __future__ import annotations

from core.application.ports.outbound import LiverRepository
from core.domain.entities import BranchEnum, LiverStatusEnum, LiverSummaryEntity


class ListLiversUsecase:
    """条件付きでライバー一覧を取得する。"""

    def __init__(self, repository: LiverRepository) -> None:
        """依存する Repository を受け取る。"""

        self._repository = repository

    async def execute(
        self,
        *,
        branch: BranchEnum | None = None,
        generation: str | None = None,
        status: LiverStatusEnum | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """条件に一致するライバー一覧と総件数を返す。"""

        resolved_status = status or LiverStatusEnum.ACTIVE
        return await self._repository.find_all(
            branch=branch,
            generation=generation,
            status=resolved_status,
            page=page,
            limit=limit,
        )