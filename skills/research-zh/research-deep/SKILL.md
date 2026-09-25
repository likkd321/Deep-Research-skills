---
name: research-deep
user-invocable: true
description: 读取调研outline，为每个item启动独立agent进行深度调研。禁用task output。
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task
---

# Research Deep - 深度调研

## 触发方式
`/research-deep`

## 执行流程

### Step 1: 自动定位Outline
在当前工作目录查找 `*/outline.yaml` 文件，读取items列表、execution配置（含mode、agent_groups）。若没有 agent_groups（旧outline），按 mode、core_items、items_per_agent 现场分组并展示给用户确认。

### Step 2: 断点续传检查
- 检查output_dir下已完成的JSON文件
- 跳过已完成的items；多item组里已完成的item从组内剔除，整组都完成则跳过该组

### Step 3: 分批执行
- 派发单位是 `execution.agent_groups` 里的一组：每组 = 一个子agent（核心item通常一组一个，其余一组多个）
- 按batch_size分批，每批最多 batch_size 个子agent同时运行（完成一批需要得到用户同意才可进行下一批，用 AskUserQuestion 可选项询问）
- 启动web-search-agent（后台并行，禁用task output）

**模型指定（按 execution.mode 决定，重要）**：读取 outline.yaml 的 `execution.mode`，取值 `性能` / `标准` / `经济`（英文写法 `performance` / `standard` / `economy` 等价；缺省视为 `标准`；旧数字值 `1` / `2` / `3` 依次视为性能 / 标准 / 经济，更早的 `efficiency` 视为 `标准`），据此决定每个 web-search-agent 子 agent 的模型。

- **性能模式（全 opus）**：所有子 agent **一律 opus**。重点核心 item 可一个 agent 只看一个，其余 item 可一个子 agent 负责多个。
- **标准模式（甜点区，默认）**：按任务难度找甜点区。**信息检索类 item 用 sonnet**（检索+抽取+填字段是广度型任务，Sonnet 约为 Opus 质量的 90-95%、成本约 0.4×、更快）；**需要大量深度判断的 item 用 opus**，即满足以下任一条件：
  1. 可靠一手来源稀疏（几乎搜不到权威来源，需从少量证据判断）；
  2. 需要从零散/间接证据做**推断或预测**，而非直接摘录；
  3. 该 item 的字段本身要求**判断/评估**（如前景研判、争议裁定）而非罗列事实。
  默认用 sonnet——多数检索型 item 用 sonnet 即可，避免退化成"全 sonnet"或"全 opus"。item 分配同性能模式。
- **经济模式（全 sonnet）**：所有子 agent **一律 sonnet**，各子 agent 分配多个 item。
- **多 item 组的模型**：取组内最高需求（组内有任一 item 需 opus 则整组 opus），所以标准模式下需 opus 的 item 尽量单独成组。
- **三种模式相同**：最终 `research-report` 的跨 item 综合与判断**始终用 opus**（只跑一趟、最吃质量，不降档）。
- **agent 类型（努力程度，按任务性质选，与模式无关）**：信息检索类 item 派 `web-search-agent`（frontmatter `effort: medium`）；需要大量深度判断的 item（即上面三条判定条件，outline 里的 `judgment_items`；旧 outline 的 `opus_items` 视同）派 `web-search-agent-deep`（`effort: high`）。两者方法论正文一致，只差努力程度与默认模型；派发工具只能临时覆盖 `model`、不能覆盖 `effort`，所以努力程度靠选 agent 类型实现。多 item 组的 agent 类型同样取组内最高需求。
- **派发方式**：网页/云端会话**必须在派发子 agent 时显式指定 model**（`model=sonnet` 或 `model=opus`；此类环境不读 agent 文件的 model 字段）；本地 CLI 由 agent 文件的 `model` 字段提供默认值（`web-search-agent` 为 sonnet、`web-search-agent-deep` 为 opus），与模式不符时派发时覆盖（如性能模式全部覆盖为 opus、经济模式全部覆盖为 sonnet）。
- **agent 类型兜底**：仓库的 SessionStart 钩子（`.claude/hooks/session-start.sh`）会在云端会话启动时自动安装 skills/agent/模块，项目级 `.claude/agents/web-search-agent.md` 与 `.claude/agents/web-search-agent-deep.md` 让这两个类型开局即注册，一般无需兜底。若 Agent 工具仍报 not found（例如会话中途才装 agent），改用 `general-purpose` 派发，并在 prompt **最前面**加一行角色设定：`（角色设定：你是 web-search-agent。开始前先 Read ~/.claude/agents/web-search-agent.md，严格按其 Research Methodology 执行，包括先读 ~/.claude/agents/web-search-modules/ 下相应模块。）`（深度判断组把其中两处 `web-search-agent` 换成 `web-search-agent-deep`）——其后的模板正文仍一字不改。注意 `general-purpose` 不带 effort 设置，会继承会话的努力程度。
- 不要用 Haiku 跑 deep 阶段：它对多源交叉、来源可信度判断、长上下文抽取偏弱，易抽浅漏口径。

