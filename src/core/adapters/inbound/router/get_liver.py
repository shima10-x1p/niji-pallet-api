"""ライバー詳細取得エンドポイントを定義する。"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, Response, status

from core.adapters.inbound.router._responses import (
    build_error_response,
    to_liver_response,
)
from core.providers import GetLiverUsecaseDependency
from core.shared.exceptions import NotFoundError
from generated.models.openapi_models import ErrorResponse, Liver

router = APIRouter()


@router.get(
    "/livers/{liverId}",
    operation_id="get_liver",
    response_model=Liver,
    response_model_by_alias=True,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "ライバーが存在しない",
        },
        422: {
            "model": ErrorResponse,
            "description": "バリデーションエラー",
        },
    },
)
async def get_liver(
    liver_id: Annotated[
        UUID,
        Path(alias="liverId", description="ライバー ID（UUID）"),
    ],
    usecase: GetLiverUsecaseDependency,
) -> Liver | Response:
    """指定されたライバーの詳細情報を返す。"""

    try:
        entity = await usecase.execute(liver_id)
    except NotFoundError as exc:
        return build_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=exc.message,
        )

    return to_liver_response(entity)