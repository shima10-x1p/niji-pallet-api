"""GetLiverColorUsecase の単体テスト。"""

from __future__ import annotations

from uuid import UUID

import pytest

from core.application.usecases import GetLiverColorUsecase
from core.shared.exceptions import NotFoundError
from tests.unit.core.application.usecases.conftest import (
    create_color_entity,
    create_liver_entity,
)


@pytest.mark.asyncio
async def test_execute_returns_current_color_without_fetching_liver(
    fake_repository,
) -> None:
    """
    現在色が見つかった場合は存在確認を追加で行わないことを確認する。

    正常系:
        観点: 余計な問い合わせを行わず現在色を返すこと
        期待値: find_by_id は呼ばれず現在色が返ること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000301")
    expected = create_color_entity()
    fake_repository.find_current_color_result = expected
    usecase = GetLiverColorUsecase(fake_repository)

    # Act
    actual = await usecase.execute(liver_id)

    # Assert
    assert actual == expected
    assert fake_repository.find_current_color_calls == [liver_id]
    assert fake_repository.find_by_id_calls == []


@pytest.mark.asyncio
async def test_execute_returns_none_when_liver_exists_but_color_is_missing(
    fake_repository,
) -> None:
    """
    色未登録だがライバーは存在する場合に None を返すことを確認する。

    正常系:
        観点: 色未登録とライバー不存在を区別できること
        期待値: find_by_id で存在確認後に None が返ること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000302")
    fake_repository.find_current_color_result = None
    fake_repository.find_by_id_result = create_liver_entity(liver_id=str(liver_id))
    usecase = GetLiverColorUsecase(fake_repository)

    # Act
    actual = await usecase.execute(liver_id)

    # Assert
    assert actual is None
    assert fake_repository.find_current_color_calls == [liver_id]
    assert fake_repository.find_by_id_calls == [liver_id]


@pytest.mark.asyncio
async def test_execute_raises_not_found_when_liver_and_color_are_missing(
    fake_repository,
) -> None:
    """
    ライバー自体が存在しない場合に NotFoundError を送出することを確認する。

    異常系:
        観点: 色未登録ではなくライバー不存在を application 例外で表現すること
        期待値: NotFoundError に対象 ID が含まれること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000303")
    usecase = GetLiverColorUsecase(fake_repository)

    # Act / Assert
    with pytest.raises(NotFoundError, match=str(liver_id)):
        await usecase.execute(liver_id)