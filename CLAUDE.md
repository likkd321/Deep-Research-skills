# CLAUDE.md — 仓库约定

本仓库是 **skill 工具仓**，不是调研产物仓库。所有 Claude 会话在这里工作时遵守以下规矩。

## 1. master 只放工具，产物永不进 master

master（及任何会合并回 master 的分支）只包含工具本身：
`skills/`、`agents/`、`agents-codex/`、`scripts/`、`tests/`、`README*`、`LICENSE`、本文件。

**调研产物一律不进 master。** 原因：git 历史永久保留文件字节，"提交后再删"并不能瘦身，只会让工具仓无限膨胀。`.gitignore` 已挡掉产物文件，防止误提交。

## 2. 中间产物走 `research/<slug>` 子分支

每次调研新开一条分支 `research/<主题-slug>`（如 `research/google-search-ai`），在该分支上 checkpoint **中间产物**：

- **只 checkpoint 这三样**（断点续传的全部依据）：
  `<topic>/outline.yaml`、`<topic>/fields.yaml`、`<topic>/results/*.json`
- 因为 master 的 `.gitignore` 挡了它们，在 research 分支上用 **`git add -f`** 强制入库。
- **不要** checkpoint `report.md` / `report.html` / `generate_report.py` / `build_*.py` —— 这些是可再生物，由 `results/*.json` 经脚本重新生成即可。
- 所有产物放在**统一的 `<topic-slug>/` 目录**下（`outline.yaml`、`fields.yaml`、`results/`），不要把文件散落在分支根目录。

## 3. 为什么这样（尤其网页/云端会话）

网页/云端会话跑在**临时容器**里，闲置或结束即回收；**未 push 的产物会随容器一起丢**。因此：

- 中断风险高的长研究，`research-deep` 每完成一批就把 `results/*.json` push 到 research 分支做 checkpoint；容器万一被回收，换个会话 clone 该分支即可从断点继续（`research-deep` 的 Step 2 靠扫 `results/*.json` 跳过已完成项）。
- 研究做完后：留着分支当存档（不影响 master），或 `git push origin --delete research/<slug>` 清理。两者都不会让 master 变大。

## 4. 子 agent 模型

子 agent 模型由 `/research` 生成 outline 时选定的 `execution.mode` 决定（默认 `efficiency`）：

- **`efficiency`（默认）**：deep 阶段子 agent 默认 **sonnet**（约 Opus 质量 90-95%、成本 ~0.4×）；仅当某 item 满足升档条件——一手来源稀疏 / 需从零散证据推断预测 / 字段本身要判断而非罗列——才**个别升 opus**（默认不升，避免退化成全 sonnet 或全 opus）。
- **`performance`**：deep 阶段子 agent **一律 opus**。
- **两种模式相同**：最终 `research-report` 的跨 item 综合始终用 **opus**（一趟、最吃质量，不降档）。
- **派发**：网页/云端会话须在**派发时显式传 `model`**（此类环境不读 `agents/web-search-agent.md` 的 model 字段）；本地 CLI 由该文件的 `model` 提供默认、需升档的 item 派发时覆盖为 opus。
- deep 阶段不要用 Haiku。

## 5. 定向补深优先复用已有 agent

某字段偏薄/单一来源/数字冲突时，优先**唤醒该 item 仍在会话中的子 agent**（带完整上下文继续）做定向补深，而不是全部 item 冷启动重跑。详见 `research-deep` 的 Step 6。
