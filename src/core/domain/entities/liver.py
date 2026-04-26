"""ライバー関連のドメインエンティティを定義する。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from uuid import UUID


class BranchEnum(StrEnum):
    """国別のグループを表す。"""

    JP = "JP"
    KR = "KR"
    ID = "ID"
    EN = "EN"
    IN = "IN"


class LiverStatusEnum(StrEnum):
    """ライバーの活動状態を表す。"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    RETIRED = "retired"


class AliasTypeEnum(StrEnum):
    """ライバー別名の種別を表す。"""

    NICKNAME = "nickname"
    FORMER_NAME = "former_name"
    ROMANIZATION = "romanization"
    OTHER = "other"


@dataclass(slots=True)
class LiverAliasEntity:
    """ライバーの別名を表す。"""

    id: UUID
    alias: str
    alias_type: AliasTypeEnum
    locale: str | None = None


@dataclass(slots=True)
class LiverColorEntity:
    """ライバーの現在カラー情報を表す。"""

    hex: str
    r: int
    g: int
    b: int
    display_name: str | None
    is_official: bool
    source: str
    source_url: str | None
    note: str | None
    updated_at: datetime


@dataclass(slots=True)
class LiverSummaryEntity:
    """一覧表示向けの軽量なライバー情報を表す。"""

    id: UUID
    name: str
    kana_name: str | None
    english_name: str | None
    branch: BranchEnum | None
    generation: str | None
    status: LiverStatusEnum
    current_color: LiverColorEntity | None = None


@dataclass(slots=True)
class LiverEntity:
    """ライバー詳細情報を表す。"""

    id: UUID
    name: str
    kana_name: str | None
    english_name: str | None
    branch: BranchEnum | None
    generation: str | None
    status: LiverStatusEnum
    debuted_at: date | None
    retired_at: date | None
    aliases: list[LiverAliasEntity] = field(default_factory=list)
    current_color: LiverColorEntity | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
