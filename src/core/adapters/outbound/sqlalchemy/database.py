"""SQLAlchemy の engine と session を管理する。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.adapters.outbound.sqlalchemy.models import Base

_ENGINES: dict[str, AsyncEngine] = {}

def get_engine(database_url: str) -> AsyncEngine:
    """データベース URL ごとに AsyncEngine を再利用する。"""

    if database_url in _ENGINES:
        return _ENGINES[database_url]

    engine = create_async_engine(database_url)

    if database_url.startswith("sqlite"):

        @event.listens_for(engine.sync_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection: Any, _: Any) -> None:
            """SQLite の外部キー制約を有効化する。"""

            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    _ENGINES[database_url] = engine
    return engine


async def clear_engine_cache() -> None:
    """テスト用に engine を破棄してキャッシュをクリアする。"""

    for engine in _ENGINES.values():
        await engine.dispose()
    _ENGINES.clear()


def build_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """AsyncSession を生成するファクトリーを返す。"""

    return async_sessionmaker(engine, expire_on_commit=False)


async def init_db(engine: AsyncEngine) -> None:
    """必要なテーブルを作成する。"""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
