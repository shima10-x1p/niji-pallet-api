# Review Instructions

## レビュー観点

### 1) アーキテクチャ境界

- 依存方向 `inbound -> usecase -> domain` が守られているか。
- usecase が port 抽象を介して外部依存へアクセスしているか。
- router にビジネスロジックが混入していないか。

### 2) 依存方向と DI

- domain / usecase が FastAPI・HTTP 実装へ依存していないか。
- `Depends` ベースで DI され、テスト時に `dependency_overrides` 可能か。

### 3) セキュリティ

- 入力検証不足、インジェクション、機密情報ハードコードがないか。
- 例外ハンドリングで情報漏えいを起こさないか。

### 4) テスト不足

- 変更箇所に対して unit テストが追加・更新されているか。
- 正常系だけでなく境界値・異常系・回帰が考慮されているか。

### 5) 保守性

- 命名・責務分割・型ヒントが明確か。
- 長大関数、過剰分岐、重複実装がないか。

### 6) 生成コード混入チェック

- `src/generated/` を手動編集していないか。
- 生成物と手書きコードの責務が分離されているか。

## レビュー出力フォーマット（推奨）

- 指摘箇所（ファイル/行）
- 重大度（高/中/低）
- 問題内容
- 推奨修正方針

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
