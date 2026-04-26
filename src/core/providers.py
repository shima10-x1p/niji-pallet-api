"""FastAPI の Depends で利用する provider 群を定義する。"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from core.adapters.outbound.sqlalchemy.database import build_session_factory
from core.adapters.outbound.sqlalchemy.database import (
    get_engine as get_sqlalchemy_engine,
)
from core.adapters.outbound.sqlalchemy.liver_repository import SqlAlchemyLiverRepository
from core.application.ports.outbound import LiverRepository
from core.shared.settings import AppSettings, get_settings

type SettingsDependency = Annotated[AppSettings, Depends(get_settings)]


def get_engine(settings: SettingsDependency) -> AsyncEngine:
    """設定から AsyncEngine を解決する。"""

    return get_sqlalchemy_engine(settings.database_url)


type EngineDependency = Annotated[AsyncEngine, Depends(get_engine)]


async def get_db_session(
    engine: EngineDependency,
) -> AsyncGenerator[AsyncSession]:
    """1 リクエスト分の AsyncSession を払い出す。"""

    session_factory = build_session_factory(engine)
    async with session_factory() as session:
        yield session


type DbSessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_liver_repository(session: DbSessionDependency) -> LiverRepository:
    """SQLite を保存先に使うライバー Repository を返す。"""

    return SqlAlchemyLiverRepository(session)


type LiverRepositoryDependency = Annotated[
    LiverRepository,
    Depends(get_liver_repository),
]
