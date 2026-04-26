"""HTTP レスポンスモデルへの変換処理をまとめる。"""

from __future__ import annotations

from fastapi.responses import JSONResponse

from core.domain.entities import (
    LiverAliasEntity,
    LiverColorEntity,
    LiverEntity,
    LiverSummaryEntity,
)
from generated.models.openapi_models import (
    ErrorDetail,
    ErrorResponse,
    Liver,
    LiverAlias,
    LiverColor,
    LiverSummary,
)


def build_error_response(
    *,
    status_code: int,
    code: str,
    message: str,
) -> JSONResponse:
    """OpenAPI 契約に沿ったエラーレスポンスを返す。"""

    payload = ErrorResponse(
        error=ErrorDetail(code=code, message=message),
    ).model_dump(mode="json")
    return JSONResponse(status_code=status_code, content=payload)


def to_color_response(entity: LiverColorEntity | None) -> LiverColor | None:
    """ドメインのカラー情報を HTTP レスポンスモデルへ変換する。"""

    if entity is None:
        return None

    return LiverColor.model_validate(
        {
            "hex": entity.hex,
            "rgb": {
                "r": entity.r,
                "g": entity.g,
                "b": entity.b,
            },
            "display_name": entity.display_name,
            "is_official": entity.is_official,
            "source": entity.source,
            "source_url": entity.source_url,
            "note": entity.note,
            "updated_at": entity.updated_at,
        },
    )


def to_summary_response(entity: LiverSummaryEntity) -> LiverSummary:
    """ドメインのライバー概要を HTTP レスポンスモデルへ変換する。"""

    return LiverSummary.model_validate(
        {
            "id": entity.id,
            "name": entity.name,
            "kana_name": entity.kana_name,
            "english_name": entity.english_name,
            "branch": entity.branch.value if entity.branch is not None else None,
            "generation": entity.generation,
            "status": entity.status.value,
            "current_color": (
                to_color_response(entity.current_color).model_dump(mode="json")
                if entity.current_color is not None
                else None
            ),
        },
    )


def to_alias_response(entity: LiverAliasEntity) -> LiverAlias:
    """ドメインの別名情報を HTTP レスポンスモデルへ変換する。"""

    return LiverAlias.model_validate(
        {
            "id": entity.id,
            "alias": entity.alias,
            "alias_type": entity.alias_type.value,
            "locale": entity.locale,
        },
    )


def to_liver_response(entity: LiverEntity) -> Liver:
    """ドメインのライバー詳細を HTTP レスポンスモデルへ変換する。"""

    return Liver.model_validate(
        {
            "id": entity.id,
            "name": entity.name,
            "kana_name": entity.kana_name,
            "english_name": entity.english_name,
            "branch": entity.branch.value if entity.branch is not None else None,
            "generation": entity.generation,
            "status": entity.status.value,
            "debuted_at": entity.debuted_at,
            "retired_at": entity.retired_at,
            "aliases": [
                to_alias_response(alias).model_dump(mode="json")
                for alias in entity.aliases
            ],
            "current_color": (
                to_color_response(entity.current_color).model_dump(mode="json")
                if entity.current_color is not None
                else None
            ),
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        },
    )