"""共通設定モジュールの単体テスト。"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from pydantic import ValidationError

from core.shared.settings import AppSettings, clear_settings_cache, get_settings


@pytest.fixture(autouse=True)
def reset_settings_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Iterator[None]:
    """
    設定キャッシュと環境変数の状態をテストごとに初期化する。
    """

    clear_settings_cache()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    yield

    clear_settings_cache()


def test_app_settings_uses_info_when_log_level_is_unset() -> None:
    """
    LOG_LEVEL 未設定時に INFO が使われることを確認する。

    正常系:
        観点: デフォルト設定が適用されること
        期待値: log_level が INFO であること
    """

    # Arrange

    # Act
    settings = AppSettings()

    # Assert
    assert settings.log_level == "INFO"


def test_app_settings_uses_env_value_when_log_level_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    LOG_LEVEL が設定されている場合はその値が使われることを確認する。

    正常系:
        観点: 環境変数でログレベルを上書きできること
        期待値: log_level が DEBUG であること
    """

    # Arrange
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Act
    settings = AppSettings()

    # Assert
    assert settings.log_level == "DEBUG"


def test_app_settings_uses_default_database_url_when_env_is_unset() -> None:
    """
    DATABASE_URL 未設定時に既定値が使われることを確認する。

    正常系:
        観点: データベース URL のデフォルト設定が適用されること
        期待値: database_url が既定の SQLite URL であること
    """

    # Arrange

    # Act
    settings = AppSettings()

    # Assert
    assert settings.database_url == "sqlite+aiosqlite:///./niji_pallet.db"


def test_app_settings_uses_env_value_when_database_url_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    DATABASE_URL が設定されている場合はその値が使われることを確認する。

    正常系:
        観点: 環境変数でデータベース URL を上書きできること
        期待値: database_url が設定値へ正規化されること
    """

    # Arrange
    monkeypatch.setenv("DATABASE_URL", " sqlite+aiosqlite:///:memory: ")

    # Act
    settings = AppSettings()

    # Assert
    assert settings.database_url == "sqlite+aiosqlite:///:memory:"


def test_app_settings_raises_validation_error_for_empty_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    空文字相当の DATABASE_URL では例外になることを確認する。

    異常系:
        観点: 空白のみのデータベース URL を拒否すること
        期待値: ValidationError が送出されること
    """

    # Arrange
    monkeypatch.setenv("DATABASE_URL", "   ")

    # Act / Assert
    with pytest.raises(ValidationError, match="DATABASE_URL"):
        AppSettings()


def test_app_settings_normalizes_log_level_with_whitespace_and_case(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    前後空白付きの LOG_LEVEL が正規化されることを確認する。

    境界値:
        観点: 前後空白と小文字を含む値でも正規化されること
        期待値: log_level が DEBUG であること
    """

    # Arrange
    monkeypatch.setenv("LOG_LEVEL", " debug ")

    # Act
    settings = AppSettings()

    # Assert
    assert settings.log_level == "DEBUG"


def test_app_settings_raises_validation_error_for_invalid_log_level(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    不正な LOG_LEVEL では例外になることを確認する。

    異常系:
        観点: 許可されていないログレベル文字列を拒否すること
        期待値: ValidationError が送出されること
    """

    # Arrange
    monkeypatch.setenv("LOG_LEVEL", "verbose")

    # Act / Assert
    with pytest.raises(ValidationError, match="有効なログレベル"):
        AppSettings()


def test_get_settings_returns_cached_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    get_settings がキャッシュされた設定インスタンスを返すことを確認する。

    正常系:
        観点: 連続呼び出しで同じインスタンスを返すこと
        期待値: 2 回の取得結果が同一オブジェクトであること
    """

    # Arrange
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # Act
    first_settings = get_settings()
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    second_settings = get_settings()

    # Assert
    assert first_settings is second_settings
    assert second_settings.log_level == "DEBUG"


def test_clear_settings_cache_recreates_settings_instance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    clear_settings_cache 後は設定インスタンスが再生成されることを確認する。

    回帰:
        観点: キャッシュクリア後に最新の環境変数が反映されること
        期待値: 新しい設定インスタンスが生成され、log_level が ERROR になること
    """

    # Arrange
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    first_settings = get_settings()
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    # Act
    clear_settings_cache()
    second_settings = get_settings()

    # Assert
    assert first_settings is not second_settings
    assert second_settings.log_level == "ERROR"
