# OpenAPI 連携ガイド

## 概要

OpenAPI 定義ファイル（`openapi.yaml`）からコードを生成し、router の request/response モデルとして利用するパターン。
この連携はオプショナルであり、手書きの Pydantic モデルでも代替可能。

## ワークフロー

### API-first（OpenAPI → コード生成）

```
openapi.yaml → OpenAPI Generator / datamodel-code-generator → src/generated/
                                                                      ↓
                                                    router が response_model として利用
```

### Code-first（コード → OpenAPI）

```
FastAPI router 定義 → FastAPI が自動生成 → /docs で確認
```

## ツール選択

### OpenAPI Generator

- **向き**: API 全体のスキャフォールディング（router のベースクラスも生成）
- **生成物**: models/, apis/, main.py 等
- **注意**: 生成コードの品質がテンプレート依存、カスタマイズが複雑になりがち

```bash
openapi-generator-cli generate \
  -i docs/openapi.yaml \
  -g python-fastapi \
  -o src/generated
```

### datamodel-code-generator

- **向き**: モデルクラスだけを生成したい場合（Pydantic v2 モデル）
- **生成物**: models.py（1 ファイル or ディレクトリ分割）
- **利点**: 軽量、Pydantic v2 ネイティブ対応、カスタマイズが容易

```bash
datamodel-codegen \
  --input docs/openapi.yaml \
  --output src/generated/models \
  --output-model-type pydantic_v2.BaseModel \
  --use-annotated
```

### 選択基準

| 観点 | OpenAPI Generator | datamodel-code-generator |
|---|---|---|
| モデルだけ欲しい | △ 過剰 | ◎ 最適 |
| Router の雛形も欲しい | ◎ 生成可能 | ❌ 非対応 |
| Pydantic v2 対応 | △ テンプレート次第 | ◎ ネイティブ |
| カスタマイズ性 | △ Mustache テンプレート | ◎ CLI オプション |
| 依存の少なさ | △ Java/Node 必要 | ◎ Python のみ |

## 生成コードの配置

```
src/
  generated/       # ← 自動生成コード（手動編集禁止）
    models/
      favorite.py
      create_favorite_request.py
      ...
  core/            # ← 手書きコード
    ...
```

**ルール**:
- `src/generated/` は手動編集しない（再生成で上書きされる）
- ruff の対象から除外: `pyproject.toml` で `exclude = ["src/generated"]`
- `__init__.py` のインポートも生成に任せる

## Router での利用パターン

```python
# 生成モデルを router の response_model / request body に使用
from generated.models.favorite import Favorite
from generated.models.create_favorite_request import CreateFavoriteRequest

@router.post("/favorites", response_model=Favorite, response_model_by_alias=True)
async def add_favorite(request: CreateFavoriteRequest, ...) -> Favorite:
    ...
    return _to_response(entity)  # domain entity → 生成モデルに変換
```

## domain entity との分離

生成モデル（HTTP model）と domain entity は別物として扱う。

```python
def _to_response(entity: FavoriteEntity) -> Favorite:
    """domain entity を API response model へ変換する。"""
    return Favorite(
        videoId=entity.video_id,      # snake_case → camelCase
        title=entity.title,
        channelName=entity.channel_name,
        ...
    )
```

**やってはいけないこと**:
- domain entity を直接 `response_model` にする
- 生成モデルを usecase / repository に渡す
- 生成モデルに domain ロジックを書く