**参数获取**：
- `{topic}`: outline.yaml中的topic字段
- `{item_name}`: item的name字段
- `{item_related_info}`: item的完整yaml内容（name + category + description等）
- `{output_dir}`: outline.yaml中execution.output_dir（默认./results）
- `{fields_path}`: {topic}/fields.yaml的绝对路径
- `{output_path}`: {output_dir}/{item_name_slug}.json的绝对路径（slugify处理item_name：空格替换为_，移除特殊字符）
- 多item组另需：`{n}` 组内item数；`{item_related_info_i}` / `{output_path_i}` 第 i 个item的完整yaml与输出路径

**硬约束**：以下prompt必须严格复述，仅替换{xxx}中的变量，禁止改写结构或措辞。

**Prompt模板**：
```python
prompt = f"""## 任务
调研 {item_related_info}，输出结构化JSON到 {output_path}

## 字段定义
读取 {fields_path} 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
{output_path}

## 验证
完成JSON输出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path}
验证通过后才算完成任务。
"""
```

**One-shot示例**（假设调研GitHub Copilot）：
```
## 任务
调研 name: GitHub Copilot
category: 国际产品
description: Microsoft/GitHub开发，首个主流AI编程助手，市场份额约40%，输出结构化JSON到 {project_dir}/results/GitHub_Copilot.json

## 字段定义
读取 {project_dir}/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
{project_dir}/results/GitHub_Copilot.json

## 验证
完成JSON输出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f {project_dir}/fields.yaml -j {project_dir}/results/GitHub_Copilot.json
验证通过后才算完成任务。
```

**多item组的Prompt模板**（组内item数 > 1 时使用；同样严格复述、仅替换变量，按组内item数重复"### Item i"段与输出路径行）：
```python
prompt = f"""## 任务
依次调研以下{n}个item，每个item输出一个结构化JSON。每完成一个item就立即写出它的JSON并运行验证，再开始下一个（中途中断时已完成的item不会丢失）。

### Item 1
调研 {item_related_info_1}，输出结构化JSON到 {output_path_1}

### Item 2
调研 {item_related_info_2}，输出结构化JSON到 {output_path_2}

## 字段定义
读取 {fields_path} 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
{output_path_1}
{output_path_2}

## 验证
每个JSON写出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path_i}
全部item验证通过后才算完成任务。
"""
```

### Step 4: 等待与监控
- 等待当前批次完成
- 每批完成后依次：校验该批JSON → checkpoint（push 到 research 分支）→ 检查补深点，有则趁热补深（见 Step 6，不要等全部批次跑完）→ 用 AskUserQuestion 询问是否开下一批（补深计划可与这一问合并成一次询问）
- 启动下一批
- 显示进度

### Step 5: 汇总报告
全部完成后输出：
- 完成数量
- 失败/不确定标记的items
- 输出目录

### Step 6: 定向补深（每批结束趁热做；复用已有agent，勿冷启动重跑）
每批完成后（不要攒到全部批次跑完）若某item字段偏薄、关键数字仅靠单一来源、或多源数字冲突：
- **趁热**：子agent的上下文存在提示缓存里，有效期从它最后一次请求起算（云端会话一般1小时；超额用量或某些本地环境为5分钟），命中即续时。缓存期内唤醒只按缓存读计费（约一成输入价）；过期后唤醒要把整段上下文重写进缓存（1小时档写入约2倍输入价），仍优于冷启动但远不如趁热。所以补深放在每批结束后、开下一批之前，补深的子agent计入 batch_size 并行上限；Step 5 汇总后只做最后一轮查漏。
- **优先唤醒该item对应的、仍在会话中的子agent**（多item组即负责该组的子agent；带完整上下文继续对话，如环境支持用其agent id/SendMessage），给出具体补深指令，例如"CTR区间只有一个来源，去读各家方法学把冲突数字调和掉并注明口径差异"。
- **补查分工**：item内部的补深（调和它见过的数字、澄清口径、补几次搜索）交给原子agent；**跨item的口径冲突**（两个item对同一数字给出不同值）或与原调研关系不大的新问题，由主线程统一，或新开一个"复核agent"集中处理——读相关JSON、按统一口径核对后写回并重新验证，多个小问题合并给同一个复核agent。
- 只对存疑字段**定向补充**，不要全部item重跑；补完重新运行validate_json.py。
- 仅当对应agent已不可唤醒（会话/容器已回收）时，才用断点续传方式对该**单个**item冷启动新agent。
- 这样既省token、又比全量重跑更快更对症。

## Agent配置
- 后台执行: 是
- Task Output: 禁用（agent完成时有明确输出文件）
- 断点续传: 是
