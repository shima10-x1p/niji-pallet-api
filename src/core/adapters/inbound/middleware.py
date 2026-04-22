"""X-REQUEST-ID を扱う FastAPI ミドルウェア。"""

from __future__ import annotations

from uuid import UUID, uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.shared.request_context import request_id_var

REQUEST_ID_HEADER_NAME = "X-REQUEST-ID"
_UUID_VERSION = 4


def _get_header_value(scope: Scope, header_name: str) -> str | None:
    """ASGI scope から指定名のヘッダー値を取得する。"""

    raw_header_name = header_name.lower().encode("latin-1")
    for key, value in scope.get("headers", []):
        if key.lower() == raw_header_name:
            return value.decode("latin-1")
    return None


def _set_header(message: Message, header_name: str, header_value: str) -> None:
    """ASGI レスポンス開始メッセージへヘッダーを設定する。"""

    raw_header_name = header_name.lower().encode("latin-1")
    raw_header_value = header_value.encode("latin-1")
    headers = [
        (key, value)
        for key, value in message.get("headers", [])
        if key.lower() != raw_header_name
    ]
    headers.append((raw_header_name, raw_header_value))
    message["headers"] = headers


def _resolve_request_id(header_value: str | None) -> str:
    """
    利用するリクエスト ID を決定する。

    有効な UUID が指定されていれば入力値をそのまま使い、
    未指定または不正値の場合は新しい UUID を生成する。
    """

    if header_value in {None, ""}:
        return str(uuid4())

    try:
        parsed_value = UUID(header_value)
    except ValueError:
        return str(uuid4())

    if parsed_value.version != _UUID_VERSION:
        return str(uuid4())

    return header_value


class XRequestIdMiddleware:
    """X-REQUEST-ID を受け渡しし、レスポンスにも付与する。"""

    def __init__(self, app: ASGIApp) -> None:
        """ラップ対象の ASGI アプリケーションを保持する。"""

        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """HTTP リクエストへ request id を設定して downstream へ渡す。"""

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _resolve_request_id(
            _get_header_value(scope, REQUEST_ID_HEADER_NAME),
        )
        token = request_id_var.set(request_id)

        async def send_wrapper(message: Message) -> None:
            """レスポンス開始時に X-REQUEST-ID を付与する。"""

            if message["type"] == "http.response.start":
                _set_header(message, REQUEST_ID_HEADER_NAME, request_id)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            request_id_var.reset(token)
