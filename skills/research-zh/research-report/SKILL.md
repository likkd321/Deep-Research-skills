---
name: research-report
user-invocable: true
description: 将deep调研结果汇总为HTML报告，覆盖所有字段，跳过不确定值，支持白天/深色模式，直接交付可下载文件。
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Research Report - 汇总报告（HTML）

## 触发方式
`/research-report`

## 执行流程

### Step 1: 定位结果目录
在当前工作目录查找 `*/outline.yaml`，读取 topic 和 output_dir 配置。

### Step 2: 扫描可选摘要字段
读取所有 JSON 结果，提取适合在目录中显示的字段（数值型、简短指标），用 AskUserQuestion 询问：
- 目录中除 item 名称外还想显示哪些字段？（基于实际 JSON 中存在的字段给动态选项）

### Step 3: 生成 HTML 报告（不再是 markdown）
在 `{topic}/` 目录下生成 `generate_report.py`，脚本读取 output_dir 下所有 JSON + fields.yaml，产出**单文件 HTML 报告**。

**输出与命名（硬规则）**：
- 报告一律 **HTML 格式**，输出为**单个自包含 `.html` 文件**（CSS/JS 全部内联，无外部依赖）。
- **文件名用报告标题**：取 outline.yaml 的 `topic`（或用户指定的标题）做 slug（空格→`-`、去特殊字符），如 `谷歌护城河与长坡厚雪.html`。不要用 `report.html` 这种通用名。
- 综合与研判由**主线程 Opus**完成（`research-report` 阶段始终 Opus，见 CLAUDE.md）。

**HTML 硬规则**：
- **白天/深色两种背景模式**：页面内置一个切换按钮（右上角），同时跟随系统 `prefers-color-scheme`；用 CSS 变量定义两套配色（`:root` 亮色 + `[data-theme="dark"]`/媒体查询暗色），`body` 显式设背景色。切换状态可用 `localStorage` 记住（try/catch 包裹）。
- 响应式：手机宽度（~400px）可读，左右留 ≥16px 边距，无横向溢出。
- 结构：标题 + 目录（带锚点跳转 + 用户选择的摘要字段，含每一个 item）+ 各 item 分节（按字段分类展示）。
- 可读性：清晰的排版层级；数字用等宽/tabular-nums；跨 item 的结论/打分若有可做简单图表（内联 SVG，配色随主题）。

**目录格式**：必须包含每一个 item；每个 item 显示序号、名称（锚点链接）、用户选择的摘要字段。

#### 脚本技术要点（必须遵循）
**1. JSON 结构兼容**：支持扁平结构（字段在顶层）与嵌套结构（字段在 category 子 dict）。查找顺序：顶层 → category 映射 key → 遍历嵌套 dict。
**2. Category 多语言映射**：fields.yaml 的 category 名与 JSON key 可能中英混合，建立双向映射（如 `基本信息↔basic_info` 等），并对本次 fields.yaml 的实际分类做兼容。
**3. 复杂值格式化**：list of dicts 每项一行、用 ` | ` 分隔 kv；普通 list 短则逗号连接、长则换行；嵌套 dict 递归；长文本（>100 字符）用换行/段落提升可读性；HTML 输出需转义特殊字符。
**4. 额外字段收集**：JSON 有但 fields.yaml 未定义的字段归入"其他信息"；过滤内部字段 `_source_file`、`uncertain`、嵌套顶级 key。
**5. 不确定值跳过**：字段值含 `[不确定]`、字段名在 `uncertain` 数组、值为 None/空 → 跳过。

### Step 4: 执行并交付
1. 运行 `python {topic}/generate_report.py` 生成 `{标题slug}.html`。
2. **交付方式（硬规则）**：**直接给用户一键可下载的文件**——用 `SendUserFile`（`display="attach"` 下载卡）把该 HTML 交付。**不要用 Artifact / 网页部署功能发布。** 本地 CLI 环境下文件已在 `{topic}/` 目录，告知路径、用户直接打开即可。

## 输出
- `{topic}/generate_report.py` - 转换脚本（可再生物，不入库）
- `{topic}/{标题slug}.html` - 汇总报告（HTML，含白天/深色切换；可再生物，不入库）
