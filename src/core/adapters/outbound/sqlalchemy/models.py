"""SQLite 保存向けの SQLAlchemy ORM モデルを定義する。"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from core.domain.entities import AliasTypeEnum, BranchEnum, LiverStatusEnum


class Base(DeclarativeBase):
    """ORM モデルの共通ベースクラス。"""


class LiverRecord(Base):
    """ライバー本体を保持するテーブル。"""

    __tablename__ = "livers"
    __table_args__ = (
        Index("ix_livers_name", "name"),
        Index("ix_livers_status", "status"),
        Index("ix_livers_branch", "branch"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kana_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    english_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    branch: Mapped[BranchEnum | None] = mapped_column(
        Enum(BranchEnum, native_enum=False),
        nullable=True,
    )
    generation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[LiverStatusEnum] = mapped_column(
        Enum(LiverStatusEnum, native_enum=False),
        nullable=False,
        default=LiverStatusEnum.ACTIVE,
    )
    debuted_at: Mapped[date | None] = mapped_column(Date(), nullable=True)
    retired_at: Mapped[date | None] = mapped_column(Date(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    aliases: Mapped[list[LiverAliasRecord]] = relationship(
        back_populates="liver",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    colors: Mapped[list[LiverColorRecord]] = relationship(
        back_populates="liver",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class LiverAliasRecord(Base):
    """ライバーの別名を保持するテーブル。"""

    __tablename__ = "liver_aliases"
    __table_args__ = (
        Index("ix_liver_aliases_liver_id", "liver_id"),
        Index("ix_liver_aliases_alias", "alias"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    liver_id: Mapped[str] = mapped_column(
        ForeignKey("livers.id", ondelete="CASCADE"),
        nullable=False,
    )
    alias: Mapped[str] = mapped_column(String(255), nullable=False)
    alias_type: Mapped[AliasTypeEnum] = mapped_column(
        Enum(AliasTypeEnum, native_enum=False),
        nullable=False,
    )
    locale: Mapped[str | None] = mapped_column(String(32), nullable=True)

    liver: Mapped[LiverRecord] = relationship(back_populates="aliases")


class LiverColorRecord(Base):
    """ライバーカラー履歴を保持するテーブル。"""

    __tablename__ = "liver_colors"
    __table_args__ = (
        Index("ix_liver_colors_liver_id", "liver_id"),
        Index("ix_liver_colors_is_current", "is_current"),
        Index(
            "uq_liver_colors_current_per_liver",
            "liver_id",
            unique=True,
            sqlite_where=text("is_current = 1"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    liver_id: Mapped[str] = mapped_column(
        ForeignKey("livers.id", ondelete="CASCADE"),
        nullable=False,
    )
    hex: Mapped[str] = mapped_column(String(7), nullable=False)
    r: Mapped[int] = mapped_column(Integer(), nullable=False)
    g: Mapped[int] = mapped_column(Integer(), nullable=False)
    b: Mapped[int] = mapped_column(Integer(), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_official: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text(), nullable=True)
    note: Mapped[str | None] = mapped_column(Text(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    is_current: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)

    liver: Mapped[LiverRecord] = relationship(back_populates="colors")
