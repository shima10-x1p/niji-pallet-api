"""ライバー詳細取得ユースケースを定義する。"""

from __future__ import annotations

from uuid import UUID

from core.application.ports.outbound import LiverRepository
from core.domain.entities import LiverEntity
from core.shared.exceptions import NotFoundError


class GetLiverUsecase:
    """ID 指定でライバー詳細を取得する。"""

    def __init__(self, repository: LiverRepository) -> None:
        """依存する Repository を受け取る。"""

        self._repository = repository

    async def execute(self, liver_id: UUID) -> LiverEntity:
        """ライバー詳細を返し、存在しなければ例外を送出する。"""

        entity = await self._repository.find_by_id(liver_id)
        if entity is None:
            raise NotFoundError(str(liver_id))
        return entity