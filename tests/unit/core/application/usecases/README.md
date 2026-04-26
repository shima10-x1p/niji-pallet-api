# core/application/usecases テスト一覧

## test_get_liver.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_returns_liver_when_repository_finds_one | GetLiverUsecase.execute | 正常系 | 該当ライバーが存在するときに詳細を返すこと |
| （なし） | test_execute_raises_not_found_when_repository_returns_none | GetLiverUsecase.execute | 異常系 | 該当ライバーが存在しないときに NotFoundError を送出すること |

## test_get_liver_color.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_returns_current_color_without_fetching_liver | GetLiverColorUsecase.execute | 正常系 | 現在色が見つかった場合は存在確認を追加で行わないこと |
| （なし） | test_execute_returns_none_when_liver_exists_but_color_is_missing | GetLiverColorUsecase.execute | 正常系 | 色未登録だがライバーは存在する場合に None を返すこと |
| （なし） | test_execute_raises_not_found_when_liver_and_color_are_missing | GetLiverColorUsecase.execute | 異常系 | ライバー自体が存在しない場合に NotFoundError を送出すること |

## test_list_livers.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_uses_active_when_status_is_omitted | ListLiversUsecase.execute | 回帰 | status 未指定時に ACTIVE が使われること |
| （なし） | test_execute_preserves_explicit_status | ListLiversUsecase.execute | 正常系 | status を明示した場合はその値を維持すること |

## test_search_livers.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_execute_returns_repository_result | SearchLiversUsecase.execute | 正常系 | execute が Repository の検索結果をそのまま返すこと |
| （なし） | test_execute_returns_empty_result_when_repository_returns_no_match | SearchLiversUsecase.execute | 正常系 | 検索結果がない場合に空の一覧を返すこと |