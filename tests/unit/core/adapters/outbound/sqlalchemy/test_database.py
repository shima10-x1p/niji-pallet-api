"""SQLAlchemy database モジュールの単体テスト。"""

from __future__ import annotations

import pytest
import pytest_asyncio
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncEngine

from core.adapters.outbound.sqlalchemy.database import (
    build_session_factory,
    clear_engine_cache,
    get_engine,
    init_db,
)

SQLITE_IN_MEMORY_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(autouse=True)
async def reset_engine_state() -> None:
    """テストごとに engine キャッシュを初期化する。"""

    await clear_engine_cache()
    yield
    await clear_engine_cache()


@pytest.mark.asyncio
async def test_get_engine_reuses_cached_engine_for_same_url() -> None:
    """
    get_engine が同じ URL では同一 engine を再利用することを確認する。

    正常系:
        観点: engine のキャッシュが URL 単位で効くこと
        期待値: 同一 URL の 2 回の取得結果が同一オブジェクトであること
    """

    # Arrange

    # Act
    first_engine = get_engine(SQLITE_IN_MEMORY_URL)
    second_engine = get_engine(SQLITE_IN_MEMORY_URL)

    # Assert
    assert first_engine is second_engine


@pytest.mark.asyncio
async def test_clear_engine_cache_disposes_engine_and_recreates_it() -> None:
    """
    clear_engine_cache が既存 engine を破棄してキャッシュを空にすることを確認する。

    回帰:
        観点: キャッシュクリア時に dispose が呼ばれ、次回取得で新しい engine になること
        期待値: dispose が 1 回 await され、取得した engine が再生成されること
    """

    # Arrange
    cached_engine = get_engine(SQLITE_IN_MEMORY_URL)
    disposed_engine_ids: list[int] = []
    original_dispose = AsyncEngine.dispose

    async def tracked_dispose(self: AsyncEngine, close: bool = True) -> None:
        disposed_engine_ids.append(id(self))
        await original_dispose(self, close=close)

    AsyncEngine.dispose = tracked_dispose

    try:
        # Act
        await clear_engine_cache()
        recreated_engine = get_engine(SQLITE_IN_MEMORY_URL)
    finally:
        AsyncEngine.dispose = original_dispose

    # Assert
    assert disposed_engine_ids == [id(cached_engine)]
    assert recreated_engine is not cached_engine


@pytest.mark.asyncio
async def test_init_db_creates_required_tables() -> None:
    """
    init_db が必要テーブルを作成することを確認する。

    正常系:
        観点: 初期化で ORM モデルのテーブルがすべて作成されること
        期待値: livers / liver_aliases / liver_colors が存在すること
    """

    # Arrange
    engine = get_engine(SQLITE_IN_MEMORY_URL)

    # Act
    await init_db(engine)
    async with engine.begin() as connection:
        table_names = await connection.run_sync(
            lambda sync_connection: inspect(sync_connection).get_table_names(),
        )

    # Assert
    assert {"livers", "liver_aliases", "liver_colors"}.issubset(set(table_names))


@pytest.mark.asyncio
async def test_build_session_factory_creates_async_session_bound_to_engine() -> None:
    """
    build_session_factory が指定 engine に紐づく AsyncSession を作ることを確認する。

    正常系:
        観点: session factory から生成した session が引数の engine を利用すること
        期待値: session.bind が指定 engine であること
    """

    # Arrange
    engine = get_engine(SQLITE_IN_MEMORY_URL)
    session_factory = build_session_factory(engine)

    # Act
    async with session_factory() as session:
        bound_engine = session.bind

    # Assert
    assert bound_engine is engine
