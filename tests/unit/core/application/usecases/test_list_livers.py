"""ListLiversUsecase の単体テスト。"""

from __future__ import annotations

import pytest

from core.application.usecases import ListLiversUsecase
from core.domain.entities import BranchEnum, LiverStatusEnum
from tests.unit.core.application.usecases.conftest import create_summary_entity


@pytest.mark.asyncio
async def test_execute_uses_active_when_status_is_omitted(
    fake_repository,
) -> None:
    """
    status 未指定時に ACTIVE が使われることを確認する。

    回帰:
        観点: OpenAPI 仕様どおり既定の活動状態で一覧取得されること
        期待値: Repository には ACTIVE が渡されること
    """

    # Arrange
    fake_repository.find_all_result = ([create_summary_entity()], 1)
    usecase = ListLiversUsecase(fake_repository)

    # Act
    items, total = await usecase.execute(
        branch=BranchEnum.JP,
        generation="1期生",
        page=2,
        limit=5,
    )

    # Assert
    assert total == 1
    assert [item.name for item in items] == ["月ノ美兎"]
    assert fake_repository.find_all_calls == [
        {
            "branch": BranchEnum.JP,
            "generation": "1期生",
            "status": LiverStatusEnum.ACTIVE,
            "page": 2,
            "limit": 5,
        },
    ]


@pytest.mark.asyncio
async def test_execute_preserves_explicit_status(fake_repository) -> None:
    """
    status を明示した場合はその値を維持することを確認する。

    正常系:
        観点: 呼び出し側が指定した絞り込み条件を上書きしないこと
        期待値: Repository へ RETIRED がそのまま渡ること
    """

    # Arrange
    fake_repository.find_all_result = ([], 0)
    usecase = ListLiversUsecase(fake_repository)

    # Act
    await usecase.execute(status=LiverStatusEnum.RETIRED)

    # Assert
    assert fake_repository.find_all_calls[-1]["status"] == LiverStatusEnum.RETIRED