"""LiverRepository ポートの単体テスト。"""

from __future__ import annotations

import pytest

from core.application.ports.outbound import LiverRepository


class _ConcreteLiverRepository(LiverRepository):
    """テスト用の具象実装。"""

    async def find_all(self, **_: object) -> tuple[list[object], int]:
        """一覧取得のテスト用ダミー実装。"""

        return [], 0

    async def find_by_id(self, liver_id: object) -> object | None:
        """ID 検索のテスト用ダミー実装。"""

        return liver_id

    async def search(self, **_: object) -> tuple[list[object], int]:
        """検索のテスト用ダミー実装。"""

        return [], 0

    async def find_current_color(self, liver_id: object) -> object | None:
        """現在色取得のテスト用ダミー実装。"""

        return liver_id


def test_liver_repository_cannot_be_instantiated_directly() -> None:
    """
    LiverRepository は抽象クラスのまま直接生成できないことを確認する。

    異常系:
        観点: 必須メソッド未実装の抽象ポートを直接利用できないこと
        期待値: TypeError が送出されること
    """

    # Arrange

    # Act / Assert
    with pytest.raises(TypeError):
        LiverRepository()


def test_concrete_liver_repository_is_treated_as_port_instance() -> None:
    """
    具象実装が LiverRepository として扱えることを確認する。

    正常系:
        観点: ポートの契約を満たす実装を差し替え可能に扱えること
        期待値: 具象実装のインスタンスが LiverRepository でもあること
    """

    # Arrange

    # Act
    repository = _ConcreteLiverRepository()

    # Assert
    assert isinstance(repository, LiverRepository)
