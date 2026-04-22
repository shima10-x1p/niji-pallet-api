"""X-REQUEST-ID ミドルウェアの単体テスト。"""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from uuid import UUID, uuid1, uuid4

import pytest
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient
from starlette.types import Message, Receive, Scope, Send

import core.adapters.inbound.middleware as middleware
from core.adapters.inbound.middleware import (
    REQUEST_ID_HEADER_NAME,
    XRequestIdMiddleware,
    _resolve_request_id,
)
from core.shared.request_context import request_id_var


@pytest.fixture(autouse=True)
def reset_request_context() -> Iterator[None]:
    """テストごとに request_id のコンテキストを初期化する。"""

    token = request_id_var.set(None)

    yield

    request_id_var.reset(token)


def _assert_uuid4(value: str) -> None:
    """与えられた文字列が UUID v4 であることを確認する。"""

    parsed_value = UUID(value)
    assert parsed_value.version == 4


def _create_app(response_header_value: str | None = None) -> FastAPI:
    """ミドルウェアを組み込んだ最小構成の FastAPI アプリを返す。"""

    app = FastAPI()
    app.add_middleware(XRequestIdMiddleware)

    @app.get("/request-id")
    async def read_request_id(
        response: Response,
    ) -> dict[str, str | None]:
        """現在の request_id をレスポンス本文で返す。"""

        if response_header_value is not None:
            response.headers[REQUEST_ID_HEADER_NAME] = response_header_value
        return {"request_id": request_id_var.get()}

    return app


def _build_http_scope(
    headers: list[tuple[bytes, bytes]] | None = None,
) -> Scope:
    """直接 ASGI 呼び出し用の HTTP scope を生成する。"""

    return {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/request-id",
        "raw_path": b"/request-id",
        "query_string": b"",
        "headers": headers or [],
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
    }


def test_resolve_request_id_generates_uuid4_when_header_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    ヘッダー未指定時に UUID v4 を生成することを確認する。

    正常系:
        観点: 未指定時に新しい request id が払い出されること
        期待値: `_resolve_request_id(None)` が固定 UUID v4 を返すこと
    """

    # Arrange
    generated_request_id = UUID("00000000-0000-4000-8000-000000000001")
    monkeypatch.setattr(middleware, "uuid4", lambda: generated_request_id)

    # Act
    actual = _resolve_request_id(None)

    # Assert
    assert actual == str(generated_request_id)


def test_resolve_request_id_generates_uuid4_when_header_is_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    空文字のヘッダーを未指定相当として扱うことを確認する。

    境界値:
        観点: 空文字でも新しい request id を生成すること
        期待値: `_resolve_request_id("")` が固定 UUID v4 を返すこと
    """

    # Arrange
    generated_request_id = UUID("00000000-0000-4000-8000-000000000002")
    monkeypatch.setattr(middleware, "uuid4", lambda: generated_request_id)

    # Act
    actual = _resolve_request_id("")

    # Assert
    assert actual == str(generated_request_id)


def test_resolve_request_id_preserves_original_value_when_valid_uuid4_is_provided() -> None:
    """
    有効な UUID v4 は入力値のまま採用することを確認する。

    正常系:
        観点: 既存の request id を正規化せずそのまま使うこと
        期待値: 大文字の UUID v4 が変換されずに返ること
    """

    # Arrange
    request_id = str(uuid4()).upper()

    # Act
    actual = _resolve_request_id(request_id)

    # Assert
    assert actual == request_id


def test_resolve_request_id_generates_uuid4_when_header_value_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    UUID として解釈できない文字列では再生成することを確認する。

    異常系:
        観点: 不正な request id をそのまま採用しないこと
        期待値: 固定 UUID v4 が返ること
    """

    # Arrange
    generated_request_id = UUID("00000000-0000-4000-8000-000000000003")
    monkeypatch.setattr(middleware, "uuid4", lambda: generated_request_id)

    # Act
    actual = _resolve_request_id("not-a-uuid")

    # Assert
    assert actual == str(generated_request_id)


def test_resolve_request_id_generates_uuid4_when_uuid_version_is_not_4(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    UUID 形式でも v4 以外なら再生成することを確認する。

    異常系/回帰:
        観点: OpenAPI の UUID v4 要件から外れる値を拒否すること
        期待値: v1 UUID ではなく固定 UUID v4 が返ること
    """

    # Arrange
    request_id = str(uuid1())
    generated_request_id = UUID("00000000-0000-4000-8000-000000000004")
    monkeypatch.setattr(middleware, "uuid4", lambda: generated_request_id)

    # Act
    actual = _resolve_request_id(request_id)

    # Assert
    assert actual == str(generated_request_id)


