# Testing Instructions

## テスト方針

- unit テストを優先し、必要に応じて integration テストへ拡張する。
- 既存プロジェクトの配置・命名規約を尊重する。
- 本番コード変更は最小限に抑え、テスト都合の過剰改変を避ける。

## テスト配置

- `tests/unit/` と `tests/integration/` を利用する。
- `src/` と同じ階層構造を維持する。

例:

```text
src/core/shared/settings.py
-> tests/unit/core/shared/test_settings.py
```

## 実行コマンド

```bash
uv run pytest
uv run pytest tests/unit
```

- まず変更箇所に近い最小スコープで実行し、必要に応じて全体実行する。

## AAA パターン

各テストは原則として AAA（Arrange / Act / Assert）で記述する。

- Arrange: 前提・入力・依存の準備
- Act: 対象処理の実行
- Assert: 期待結果・副作用・例外の検証

## mock / fixture / parametrized test

- モックを濫用せず、可能なら fake / stub / fixture を優先する。
- `pytest.mark.parametrize` を使って境界値やバリエーションを簡潔に表現する。
- 時刻・乱数・外部通信など非決定要素を隔離し、再現性を確保する。

## テスト追加時の確認観点

- 正常系
- 境界値
- 異常系
- 回帰（過去不具合の再発防止）

## テスト README の更新

テストの追加・変更・削除時は `.github/skills/test-readme/SKILL.md` のルールに従い、
`tests/unit/README.md` と必要なサブ README を更新する。

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
