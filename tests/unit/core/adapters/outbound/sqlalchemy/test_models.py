"""SQLAlchemy ORM モデル定義の単体テスト。"""

from __future__ import annotations

from core.adapters.outbound.sqlalchemy.models import (
    Base,
    LiverAliasRecord,
    LiverColorRecord,
    LiverRecord,
)


def test_base_metadata_contains_required_tables() -> None:
    """
    ORM メタデータに必要テーブルが登録されていることを確認する。

    正常系:
        観点: ライバー本体・別名・色履歴のテーブル定義が揃っていること
        期待値: 3 つのテーブル名が metadata に含まれること
    """

    # Arrange

    # Act
    table_names = set(Base.metadata.tables)

    # Assert
    assert {"livers", "liver_aliases", "liver_colors"}.issubset(table_names)


def test_liver_record_defines_alias_and_color_relationships() -> None:
    """
    LiverRecord が別名と色履歴のリレーションを持つことを確認する。

    正常系:
        観点: ORM 上で関連テーブルへ辿れること
        期待値: aliases と colors がそれぞれ対応モデルへ関連付いていること
    """

    # Arrange

    # Act
    alias_mapper = LiverRecord.aliases.property.mapper.class_
    color_mapper = LiverRecord.colors.property.mapper.class_

    # Assert
    assert alias_mapper is LiverAliasRecord
    assert color_mapper is LiverColorRecord


def test_liver_color_record_has_unique_current_color_index_per_liver() -> None:
    """
    LiverColorRecord が現在色を 1 ライバー 1 件に制約していることを確認する。

    回帰:
        観点: current color 用の一意インデックスが定義されていること
        期待値: 対象インデックスが unique かつ liver_id 列を対象にしていること
    """

    # Arrange
    indexes = {
        index.name: index
        for index in LiverColorRecord.__table__.indexes
    }

    # Act
    current_index = indexes["uq_liver_colors_current_per_liver"]

    # Assert
    assert current_index.unique is True
    assert [column.name for column in current_index.columns] == ["liver_id"]
