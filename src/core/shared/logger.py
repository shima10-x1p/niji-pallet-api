"""アプリケーション共通のロガーを提供するモジュール。"""

from __future__ import annotations

import logging
import sys

from core.shared.settings import get_settings

_LOGGER_NAME = "niji_pallet"
_logger: logging.Logger | None = None


def _build_formatter() -> logging.Formatter:
    """要求された形式のログフォーマッターを生成する。"""

    return logging.Formatter(
        fmt="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_handler() -> logging.Handler:
    """標準出力へ書き込むハンドラーを生成する。"""

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    return handler


def _configure_logger(logger: logging.Logger) -> logging.Logger:
    """共通ロガーのハンドラーとレベルを設定する。"""

    settings = get_settings()
    logger.setLevel(settings.log_level)
    logger.handlers.clear()
    logger.addHandler(_build_handler())
    logger.propagate = False
    return logger


def get_logger() -> logging.Logger:
    """アプリ全体で共有するシングルトンロガーを返す。"""

    global _logger

    if _logger is None:
        _logger = _configure_logger(logging.getLogger(_LOGGER_NAME))
    return _logger


def clear_logger_cache() -> None:
    """テスト用にロガーのキャッシュとハンドラーを初期化する。"""

    global _logger

    if _logger is not None:
        for handler in list(_logger.handlers):
            _logger.removeHandler(handler)
            handler.close()
    _logger = None
