"""ライバー現在色取得ユースケースを定義する。"""

from __future__ import annotations

from uuid import UUID

from core.application.ports.outbound import LiverRepository
from core.domain.entities import LiverColorEntity
from core.shared.exceptions import NotFoundError


class GetLiverColorUsecase:
    """ライバーの現在色を取得する。"""

    def __init__(self, repository: LiverRepository) -> None:
        """依存する Repository を受け取る。"""

        self._repository = repository

    async def execute(self, liver_id: UUID) -> LiverColorEntity | None:
        """現在色を返し、ライバー自体がなければ例外を送出する。"""

        current_color = await self._repository.find_current_color(liver_id)
        if current_color is not None:
            return current_color

        liver = await self._repository.find_by_id(liver_id)
        if liver is None:
            raise NotFoundError(str(liver_id))
        return None