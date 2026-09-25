---
name: research
user-invocable: true
allowed-tools: Read, Write, Glob, WebSearch, Task, AskUserQuestion
description: Conduct preliminary research on a topic and generate research outline. For academic research, benchmark research, technology selection, etc.
---

# Research Skill - Preliminary Research

## Trigger
`/research <topic>`

## Workflow

### Step 1: Generate Initial Framework from Model Knowledge
Based on topic, use model's existing knowledge to generate:
- Main research objects/items list in this domain
- Suggested research field framework

Output {step1_output}, use AskUserQuestion to confirm:
- Need to add/remove items?
- Does field framework meet requirements?

### Step 2: Web Search Supplement
Before the run starts, use AskUserQuestion to settle four things in one pass (exactly the 4-question limit of one AskUserQuestion call):
1. **Time range** (e.g., last 6 months, since 2024, unlimited);
2. **Execution mode** (Performance = all-Opus / Standard = sweet spot, default / Economy = all-Sonnet; meaning defined in Step 4's execution.mode);
3. **Max parallel subagents** (the cap on subagents running at once per batch, written to execution.batch_size, default 3; offer common options like 2/3/5);
4. **Item allocation** (how items are assigned to subagents and how many each takes): name the suggested core items in the question and offer options such as "each core item gets its own agent, the rest 2–3 per agent (recommended for Performance/Standard)" / "one item per agent" / "3–4 items per agent (recommended for Economy)"; if this conflicts with the mode chosen in question 2, the mode wins (in Economy mode core items are grouped too). Written to execution.core_items and execution.items_per_agent.

**Parameter Retrieval**:
- `{topic}`: User input research topic
- `{YYYY-MM-DD}`: Current date
- `{step1_output}`: Complete output from Step 1
- `{time_range}`: User specified time range

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

Launch 1 web-search-agent (background; web/cloud sessions pass the model explicitly, and the agent-type fallback in research-deep Step 3 applies), **Prompt Template**:
```python
prompt = f"""## Task
Research topic: {topic}
Current date: {YYYY-MM-DD}

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
{step1_output}

## Goals
1. Verify if existing items are missing important objects
2. Supplement items based on missing objects
3. Continue searching for {topic} related items within {time_range} and supplement
4. Supplement new fields

## Output Requirements
Return structured results directly (do not write files):

### Supplementary Items
- item_name: Brief explanation (why it should be added)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed)
...

### Sources
- [Source1](url1)
- [Source2](url2)
"""
```

**One-shot Example** (assuming researching AI Coding History):
```
## Task
Research topic: AI Coding History
Current date: 2025-12-30

Based on the following initial framework, supplement latest items and recommended research fields.

## Existing Framework
### Items List
1. GitHub Copilot: Developed by Microsoft/GitHub, first mainstream AI coding assistant
2. Cursor: AI-first IDE, based on VSCode
...

### Field Framework
- Basic Info: name, release_date, company
- Technical Features: underlying_model, context_window
...

## Goals
1. Verify if existing items are missing important objects
2. Supplement items based on missing objects
3. Continue searching for AI Coding History related items within since 2024 and supplement
4. Supplement new fields

## Output Requirements
Return structured results directly (do not write files):

### Supplementary Items
- item_name: Brief explanation (why it should be added)
...

### Recommended Supplementary Fields
- field_name: Field description (why this dimension is needed)
...

### Sources
- [Source1](url1)
- [Source2](url2)
```

### Step 3: Ask User for Existing Fields
Use AskUserQuestion to ask if user has existing field definition file, if so read and merge.

### Step 4: Generate Outline (Separate Files)
Merge {step1_output}, {step2_output} and user's existing fields, generate two files:

**outline.yaml** (items + config):
- topic: Research topic
- request: The starting question — the user's original prompt condensed into one or two sentences (goes into the report's "production info")
- started_at: When the research started, with time zone (e.g. `2026-09-24T12:06+08:00`; used for the production time in the report)
- items: Research objects list
- execution:
  - batch_size: Max parallel subagents, i.e. the cap on subagents running at once per batch (confirm with AskUserQuestion)
  - mode: Execution mode, one of performance/standard/economy (confirm with AskUserQuestion, default standard; legacy numeric values 1/2/3 mean performance/standard/economy)
    - `performance` (all Opus): deep-phase subagents all use Opus; each core item may get its own agent, other items may share one subagent; for high-value, contested-data, or publish-grade research
    - `standard` (sweet spot, default): pick the sweet spot by task difficulty — Sonnet for information-retrieval items, Opus for items that need heavy deep judgment (criteria in research-deep Step 3); allocation as in performance mode; fits most research
    - `economy` (all Sonnet): deep-phase subagents all use Sonnet, each subagent takes several items; cheapest, for exploratory / mostly information-gathering research
    - In all three modes the final report synthesis uses Opus (see research-deep)
  - core_items: Core items, each dispatched to its own subagent (performance/standard modes; confirm with AskUserQuestion; may be empty in economy mode)
  - items_per_agent: How many non-core items each subagent takes (applies to all items in economy mode; confirm with AskUserQuestion)
  - judgment_items: Items that need heavy deep judgment (generated from the criteria in research-deep Step 3; mark them in every mode): dispatched to `web-search-agent-deep` (effort high), and in standard mode also on Opus; all other items go to `web-search-agent` (effort medium)
  - agent_groups: The actual dispatch groups derived from the above; each group = one subagent, formatted `{agent: web-search-agent|web-search-agent-deep, model: opus|sonnet, items: [item name, ...]}`; a group takes the highest agent type and model any of its items needs; put same-topic/same-source items together; order by priority (core groups first)
  - output_dir: Results output directory (default: ./results)

**fields.yaml** (field definitions):
- Field categories and definitions
- Each field's name, description, detail_level
- detail_level hierarchy: brief -> moderate -> detailed
- uncertain: Uncertain fields list (reserved field, auto-filled in deep phase)

### Step 5: Output and Confirm
- Create directory: `./{topic_slug}/`
- Save: `outline.yaml` and `fields.yaml`
- Show to user (including agent_groups: how many subagents, which items each takes, and which model) and confirm with AskUserQuestion options

## Output Path
```
{current_working_directory}/{topic_slug}/
  ├── outline.yaml    # items list + execution config
  └── fields.yaml     # field definitions
```

## Follow-up Commands
- `/research-add-items` - Supplement items
- `/research-add-fields` - Supplement fields
- `/research-deep` - Start deep research
