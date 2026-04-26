"""ライバー現在色取得エンドポイントを定義する。"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, Response, status

from core.adapters.inbound.router._responses import (
    build_error_response,
    to_color_response,
)
from core.providers import GetLiverColorUsecaseDependency
from core.shared.exceptions import NotFoundError
from generated.models.openapi_models import ErrorResponse, LiverColor

router = APIRouter()


@router.get(
    "/livers/{liverId}/color",
    operation_id="get_liver_color",
    response_model=LiverColor | None,
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
async def get_liver_color(
    liver_id: Annotated[
        UUID,
        Path(alias="liverId", description="ライバー ID（UUID）"),
    ],
    usecase: GetLiverColorUsecaseDependency,
) -> LiverColor | None | Response:
    """指定されたライバーの現在色を返す。"""

    try:
        entity = await usecase.execute(liver_id)
    except NotFoundError as exc:
        return build_error_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=exc.message,
        )

    return to_color_response(entity)