"""FastAPI アプリケーションのエントリポイント。"""

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from core.adapters.inbound.middleware import XRequestIdMiddleware
from core.adapters.inbound.router import livers_router
from core.adapters.inbound.router._responses import build_error_response
from core.adapters.outbound.sqlalchemy.database import (
    get_engine as get_sqlalchemy_engine,
)
from core.adapters.outbound.sqlalchemy.database import (
    init_db,
)
from core.shared.settings import get_settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """アプリ起動時に必要な初期化を行う。"""

    settings = get_settings()
    engine = get_sqlalchemy_engine(settings.database_url)
    await init_db(engine)
    yield


def _build_validation_message(errors: Sequence[object]) -> str:
    """バリデーションエラー配列から要約メッセージを組み立てる。"""

    if not errors:
        return "リクエストの形式が正しくありません。"

    first_error = errors[0]
    if not isinstance(first_error, dict):
        return "リクエストの形式が正しくありません。"

    location = first_error.get("loc")
    message = first_error.get("msg")
    if not isinstance(location, tuple) or not isinstance(message, str):
        return "リクエストの形式が正しくありません。"

    location_text = ".".join(str(item) for item in location)
    return f"入力値が不正です: {location_text} - {message}"


app = FastAPI(
    title="Nijisanji Liver Color API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    _: Request,
    exc: RequestValidationError,
) -> object:
    """FastAPI の 422 を OpenAPI 契約に沿う形式へ変換する。"""

    return build_error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message=_build_validation_message(exc.errors()),
    )


app.add_middleware(XRequestIdMiddleware)
app.include_router(livers_router)