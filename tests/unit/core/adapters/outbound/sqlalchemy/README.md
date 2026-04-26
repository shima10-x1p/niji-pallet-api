# core/adapters/outbound/sqlalchemy テスト一覧

## test_database.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_get_engine_reuses_cached_engine_for_same_url | get_engine | 正常系 | 同じ `DATABASE_URL` では同一の `AsyncEngine` を再利用すること |
| （なし） | test_clear_engine_cache_disposes_engine_and_recreates_it | clear_engine_cache / get_engine | 回帰 | `clear_engine_cache()` が既存 engine を破棄し、次回取得で再生成すること |
| （なし） | test_init_db_creates_required_tables | init_db | 正常系 | 初期化で `livers` / `liver_aliases` / `liver_colors` テーブルが作成されること |
| （なし） | test_build_session_factory_creates_async_session_bound_to_engine | build_session_factory | 正常系 | session factory が指定 engine に紐づく `AsyncSession` を作ること |

## test_liver_repository.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_find_all_returns_empty_result_when_no_records | SqlAlchemyLiverRepository.find_all | 正常系 | データ未登録時に空配列と総件数 0 を返すこと |
| （なし） | test_find_all_filters_by_branch_and_status | SqlAlchemyLiverRepository.find_all | 正常系 | `branch` と `status` の複合条件で一覧を絞り込めること |
| （なし） | test_find_all_applies_paging_and_stable_sort | SqlAlchemyLiverRepository.find_all | 正常系 | `name, id` の安定ソート上で offset/limit によるページングが効くこと |
| （なし） | test_find_by_id_returns_entity_when_found | SqlAlchemyLiverRepository.find_by_id | 正常系 | 詳細取得時に別名と現在色を含むエンティティへ変換できること |
| （なし） | test_find_by_id_returns_none_when_not_found | SqlAlchemyLiverRepository.find_by_id | 正常系 | 未登録 ID では `None` を返すこと |
| （なし） | test_search_matches_name_related_fields | SqlAlchemyLiverRepository.search | 正常系 | `name` / `kana_name` / `english_name` / `alias` を横断して検索できること |
| （なし） | test_search_returns_empty_result_for_blank_query | SqlAlchemyLiverRepository.search | 境界値 | 空白だけの query を早期リターンして検索しないこと |
| （なし） | test_find_current_color_returns_current_color_when_found | SqlAlchemyLiverRepository.find_current_color | 正常系 | `is_current=True` の現在色を返すこと |
| （なし） | test_find_current_color_returns_none_when_not_found | SqlAlchemyLiverRepository.find_current_color | 正常系 | 現在色未登録時に `None` を返すこと |

## test_models.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_base_metadata_contains_required_tables | Base.metadata | 正常系 | ORM メタデータに必要な 3 テーブルが登録されていること |
| （なし） | test_liver_record_defines_alias_and_color_relationships | LiverRecord | 正常系 | `aliases` と `colors` のリレーションが対応モデルへ関連付いていること |
| （なし） | test_liver_color_record_has_unique_current_color_index_per_liver | LiverColorRecord | 回帰 | 現在色を 1 ライバー 1 件に制約する一意インデックスが定義されていること |
