# Workflow: Design

## 目的

要件を Hexagonal Architecture に沿った設計へ落とし込み、依存境界と責務を定義する。

## 手順

1. ユースケース分解（何を達成する処理か）
2. domain モデル / value object の設計
3. outbound port 抽象の定義
4. adapter 責務（inbound / outbound）の切り分け
5. エラー分類（domain/application/http）
6. テスト観点（正常系・境界値・異常系・回帰）の先行定義

## 出力物

- 設計サマリ
- 変更対象候補ファイル
- リスクとトレードオフ

## Decision Gate

設計選択肢が複数ある場合は、実装に進まず `Decision Request` を提示して停止する。
