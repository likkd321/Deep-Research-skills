# CLAUDE.md — 仓库约定

本仓库是 **skill 工具仓**，不是调研产物仓库。所有 Claude 会话在这里工作时遵守以下规矩。

## 1. master 只放工具，产物永不进 master

master（及任何会合并回 master 的分支）只包含工具本身：
`skills/`、`agents/`、`agents-codex/`、`scripts/`、`tests/`、`.claude/`（云端会话启动钩子与项目级 agent 注册）、`README*`、`LICENSE`、本文件。

**调研产物一律不进 master。** 原因：git 历史永久保留文件字节，"提交后再删"并不能瘦身，只会让工具仓无限膨胀。`.gitignore` 已挡掉产物文件，防止误提交。

## 2. 中间产物走 `research/<slug>` 子分支

每次调研新开一条分支 `research/<主题-slug>`（如 `research/google-search-ai`），在该分支上 checkpoint **中间产物**：

- **只 checkpoint 这三样**（断点续传的全部依据）：
  `<topic>/outline.yaml`、`<topic>/fields.yaml`、`<topic>/results/*.json`
- 因为 master 的 `.gitignore` 挡了它们，在 research 分支上用 **`git add -f`** 强制入库。
- **不要** checkpoint 报告文件(`*.html`、`report.md`)/ `generate_report.py` / `build_*.py` —— 这些是可再生物，由 `results/*.json` 经脚本重新生成即可（`.gitignore` 已按 `**/*.html` 等挡掉）。
- 所有产物放在**统一的 `<topic-slug>/` 目录**下（`outline.yaml`、`fields.yaml`、`results/`），不要把文件散落在分支根目录。

## 3. 为什么这样（尤其网页/云端会话）

网页/云端会话跑在**临时容器**里，闲置或结束即回收；**未 push 的产物会随容器一起丢**。因此：

- 中断风险高的长研究，`research-deep` 每完成一批就把 `results/*.json` push 到 research 分支做 checkpoint；容器万一被回收，换个会话 clone 该分支即可从断点继续（`research-deep` 的 Step 2 靠扫 `results/*.json` 跳过已完成项）。
- 研究做完后：留着分支当存档（不影响 master），或 `git push origin --delete research/<slug>` 清理。两者都不会让 master 变大。

## 4. 执行模式：子 agent 模型与 item 分配

由 `/research` 生成 outline 时选定的 `execution.mode` 决定，取值 `性能` / `标准` / `经济`（默认 `标准`；英文版 skill 写作 `performance` / `standard` / `economy`，两套写法等价）：

- **性能模式（全 opus）**：deep 阶段子 agent **一律 opus**。重点核心 item 可一个 agent 只看一个；其他 item 可一个子 agent 负责多个。
- **标准模式（甜点区，默认）**：按任务难度找甜点区——**信息检索类 item 用 sonnet**（约 Opus 质量 90-95%、成本 ~0.4×），**需要大量深度判断的 item 用 opus**（一手来源稀疏 / 需从零散证据推断预测 / 字段本身要判断而非罗列，满足任一即算；默认用 sonnet，避免退化成全 sonnet 或全 opus）。item 分配同性能模式。
- **经济模式（全 sonnet）**：deep 阶段子 agent **一律 sonnet**，各子 agent 分配多个 item。
- **多 item 的子 agent**：一组 item 共用一个子 agent，模型取组内最高需求（组内有任一 item 需 opus 则整组 opus），所以标准模式下需 opus 的 item 尽量单独成组；同主题、同来源的 item 尽量分到一组。
- **三种模式相同**：最终 `research-report` 的跨 item 综合始终用 **opus**（一趟、最吃质量，不降档）。
- **agent 类型与努力程度**（按任务性质选，与模式无关）：信息检索类用 `web-search-agent`（`effort: medium`），需要大量深度判断的用 `web-search-agent-deep`（`effort: high`）；模型仍按模式在派发时显式传。派发工具只能临时覆盖 `model`、不能覆盖 `effort`，所以努力程度靠 agent 类型区分；多 item 组取组内最高需求。
- **派发**：网页/云端会话须在**派发时显式传 `model`**（此类环境不读 agent 文件的 model 字段）；本地 CLI 由 agent 文件的 `model` 提供默认（`web-search-agent` 为 sonnet、`web-search-agent-deep` 为 opus），与模式不符时派发时覆盖。
- deep 阶段不要用 Haiku。
- 兼容旧 outline：旧数字值 `1` / `2` / `3` 依次按性能 / 标准 / 经济处理；更早的 `mode: efficiency` 按标准处理，`mode: performance` 即性能模式。

## 5. 定向补深：复用已有 agent，每批结束趁热补

某字段偏薄/单一来源/数字冲突时，优先**唤醒该 item 仍在会话中的子 agent**（带完整上下文继续）做定向补深，而不是全部 item 冷启动重跑。详见 `research-deep` 的 Step 6。

