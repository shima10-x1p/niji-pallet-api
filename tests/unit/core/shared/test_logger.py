"""共通ロガーモジュールの単体テスト。"""

from __future__ import annotations

import logging
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest

from core.shared.logger import RequestIdFilter, clear_logger_cache, get_logger
from core.shared.request_context import request_id_var
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
    token = request_id_var.set(None)
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    yield

    request_id_var.reset(token)
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


def test_get_logger_uses_stdout_handler_and_request_id_filter() -> None:
    """
    get_logger が stdout と request id フィルターを使うことを確認する。

    正常系:
        観点: ロガー名とハンドラー構成が要求どおりであること
        期待値: stdout 向けハンドラーに RequestIdFilter が付くこと
    """

    # Arrange

    # Act
    logger = get_logger()
    handler = logger.handlers[0]

    # Assert
    assert logger.name == "niji_pallet"
    assert isinstance(handler, logging.StreamHandler)
    assert handler.stream is sys.stdout
    assert any(
        isinstance(filter_, RequestIdFilter)
        for filter_ in handler.filters
    )


def test_get_logger_outputs_message_with_expected_format_and_dash_request_id(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    ログ出力が要求されたフォーマットに一致することを確認する。

    回帰:
        観点: request_id 未設定時は `-` がログへ埋め込まれること
        期待値: 出力 1 行が指定フォーマットに一致すること
    """

    # Arrange
    message = "ログフォーマット検証メッセージ"
    pattern = re.compile(
        rf"\[\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}\.\d{{3}}\] "
        rf"\[INFO\] \[-\] {re.escape(message)}"
    )

    # Act
    logger = get_logger()
    logger.info(message)
    captured = capsys.readouterr()

    # Assert
    assert captured.err == ""
    assert pattern.fullmatch(captured.out.strip()) is not None


def test_get_logger_outputs_current_request_id_from_context_var(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    ContextVar に設定された request_id がログ出力へ反映されることを確認する。

    正常系/回帰:
        観点: リクエストスコープの request_id が自動でログへ入ること
        期待値: 出力に設定済みの request_id が含まれること
    """

    # Arrange
    request_id = str(uuid4())
    token = request_id_var.set(request_id)
    logger = get_logger()

    try:
        # Act
        logger.info("request scoped log")
        captured = capsys.readouterr()
    finally:
        request_id_var.reset(token)

    # Assert
    assert captured.err == ""
    assert f"[{request_id}] request scoped log" in captured.out


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
