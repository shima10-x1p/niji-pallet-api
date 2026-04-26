"""GET /v1/livers/{liverId} の integration テスト。"""

from __future__ import annotations

from uuid import UUID

import pytest

from core.providers import get_get_liver_usecase
from main import app
from tests.integration.core.adapters.inbound.router.conftest import (
    StubGetLiverUsecase,
)


@pytest.mark.asyncio
async def test_get_liver_returns_liver_detail(
    client,
    override_get_liver_usecase,
) -> None:
    """
    ライバー詳細 API が詳細情報を返すことを確認する。

    正常系:
        観点: alias や current_color を含む詳細レスポンスへ整形できること
        期待値: 200 かつ aliases[0].alias が委員長であること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000402")

    # Act
    response = await client.get(f"/v1/livers/{liver_id}")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "月ノ美兎"
    assert body["aliases"][0]["alias"] == "委員長"
    assert override_get_liver_usecase.calls == [liver_id]


@pytest.mark.asyncio
async def test_get_liver_returns_error_response_when_not_found(client) -> None:
    """
    未登録ライバーで ErrorResponse 形式の 404 を返すことを確認する。

    異常系:
        観点: NotFoundError が共通エラーフォーマットへ変換されること
        期待値: code が NOT_FOUND で message に対象 ID が含まれること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000499")
    app.dependency_overrides[get_get_liver_usecase] = lambda: StubGetLiverUsecase()

    # Act
    response = await client.get(f"/v1/livers/{liver_id}")

    # Assert
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert str(liver_id) in response.json()["error"]["message"]