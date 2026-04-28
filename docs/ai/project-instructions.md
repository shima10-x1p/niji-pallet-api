# Project Instructions

## プロジェクト概要

- 本プロジェクトは Python 3.14 + FastAPI で構成された、にじさんじライバーカラー管理 API。
- API 仕様は `docs/openapi.yaml` を基準に管理する。
- アーキテクチャは Ports and Adapters（Hexagonal Architecture）を採用する。

## アーキテクチャ方針

依存方向は次を厳守する。

```text
inbound adapter (router) → usecase → domain
                 usecase → ports/outbound (抽象)
outbound adapter → ports/outbound を実装
```

- domain / usecase は FastAPI・HTTP ライブラリへ直接依存しない。
- router は薄く保ち、ビジネスロジックを持たせない。
- 保存先アクセスは `ports/outbound` 経由で行い、差し替え可能にする。

## 依存関係・ディレクトリ前提

```text
src/
  core/
    domain/
    application/
      usecases/
      ports/outbound/
    adapters/
      inbound/
      outbound/
    shared/
  generated/  # OpenAPI 由来の生成コード

tests/
  unit/
  integration/
```

- テストは `src/` に混在させず `tests/` 配下へ分離する。
- `tests/unit`・`tests/integration` は `src/` と同じ階層構造で配置する。

## 生成コードと手書きコード

- `src/generated/` は自動生成コード。手動編集禁止。
- OpenAPI 変更が必要な場合は `docs/openapi.yaml` を更新し、再生成で反映する。
- 手書きロジックは `src/core/` 配下に配置する。

## 共通ルール

- 依存管理は `uv` を使用し、`pip install` は使わない。
- コメント・docstring は日本語を基本とする。
- ログは `src/core/shared/logger.py` のロガーを利用する。

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
