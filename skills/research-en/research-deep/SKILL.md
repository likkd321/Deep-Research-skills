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

**Model selection (driven by execution.mode, important)**: Read `execution.mode` from outline.yaml (treat missing as `efficiency`) and choose each web-search-agent subagent's model accordingly.

- **`efficiency` (default)**: subagents **default to sonnet** (breadth retrieval + extraction + field-filling suits Sonnet — ~90-95% of Opus quality at ~0.4× the cost and faster).
  Upgrade **only that individual item** to opus (not all of them) when it meets ANY of these **upgrade conditions**:
  1. reliable primary sources are sparse (little authoritative material; must judge from scant evidence);
  2. the item requires **inference or forecasting** from scattered/indirect evidence rather than direct extraction;
  3. the item's own fields call for **judgment/assessment** (e.g. outlook calls, adjudicating disputes) rather than listing facts.
  Default to NOT upgrading — most retrieval items are fine on sonnet; this keeps "auto-select" from degenerating into all-sonnet or all-opus.
- **`performance`**: all subagents use **opus**.
- **Same in both modes**: the final `research-report` cross-item synthesis and judgment **always uses opus** (a single pass, most quality-sensitive; never downgraded).
- **Dispatch**: web/cloud sessions **MUST explicitly pass the model** when dispatching subagents (`model=sonnet` or `model=opus`; such environments do NOT read the `model` field in `agents/web-search-agent.md`); local CLI takes the default from that file's `model` field and overrides upgraded items to opus at dispatch.
- **Agent-type fallback**: the repo's SessionStart hook (`.claude/hooks/session-start.sh`) installs the skills/agent/modules when a web session starts, and the project-level `.claude/agents/web-search-agent.md` registers `web-search-agent` from the first turn, so a fallback is normally unnecessary. If the Agent tool still reports `web-search-agent` not found (e.g. the agent was installed mid-session), dispatch `general-purpose` instead and put one role line at the very **top** of the prompt: `(Role: you are web-search-agent. Before anything else, Read ~/.claude/agents/web-search-agent.md and follow its Research Methodology exactly, including loading the relevant ~/.claude/agents/web-search-modules/ module first.)` — the template body after it stays verbatim.
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
