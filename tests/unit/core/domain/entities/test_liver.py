"""ライバー系ドメインエンティティの単体テスト。"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import UUID

from core.domain.entities import (
    AliasTypeEnum,
    BranchEnum,
    LiverAliasEntity,
    LiverColorEntity,
    LiverEntity,
    LiverStatusEnum,
    LiverSummaryEntity,
)


def test_liver_entity_initializes_optional_fields_with_expected_defaults() -> None:
    """
    LiverEntity の省略可能フィールドが期待どおり初期化されることを確認する。

    正常系:
        観点: 最小入力でも安全に詳細エンティティを生成できること
        期待値: aliases は空リストで、現在色と時刻系フィールドは None であること
    """

    # Arrange
    liver_id = UUID("00000000-0000-0000-0000-000000000001")

    # Act
    entity = LiverEntity(
        id=liver_id,
        name="月ノ美兎",
        kana_name="つきのみと",
        english_name="Tsukino Mito",
        branch=BranchEnum.JP,
        generation="1期生",
        status=LiverStatusEnum.ACTIVE,
        debuted_at=date(2018, 2, 8),
        retired_at=None,
    )

    # Assert
    assert entity.aliases == []
    assert entity.current_color is None
    assert entity.created_at is None
    assert entity.updated_at is None


def test_liver_entity_uses_independent_alias_lists_per_instance() -> None:
    """
    LiverEntity ごとに aliases の初期リストが独立していることを確認する。

    回帰:
        観点: mutable default の共有が起きないこと
        期待値: 一方の aliases を更新しても他方へ影響しないこと
    """

    # Arrange
    first = LiverEntity(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        name="える",
        kana_name=None,
        english_name="Elu",
        branch=BranchEnum.JP,
        generation=None,
        status=LiverStatusEnum.ACTIVE,
        debuted_at=None,
        retired_at=None,
    )
    second = LiverEntity(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        name="樋口楓",
        kana_name="ひぐちかえで",
        english_name="Kaede Higuchi",
        branch=BranchEnum.JP,
        generation="1期生",
        status=LiverStatusEnum.ACTIVE,
        debuted_at=None,
        retired_at=None,
    )
    alias = LiverAliasEntity(
        id=UUID("00000000-0000-0000-0000-000000000004"),
        alias="でろーん",
        alias_type=AliasTypeEnum.NICKNAME,
        locale="ja",
    )

    # Act
    first.aliases.append(alias)

    # Assert
    assert first.aliases == [alias]
    assert second.aliases == []


def test_liver_summary_entity_keeps_current_color_value() -> None:
    """
    LiverSummaryEntity が現在色を保持できることを確認する。

    正常系:
        観点: 一覧向けエンティティへ現在色を関連付けられること
        期待値: 渡した現在色オブジェクトがそのまま保持されること
    """

    # Arrange
    current_color = LiverColorEntity(
        hex="#19A0E6",
        r=25,
        g=160,
        b=230,
        display_name="ライトブルー",
        is_official=True,
        source="official",
        source_url="https://example.com/colors/mito",
        note=None,
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    # Act
    entity = LiverSummaryEntity(
        id=UUID("00000000-0000-0000-0000-000000000005"),
        name="月ノ美兎",
        kana_name="つきのみと",
        english_name="Tsukino Mito",
        branch=BranchEnum.JP,
        generation="1期生",
        status=LiverStatusEnum.ACTIVE,
        current_color=current_color,
    )

    # Assert
    assert entity.current_color is current_color
