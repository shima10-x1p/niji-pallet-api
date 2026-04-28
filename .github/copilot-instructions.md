# GitHub Copilot instructions

This repository keeps shared AI guidance under `docs/ai/`.

Follow:
- `docs/ai/project-instructions.md`
- `docs/ai/coding-instructions.md`
- `docs/ai/testing-instructions.md`

For review tasks, also follow:
- `docs/ai/review-instructions.md`

---

# Copilot Instructions — niji-pallet-api

## このリポジトリの目的

Python 3.14 + FastAPI で **にじさんじライバーカラー管理 API** を構築する。
ライバーごとのライバーカラーを取得・検索できる REST API を提供する。
アーキテクチャは **Ports and Adapters (Hexagonal Architecture)** を採用し、責務の追いやすさ・差し替えやすさを優先する。

OpenAPI スキーマは [`docs/openapi.yaml`](../docs/openapi.yaml) で管理する。
`src/generated/` は OpenAPI Generator による自動生成コード（編集禁止）。

## ビルド / 実行コマンド

```bash
uv run fastapi dev          # 開発サーバー起動
uv run pytest               # テスト実行
uv run pytest tests/unit    # unit テストのみ
uv run ruff check .         # lint
uv run ruff format .        # format
uvx --from datamodel-code-generator datamodel-codegen # OpenAPI スキーマから Pydantic モデルを生成
```

依存管理は **uv** のみ使用。`pip install` は使わない。

## ディレクトリ構成
```
src/
  core/
    domain/               # Entity / Value Object / Enum / Domain Service
    application/
      usecases/           # ユースケース (framework 非依存)
      ports/outbound/     # 外部依存の抽象 (Repository など)
    adapters/
      inbound/            # FastAPI router + request/response 変換
      outbound/           # CSV / SQLite / S3 など保存先の実装
  generated/              # OpenAPI Generator による自動生成コード（編集禁止）
tests/
  unit/                   # 作成したコード の unit テスト
```

テストは `src/` に混ぜず `tests/` に分離すること（ユーザー設定）。

### テストのディレクトリ構成

`tests/unit/` および `tests/integration/` 配下は **`src/` と同じ階層構造**を維持する。

```
src/core/shared/settings.py
→ tests/unit/core/shared/test_settings.py

src/core/application/usecases/list_livers.py
→ tests/unit/core/application/usecases/test_list_livers.py
```

テストファイルを新規作成するときは、対応する `src/` のパスに合わせてディレクトリを切ること。

## アーキテクチャ上の重要ルール

### 依存の方向
```
inbound → usecase → domain
usecase → ports/outbound (抽象)
adapters/outbound → ports/outbound を実装
```
- domain / usecase は FastAPI・Pydantic・HTTP ライブラリに依存しない
- router は薄く保つ。business logic を書かない
- 保存先（CSV / SQLite / S3 等）は `ports/outbound` の抽象を介してアクセスし、`adapters/outbound` で実装する

### DI パターン
FastAPI の `Depends` を使い、router から直接 `new` しない。

```python
# provider 関数例
def get_liver_repository() -> LiverRepository: ...
def get_list_livers_usecase(
    repo: Annotated[LiverRepository, Depends(get_liver_repository)],
) -> ListLiversUsecase: ...
```

テストでは `app.dependency_overrides` で差し替える。

## 主なユースケースとエンドポイント

| ユースケース | エンドポイント |
|------------|--------------|
| ライバー一覧取得 | `GET /v1/livers` |
| ライバー名前検索 | `GET /v1/livers/search` |
| ライバー単体取得 | `GET /v1/livers/{liverId}` |
| 現在色取得 | `GET /v1/livers/{liverId}/color` |

`GET /v1/livers/search` は静的パスなので、`/v1/livers/{liverId}` より**前に**定義すること（FastAPI のルーティング順）。

HTTP schema (request/response) と domain model は一致させることを前提にしない。

## 保存先の差し替え

ライバーデータの保存先は DI で差し替え可能にする。

- **In-Memory**: 最初の実装として使うシンプルな保存先
- **SQLite**: ローカル DB による永続化
- **S3**: クラウドストレージへの保存

`LiverRepository` の抽象インターフェースを定義し、各保存先の adapter を実装する。

## コーディング規則

- **型ヒント**: Python 3.12 構文を使用。`Annotated` を積極活用
- **モデル**: Pydantic v2 (`model_config`, `model_validator` など v2 API)
- **非同期**: 同期/非同期を途中で混在させない。方針を決めたら一貫させる
- **例外**: domain 例外 / application 例外 / HTTP 例外を層で分ける
- **コメント / docstring の言語**: このプロジェクトではコメント・docstringを日本語で記述する
- **コメント**: 「何をしているか」は最小限・処理が追える程度に書く。「なぜそうしているか」を中心に書く
  - 詳細な Python スタイルは [`.github/instructions/python.instructions.md`](instructions/python.instructions.md) を参照
- **ログ**: ロギングは `src/core/shared/logger.py` の get_logger で取得したロガーを使用すること
  - ログレベルは `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` を適切に使い分けること
  - ログメッセージは簡潔に、かつ問題のトラブルシューティングに必要な情報を含めること
  - ログに個人情報や機密情報を含めないこと
  - 関数の開始・終了: `DEBUG` レベルでログを出す。例: `logger.debug("Started function X with args: %s", args)`
  - 重要なイベント: `INFO` レベルでログを出す。例: `logger.info("User %s logged in", user_id)`
  - 警告: `WARNING` レベルでログを出す。処理に失敗したが、システム全体には影響がない場合に使用。例: `logger.warning("Disk space is low: %d%% remaining", disk_space)`
  - エラー: `ERROR` レベルでログを出す。システム全体に影響がある場合に使用。例: `logger.error("Failed to process request: %s", error_message)`

### docstring の例

```python
def example_function(param1: int, param2: str) -> bool:
    """
    例示用の関数

    Args:
        param1 (int): 整数のパラメータ
        param2 (str): 文字列のパラメータ

    Returns:
        bool: 処理結果

    Exceptions:
        ValueError: param1 が負の値の場合に発生
        TypeError: param2 が空文字列の場合に発生
    """
    return True

## 実装順序（新機能追加時の標準手順）

1. `domain/` に Entity / Value Object を定義
2. `ports/outbound/` に抽象インターフェースを定義
3. `usecases/` にユースケースを実装（port を引数で受け取る）
4. `adapters/outbound/` に実装（in-memory 実装から始める）
5. `adapters/inbound/` に router を追加
6. `tests/unit/core/...` に usecase の unit test（`src/` と同じ階層）
7. `tests/integration/core/...` に router テスト（`src/` と同じ階層）

## やってはいけないこと

- 1ファイルに複数層を詰め込む
- router で保存先を直接操作する（必ず usecase / port 経由）
- 永続化モデルをそのまま API response に返す
- Lab なのに最初から複雑な抽象化を積み上げる（まず小さく動かす）
- `src/generated/` 配下のファイルを手動編集する（OpenAPI Generator で再生成するため上書きされる）
