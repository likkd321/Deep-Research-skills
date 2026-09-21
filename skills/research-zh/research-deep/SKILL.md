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
在当前工作目录查找 `*/outline.yaml` 文件，读取items列表、execution配置（含items_per_agent）。

### Step 2: 断点续传检查
- 检查output_dir下已完成的JSON文件
- 跳过已完成的items

### Step 3: 分批执行
- 按batch_size分批（完成一批需要得到用户同意才可进行下一批）
- 每个agent负责items_per_agent个项目
- 启动web-search-agent（后台并行，禁用task output）

**模型指定（按 execution.mode 决定，重要）**：读取 outline.yaml 的 `execution.mode`（缺省视为 `efficiency`），据此决定每个 web-search-agent 子 agent 的模型。

- **`efficiency`（效率模式，默认）**：子 agent **默认 sonnet**（检索+抽取+填字段是广度型任务，Sonnet 约为 Opus 质量的 90-95%、成本约 0.4×、更快）。
  仅当某个 item 满足以下任一**升档条件**时，**该 item 单独升 opus**（而非全部升档）：
  1. 可靠一手来源稀疏（几乎搜不到权威来源，需从少量证据判断）；
  2. 需要从零散/间接证据做**推断或预测**，而非直接摘录；
  3. 该 item 的字段本身要求**判断/评估**（如前景研判、争议裁定）而非罗列事实。
  默认不升——多数检索型 item 用 sonnet 即可，避免"自选"退化成"全 sonnet"或"全 opus"。
- **`performance`（性能模式）**：所有子 agent **一律 opus**。
- **两种模式相同**：最终 `research-report` 的跨 item 综合与判断**始终用 opus**（只跑一趟、最吃质量，不降档）。
- **派发方式**：网页/云端会话**必须在派发子 agent 时显式指定 model**（`model=sonnet` 或 `model=opus`；此类环境不读 `agents/web-search-agent.md` 的 model 字段）；本地 CLI 由该文件的 `model` 字段提供默认值，需要升档的 item 在派发时覆盖为 opus。
- 不要用 Haiku 跑 deep 阶段：它对多源交叉、来源可信度判断、长上下文抽取偏弱，易抽浅漏口径。

**参数获取**：
- `{topic}`: outline.yaml中的topic字段
- `{item_name}`: item的name字段
- `{item_related_info}`: item的完整yaml内容（name + category + description等）
- `{output_dir}`: outline.yaml中execution.output_dir（默认./results）
- `{fields_path}`: {topic}/fields.yaml的绝对路径
- `{output_path}`: {output_dir}/{item_name_slug}.json的绝对路径（slugify处理item_name：空格替换为_，移除特殊字符）

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

### Step 4: 等待与监控
- 等待当前批次完成
- 启动下一批
- 显示进度

### Step 5: 汇总报告
全部完成后输出：
- 完成数量
- 失败/不确定标记的items
- 输出目录

### Step 6: 定向补深（复用已有agent，勿冷启动重跑）
汇总后若某item字段偏薄、关键数字仅靠单一来源、或多源数字冲突：
- **优先唤醒该item对应的、仍在会话中的子agent**（带完整上下文继续对话，如环境支持用其agent id/SendMessage），给出具体补深指令，例如"CTR区间只有一个来源，去读各家方法学把冲突数字调和掉并注明口径差异"。
- 只对存疑字段**定向补充**，不要全部item重跑；补完重新运行validate_json.py。
- 仅当对应agent已不可唤醒（会话/容器已回收）时，才用断点续传方式对该**单个**item冷启动新agent。
- 这样既省token、又比全量重跑更快更对症。

## Agent配置
- 后台执行: 是
- Task Output: 禁用（agent完成时有明确输出文件）
- 断点续传: 是
