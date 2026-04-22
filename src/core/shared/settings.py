"""アプリケーション共通の設定を管理するモジュール。"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ALLOWED_LOG_LEVELS = {
    "CRITICAL",
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "NOTSET",
}


class AppSettings(BaseSettings):
    """アプリケーション共通の設定を表す。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
        validate_default=True,
    )

    log_level: str = Field(
        default="INFO",
        min_length=1,
        validation_alias="LOG_LEVEL",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """ログレベル文字列を正規化し、不正値を拒否する。"""

        normalized = value.strip().upper()
        if normalized not in _ALLOWED_LOG_LEVELS:
            msg = "LOG_LEVEL には有効なログレベルを指定してください。"
            raise ValueError(msg)
        return normalized


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """キャッシュされた共通設定を返す。"""

    return AppSettings()


def clear_settings_cache() -> None:
    """テスト用に設定キャッシュをクリアする。"""

    get_settings.cache_clear()
