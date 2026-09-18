# CLAUDE.md

本仓库是一套用于 Claude Code / OpenCode / Codex 的**结构化深度调研 skill**。
在本仓库中接到调研类任务时，一律走本文件定义的流程与产出规范。

## 标准要求

任何调研任务默认满足以下四条，除非用户当次明确改口：

1. **用本仓库的 skill 做调研**，不要自己临时发挥。完整走 `/research` → `/research-deep` → `/research-report` 三阶段。
2. **报告用 HTML 形式**输出（`report.html`）。markdown 只作为中间产物保留。
3. **报告背景用深色**。
4. **子 agent 一律用 Sonnet 5**（`model: "sonnet"`）。

## 调研工作流

| 阶段 | 命令 | 产出 |
|---|---|---|
| 1 生成 outline | `/research <topic>` | `{topic}/outline.yaml`、`{topic}/fields.yaml` |
| 1.5 增补（可选） | `/research-add-items`、`/research-add-fields` | 同上，增量更新 |
| 2 深度调研 | `/research-deep` | `{topic}/results/*.json`，每个 item 一个 |
| 3 汇总报告 | `/research-report` | `{topic}/report.html`（深色）、`{topic}/report.md` |

Step 1 与 Step 2 的 agent prompt 在 SKILL.md 中被标为**硬约束**：必须严格复述模板，
只替换 `{xxx}` 变量，不要改写结构或措辞。需要额外传递的约定（如输出格式要求），
写进 outline.yaml 的 item 字段里，通过 `{item_related_info}` 变量带进去。

## 环境准备

skill 与 agent 必须先装到规定路径，否则 `/research-deep` 的校验步骤和
`web-search-agent` 子 agent 类型都会失效：

```bash
cp -r skills/research-zh/* ~/.claude/skills/        # 中文版；英文版用 research-en
cp agents/web-search-agent.md ~/.claude/agents/
cp -r agents/web-search-modules ~/.claude/agents/
pip install pyyaml
```

## 硬性约定（踩过的坑）

**fields.yaml 只接受一种 schema**，`validate_json.py` 对其它写法直接报错退出：

```yaml
fields:
  <分类名>:
    - name: <字段名>
      description: <字段说明>
      detail_level: 极简 | 简要 | 详细
uncertain: []
```

未显式标 `required:` 时，**所有字段都视为必填**。

**深调产出的 JSON 必须是扁平结构**——所有字段名作为顶层 key，不要用分类层级包裹。
`validate_json.py` 只对 `CATEGORY_MAPPING` 里预置的英文分类 key（`basic_info`、
`technical_features` 等）递归下钻；自定义分类名（尤其中文分类）下的嵌套字段**不会被识别**，
会导致覆盖率为 0 而验证失败。

**打分类字段需要横向校准。** 各 item 由独立 agent 并行调研，彼此不可见，
所以要求它们给"绝对锚点分"而非"相对排名分"，再由主线程在报告阶段统一 normalize。
同理，各家胜率之和需要在主线程归一，不能指望子 agent 自行协调。

**引用可追溯。** 让每个子 agent 在 JSON 里额外输出 `sources` 数组（标题 + url + 日期），
报告的"信息来源"段落依赖它。

## 报告生成

`generate_report.py` 由 `/research-report` 阶段生成，放在 `{topic}/` 下，需要：

- 动态读取 `fields.yaml`，不要硬编码字段名
- 跳过值含 `[不确定]` 的字段，以及 `uncertain` 数组中列出的字段名
- 目录包含每一个 item，带锚点跳转
- 深色主题：正文底色与面板色分层，图表配色需在深色背景下通过对比度与色盲可辨性校验
- 跨 item 的校准结论（打分表、胜率、综合判断）单独放在 `synthesis.json`，
  由脚本读取后渲染在报告前部，与各 item 的原始字段明细分开

## Token 经济性（重要）

深度调研的成本 ≈ **agent 数 × 字段数 × 检索轮数**，三者都要主动压。
默认按以下方式跑，除非用户要求不计成本地穷尽。

### 调研产物一律不入库

本仓库是 skill 仓库，不是调研产物仓库。**调研过程与产出全部本地处理，不提交**——
包括 `results/`、构建脚本、`synthesis.json`，以及最终的 `report.html`。
`.gitignore` 已排除。

调研结束后把报告交给用户即可，不要为了"留档"而往仓库里塞。

### 断点续传（注意：仅限同一会话内）

`/research-deep` 会扫描 `output_dir` 下已完成的 JSON 并跳过对应 item。
但由于 `results/` 不入库，**这个机制只在同一会话、同一容器内有效**。

必须清楚这个取舍：

- 仓库保持干净，代价是**会话中断 = 已完成的 item 全部丢失，需要重跑**
- 因此单次会话内要尽快跑完；预计跑不完时，主动提醒用户这个风险
- 用户若要跨会话续传，需当场把 `results/` 手动备份出去，或临时取消 gitignore

