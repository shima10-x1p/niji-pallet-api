"""アプリケーション共通のロガーを提供するモジュール。"""

from __future__ import annotations

import logging
import sys

from core.shared.request_context import request_id_var
from core.shared.settings import get_settings

_LOGGER_NAME = "niji_pallet"
_logger: logging.Logger | None = None


class RequestIdFilter(logging.Filter):
    """ログレコードへリクエスト ID を注入するフィルター。"""

    def filter(self, record: logging.LogRecord) -> bool:
        """コンテキストにあるリクエスト ID をログレコードへ設定する。"""

        record.request_id = request_id_var.get() or "-"
        return True


def _build_formatter() -> logging.Formatter:
    """要求された形式のログフォーマッターを生成する。"""

    return logging.Formatter(
        fmt=(
            "[%(asctime)s.%(msecs)03d] [%(levelname)s] "
            "[%(request_id)s] %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_handler() -> logging.Handler:
    """標準出力へ書き込むハンドラーを生成する。"""

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    handler.setFormatter(_build_formatter())
    return handler


def _configure_logger(logger: logging.Logger) -> logging.Logger:
    """共通ロガーのハンドラーとレベルを設定する。"""

    settings = get_settings()
    logger.setLevel(settings.log_level)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
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
