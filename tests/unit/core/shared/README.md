# core/shared テスト一覧

## test_logger.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_get_logger_returns_same_singleton_instance | get_logger | 正常系 | `get_logger()` が同一の共有ロガーを返すこと |
| （なし） | test_get_logger_uses_stdout_handler_and_expected_name | get_logger | 正常系 | ロガー名が `niji_pallet` で出力先が stdout であること |
| （なし） | test_get_logger_outputs_message_with_expected_format | get_logger | 回帰 | ログ 1 行が日時・ミリ秒・ログレベル・メッセージを含む形式で出力されること |
| （なし） | test_clear_logger_cache_reinitializes_logger_with_latest_settings | clear_logger_cache / get_logger | 正常系/回帰 | キャッシュクリア後に最新設定でハンドラーとログレベルが再設定されること |

## test_settings.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_app_settings_uses_info_when_log_level_is_unset | AppSettings | 正常系 | `LOG_LEVEL` 未設定時に `INFO` が使われること |
| （なし） | test_app_settings_uses_env_value_when_log_level_is_set | AppSettings | 正常系 | 環境変数で `LOG_LEVEL` を上書きできること |
| （なし） | test_app_settings_normalizes_log_level_with_whitespace_and_case | AppSettings | 境界値 | 前後空白付きかつ小文字の `LOG_LEVEL` が `DEBUG` に正規化されること |
| （なし） | test_app_settings_raises_validation_error_for_invalid_log_level | AppSettings | 異常系 | 不正な `LOG_LEVEL` で `ValidationError` が送出されること |
| （なし） | test_get_settings_returns_cached_instance | get_settings | 正常系 | `get_settings()` がキャッシュ済みインスタンスを返すこと |
| （なし） | test_clear_settings_cache_recreates_settings_instance | clear_settings_cache / get_settings | 回帰 | `clear_settings_cache()` 後に設定インスタンスが再生成されること |
