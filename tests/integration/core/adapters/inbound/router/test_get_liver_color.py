"""GET /v1/livers/{liverId}/color の integration テスト。"""

from __future__ import annotations

from uuid import UUID

import pytest

from core.providers import get_get_liver_color_usecase
from main import app
from tests.integration.core.adapters.inbound.router.conftest import (
    StubGetLiverColorUsecase,
)


@pytest.mark.asyncio
async def test_get_liver_color_returns_color_when_registered(
    client,
    override_get_liver_color_usecase,
) -> None:
    """
    色登録済みのライバーではカラー情報を返すことを確認する。

    正常系:
        観点: Router が LiverColor をそのまま返せること
        期待値: 200 かつ hex が期待値であること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000402")

    # Act
    response = await client.get(f"/v1/livers/{liver_id}/color")

    # Assert
    assert response.status_code == 200
    assert response.json()["hex"] == "#19A0E6"
    assert override_get_liver_color_usecase.calls == [liver_id]


@pytest.mark.asyncio
async def test_get_liver_color_returns_null_when_color_is_missing(client) -> None:
    """
    色未登録だがライバーが存在する場合に 200 null を返すことを確認する。

    正常系:
        観点: null 応答で色未登録を表現できること
        期待値: HTTP 200 かつ JSON body が null であること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000402")
    app.dependency_overrides[get_get_liver_color_usecase] = lambda: StubGetLiverColorUsecase(
        None,
    )

    # Act
    response = await client.get(f"/v1/livers/{liver_id}/color")

    # Assert
    assert response.status_code == 200
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_liver_color_returns_error_response_when_not_found(client) -> None:
    """
    未登録ライバーでは ErrorResponse 形式の 404 を返すことを確認する。

    異常系:
        観点: NotFoundError が 404 の共通エラーフォーマットへ変換されること
        期待値: code が NOT_FOUND で message に対象 ID が含まれること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000599")
    app.dependency_overrides[get_get_liver_color_usecase] = lambda: (
        StubGetLiverColorUsecase(None, exists=False)
    )

    # Act
    response = await client.get(f"/v1/livers/{liver_id}/color")

    # Assert
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert str(liver_id) in response.json()["error"]["message"]