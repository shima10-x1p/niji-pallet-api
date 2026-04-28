# Codex Migration Report

## 1. 調査した Copilot 向けファイル

| 区分 | ファイル | 主な内容 | 備考 |
|---|---|---|---|
| Copilot 入口 | `.github/copilot-instructions.md` | プロジェクト全体規約、実装順序、ディレクトリ規約 | 共有化のため `docs/ai/*` 参照を追加 |
| Instructions | `.github/instructions/python.instructions.md` | Python コーディング規約 | coding/testing へ反映 |
| Instructions | `.github/instructions/fastapi.instructions.md` | FastAPI + Hexagonal 規約 | project/coding/review へ反映 |
| Prompt | `.github/prompts/implement-plan.prompt.md` | 実装計画実行フロー、サブエージェント呼び出し | workflow + agent TOML へ変換 |
| Custom Agent | `.github/agents/python-test-agent.agent.md` | AAA テスト作成、askQuestions 利用 | testing/workflows + quality-review/intake へ変換 |
| Custom Agent | `.github/agents/code-review.agent.md` | レビュー観点、askQuestions 利用 | review-instructions + quality-review.toml へ変換 |
| Skill | `.github/skills/implement-plan/SKILL.md` | implement-plan 手順 | workflows/implement-plan + implement-plan.toml へ変換 |
| Skill | `.github/skills/test-readme/SKILL.md` | テスト README 更新ルール | testing-instructions + implementation workflow へ反映 |

## 2. Codex 向けに作成・更新したファイル

| 種別 | ファイル | 目的 |
|---|---|---|
| 入口 | `AGENTS.md` | Codex/Copilot 互換の短い入口と Decision Gate 集約 |
| 共通指示 | `docs/ai/project-instructions.md` | プロジェクト概要・構造・生成コード扱い |
| 共通指示 | `docs/ai/coding-instructions.md` | 実装・配置・lint/format 規約 |
| 共通指示 | `docs/ai/testing-instructions.md` | テスト方針、AAA、README 更新方針 |
| 共通指示 | `docs/ai/review-instructions.md` | レビュー観点統合 |
| Workflow | `docs/ai/workflows/intake.md` | 要件整理と Decision Request |
| Workflow | `docs/ai/workflows/design.md` | 設計フェーズの進行手順 |
| Workflow | `docs/ai/workflows/implement-plan.md` | 実装計画フェーズの標準化 |
| Workflow | `docs/ai/workflows/implementation.md` | 実装・検証手順の標準化 |
| Workflow | `docs/ai/workflows/quality-review.md` | 品質レビュー手順の標準化 |
| Codex agent | `.codex/agents/intake.toml` | Intake 向け subagent 定義 |
| Codex agent | `.codex/agents/design.toml` | 設計向け subagent 定義 |
| Codex agent | `.codex/agents/implement-plan.toml` | 実装計画向け subagent 定義 |
| Codex agent | `.codex/agents/implementation.toml` | 実装向け subagent 定義 |
| Codex agent | `.codex/agents/quality-review.toml` | レビュー向け subagent 定義 |
| Copilot 入口更新 | `.github/copilot-instructions.md` | 共有 instructions 参照を追記 |

## 3. 変換マッピング（Copilot -> Codex）

| Copilot 資産 | Codex 側の受け皿 | 変換内容 |
|---|---|---|
| `copilot-instructions.md` | `AGENTS.md`, `docs/ai/project-instructions.md`, `docs/ai/coding-instructions.md` | 共通ルールを docs/ai に分離し、入口を簡素化 |
| `python.instructions.md` | `docs/ai/coding-instructions.md`, `docs/ai/testing-instructions.md` | Python 実装・テスト規約として再編 |
| `fastapi.instructions.md` | `docs/ai/project-instructions.md`, `docs/ai/review-instructions.md` | Hexagonal/DI/境界ルールを統合 |
| `implement-plan.prompt.md` | `docs/ai/workflows/implement-plan.md`, `.codex/agents/implement-plan.toml` | prompt 主導フローを workflow + agent 定義へ変換 |
| `python-test-agent.agent.md` | `docs/ai/testing-instructions.md`, `.codex/agents/quality-review.toml` (観点), `.codex/agents/intake.toml` (確認手順) | askQuestions 依存を Decision Request へ置換 |
| `code-review.agent.md` | `docs/ai/review-instructions.md`, `.codex/agents/quality-review.toml` | レビュー観点を Codex 用 developer_instructions 化 |
| `skills/implement-plan` | `docs/ai/workflows/implement-plan.md` | スキル手順を workflow 文書へ反映 |
| `skills/test-readme` | `docs/ai/testing-instructions.md` | テスト README 更新ルールを保持 |

## 4. 完全変換できなかったもの

| 項目 | 理由 | 代替 |
|---|---|---|
| `tools` フィールド（`vscode/askQuestions` など） | Copilot 固有の tool 実装に依存 | Decision Request + Markdown 手順で代替 |
| `agent` / `user-invocable` / `argument-hint` frontmatter の実行制御 | Codex 側で同等メタが直接互換でない | `.codex/agents/*.toml` の `name/description/developer_instructions` に意図を移植 |
| `handoff` 的な明示遷移 | 実行環境差異 | workflow ドキュメント内で「次フェーズ入力/出力」を明示 |

## 5. askQuestions / handoff / Copilot 固有 tool の代替方針

| Copilot 固有要素 | Codex 代替方針 |
|---|---|
| askQuestions / askQuestion | Decision Gate + `Decision Request` を Markdown で提示し、ユーザー回答待ち |
| handoff | `workflows/*.md` と agent instructions に「引き継ぎメモ（入力/出力/未解決）」を記述 |
| tools/frontmatter 連携 | 実行依存を外し、手順・判断基準・停止条件を文書化 |

## 6. 手作業で確認したほうがよい点

| 確認項目 | 推奨アクション |
|---|---|
| Copilot Chat 実行時の参照順 | `.github/copilot-instructions.md` から `docs/ai/*` 参照が効いているか確認 |
| Codex subagent 運用 | `.codex/agents/*.toml` を使った運用手順をチーム内で 1 回ドライラン |
| Decision Gate の運用定着 | プランニング系タスクで Decision Request を実際にテンプレ運用 |
| docs/ai の重複 | 既存 `.github/instructions` と乖離が増えないよう、更新窓口を `docs/ai` 優先に統一 |
