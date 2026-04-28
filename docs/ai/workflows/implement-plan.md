# Workflow: Implement Plan

## 目的

合意済み設計を、実装手順・検証計画・レビュー観点付きの実行可能プランへ変換する。

## 手順

1. 対象プランの特定（会話履歴・ドキュメント・引数）
2. スコープ定義（対象/非対象）
3. 実装ステップ分解
   - domain
   - ports/outbound
   - usecases
   - adapters/outbound
   - adapters/inbound
4. テスト計画作成（unit 優先）
5. レビュー計画作成（セキュリティ/境界/保守性）
6. 実行前確認（ユーザー合意）

## Decision Gate

プランが複数ある、または優先順位が曖昧な場合は `Decision Request` を提示し、ユーザー合意まで停止する。
