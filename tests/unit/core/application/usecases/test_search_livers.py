"""SearchLiversUsecase の単体テスト。"""

from __future__ import annotations

import pytest

from core.application.usecases import SearchLiversUsecase
from tests.unit.core.application.usecases.conftest import create_summary_entity


@pytest.mark.asyncio
async def test_execute_returns_repository_result(fake_repository) -> None:
    """
    execute が Repository の検索結果をそのまま返すことを確認する。

    正常系:
        観点: UseCase が余計な変換を挟まず検索結果を返すこと
        期待値: items と total が Repository と一致すること
    """

    # Arrange
    fake_repository.search_result = ([create_summary_entity()], 1)
    usecase = SearchLiversUsecase(fake_repository)

    # Act
    items, total = await usecase.execute(query="美兎", page=3, limit=10)

    # Assert
    assert total == 1
    assert [item.name for item in items] == ["月ノ美兎"]
    assert fake_repository.search_calls == [
        {"query": "美兎", "page": 3, "limit": 10},
    ]


@pytest.mark.asyncio
async def test_execute_returns_empty_result_when_repository_returns_no_match(
    fake_repository,
) -> None:
    """
    検索結果がない場合に空の一覧を返すことを確認する。

    正常系:
        観点: ヒットなしでも UseCase が安全に空結果を返すこと
        期待値: items は空で total は 0 であること
    """

    # Arrange
    fake_repository.search_result = ([], 0)
    usecase = SearchLiversUsecase(fake_repository)

    # Act
    items, total = await usecase.execute(query="該当なし")

    # Assert
    assert items == []
    assert total == 0