# Workflow: Implementation

## 目的

合意済みプランに従い、安全に実装・自己検証・成果報告を行う。

## 手順

1. 実装前チェック
   - 対象ファイル
   - 非対象ファイル
   - 依存方向違反の有無
2. 実装
   - 1 ステップずつ最小変更で進める
   - 生成コード編集禁止
3. テスト
   - 変更近傍テスト -> 単体テスト全体
4. 整形・静的検査
   - ruff check / format
5. 変更サマリ作成
   - 変更ファイル一覧
   - 検証コマンド結果

## 注意

- Copilot 固有機能（askQuestions/handoff/tools）は Codex では直接再現せず、
  Markdown ベースの進行管理と Decision Request で代替する。

## Decision Gate

実装途中で新しい設計選択が発生した場合、即時実装せず `Decision Request` を提示して停止する。