相应地，子 agent 的**分段落盘**纪律变得更重要（见下文经验），
因为它是会话内唯一的止损手段。

### 控制调研对象数量

只为**会改变结论**的对象派 agent。判断标准：如果某个对象的全部字段都填满，
结论会不会变？不会就不要立 item。

不改变结论的对象，用 `synthesis_only_variables` 记在 outline.yaml 里——
保留它的关键数字与信源，在 synthesis 阶段直接引用，省掉一整个 agent。

对照标杆同理：只取校准所需的最小必要集，不要为它填满全字段。

### 增量补录，不要重跑

中途通过 `/research-add-fields` 新增字段时，**不要重跑整个 item**。
派轻量 agent 只补差额字段，读取已有 JSON 后合并写回。
重跑一个 item 的成本是补录的 5-10 倍。

### 子 agent 必须分片落盘

子 agent 的默认行为是**检索完全部字段、最后一次性写 JSON**。
在那次写盘之前磁盘上什么都没有，成果只存在于它的上下文里——
agent 一被杀（限额、超时），上下文蒸发，所有检索等于白做。

派 agent 时在 prompt 里强制要求：**每完成约 15 个字段就落一次盘。**

写法必须是**分片追加**，不是全量覆盖：

- 分片追加：每片只输出新增字段（`xxx.part1.json`、`part2.json`…最后合并），
  每个字段内容只输出一次，**几乎零额外成本**
- 全量覆盖：每次重写完整 JSON，前面的字段被反复输出，
  一个 78 字段的调研会多烧约 60-70% 的 token

对照基准：中断后重跑一个 agent 是整整 15 万 token 全损重来。
分片落盘不要钱却能把损失从 100% 压到 20%，没有理由不做。

由于调研产物不入库（见上文），**这是会话内唯一的止损手段**。

### 中断抢救：先找构建脚本，再考虑重跑

agent 因限额/超时中断时，**不要立刻重跑**。先去 scratchpad 和
`research-archive/` 找它的 `build_*.py`。

子 agent 处理大量中文时，常会先写一个构建脚本把结果拼成 Python 字面量、
再执行它生成 JSON。如果它死在"脚本已写、尚未执行"这一步，
直接 `python` 跑一遍脚本就能**零成本**拿回全部结果。

2026-09-18 那次 6 个 agent 全部被会话限额打断，靠这一招救回 4 个。

### 子 agent 纪律

- 一律用 `model: "sonnet"`，不要用更贵的模型做检索
- 让子 agent **直接写文件**，不要回传大段正文（`/research-deep` 明确要求禁用 task output）
- **绝对不要读子 agent 的 transcript 输出文件**（`tasks/*.output`）——那是完整 JSONL，
  会直接撑爆主线程 context。要进度就看 `results/` 下的文件数
- 主线程不要重复子 agent 正在做的检索

### 字段规模

字段数是乘在每个 agent 上的成本。定义字段时优先合并同类项，
砍掉"知道了也不影响判断"的字段。67 个字段已属偏多，
超过 80 个应当先问自己是不是该拆成两轮调研。

### 人在回路是省钱的

outline 阶段的 `AskUserQuestion` 确认不是流程摆设：
方向跑偏后重来一轮的成本，远高于提前问清楚。
可以把多个确认合并到一次 `AskUserQuestion` 调用里（最多 4 个问题），
减少往返轮次。

## 中间产物归档

调研过程中产生的中间产物（子 agent 的 `build_*.py` 构建脚本、临时脚本、抓取缓存等）
统一归档到：

```
research-archive/<调研标题>-<YYYY-MM-DD>/
```

**非当次调研不要读这个目录。** 里面的构建脚本动辄 700+ 行，
读进主线程只会浪费 token。要看某次调研的结论，读它的 `report.html` 或 `results/*.json`。

保留构建脚本的唯一目的是**抢救中断的调研**，见下文「经验」。

## 调研对象取舍（硬规则）

**只为会改变结论的对象派 agent。** 这是省 token 的最大杠杆，远大于其它所有技巧。

绝不为以下对象单独起 agent：

- **国际对照标杆**（Microsoft 365 Copilot、Google Workspace、Slack 等）——
  只需要几个数据点做代差校准，不需要填满全字段
- **赛道旁支玩家**（如百度库库AI 之于"飞书/企微/钉钉"的调研）——
  不在用户圈定范围内，其定价、渠道、部署细节不影响结论
- 任何"填满全部字段后结论也不会变"的对象

这些一律写进 `outline.yaml` 的 `synthesis_only_variables`，
保留关键数字与信源，在 synthesis 阶段直接引用。

判断方法：问自己"如果这个对象所有字段都填满，我的结论会变吗？"不会就不立 item。

## 语言

调研过程可用英文检索，但**最终 JSON 字段值与报告正文一律用中文**。
