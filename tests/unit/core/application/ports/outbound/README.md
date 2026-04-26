# core/application/ports/outbound テスト一覧

## test_liver_repository.py

| クラス | テスト名 | 対象 | 観点 | 意図 |
|---|---|---|---|---|
| （なし） | test_liver_repository_cannot_be_instantiated_directly | LiverRepository | 異常系 | 抽象ポートを未実装のまま直接生成できないこと |
| （なし） | test_concrete_liver_repository_is_treated_as_port_instance | LiverRepository | 正常系 | 具象実装が `LiverRepository` 契約を満たし差し替え可能であること |
