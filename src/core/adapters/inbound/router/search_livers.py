"""ライバー検索エンドポイントを定義する。"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from core.adapters.inbound.router._responses import to_summary_response
from core.providers import SearchLiversUsecaseDependency
from generated.models.openapi_models import ErrorResponse, LiverListResponse

router = APIRouter()


@router.get(
    "/livers/search",
    operation_id="search_livers",
    response_model=LiverListResponse,
    response_model_by_alias=True,
    responses={
        200: {"description": "OK"},
        422: {
            "model": ErrorResponse,
            "description": "バリデーションエラー",
        },
    },
)
async def search_livers(
    usecase: SearchLiversUsecaseDependency,
    q: Annotated[
        str,
        Query(min_length=1, description="検索キーワード"),
    ],
    page: Annotated[
        int,
        Query(ge=1, description="ページ番号（1始まり）"),
    ] = 1,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="1ページあたりの取得件数"),
    ] = 20,
) -> LiverListResponse:
    """検索キーワードに一致するライバー一覧を返す。"""

    items, total = await usecase.execute(query=q, page=page, limit=limit)
    return LiverListResponse(
        items=[to_summary_response(item) for item in items],
        page=page,
        limit=limit,
        total=total,
    )