# core/adapters/inbound テスト一覧

## test_middleware.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_resolve_request_id_generates_uuid4_when_header_is_missing | _resolve_request_id | 正常系 | ヘッダー未指定時に新しい UUID v4 を生成すること |
| （なし） | test_resolve_request_id_generates_uuid4_when_header_is_empty | _resolve_request_id | 境界値 | 空文字のヘッダーを未指定相当として UUID v4 を生成すること |
| （なし） | test_resolve_request_id_preserves_original_value_when_valid_uuid4_is_provided | _resolve_request_id | 正常系 | 有効な UUID v4 を入力値のまま返すこと |
| （なし） | test_resolve_request_id_generates_uuid4_when_header_value_is_invalid | _resolve_request_id | 異常系 | UUID として解釈できない値では新しい UUID v4 を返すこと |
| （なし） | test_resolve_request_id_generates_uuid4_when_uuid_version_is_not_4 | _resolve_request_id | 異常系/回帰 | v4 以外の UUID 形式を受け取ったときに新しい UUID v4 を返すこと |
| （なし） | test_middleware_sets_generated_request_id_to_context_and_response_when_header_is_missing | XRequestIdMiddleware | 正常系 | ヘッダー未指定時に生成した request id が本文とレスポンスヘッダーへ反映されること |
| （なし） | test_middleware_keeps_valid_request_id_in_context_and_response | XRequestIdMiddleware | 正常系/回帰 | 有効な request id が本文とレスポンスヘッダーへそのまま流れること |
| （なし） | test_middleware_replaces_invalid_request_id_in_context_and_response | XRequestIdMiddleware | 異常系/回帰 | 不正な request id を本文とレスポンスヘッダーへ残さず新しい UUID v4 に置き換えること |
| （なし） | test_middleware_overrides_existing_response_header_without_duplication | XRequestIdMiddleware | 回帰 | downstream が同名ヘッダーを設定しても `X-REQUEST-ID` を 1 つだけに保つこと |
| （なし） | test_middleware_resets_request_context_after_request_completion | XRequestIdMiddleware / request_id_var | 回帰 | リクエスト完了後に `request_id_var` が `None` に戻ること |
| （なし） | test_middleware_passes_through_non_http_scope_without_mutating_request_context | XRequestIdMiddleware / request_id_var | 回帰 | HTTP 以外の scope では request_id コンテキストを汚染せず素通しすること |
