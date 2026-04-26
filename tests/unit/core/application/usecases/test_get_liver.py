"""GetLiverUsecase の単体テスト。"""

from __future__ import annotations

from uuid import UUID

import pytest

from core.application.usecases import GetLiverUsecase
from core.shared.exceptions import NotFoundError
from tests.unit.core.application.usecases.conftest import create_liver_entity


@pytest.mark.asyncio
async def test_execute_returns_liver_when_repository_finds_one(
    fake_repository,
) -> None:
    """
    該当ライバーが存在するときに詳細を返すことを確認する。

    正常系:
        観点: Repository から取得したエンティティをそのまま返すこと
        期待値: 返却された ID と名前がサンプルと一致すること
    """

    # Arrange
    expected = create_liver_entity()
    fake_repository.find_by_id_result = expected
    usecase = GetLiverUsecase(fake_repository)

    # Act
    actual = await usecase.execute(expected.id)

    # Assert
    assert actual == expected
    assert fake_repository.find_by_id_calls == [expected.id]


@pytest.mark.asyncio
async def test_execute_raises_not_found_when_repository_returns_none(
    fake_repository,
) -> None:
    """
    該当ライバーが存在しないときに NotFoundError を送出することを確認する。

    異常系:
        観点: UseCase が未発見を application 例外へ変換すること
        期待値: NotFoundError に対象 ID が含まれること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000299")
    usecase = GetLiverUsecase(fake_repository)

    # Act / Assert
    with pytest.raises(NotFoundError, match=str(liver_id)):
        await usecase.execute(liver_id)