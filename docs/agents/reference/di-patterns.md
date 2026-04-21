# FastAPI DI パターン集

## 概要

FastAPI の `Depends` を使い、Hexagonal Architecture の依存注入を実現するパターン集。
router から直接 `new` せず、provider 関数チェーンで組み立てる。

## 基本構造

```
get_settings (lru_cache)
  ↓
get_xxx_repository (settings → repository)
  ↓
get_xxx_usecase (repository → usecase)
```

## パターン 1: Settings のシングルトン化

```python
from functools import lru_cache
from core.shared.settings import AppSettings

@lru_cache
def get_settings() -> AppSettings:
    """環境変数から共有設定を読み込み、キャッシュして返す。"""
    return AppSettings()

def clear_settings_cache() -> None:
    """テストや再読み込み向けに設定キャッシュを破棄する。"""
    get_settings.cache_clear()
```

**ポイント**: `lru_cache` で呼び出しごとの再読み込みを防ぐ。テスト用に `clear_*_cache()` を公開。

## パターン 2: Repository のパス正規化 + キャッシュ

```python
def _normalize_csv_path(csv_path: Path) -> Path:
    """パス表現を正規化して cache key の衝突を防ぐ。"""
    return csv_path.expanduser().resolve()

@lru_cache
def _build_csv_xxx_repository(csv_path: Path) -> CsvXxxRepository:
    """CSV repository をパス単位で再利用する。"""
    return CsvXxxRepository(csv_path)

def get_csv_xxx_repository(settings: SettingsDependency) -> XxxRepository:
    """CSV 保存先を使う repository を返す。"""
    csv_path = _normalize_csv_path(settings.xxx_csv_path)
    return _build_csv_xxx_repository(csv_path)
```

**ポイント**: `expanduser().resolve()` で `~/data` と `/home/user/data` が同じ cache key になる。

## パターン 3: type alias による Annotated の短縮

```python
from typing import Annotated
from fastapi import Depends

type SettingsDependency = Annotated[AppSettings, Depends(get_settings)]
type XxxRepositoryDependency = Annotated[XxxRepository, Depends(get_csv_xxx_repository)]
type AddXxxUsecaseDependency = Annotated[AddXxxUsecase, Depends(get_add_xxx_usecase)]
```

**ポイント**: Python 3.12+ の `type` statement で可読性向上。Router の関数シグネチャがスッキリする。

## パターン 4: Usecase の provider

```python
def get_add_xxx_usecase(repo: XxxRepositoryDependency) -> AddXxxUsecase:
    """○○追加 usecase を返す。"""
    return AddXxxUsecase(repo)
```

**ポイント**: Usecase は repository を引数で受け取るだけ。DI チェーンが自動で repository を解決する。

## パターン 5: テストでの差し替え

```python
# テストコード
@pytest.fixture
def test_app() -> Iterator[FastAPI]:
    app = FastAPI()
    app.include_router(router)
    yield app
    app.dependency_overrides.clear()

# 各テスト内
test_app.dependency_overrides[get_add_xxx_usecase] = lambda: spy_usecase
client = TestClient(test_app)
```

**ポイント**: `dependency_overrides` で provider 関数を丸ごと差し替え。テスト後に `.clear()` でリセット。

## パターン 6: Adapter の切り替え

環境変数や設定でアダプターを切り替える場合:

```python
def get_xxx_repository(settings: SettingsDependency) -> XxxRepository:
    """設定に基づいて適切な repository 実装を返す。"""
    match settings.storage_backend:
        case "csv":
            return _build_csv_xxx_repository(...)
        case "sqlite":
            return _build_sqlite_xxx_repository(...)
        case _:
            msg = f"未対応の storage backend: {settings.storage_backend}"
            raise ValueError(msg)
```

## DI 登録チェックリスト

新しいコンポーネントを追加する際のチェックリスト:

- [ ] provider 関数を `dependencies.py` に追加
- [ ] `type` alias を定義
- [ ] テスト用の `clear_*_cache()` 関数を公開（`lru_cache` 使用時）
- [ ] Router で `Annotated[..., Depends(...)]` 型の type alias を使用
