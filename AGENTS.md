# AGENTS Entry Point

この `AGENTS.md` は、GitHub Copilot / Codex など複数の AI agent が共通で参照する**互換入口ファイル**です。
詳細な規約・手順は `docs/ai/` 配下に分離しています。

## Read First（作業前に読む）

1. `docs/ai/project-instructions.md`
2. `docs/ai/coding-instructions.md`
3. `docs/ai/testing-instructions.md`
4. `docs/ai/review-instructions.md`
5. `docs/ai/workflows/intake.md`

## Phase ごとの参照先

- 要件整理 / ヒアリング: `docs/ai/workflows/intake.md`
- 設計: `docs/ai/workflows/design.md`
- 実装計画: `docs/ai/workflows/implement-plan.md`
- 実装: `docs/ai/workflows/implementation.md`
- 品質レビュー: `docs/ai/workflows/quality-review.md`

## Decision Gate（不明点・設計分岐がある場合）

仕様や設計の選択肢が複数ある場合は、実装を開始せずに `Decision Request` を提示してください。

`Decision Request` には以下を含めます。
- decision to make
- 2〜4 options
- recommended option
- option ごとの差分（何が変わるか）
- clear stop condition

`Decision Request` を提示したら停止し、ユーザーの選択を待ってください。
ユーザーが明示的に選択するまで、ファイル変更・実装コマンド実行・実装継続を行わないでください。
