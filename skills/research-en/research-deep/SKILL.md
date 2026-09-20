---
name: research-deep
user-invocable: true
description: Read research outline, launch independent agent for each item for deep research. Disable task output.
allowed-tools: Bash, Read, Write, Glob, WebSearch, Task
---

# Research Deep - Deep Research

## Trigger
`/research-deep`

## Workflow

### Step 1: Auto-locate Outline
Find `*/outline.yaml` file in current working directory, read items list, execution config (including items_per_agent).

### Step 2: Resume Check
- Check completed JSON files in output_dir
- Skip completed items

### Step 3: Batch Execution
- Batch by batch_size (need user approval before next batch)
- Each agent handles items_per_agent items
- Launch web-search-agent (background parallel, disable task output)

**Model selection (important)**: Dispatch each web-search-agent subagent on the **sonnet** model. Breadth retrieval + fact extraction + field-filling is well-suited to Sonnet (~90-95% of Opus quality at ~1/5 the cost and faster); cross-item synthesis and judgment are handled by the main thread / `research-report` step on Opus, so downgrading subagents costs almost no final quality.
- **Web/cloud sessions**: the executor MUST **explicitly pass model=sonnet** when dispatching subagents (such environments do NOT read the `model` field in `agents/web-search-agent.md`; the model is decided at dispatch time).
- **Local CLI**: controlled automatically by the `model: sonnet` field in `agents/web-search-agent.md`; no extra action needed.
- Do not use Haiku for the deep phase: it is weaker at multi-source cross-checking, source-credibility judgment, and long-context extraction.

**Parameter Retrieval**:
- `{topic}`: topic field from outline.yaml
- `{item_name}`: item's name field
- `{item_related_info}`: item's complete yaml content (name + category + description etc.)
- `{output_dir}`: execution.output_dir from outline.yaml (default: ./results)
- `{fields_path}`: absolute path to {topic}/fields.yaml
- `{output_path}`: absolute path to {output_dir}/{item_name_slug}.json (slugify item_name: replace spaces with _, remove special chars)

**Hard Constraint**: The following prompt must be strictly reproduced, only replacing variables in {xxx}, do not modify structure or wording.

**Prompt Template**:
```python
prompt = f"""## Task
Research {item_related_info}, output structured JSON to {output_path}

## Field Definitions
Read {fields_path} to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
{output_path}

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ~/.claude/skills/research/validate_json.py -f {fields_path} -j {output_path}
Task is complete only after validation passes.
"""
```

**One-shot Example** (assuming researching GitHub Copilot):
```
## Task
Research name: GitHub Copilot
category: International Product
description: Developed by Microsoft/GitHub, first mainstream AI coding assistant, ~40% market share, output structured JSON to {project_dir}/results/GitHub_Copilot.json

## Field Definitions
Read {project_dir}/fields.yaml to get all field definitions

## Output Requirements
1. Output JSON according to fields defined in fields.yaml
2. Mark uncertain field values with [uncertain]
3. Add uncertain array at the end of JSON, listing all uncertain field names
4. All field values must be in English

## Output Path
{project_dir}/results/GitHub_Copilot.json

## Validation
After completing JSON output, run validation script to ensure complete field coverage:
python ~/.claude/skills/research/validate_json.py -f {project_dir}/fields.yaml -j {project_dir}/results/GitHub_Copilot.json
Task is complete only after validation passes.
```

### Step 4: Wait and Monitor
- Wait for current batch to complete
- Launch next batch
- Display progress

### Step 5: Summary Report
After all complete, output:
- Completion count
- Failed/uncertain marked items
- Output directory

### Step 6: Targeted Deepening (reuse existing agents, do not cold-restart)
After summarizing, if an item has thin fields, a key figure backed by a single source, or conflicting numbers across sources:
- **Prefer waking the still-alive subagent for that item** (continue the conversation with full context — use its agent id / SendMessage where the environment supports it) and give a specific deepening instruction, e.g. "the CTR range rests on one source; read each study's methodology, reconcile the conflicting numbers, and note the differing definitions."
- Deepen **only the questionable fields** — do not re-run all items; re-run validate_json.py afterwards.
- Only when that agent can no longer be woken (session/container reclaimed) should you cold-start a new agent for that **single** item via the resume mechanism.
- This saves tokens and is faster and more targeted than a full re-run.

## Agent Config
- Background execution: Yes
- Task Output: Disabled (agent has explicit output file when complete)
- Resume support: Yes
