# Workflow: Intake

## 目的

依頼内容・制約・期待成果物を明確化し、実装着手前の不確実性を減らす。

## 手順

1. 依頼要約（1〜3 行）
2. 既知情報と不足情報の整理
3. 調査対象ファイルの特定
4. 制約（非機能要件、互換性、期限）の確認
5. Decision Gate の判定

## Decision Request テンプレート

```md
## Decision Request

### Decision to make
- <何を決めるか>

### Options
1. <Option A>
2. <Option B>
3. <Option C>

### Recommended
- <推奨オプションと理由>

### Impact by option
- Option A: <何が変わるか>
- Option B: <何が変わるか>
- Option C: <何が変わるか>

### Stop condition
- ユーザーが Option を明示選択するまで停止する
```

## 完了条件

- 要件と制約が明文化されている。
- 不明点がある場合、Decision Request を提示して停止している。
