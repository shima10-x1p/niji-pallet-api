# core/domain/entities テスト一覧

## test_liver.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_liver_entity_initializes_optional_fields_with_expected_defaults | LiverEntity | 正常系 | 最小入力でも optional フィールドが安全な初期値で生成されること |
| （なし） | test_liver_entity_uses_independent_alias_lists_per_instance | LiverEntity | 回帰 | `aliases` のデフォルトリストがインスタンス間で共有されないこと |
| （なし） | test_liver_summary_entity_keeps_current_color_value | LiverSummaryEntity | 正常系 | 一覧用エンティティが現在色オブジェクトを保持できること |