- **每批结束就趁热补，不要攒到全部批次跑完再补**：子 agent 的上下文存在提示缓存（KV cache）里，有效期从它最后一次请求开始计时（云端会话一般 1 小时；进入超额用量或某些本地环境为 5 分钟），每次命中都会续时。缓存期内唤醒，读缓存只收约一成输入价；过期后再唤醒，要把它十几万 token 的上下文整段重写进缓存（1 小时档写入约 2 倍输入价）——仍比冷启动重跑省，但远不如趁热。
- **顺序**：每批完成 → 校验 JSON 并 checkpoint 到 research 分支 → 若发现补深点，用可选项把"补什么、先补还是与下一批一起跑"和"是否开下一批"合并成一次询问 → 趁热补深（补深的子 agent 计入 `batch_size` 并行上限）→ 开下一批。
- **主线程同理**：等用户回复超过缓存期，下一次请求会把主线程上下文整段重写一次缓存；内容不会丢，只是那一次更贵、更慢。子 agent 运行期间不会替主线程续缓存，但它们完成时的通知会唤醒主线程、顺带续时。

## 6. 询问阶段与报告交付

- **需要用户确认或选择的询问，一律用可选项**（`AskUserQuestion`；Codex 版用 `request_user_input`）：每问给 2–4 个互斥选项，推荐项放第一个并标"(Recommended)"，用户可随时选 Other 自由输入；不要只在正文里用文字提问、让用户打字回复。适用于开跑前询问、outline 确认、每批结束后"是否开下一批 / 是否补深"、报告交付前确认等所有需要用户拍板的节点。
- **开跑前的询问**（`/research` Step 2，一次问清）：时间范围、执行模式(性能/标准/经济)、**最大子agent并行数**(每批同时运行上限，写入 `execution.batch_size`，默认3)、**item 分配**(每个 item 如何分配给子 agent：哪些核心 item 单独一个 agent、其余每个 agent 负责几个；写入 `execution.core_items` / `execution.items_per_agent`，据此生成 `execution.agent_groups`，在 Step 5 连同 outline 给用户确认)。
- **报告是讲述版**：最终报告由主线程把全部调研汇聚、浓缩后，像给客户讲解、给小孩讲故事一样有条有理地讲出来——**只展示推导/判断过程、核心数据和结论**；**正文不逐句标来源，也不展示各 item 的详情**（全量来源与明细留在 research 分支的 `results/*.json` 备查），不要把调研内容一股脑搬上来。
- **页面最下方附"核心参考网页"**：从各 item 的 `sources` 中精选一部分高价值网页（优先 opus 且单 item 子 agent 的核心来源，以及财报、业绩公告、电话会纪要、官方公告/文档等一手来源），按主题分组，每条写标题 + 链接（可加日期），约 10–25 条；是精选，不是全量来源列表。
- **报告必须记录"制作信息"**：起始问题（把用户最初的提示词压缩提炼成一两句）、主模型（主线程实际使用的模型，生成报告时向会话查询，不凭记忆写）、使用的 skill（如 `research` → `research-deep` → `research-report`，及子 agent 类型）、执行模式（性能/标准/经济）、制作时间（开始—完成，注明时区）。起始问题与开始时间在 `/research` Step 4 写入 outline.yaml 的 `request` / `started_at`；主模型只写进报告，不写进入库文件。
- **报告一律 HTML**：最终报告只出**单文件自包含 HTML**（不再 markdown），**文件名用报告标题**的 slug（不要用 `report.html` 这种通用名）。
- **背景白天/深色两种模式**：HTML 内置切换按钮 + 跟随系统 `prefers-color-scheme`，两套 CSS 变量配色，`body` 显式设背景。
- **交付方式**：**直接给用户一键可下载的文件**（`SendUserFile`，`display="attach"`）。**不要用 Artifact / 网页部署功能发布报告。** 本地 CLI 则文件在 `{topic}/` 目录、告知路径即可。
- 报告的综合与研判由主线程 **Opus** 完成（见第 4 节）。

## 7. 云端会话开箱即用（SessionStart 钩子）

- `.claude/settings.json` 注册了 `.claude/hooks/session-start.sh`：**仅在云端会话**（`CLAUDE_CODE_REMOTE=true`）启动时，把 `skills/research-zh/*` 装进 `~/.claude/skills/`、把 `agents/web-search-agent.md`、`agents/web-search-agent-deep.md` 与 `agents/web-search-modules/` 装进 `~/.claude/agents/`，并确保 `pyyaml` 可用。幂等、同步执行。要英文版 skills 就在环境变量里设 `RESEARCH_SKILLS_LANG=en`。
- 项目级 `.claude/agents/web-search-agent.md` 与 `.claude/agents/web-search-agent-deep.md` 让这两个子 agent 类型在会话开局即注册。**它们必须与 `agents/` 下同名文件保持逐字一致**，且两个 agent 的正文（方法论）也必须一致、只差 frontmatter（effort/model/description）——改 agent 时几处一起改（`tests/test_session_start_hook.sh` 会检查）。
- 若仍遇到 agent 类型未注册，按 `research-deep` Step 3 的"agent 类型兜底"用 `general-purpose` 派发。
