"""provider 群の単体テスト。"""

from __future__ import annotations

import pytest
import pytest_asyncio

from core.adapters.outbound.sqlalchemy.database import clear_engine_cache, init_db
from core.adapters.outbound.sqlalchemy.liver_repository import SqlAlchemyLiverRepository
from core.application.ports.outbound import LiverRepository
from core.providers import get_db_session, get_engine, get_liver_repository
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
