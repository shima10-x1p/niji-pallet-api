"""provider 群の単体テスト。"""

from __future__ import annotations

from unittest.mock import create_autospec

import pytest
import pytest_asyncio

from core.adapters.outbound.sqlalchemy.database import (
    clear_engine_cache,
    init_db,
)
from core.adapters.outbound.sqlalchemy.liver_repository import SqlAlchemyLiverRepository
from core.application.ports.outbound import LiverRepository
from core.application.usecases import (
    GetLiverColorUsecase,
    GetLiverUsecase,
    ListLiversUsecase,
    SearchLiversUsecase,
)
from core.providers import (
    get_db_session,
    get_engine,
    get_get_liver_color_usecase,
    get_get_liver_usecase,
    get_list_livers_usecase,
    get_liver_repository,
    get_search_livers_usecase,
)
from core.shared.settings import AppSettings

SQLITE_IN_MEMORY_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(autouse=True)
async def reset_engine_state() -> None:
    """テストごとに engine キャッシュを初期化する。"""

    await clear_engine_cache()
    yield
    await clear_engine_cache()


@pytest.mark.asyncio
async def test_get_liver_repository_returns_sqlalchemy_repository_as_port() -> None:
    """
    get_liver_repository が LiverRepository 抽象として扱える実装を返すことを確認する。

    正常系:
        観点: provider から返る Repository がポート契約を満たしていること
        期待値: SqlAlchemyLiverRepository かつ LiverRepository として扱えること
    """

    # Arrange
    settings = AppSettings(database_url=SQLITE_IN_MEMORY_URL)
    engine = get_engine(settings)
    await init_db(engine)
    session_generator = get_db_session(engine)
    session = await anext(session_generator)

    try:
        # Act
        repository = get_liver_repository(session)

        # Assert
        assert isinstance(repository, SqlAlchemyLiverRepository)
        assert isinstance(repository, LiverRepository)
    finally:
        await session_generator.aclose()


def test_get_list_livers_usecase_returns_expected_usecase_instance() -> None:
    """
    get_list_livers_usecase が ListLiversUsecase を返すことを確認する。

    正常系:
        観点: provider が一覧取得用ユースケースを組み立てられること
        期待値: 返却値が ListLiversUsecase のインスタンスであること
    """

    # Arrange
    repository = create_autospec(LiverRepository, instance=True)

    # Act
    usecase = get_list_livers_usecase(repository)

    # Assert
    assert isinstance(usecase, ListLiversUsecase)


def test_get_search_livers_usecase_returns_expected_usecase_instance() -> None:
    """
    get_search_livers_usecase が SearchLiversUsecase を返すことを確認する。

    正常系:
        観点: provider が検索用ユースケースを組み立てられること
        期待値: 返却値が SearchLiversUsecase のインスタンスであること
    """

    # Arrange
    repository = create_autospec(LiverRepository, instance=True)

    # Act
    usecase = get_search_livers_usecase(repository)

    # Assert
    assert isinstance(usecase, SearchLiversUsecase)


def test_get_get_liver_usecase_returns_expected_usecase_instance() -> None:
    """
    get_get_liver_usecase が GetLiverUsecase を返すことを確認する。

    正常系:
        観点: provider が詳細取得用ユースケースを組み立てられること
        期待値: 返却値が GetLiverUsecase のインスタンスであること
    """

    # Arrange
    repository = create_autospec(LiverRepository, instance=True)

    # Act
    usecase = get_get_liver_usecase(repository)

    # Assert
    assert isinstance(usecase, GetLiverUsecase)


def test_get_get_liver_color_usecase_returns_expected_usecase_instance() -> None:
    """
    get_get_liver_color_usecase が GetLiverColorUsecase を返すことを確認する。

    正常系:
        観点: provider が色取得用ユースケースを組み立てられること
        期待値: 返却値が GetLiverColorUsecase のインスタンスであること
    """

    # Arrange
    repository = create_autospec(LiverRepository, instance=True)

    # Act
    usecase = get_get_liver_color_usecase(repository)

    # Assert
    assert isinstance(usecase, GetLiverColorUsecase)
