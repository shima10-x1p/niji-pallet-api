# core テスト一覧

## test_providers.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_get_liver_repository_returns_sqlalchemy_repository_as_port | get_liver_repository | 正常系 | provider が `LiverRepository` 契約を満たす `SqlAlchemyLiverRepository` を返すこと |
| （なし） | test_get_list_livers_usecase_returns_expected_usecase_instance | get_list_livers_usecase | 正常系 | provider が一覧取得用ユースケースを組み立てられること |
| （なし） | test_get_search_livers_usecase_returns_expected_usecase_instance | get_search_livers_usecase | 正常系 | provider が検索用ユースケースを組み立てられること |
| （なし） | test_get_get_liver_usecase_returns_expected_usecase_instance | get_get_liver_usecase | 正常系 | provider が詳細取得用ユースケースを組み立てられること |
| （なし） | test_get_get_liver_color_usecase_returns_expected_usecase_instance | get_get_liver_color_usecase | 正常系 | provider が色取得用ユースケースを組み立てられること |
