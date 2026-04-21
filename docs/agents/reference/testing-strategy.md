# テスト戦略

## 基本方針

- **テストディレクトリ**: `tests/unit/` 配下で `src/` と同じ階層構造を維持
- **モック戦略**: `unittest.mock` は使わず、Port (ABC) を直接継承した手書きスパイ / スタブを使用
- **テスト命名**: `test_{対象の動作}_{条件}` + 日本語 docstring
- **async テスト**: `asyncio.run()` でラップ（pytest-asyncio を使わない場合）

## テストディレクトリのミラーリング

```
src/core/domain/favorite.py
→ tests/unit/core/domain/test_favorite.py

src/core/application/usecases/add_favorite.py
→ tests/unit/core/application/usecases/test_add_favorite.py

src/core/adapters/inbound/favorites_router.py
→ tests/unit/core/adapters/inbound/test_favorites_router.py
```

## 手書きスパイ / スタブ

### なぜ unittest.mock を使わないか

- **型安全**: ABC を継承するため、port のインターフェース変更時にコンパイル時（型チェック時）に検知できる
- **明示的**: スパイの振る舞いがコードとして読める
- **テストの意図が明確**: どのメソッドが呼ばれることを期待しているかが一目でわかる

### スパイのパターン

```python
class SaveSpyRepository(XxxRepository):
    """save 呼び出しを観測する repository スパイ。"""

    def __init__(self, *, error: Exception | None = None) -> None:
        self.saved_entity: XxxEntity | None = None
        self._error = error

    async def save(self, entity: XxxEntity) -> XxxEntity:
        self.saved_entity = entity
        if self._error is not None:
            raise self._error
        return entity

    # このテストで使わないメソッドは AssertionError を raise
    async def find_by_id(self, id: str) -> XxxEntity | None:
        raise AssertionError("find_by_id はこのテストでは使いません。")
```

### スタブのパターン

```python
class StubFindRepository(XxxRepository):
    """find_by_id の戻り値を固定する repository スタブ。"""

    def __init__(self, entity: XxxEntity | None) -> None:
        self._entity = entity

    async def find_by_id(self, id: str) -> XxxEntity | None:
        return self._entity

    async def save(self, entity: XxxEntity) -> XxxEntity:
        raise AssertionError("save はこのテストでは使いません。")
```

## テストヘルパー

各テストファイル内にファクトリ関数を定義する（共有せずファイルに閉じる）。

```python
def _build_entity(**overrides: object) -> XxxEntity:
    """テスト用のデフォルト entity を組み立てる。"""
    defaults = {
        "id": "test-id-12345",
        "name": "テスト名",
        ...
    }
    defaults.update(overrides)
    return XxxEntity(**defaults)

def _build_input(**overrides: object) -> XxxInput:
    """テスト用のデフォルト入力値を組み立てる。"""
    defaults = {"field1": "value1", "field2": 42}
    defaults.update(overrides)
    return XxxInput(**defaults)
```

## Usecase テストのパターン

```python
import asyncio

class TestAddXxx:
    def test_execute_saves_entity_to_repository(self) -> None:
        """入力値から entity を組み立てて repository に保存する。"""
        spy = SaveSpyRepository()
        usecase = AddXxxUsecase(spy)
        input_data = _build_input()

        result = asyncio.run(usecase.execute(input_data))

        assert spy.saved_entity is not None
        assert spy.saved_entity.name == input_data.name
        assert result == spy.saved_entity

    def test_execute_raises_when_repository_fails(self) -> None:
        """repository がエラーを返した場合、そのまま伝播する。"""
        spy = SaveSpyRepository(error=ConflictError("xxx-id"))
        usecase = AddXxxUsecase(spy)

        with pytest.raises(ConflictError):
            asyncio.run(usecase.execute(_build_input()))
```

## Router テストのパターン

```python
import pytest
from collections.abc import Iterator
from fastapi import FastAPI
from fastapi.testclient import TestClient

@pytest.fixture
def test_app() -> Iterator[FastAPI]:
    app = FastAPI()
    app.include_router(router)
    yield app
    app.dependency_overrides.clear()

class TestGetXxx:
    def test_returns_200_with_entity(self, test_app: FastAPI) -> None:
        """正常系: entity が見つかれば 200 で返す。"""
        usecase = StubGetXxxUsecase(entity=_build_entity())
        test_app.dependency_overrides[get_get_xxx_usecase] = lambda: usecase
        client = TestClient(test_app)

        response = client.get("/v1/xxx/valid-id")

        assert response.status_code == 200
        assert response.json()["name"] == "テスト名"

    def test_returns_404_when_not_found(self, test_app: FastAPI) -> None:
        """異常系: entity が見つからなければ 404。"""
        usecase = StubGetXxxUsecase(error=NotFoundError("invalid-id"))
        test_app.dependency_overrides[get_get_xxx_usecase] = lambda: usecase
        client = TestClient(test_app)

        response = client.get("/v1/xxx/invalid-id")

        assert response.status_code == 404
```

## Adapter テストのパターン

```python
class TestCsvXxxRepository:
    def test_save_then_find_returns_same_entity(self, tmp_path: Path) -> None:
        """保存した entity を find_by_id で取得できる。"""
        csv_path = tmp_path / "test.csv"
        repo = CsvXxxRepository(csv_path)
        entity = _build_entity()

        async def scenario() -> XxxEntity | None:
            await repo.save(entity)
            return await repo.find_by_id(entity.id)

        found = asyncio.run(scenario())
        assert found is not None
        assert found.id == entity.id
```

## Fixture パターン

- `tmp_path` (pytest 組み込み): 一時ディレクトリ（Adapter テスト向け）
- `monkeypatch`: 環境変数の操作
- `autouse=True` の cache clear fixture: `lru_cache` をテスト前後でリセット

```python
@pytest.fixture(autouse=True)
def _clear_caches() -> Iterator[None]:
    yield
    clear_settings_cache()
    clear_csv_favorite_repository_cache()
```

## テスト実行

```bash
uv run pytest tests/unit -q --tb=short       # 全 unit test
uv run pytest tests/unit/core -q --tb=short   # core のみ
uv run ruff check tests/unit                  # テストコードの lint
```
