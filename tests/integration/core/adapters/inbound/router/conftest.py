"""Router integration テスト用の共通 fixture と stub。"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from datetime import UTC, date, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from core.domain.entities import (
    AliasTypeEnum,
    BranchEnum,
    LiverAliasEntity,
    LiverColorEntity,
    LiverEntity,
    LiverStatusEnum,
    LiverSummaryEntity,
)
from core.providers import (
    get_get_liver_color_usecase,
    get_get_liver_usecase,
    get_list_livers_usecase,
    get_search_livers_usecase,
)
from core.shared.exceptions import NotFoundError
from core.shared.settings import clear_settings_cache
from main import app


def _dt(day: int, hour: int = 0) -> datetime:
    """UTC 固定の datetime を生成する。"""

    return datetime(2026, 4, day, hour, tzinfo=UTC)


def create_color_entity(hex_code: str = "#19A0E6") -> LiverColorEntity:
    """テスト用のカラーエンティティを生成する。"""

    return LiverColorEntity(
        hex=hex_code,
        r=int(hex_code[1:3], 16),
        g=int(hex_code[3:5], 16),
        b=int(hex_code[5:7], 16),
        display_name="公式色",
        is_official=True,
        source="official_profile",
        source_url="https://example.com/colors",
        note=None,
        updated_at=_dt(1),
    )


def create_summary_entity() -> LiverSummaryEntity:
    """テスト用のライバー概要エンティティを生成する。"""

    return LiverSummaryEntity(
        id=UUID("00000000-0000-0000-0000-000000000401"),
        name="月ノ美兎",
        kana_name="つきのみと",
        english_name="Tsukino Mito",
        branch=BranchEnum.JP,
        generation="1期生",
        status=LiverStatusEnum.ACTIVE,
        current_color=create_color_entity(),
    )


def create_liver_entity() -> LiverEntity:
    """テスト用のライバー詳細エンティティを生成する。"""

    return LiverEntity(
        id=UUID("00000000-0000-0000-0000-000000000402"),
        name="月ノ美兎",
        kana_name="つきのみと",
        english_name="Tsukino Mito",
        branch=BranchEnum.JP,
        generation="1期生",
        status=LiverStatusEnum.ACTIVE,
        debuted_at=date(2018, 2, 8),
        retired_at=None,
        aliases=[
            LiverAliasEntity(
                id=UUID("00000000-0000-0000-0000-000000000403"),
                alias="委員長",
                alias_type=AliasTypeEnum.NICKNAME,
                locale="ja",
            ),
        ],
        current_color=create_color_entity(),
        created_at=_dt(2),
        updated_at=_dt(3),
    )


class StubListLiversUsecase:
    """一覧取得ルーター向けの stub usecase。"""

    def __init__(self, result: tuple[list[LiverSummaryEntity], int]) -> None:
        """返却値と呼び出し履歴を初期化する。"""

        self._result = result
        self.calls: list[dict[str, object]] = []

    async def execute(self, **kwargs: object) -> tuple[list[LiverSummaryEntity], int]:
        """呼び出し引数を保存して固定結果を返す。"""

        self.calls.append(kwargs)
        return self._result


class StubSearchLiversUsecase:
    """検索ルーター向けの stub usecase。"""

    def __init__(self, result: tuple[list[LiverSummaryEntity], int]) -> None:
        """返却値と呼び出し履歴を初期化する。"""

        self._result = result
        self.calls: list[dict[str, object]] = []

    async def execute(self, **kwargs: object) -> tuple[list[LiverSummaryEntity], int]:
        """呼び出し引数を保存して固定結果を返す。"""

        self.calls.append(kwargs)
        return self._result


class StubGetLiverUsecase:
    """詳細取得ルーター向けの stub usecase。"""

    def __init__(self, result: LiverEntity | None = None) -> None:
        """返却値と呼び出し履歴を初期化する。"""

        self._result = result
        self.calls: list[UUID] = []

    async def execute(self, liver_id: UUID) -> LiverEntity:
        """呼び出し ID を保存し、結果または例外を返す。"""

        self.calls.append(liver_id)
        if self._result is None:
            raise NotFoundError(str(liver_id))
        return self._result


class StubGetLiverColorUsecase:
    """色取得ルーター向けの stub usecase。"""

    def __init__(self, result: LiverColorEntity | None, *, exists: bool = True) -> None:
        """返却値と存在可否を初期化する。"""

        self._result = result
        self._exists = exists
        self.calls: list[UUID] = []

    async def execute(self, liver_id: UUID) -> LiverColorEntity | None:
        """呼び出し ID を保存し、結果または例外を返す。"""

        self.calls.append(liver_id)
        if not self._exists:
            raise NotFoundError(str(liver_id))
        return self._result


@pytest.fixture(autouse=True)
def reset_dependency_overrides(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """dependency_overrides と設定キャッシュを毎テスト初期化する。"""

    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    clear_settings_cache()
    app.dependency_overrides.clear()

    yield

    app.dependency_overrides.clear()
    clear_settings_cache()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """ASGITransport を使う非同期 HTTP クライアントを返す。"""

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client


@pytest.fixture
def override_list_livers_usecase() -> StubListLiversUsecase:
    """一覧取得 usecase の override を設定する。"""

    stub = StubListLiversUsecase(([create_summary_entity()], 1))
    app.dependency_overrides[get_list_livers_usecase] = lambda: stub
    return stub


@pytest.fixture
def override_search_livers_usecase() -> StubSearchLiversUsecase:
    """検索 usecase の override を設定する。"""

    stub = StubSearchLiversUsecase(([create_summary_entity()], 1))
    app.dependency_overrides[get_search_livers_usecase] = lambda: stub
    return stub


@pytest.fixture
def override_get_liver_usecase() -> StubGetLiverUsecase:
    """詳細取得 usecase の override を設定する。"""

    stub = StubGetLiverUsecase(create_liver_entity())
    app.dependency_overrides[get_get_liver_usecase] = lambda: stub
    return stub


@pytest.fixture
def override_get_liver_color_usecase() -> StubGetLiverColorUsecase:
    """色取得 usecase の override を設定する。"""

    stub = StubGetLiverColorUsecase(create_color_entity())
    app.dependency_overrides[get_get_liver_color_usecase] = lambda: stub
    return stub