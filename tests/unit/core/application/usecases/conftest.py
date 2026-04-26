"""UseCase テスト用の fake repository とサンプル生成関数。"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

import pytest

from core.application.ports.outbound import LiverRepository
from core.domain.entities import (
    AliasTypeEnum,
    BranchEnum,
    LiverAliasEntity,
    LiverColorEntity,
    LiverEntity,
    LiverStatusEnum,
    LiverSummaryEntity,
)


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


def create_summary_entity(
    *,
    liver_id: str = "00000000-0000-0000-0000-000000000101",
    name: str = "月ノ美兎",
    status: LiverStatusEnum = LiverStatusEnum.ACTIVE,
    current_color: LiverColorEntity | None = None,
) -> LiverSummaryEntity:
    """テスト用のライバー概要エンティティを生成する。"""

    return LiverSummaryEntity(
        id=UUID(liver_id),
        name=name,
        kana_name="つきのみと",
        english_name="Tsukino Mito",
        branch=BranchEnum.JP,
        generation="1期生",
        status=status,
        current_color=current_color,
    )


def create_liver_entity(
    *,
    liver_id: str = "00000000-0000-0000-0000-000000000201",
    current_color: LiverColorEntity | None = None,
) -> LiverEntity:
    """テスト用のライバー詳細エンティティを生成する。"""

    return LiverEntity(
        id=UUID(liver_id),
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
                id=UUID("00000000-0000-0000-0000-000000000202"),
                alias="委員長",
                alias_type=AliasTypeEnum.NICKNAME,
                locale="ja",
            ),
        ],
        current_color=current_color,
        created_at=_dt(2),
        updated_at=_dt(3),
    )


class FakeLiverRepository(LiverRepository):
    """UseCase テスト用の fake repository。"""

    def __init__(self) -> None:
        """戻り値と呼び出し履歴の保存先を初期化する。"""

        self.find_all_result: tuple[list[LiverSummaryEntity], int] = ([], 0)
        self.find_by_id_result: LiverEntity | None = None
        self.search_result: tuple[list[LiverSummaryEntity], int] = ([], 0)
        self.find_current_color_result: LiverColorEntity | None = None
        self.find_all_calls: list[dict[str, object]] = []
        self.find_by_id_calls: list[UUID] = []
        self.search_calls: list[dict[str, object]] = []
        self.find_current_color_calls: list[UUID] = []

    async def find_all(
        self,
        *,
        branch: BranchEnum | None = None,
        generation: str | None = None,
        status: LiverStatusEnum | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """呼び出し引数を保存して一覧結果を返す。"""

        self.find_all_calls.append(
            {
                "branch": branch,
                "generation": generation,
                "status": status,
                "page": page,
                "limit": limit,
            },
        )
        return self.find_all_result

    async def find_by_id(self, liver_id: UUID) -> LiverEntity | None:
        """呼び出し ID を保存して詳細結果を返す。"""

        self.find_by_id_calls.append(liver_id)
        return self.find_by_id_result

    async def search(
        self,
        *,
        query: str,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[LiverSummaryEntity], int]:
        """呼び出し引数を保存して検索結果を返す。"""

        self.search_calls.append(
            {
                "query": query,
                "page": page,
                "limit": limit,
            },
        )
        return self.search_result

    async def find_current_color(self, liver_id: UUID) -> LiverColorEntity | None:
        """呼び出し ID を保存して現在色を返す。"""

        self.find_current_color_calls.append(liver_id)
        return self.find_current_color_result


@pytest.fixture
def fake_repository() -> FakeLiverRepository:
    """初期状態の fake repository を返す。"""

    return FakeLiverRepository()