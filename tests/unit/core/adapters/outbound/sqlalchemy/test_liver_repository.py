"""SqlAlchemyLiverRepository の単体テスト。"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.adapters.outbound.sqlalchemy.database import (
    build_session_factory,
    clear_engine_cache,
    get_engine,
    init_db,
)
from core.adapters.outbound.sqlalchemy.liver_repository import SqlAlchemyLiverRepository
from core.adapters.outbound.sqlalchemy.models import (
    LiverAliasRecord,
    LiverColorRecord,
    LiverRecord,
)
from core.domain.entities import AliasTypeEnum, BranchEnum, LiverStatusEnum

SQLITE_IN_MEMORY_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(autouse=True)
async def reset_engine_state() -> None:
    """テストごとに engine キャッシュを初期化する。"""

    await clear_engine_cache()
    yield
    await clear_engine_cache()


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """初期化済みの SQLite in-memory session を返す。"""

    engine = get_engine(SQLITE_IN_MEMORY_URL)
    await init_db(engine)
    session_factory = build_session_factory(engine)

    async with session_factory() as session:
        yield session


def _dt(day: int, hour: int = 0) -> datetime:
    """UTC 固定の datetime を生成する。"""

    return datetime(2026, 1, day, hour, tzinfo=UTC)


def _create_alias_record(
    *,
    alias_id: str,
    liver_id: str,
    alias: str,
    alias_type: AliasTypeEnum = AliasTypeEnum.NICKNAME,
    locale: str | None = "ja",
) -> LiverAliasRecord:
    """テスト用の別名レコードを生成する。"""

    return LiverAliasRecord(
        id=alias_id,
        liver_id=liver_id,
        alias=alias,
        alias_type=alias_type,
        locale=locale,
    )


def _create_color_record(
    *,
    color_id: str,
    liver_id: str,
    hex_code: str,
    updated_at: datetime,
    is_current: bool,
    display_name: str | None = None,
) -> LiverColorRecord:
    """テスト用のカラー履歴レコードを生成する。"""

    return LiverColorRecord(
        id=color_id,
        liver_id=liver_id,
        hex=hex_code,
        r=int(hex_code[1:3], 16),
        g=int(hex_code[3:5], 16),
        b=int(hex_code[5:7], 16),
        display_name=display_name,
        is_official=True,
        source="official",
        source_url="https://example.com/colors",
        note=None,
        updated_at=updated_at,
        is_current=is_current,
    )


def _create_liver_record(
    *,
    liver_id: str,
    name: str,
    kana_name: str | None,
    english_name: str | None,
    branch: BranchEnum | None,
    generation: str | None,
    status: LiverStatusEnum,
    aliases: list[LiverAliasRecord] | None = None,
    colors: list[LiverColorRecord] | None = None,
    debuted_at: date | None = None,
    retired_at: date | None = None,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
) -> LiverRecord:
    """テスト用のライバーレコードを生成する。"""

    created = created_at or _dt(1)
    updated = updated_at or _dt(2)
    return LiverRecord(
        id=liver_id,
        name=name,
        kana_name=kana_name,
        english_name=english_name,
        branch=branch,
        generation=generation,
        status=status,
        debuted_at=debuted_at,
        retired_at=retired_at,
        created_at=created,
        updated_at=updated,
        aliases=aliases or [],
        colors=colors or [],
    )


async def _save_records(session: AsyncSession, *records: LiverRecord) -> None:
    """レコード群をまとめて保存する。"""

    session.add_all(list(records))
    await session.commit()


@pytest.mark.asyncio
async def test_find_all_returns_empty_result_when_no_records(
    db_session: AsyncSession,
) -> None:
    """
    find_all がデータなしでは空結果を返すことを確認する。

    正常系:
        観点: 保存データがなくても一覧取得が安全に動作すること
        期待値: items は空で total は 0 であること
    """

    # Arrange
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    items, total = await repository.find_all()

    # Assert
    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_find_all_filters_by_branch_and_status(
    db_session: AsyncSession,
) -> None:
    """
    find_all が branch と status で絞り込めることを確認する。

    正常系:
        観点: 複数条件を組み合わせた一覧取得ができること
        期待値: 条件に一致するライバーだけが返ること
    """

    # Arrange
    await _save_records(
        db_session,
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000011",
            name="JP Active",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.JP,
            generation="1期生",
            status=LiverStatusEnum.ACTIVE,
        ),
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000012",
            name="JP Retired",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.JP,
            generation="1期生",
            status=LiverStatusEnum.RETIRED,
        ),
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000013",
            name="EN Active",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.EN,
            generation="Wave 1",
            status=LiverStatusEnum.ACTIVE,
        ),
    )
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    items, total = await repository.find_all(
        branch=BranchEnum.JP,
        status=LiverStatusEnum.ACTIVE,
    )

    # Assert
    assert total == 1
    assert [item.name for item in items] == ["JP Active"]


@pytest.mark.asyncio
async def test_find_all_applies_paging_and_stable_sort(
    db_session: AsyncSession,
) -> None:
    """
    find_all が名前と ID による安定ソートの上でページングすることを確認する。

    正常系:
        観点: 同名データを含んでも順序が安定し、offset/limit が効くこと
        期待値: 2 ページ目 1 件取得で 2 番目の Alpha が返ること
    """

    # Arrange
    await _save_records(
        db_session,
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000021",
            name="Alpha",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.JP,
            generation=None,
            status=LiverStatusEnum.ACTIVE,
        ),
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000022",
            name="Alpha",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.JP,
            generation=None,
            status=LiverStatusEnum.ACTIVE,
        ),
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000023",
            name="Beta",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.JP,
            generation=None,
            status=LiverStatusEnum.ACTIVE,
        ),
    )
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    items, total = await repository.find_all(page=2, limit=1)

    # Assert
    assert total == 3
    assert [str(item.id) for item in items] == [
        "00000000-0000-0000-0000-000000000022",
    ]


@pytest.mark.asyncio
async def test_find_by_id_returns_entity_when_found(
    db_session: AsyncSession,
) -> None:
    """
    find_by_id が詳細情報と現在色を返すことを確認する。

    正常系:
        観点: 別名と色履歴を含む詳細エンティティへ変換できること
        期待値: 該当ライバーが返り、current_color は is_current=True の色になること
    """

    # Arrange
    liver_id = "00000000-0000-0000-0000-000000000031"
    current_color = _create_color_record(
        color_id="00000000-0000-0000-0000-000000000032",
        liver_id=liver_id,
        hex_code="#19A0E6",
        updated_at=_dt(3),
        is_current=True,
        display_name="公式色",
    )
    old_non_current_color = _create_color_record(
        color_id="00000000-0000-0000-0000-000000000033",
        liver_id=liver_id,
        hex_code="#222222",
        updated_at=_dt(5),
        is_current=False,
        display_name="旧色",
    )
    alias = _create_alias_record(
        alias_id="00000000-0000-0000-0000-000000000034",
        liver_id=liver_id,
        alias="委員長",
    )
    await _save_records(
        db_session,
        _create_liver_record(
            liver_id=liver_id,
            name="月ノ美兎",
            kana_name="つきのみと",
            english_name="Tsukino Mito",
            branch=BranchEnum.JP,
            generation="1期生",
            status=LiverStatusEnum.ACTIVE,
            aliases=[alias],
            colors=[current_color, old_non_current_color],
            debuted_at=date(2018, 2, 8),
        ),
    )
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    entity = await repository.find_by_id(UUID(liver_id))

    # Assert
    assert entity is not None
    assert entity.name == "月ノ美兎"
    assert [item.alias for item in entity.aliases] == ["委員長"]
    assert entity.current_color is not None
    assert entity.current_color.hex == "#19A0E6"


@pytest.mark.asyncio
async def test_find_by_id_returns_none_when_not_found(
    db_session: AsyncSession,
) -> None:
    """
    find_by_id が未登録 ID では None を返すことを確認する。

    正常系:
        観点: 未登録データに対して not found を安全に表現できること
        期待値: None が返ること
    """

    # Arrange
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    entity = await repository.find_by_id(
        UUID("00000000-0000-0000-0000-000000000041"),
    )

    # Assert
    assert entity is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("query", "expected_name"),
    [
        ("月ノ美兎", "月ノ美兎"),
        ("つきのみと", "月ノ美兎"),
        ("Tsukino", "月ノ美兎"),
        ("委員長", "月ノ美兎"),
    ],
)
async def test_search_matches_name_related_fields(
    db_session: AsyncSession,
    query: str,
    expected_name: str,
) -> None:
    """
    search が name / kana_name / english_name / alias の各項目にマッチすることを確認する。

    正常系:
        観点: 検索対象の主要フィールド全体を横断して一致判定できること
        期待値: どの入力でも対象ライバー 1 件が返ること
    """

    # Arrange
    liver_id = "00000000-0000-0000-0000-000000000051"
    await _save_records(
        db_session,
        _create_liver_record(
            liver_id=liver_id,
            name="月ノ美兎",
            kana_name="つきのみと",
            english_name="Tsukino Mito",
            branch=BranchEnum.JP,
            generation="1期生",
            status=LiverStatusEnum.ACTIVE,
            aliases=[
                _create_alias_record(
                    alias_id="00000000-0000-0000-0000-000000000052",
                    liver_id=liver_id,
                    alias="委員長",
                ),
            ],
        ),
        _create_liver_record(
            liver_id="00000000-0000-0000-0000-000000000053",
            name="静凛",
            kana_name="しずかりん",
            english_name="Shizuka Rin",
            branch=BranchEnum.JP,
            generation="1期生",
            status=LiverStatusEnum.ACTIVE,
        ),
    )
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    items, total = await repository.search(query=query, page=1, limit=10)

    # Assert
    assert total == 1
    assert [item.name for item in items] == [expected_name]


@pytest.mark.asyncio
async def test_search_returns_empty_result_for_blank_query(
    db_session: AsyncSession,
) -> None:
    """
    search が空白だけの query では空結果を返すことを確認する。

    境界値:
        観点: 空白入力を検索せず早期リターンすること
        期待値: items は空で total は 0 であること
    """

    # Arrange
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    items, total = await repository.search(query="   ")

    # Assert
    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_find_current_color_returns_current_color_when_found(
    db_session: AsyncSession,
) -> None:
    """
    find_current_color が現在色を返すことを確認する。

    正常系:
        観点: is_current=True の色履歴を取得できること
        期待値: 該当ライバーの現在色が返ること
    """

    # Arrange
    liver_id = "00000000-0000-0000-0000-000000000061"
    await _save_records(
        db_session,
        _create_liver_record(
            liver_id=liver_id,
            name="壱百満天原サロメ",
            kana_name="ひゃくまんてんばらさろめ",
            english_name="Hyakumantenbara Salome",
            branch=BranchEnum.JP,
            generation=None,
            status=LiverStatusEnum.ACTIVE,
            colors=[
                _create_color_record(
                    color_id="00000000-0000-0000-0000-000000000062",
                    liver_id=liver_id,
                    hex_code="#FFB6C1",
                    updated_at=_dt(4),
                    is_current=True,
                    display_name="Pink",
                ),
            ],
        ),
    )
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    current_color = await repository.find_current_color(UUID(liver_id))

    # Assert
    assert current_color is not None
    assert current_color.hex == "#FFB6C1"
    assert current_color.display_name == "Pink"


@pytest.mark.asyncio
async def test_find_current_color_returns_none_when_not_found(
    db_session: AsyncSession,
) -> None:
    """
    find_current_color が現在色未登録では None を返すことを確認する。

    正常系:
        観点: 現在色を持たないライバーでも安全に問い合わせできること
        期待値: None が返ること
    """

    # Arrange
    liver_id = "00000000-0000-0000-0000-000000000071"
    await _save_records(
        db_session,
        _create_liver_record(
            liver_id=liver_id,
            name="Colorless",
            kana_name=None,
            english_name=None,
            branch=BranchEnum.JP,
            generation=None,
            status=LiverStatusEnum.ACTIVE,
        ),
    )
    repository = SqlAlchemyLiverRepository(db_session)

    # Act
    current_color = await repository.find_current_color(UUID(liver_id))

    # Assert
    assert current_color is None
