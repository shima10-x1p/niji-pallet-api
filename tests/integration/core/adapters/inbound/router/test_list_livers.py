"""GET /v1/livers の integration テスト。"""

from __future__ import annotations

import pytest

from core.domain.entities import BranchEnum, LiverStatusEnum


@pytest.mark.asyncio
async def test_list_livers_returns_items_and_forwards_filters(
    client,
    override_list_livers_usecase,
) -> None:
    """
    一覧取得がレスポンス整形とクエリ引き渡しを行うことを確認する。

    正常系:
        観点: Query を UseCase へ渡し、HTTP レスポンスへ整形できること
        期待値: 200 かつ items[0] に current_color を含むこと
    """

    # Arrange

    # Act
    response = await client.get(
        "/v1/livers",
        params={
            "branch": "JP",
            "status": "retired",
            "page": 2,
            "limit": 5,
        },
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["limit"] == 5
    assert body["total"] == 1
    assert body["items"][0]["name"] == "月ノ美兎"
    assert body["items"][0]["current_color"]["hex"] == "#19A0E6"
    assert override_list_livers_usecase.calls == [
        {
            "branch": BranchEnum.JP,
            "generation": None,
            "status": LiverStatusEnum.RETIRED,
            "page": 2,
            "limit": 5,
        },
    ]