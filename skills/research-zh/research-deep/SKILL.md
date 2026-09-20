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

**模型指定（重要）**：派发每个web-search-agent子agent时使用 **sonnet** 模型。检索+事实抽取+填字段是广度型任务，Sonnet性价比最优（约为Opus质量的90-95%，成本约1/5、更快）；跨item的综合与判断留给主线程/`research-report`阶段用Opus兜底，因此子agent降档几乎不损失最终质量。
- **网页/云端会话**：执行者必须在派发子agent时**显式指定 model=sonnet**（此类环境不会读取 `agents/web-search-agent.md` 的 model 字段，模型由派发时决定）。
- **本地CLI**：由 `agents/web-search-agent.md` 的 `model: sonnet` 字段自动控制，无需额外操作。
- 不要用Haiku跑deep阶段：它对多源交叉、来源可信度判断、长上下文抽取偏弱，易抽浅漏口径。

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
