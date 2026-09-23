---
name: research
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: 对目标话题进行初步调研，生成调研outline。用于学术调研、benchmark调研、技术选型等场景。
---

# Research Skill - 初步调研

## 触发方式
`/research <topic>`

## 执行流程

### Step 1: 模型内部知识生成初步框架
基于topic，利用模型已有知识生成：
- 该领域的主要研究对象/items列表
- 建议的调研字段框架

输出{step1_output}，使用AskUserQuestion确认：
- items列表是否需要增减？
- 字段框架是否满足需求？

### Step 2: Web Search补充
使用AskUserQuestion在正式开跑前一次问清四件事（正好是一次AskUserQuestion的4问上限）：
1. **时间范围**（如：最近6个月、2024年至今、不限）；
2. **执行模式**（模式1 全opus / 模式2 甜点区=默认 / 模式3 全sonnet，含义见Step 4的execution.mode）；
3. **最大子agent并行数**（即每批同时运行的子agent上限，写入 execution.batch_size，默认3；给几个常用档如 2/3/5 供选）；
4. **item分配**（每个item如何分配给子agent、每个子agent负责几个）：在问题里点名建议的重点核心item，给出如"核心item各自单独一个agent、其余每个agent 2–3个（模式1/2推荐）"/"每个agent只负责1个"/"每个agent 3–4个（模式3推荐）"等选项；与第2问的模式冲突时以模式为准（模式3下核心item也合并分组）。写入 execution.core_items 与 execution.items_per_agent。

**参数获取**：
- `{topic}`: 用户输入的调研话题
- `{YYYY-MM-DD}`: 当前日期
- `{step1_output}`: Step 1生成的完整输出内容
- `{time_range}`: 用户指定的时间范围

**硬约束**：以下prompt必须严格复述，仅替换{xxx}中的变量，禁止改写结构或措辞。

启动1个web-search-agent（后台；网页/云端会话显式传 model，agent 类型兜底规则同 research-deep 的 Step 3），**Prompt模板**：
```python
prompt = f"""## 任务
调研话题: {topic}
当前日期: {YYYY-MM-DD}

基于以下初步框架，补充最新items和推荐调研字段。

## 已有框架
{step1_output}

## 目标
1. 验证已有items是否遗漏重要对象
2. 根据遗漏对象进行补充items
3. 继续搜索{topic}相关且{time_range}内的items并补充
4. 补充新fields

## 输出要求
直接返回结构化结果（不写文件）：

### 补充Items
- item_name: 简要说明（为什么应该加入）
...

### 推荐补充字段
- field_name: 字段描述（为什么需要这个维度）
...

### 信息来源
- [来源1](url1)
- [来源2](url2)
"""
```

**One-shot示例**（假设调研AI Coding发展史）：
```
## 任务
调研话题: AI Coding 发展史
当前日期: 2025-12-30

基于以下初步框架，补充最新items和推荐调研字段。

## 已有框架
### Items列表
1. GitHub Copilot: Microsoft/GitHub开发，首个主流AI编程助手
2. Cursor: AI-first IDE，基于VSCode
...

### 字段框架
- 基本信息: name, release_date, company
- 技术特性: underlying_model, context_window
...

## 目标
1. 验证已有items是否遗漏重要对象
2. 根据遗漏对象进行补充items
3. 继续搜索AI Coding 发展史相关且2024年至今内的items并补充
4. 补充新fields

## 输出要求
直接返回结构化结果（不写文件）：

### 补充Items
- item_name: 简要说明（为什么应该加入）
...

### 推荐补充字段
- field_name: 字段描述（为什么需要这个维度）
...

### 信息来源
- [来源1](url1)
- [来源2](url2)
```

### Step 3: 询问用户已有字段
使用AskUserQuestion询问用户是否有已定义的字段文件，如有则读取并合并。

### Step 4: 生成Outline（分离文件）
合并{step1_output}、{step2_output}和用户已有字段，生成两个文件：

**outline.yaml**（items + 配置）：
- topic: 调研主题
- items: 调研对象列表
- execution:
  - batch_size: 最大并行子agent数，即每批同时运行的子agent上限（需AskUserQuestion确认）
  - mode: 执行模式，取值 1/2/3（需AskUserQuestion确认，默认 2）
    - `1`（模式1，全opus）：deep阶段子agent一律Opus；重点核心item可一个agent只看一个，其他item可一个子agent负责多个；适合高价值、数据有争议、要对外发布的研究
    - `2`（模式2，甜点区，默认）：按任务难度找甜点区——信息检索类item用Sonnet，需要大量深度判断的item用Opus（判定条件见research-deep Step 3）；item分配同模式1；适合大多数研究
    - `3`（模式3，全sonnet）：deep阶段子agent一律Sonnet，各子agent分配多个item；最省，适合探索性、以信息汇总为主的研究
    - 三种模式下最终report综合都用Opus（见research-deep）
  - core_items: 重点核心item列表，每个单独一个子agent（模式1/2；需AskUserQuestion确认；模式3可留空）
  - items_per_agent: 非核心item每个子agent负责几个（模式3下适用于全部item；需AskUserQuestion确认）
  - judgment_items: 需要大量深度判断的item（按research-deep Step 3的判定条件生成，三种模式都要标）：派 `web-search-agent-deep`（effort high），模式2下同时用Opus；其余item派 `web-search-agent`（effort medium）
  - agent_groups: 由以上各项生成的实际派发分组，每组 = 一个子agent，格式 `{agent: web-search-agent|web-search-agent-deep, model: opus|sonnet, items: [item名, ...]}`；同组的agent类型与模型都取组内最高需求；同主题/同来源的item尽量分到一组；按优先级排序（核心组在前）
  - output_dir: 结果输出目录（默认./results）

**fields.yaml**（字段定义）：
- 字段分类和定义
- 每个字段的name、description、detail_level
- detail_level分层：极简 → 简要 → 详细
- uncertain: 不确定字段列表（保留字段，deep阶段自动填充）

### Step 5: 输出并确认
- 创建目录: `./{topic_slug}/`
- 保存: `outline.yaml` 和 `fields.yaml`
- 展示给用户确认（含 agent_groups：共几个子agent、每个负责哪些item、用什么模型）

## 输出路径
```
{当前工作目录}/{topic_slug}/
  ├── outline.yaml    # items列表 + execution配置
  └── fields.yaml     # 字段定义
```

## 后续命令
- `/research-add-items` - 补充items
- `/research-add-fields` - 补充字段
- `/research-deep` - 开始深度调研
