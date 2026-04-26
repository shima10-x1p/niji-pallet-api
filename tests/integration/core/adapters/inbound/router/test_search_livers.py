"""GET /v1/livers/search の integration テスト。"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_search_livers_returns_items_when_query_is_valid(
    client,
    override_search_livers_usecase,
) -> None:
    """
    検索 API が結果を返すことを確認する。

    正常系:
        観点: 検索キーワードを UseCase へ渡し、一覧レスポンスへ整形できること
        期待値: 200 かつ q/page/limit が UseCase へ渡ること
    """

    # Arrange

    # Act
    response = await client.get(
        "/v1/livers/search",
        params={"q": "美兎", "page": 3, "limit": 7},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "月ノ美兎"
    assert override_search_livers_usecase.calls == [
        {"query": "美兎", "page": 3, "limit": 7},
    ]


@pytest.mark.asyncio
async def test_search_livers_returns_error_response_when_query_is_missing(
    client,
) -> None:
    """
    q 未指定時に ErrorResponse 形式の 422 を返すことを確認する。

    異常系:
        観点: RequestValidationError が共通エラーフォーマットへ変換されること
        期待値: code が VALIDATION_ERROR で message に query.q が含まれること
    """

    # Arrange

    # Act
    response = await client.get("/v1/livers/search")

    # Assert
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert "query.q" in response.json()["error"]["message"]