def test_middleware_sets_generated_request_id_to_context_and_response_when_header_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    ヘッダー未指定時に生成値が本文とレスポンスヘッダーへ入ることを確認する。

    正常系:
        観点: 生成された request id が一貫して使われること
        期待値: 本文とレスポンスヘッダーが同じ UUID v4 であること
    """

    # Arrange
    generated_request_id = UUID("00000000-0000-4000-8000-000000000005")
    monkeypatch.setattr(middleware, "uuid4", lambda: generated_request_id)
    client = TestClient(_create_app())

    # Act
    response = client.get("/request-id")

    # Assert
    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER_NAME] == str(generated_request_id)
    assert response.json()["request_id"] == str(generated_request_id)


def test_middleware_keeps_valid_request_id_in_context_and_response() -> None:
    """
    有効な UUID v4 が本文とレスポンスヘッダーへそのまま流れることを確認する。

    正常系/回帰:
        観点: 既存の request id を変えずに downstream へ渡すこと
        期待値: 本文とレスポンスヘッダーが入力値と一致すること
    """

    # Arrange
    request_id = str(uuid4()).upper()
    client = TestClient(_create_app())

    # Act
    response = client.get(
        "/request-id",
        headers={REQUEST_ID_HEADER_NAME: request_id},
    )

    # Assert
    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER_NAME] == request_id
    assert response.json()["request_id"] == request_id


def test_middleware_replaces_invalid_request_id_in_context_and_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    不正なヘッダー値では新しい UUID v4 へ置き換えることを確認する。

    異常系/回帰:
        観点: 不正な request id が本文とレスポンスへ残らないこと
        期待値: 固定 UUID v4 が本文とレスポンスヘッダーへ入ること
    """

    # Arrange
    generated_request_id = UUID("00000000-0000-4000-8000-000000000006")
    monkeypatch.setattr(middleware, "uuid4", lambda: generated_request_id)
    client = TestClient(_create_app())

    # Act
    response = client.get(
        "/request-id",
        headers={REQUEST_ID_HEADER_NAME: "broken-request-id"},
    )

    # Assert
    assert response.status_code == 200
    assert response.headers[REQUEST_ID_HEADER_NAME] == str(generated_request_id)
    assert response.json()["request_id"] == str(generated_request_id)


def test_middleware_overrides_existing_response_header_without_duplication() -> None:
    """
    downstream が同名ヘッダーを設定しても最終値を 1 つに保つことを確認する。

    回帰:
        観点: ミドルウェアが重複ヘッダーを残さないこと
        期待値: `X-REQUEST-ID` が 1 つだけ存在し入力値と一致すること
    """

    # Arrange
    request_id = str(uuid4()).upper()
    client = TestClient(_create_app(response_header_value="stale-value"))

    # Act
    response = client.get(
        "/request-id",
        headers={REQUEST_ID_HEADER_NAME: request_id},
    )
    header_values = [
        value
        for name, value in response.headers.multi_items()
        if name.lower() == REQUEST_ID_HEADER_NAME.lower()
    ]

    # Assert
    assert response.status_code == 200
    assert header_values == [request_id]
    assert response.json()["request_id"] == request_id


def test_middleware_resets_request_context_after_request_completion() -> None:
    """
    リクエスト完了後に request_id のコンテキストが元へ戻ることを確認する。

    回帰:
        観点: request_id が次の処理へ漏れないこと
        期待値: リクエスト中は値が見え、完了後は `None` に戻ること
    """

    # Arrange
    request_id = str(uuid4())
    observed_request_ids: list[str | None] = []

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        observed_request_ids.append(request_id_var.get())
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [],
            },
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            },
        )

    async def receive() -> Message:
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    async def send(_: Message) -> None:
        return None

    scope = _build_http_scope(
        headers=[
            (
                b"x-request-id",
                request_id.encode("latin-1"),
            ),
        ],
    )
    middleware_app = XRequestIdMiddleware(app)

    # Act
    asyncio.run(middleware_app(scope, receive, send))

    # Assert
    assert observed_request_ids == [request_id]
    assert request_id_var.get() is None


def test_middleware_passes_through_non_http_scope_without_mutating_request_context() -> None:
    """
    HTTP 以外の scope では request_id を変更せず素通しすることを確認する。

    回帰:
        観点: WebSocket などでは request_id を汚染しないこと
        期待値: downstream から見える request_id が `None` のままであること
    """

    # Arrange
    observed_request_ids: list[str | None] = []
    observed_scope_types: list[str] = []

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        observed_scope_types.append(scope["type"])
        observed_request_ids.append(request_id_var.get())

    async def receive() -> Message:
        return {"type": "websocket.disconnect", "code": 1000}

    async def send(_: Message) -> None:
        return None

    scope: Scope = {
        "type": "websocket",
        "headers": [],
    }
    middleware_app = XRequestIdMiddleware(app)

    # Act
    asyncio.run(middleware_app(scope, receive, send))

    # Assert
    assert observed_scope_types == ["websocket"]
    assert observed_request_ids == [None]
    assert request_id_var.get() is None
