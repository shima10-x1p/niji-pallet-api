# Coding Instructions

## 実装ルール

- 実装順序は原則として `domain -> ports/outbound -> usecases -> adapters/outbound -> adapters/inbound`。
- 1 ファイルに複数レイヤーを混在させない。
- router から repository を直接操作しない（必ず usecase / port 経由）。
- 永続化モデルをそのまま API response に返さない。

## 命名・責務分割

- 変数・関数・クラス名は意図が分かる名前を使う。
- 関数は単一責務を意識し、長すぎる関数を分割する。
- `Annotated` を活用し、依存関係やバリデーション意図を明示する。

## ファイル配置

- domain: `src/core/domain/`
- usecase: `src/core/application/usecases/`
- outbound port: `src/core/application/ports/outbound/`
- inbound adapter(router): `src/core/adapters/inbound/`
- outbound adapter: `src/core/adapters/outbound/`
- shared concerns (settings/logger/DI): `src/core/shared/`

## Python / FastAPI 規約

- Python スタイルは PEP 8 準拠。
- 型ヒントを必須化し、Pydantic は v2 API を使用する。
- sync/async はプロジェクト内で混在させず、一貫した方針を維持する。
- DI は FastAPI `Depends` を使い、router で直接 `new` しない。
- ルーティング順序に依存するパス（例: `/search` と `/{id}`）は衝突を避けて定義する。

## フォーマット / lint / 型チェック

推奨コマンド:

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

必要に応じて、変更範囲を絞ったテスト実行を先行する。

## 変更時の注意点

- `src/generated/` は編集しない。
- API 仕様変更時は OpenAPI を更新し、必要なモデルを再生成する。
- コメントは「なぜそうするか」を優先して記述する。
- 既存 Copilot 資産（`.github/`）は削除・破壊しない。

## Decision Gate

When a task requires a design choice, do not implement immediately.

First, output a `Decision Request` with:

- the decision to make
- 2 to 4 options
- the recommended option
- what changes depending on each option
- a clear stop condition

After outputting a `Decision Request`, stop and wait for the user's reply.

Do not modify files, run implementation commands, or continue into implementation until the user explicitly selects an option.
