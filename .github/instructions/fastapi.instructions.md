---
description: 'FastAPI + Hexagonal Architecture conventions — FastAPI 固有規約'
applyTo: '**/*.py'
---

# FastAPI + Hexagonal Architecture 規約

## アーキテクチャ（依存方向）

```
inbound adapter (router) → usecase → domain entity
                 usecase → port (抽象)
outbound adapter → port を実装
```

- domain / usecase は FastAPI・Pydantic・HTTP ライブラリに依存しない
- router は薄く保つ。business logic を書かない
- 保存先は `ports/outbound` の抽象を介してアクセスし `adapters/outbound` で実装

## ディレクトリ構成

```
src/
  core/
    domain/               # Entity / Value Object
    application/
      usecases/           # ユースケース (framework 非依存)
      ports/outbound/     # 外部依存の抽象 (Repository など)
    adapters/
      inbound/            # FastAPI router
      outbound/           # CSV / SQLite / S3 など保存先の実装
    shared/               # 横断関心事 (Settings, DI, Logger, 例外)
tests/
  unit/                   # src/ と同じ階層構造を維持
```

## DI パターン

- FastAPI の `Depends` を使い、router から直接 `new` しない
- `lru_cache` で設定・repository をシングルトン化
- テスト向けに `clear_*_cache()` 関数を公開
- `type` alias で `Annotated[..., Depends(...)]` を短縮:

```python
type SettingsDependency = Annotated[AppSettings, Depends(get_settings)]
type FavoriteRepositoryDependency = Annotated[FavoriteRepository, Depends(get_csv_favorite_repository)]
```

- テストでは `app.dependency_overrides` で差し替え

## Router 規約

- `APIRouter(prefix="/v1", tags=["..."])`
- `operation_id` を OpenAPI 定義と一致させる
- `response_model_by_alias=True` でレスポンスの camelCase を保証
- `responses` ディクショナリで想定ステータスコードを明示
- Path パラメータ:

```python
video_id: Annotated[
    str,
    Path(alias="videoId", pattern=r"^[a-zA-Z0-9_-]{11}$", description="..."),
]
```

- Query パラメータのデフォルト値は `Param` 側でなく関数引数側に置く:

```python
limit: Annotated[int, Query(ge=1, le=100, description="...")] = 20
```

## Request/Response 変換

- domain entity と HTTP model は分離する
- router 内に薄い `_to_response()` 変換関数を配置
- 永続化モデルをそのまま API response に返さない

```python
def _to_response(entity: FavoriteEntity) -> Favorite:
    return Favorite(
        videoId=entity.video_id,
        title=entity.title,
        ...
    )
```

## 例外ハンドリング

- 3 層に分離:
  - **Domain**: `DomainError` — domain 層のバリデーション・不変条件違反
  - **Application**: `ApplicationError` → `NotFoundError`, `ConflictError` — ビジネスロジックエラー
  - **HTTP**: `HTTPException` — router 内のみ
- router で domain/application 例外を `HTTPException` に変換
- `NoReturn` 型ヒント付きヘルパー:

```python
def _raise_not_found(detail: str) -> NoReturn:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
```

## 非同期方針

- **sync/async はプロジェクト全体で統一する。混在させない**
- async の場合: 全レイヤーで `async def`、ブロッキング I/O は `asyncio.to_thread` で包む
- sync の場合: 全レイヤーで通常の `def`

## 設定管理

- `pydantic-settings` の `BaseSettings` を使用
- `SettingsConfigDict(case_sensitive=False, extra="ignore", populate_by_name=True, validate_default=True)`
- 環境変数名は `validation_alias` で明示
- `min_length=1` で空文字拒否

```python
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(...)
    app_name: str = Field(default="...", min_length=1, validation_alias="APP_NAME")
```

## 実装順序（新機能追加時）

1. `domain/` に Entity / Value Object を定義
2. `ports/outbound/` に抽象インターフェースを定義
3. `usecases/` にユースケースを実装（port を引数で受け取る）
4. `adapters/outbound/` に実装
5. `adapters/inbound/` に router を追加
6. `shared/dependencies.py` に DI provider を登録
7. テストを作成（`src/` と同じ階層に配置）

## やってはいけないこと

- 1 ファイルに複数層を詰め込む
- router で保存先を直接操作する（必ず usecase / port 経由）
- 永続化モデルをそのまま API response に返す
- domain / usecase で FastAPI や HTTP に依存する
- sync/async を混在させる
