"""ライバー一覧取得エンドポイントを定義する。"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query

from core.adapters.inbound.router._responses import to_summary_response
from core.domain.entities import BranchEnum, LiverStatusEnum
from core.providers import ListLiversUsecaseDependency
from generated.models.openapi_models import LiverListResponse

router = APIRouter()


@router.get(
    "/livers",
    operation_id="list_livers",
    response_model=LiverListResponse,
    response_model_by_alias=True,
    responses={
        200: {"description": "OK"},
        422: {"description": "バリデーションエラー"},
    },
)
async def list_livers(
    usecase: ListLiversUsecaseDependency,
    branch: Annotated[
        BranchEnum | None,
        Query(description="国別で絞り込む"),
    ] = None,
    generation: Annotated[
        str | None,
        Query(description='デビュー区分で絞り込む（例: "1期生", "SEEDs"）'),
    ] = None,
    status: Annotated[
        LiverStatusEnum | None,
        Query(description="活動状態で絞り込む（指定なしの場合は active のみ）"),
    ] = None,
    page: Annotated[
        int,
        Query(ge=1, description="ページ番号（1始まり）"),
    ] = 1,
    limit: Annotated[
        int,
        Query(ge=1, le=100, description="1ページあたりの取得件数"),
    ] = 20,
) -> LiverListResponse:
    """条件に一致するライバー一覧を返す。"""

    items, total = await usecase.execute(
        branch=branch,
        generation=generation,
        status=status,
        page=page,
        limit=limit,
    )
    return LiverListResponse(
        items=[to_summary_response(item) for item in items],
        page=page,
        limit=limit,
        total=total,
    )