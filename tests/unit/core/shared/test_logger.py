"""共通ロガーモジュールの単体テスト。"""

from __future__ import annotations

import logging
import re
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

from core.shared.logger import clear_logger_cache, get_logger
from core.shared.settings import clear_settings_cache


@pytest.fixture(autouse=True)
def reset_logger_state(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> Iterator[None]:
    """
    ロガーと設定の状態をテストごとに初期化する。
    """

    clear_logger_cache()
    clear_settings_cache()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    yield

    clear_logger_cache()
    clear_settings_cache()


def test_get_logger_returns_same_singleton_instance() -> None:
    """
    get_logger が同一の共有ロガーを返すことを確認する。

    正常系:
        観点: 共有ロガーがシングルトンとして振る舞うこと
        期待値: 2 回の取得結果が同一オブジェクトであること
    """

    # Arrange

    # Act
    first_logger = get_logger()
    second_logger = get_logger()

    # Assert
    assert first_logger is second_logger
    assert len(first_logger.handlers) == 1


def test_get_logger_uses_stdout_handler_and_expected_name() -> None:
    """
    get_logger が stdout を使う指定名のロガーを返すことを確認する。

    正常系:
        観点: ロガー名と出力先が要求どおりに構成されること
        期待値: ロガー名が niji_pallet で、ハンドラー出力先が stdout であること
    """

    # Arrange

    # Act
    logger = get_logger()
    handler = logger.handlers[0]

    # Assert
    assert logger.name == "niji_pallet"
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout


def test_get_logger_outputs_message_with_expected_format(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    ログ出力が要求されたフォーマットに一致することを確認する。

    回帰:
        観点: ログ行に日時、ミリ秒、ログレベル、メッセージが含まれること
        期待値: 出力 1 行が指定フォーマットに一致すること
    """

    # Arrange
    message = "ログフォーマット検証メッセージ"
    pattern = re.compile(
        rf"\[\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}\.\d{{3}}\] "
        rf"\[INFO\] {re.escape(message)}"
    )

    # Act
    logger = get_logger()
    logger.info(message)
    captured = capsys.readouterr()

    # Assert
    assert captured.err == ""
    assert pattern.fullmatch(captured.out.strip()) is not None


def test_clear_logger_cache_reinitializes_logger_with_latest_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    clear_logger_cache 後は最新設定でロガーが再初期化されることを確認する。

    正常系/回帰:
        観点: キャッシュクリア後にハンドラーとログレベルが再設定されること
        期待値: 新しいハンドラーが設定され、ログレベルが ERROR になること
    """

    # Arrange
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    first_logger = get_logger()
    first_handler = first_logger.handlers[0]
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    # Act
    clear_settings_cache()
    clear_logger_cache()
    second_logger = get_logger()
    second_handler = second_logger.handlers[0]

    # Assert
    assert second_logger.level == logging.ERROR
    assert second_handler is not first_handler
    assert len(second_logger.handlers) == 1
