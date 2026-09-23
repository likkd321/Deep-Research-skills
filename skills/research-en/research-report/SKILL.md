---
name: research-report
user-invocable: true
description: Condense deep research results into a narrative HTML report that shows only the reasoning/judgment process, core data and conclusions (no source lists, no per-item details); supports light/dark mode; delivered as a downloadable file.
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Research Report - Narrative Report (HTML)

## Trigger
`/research-report`

## Purpose (hard rule)
The final report is the **narrative version** the main thread (Opus) writes after **gathering and condensing** all the research — organized and easy to follow, the way you would walk a client through it or tell a child a story, not a dump of everything the research collected.
- **Show only**: the reasoning/judgment process, the core data that supports each step, and the conclusions.
- **Do not show**: sources (source lists, links, per-sentence citations); per-item field details, an item table of contents, or raw field dumps.
- Sources and details stay in `results/*.json` (on the research branch) for reference; the report does not repeat them.

## Workflow

### Step 1: Locate Results
Find `*/outline.yaml` in the current working directory; read topic, questions (the user's original questions, if present) and output_dir.

### Step 2: Read and Distill (main thread, Opus)
Read every JSON under output_dir (flat or nested; skip values containing `[uncertain]`, fields listed in the uncertain array, and empty values) and distill:
- the **key facts and figures** needed to answer each core question — when sources disagree, reconcile the definitions first and keep a single figure in the report;
- a **storyline** that ties all the questions together, starting from the background and building step by step to the conclusions;
- the **chain of reasoning** behind each judgment: because A (data) → therefore B → so C; mark what is an estimate and what is a subjective judgment.

### Step 3: Write the Narrative HTML
Generate `generate_report.py` in `{topic}/` (the narrative text may live in `build_report_content.py` next to it; neither is committed) and produce a **single self-contained HTML file**.

**Narrative structure** (adapt to the topic; no need to follow slavishly):
1. **Conclusion first**: a one-sentence answer + 3–5 core numbers (number cards show only the value, what it means and its time frame — no source).
2. **Chapter navigation**: list the chapter titles (anchor links) so the reader sees the shape of the story at a glance.
3. **One chapter per step, "question → reasoning → data → conclusion"**: open each chapter with a question, give the answer first and then the reasons; include only the data that supports that step; link chapters together ("which raises the next question…"). Prefer the user's original questions (outline `questions`) as the chapter spine.
4. **Analogies and charts**: explain complex mechanisms with apt analogies; chart only the key data behind the reasoning (follow the dataviz guidance, theme-aware colors), each chart with an expandable data table.
5. **Wrap-up**: a one-page summary (a few points) + the signals/metrics to watch next.
6. **Reading notes** (optional, short): which figures are estimates and which definitions are not fully comparable; no sources.

**Writing**: plain and orderly, one idea per paragraph; conclusion before reasons; few, well-chosen numbers — only the one that makes the point; keep facts and judgments apart (phrase judgments as "I judge", "likely"); no jargon piles, no long lists.

**Output & naming (hard rules)**:
- The report is always **HTML**, emitted as **one self-contained `.html` file** (all CSS/JS inlined, no external dependencies).
- **Name the file after the report title**: slugify outline.yaml's `topic` (or a user-specified title) (spaces→`-`, drop special chars), e.g. `google-moat-and-long-runway.html`. Do NOT use a generic name like `report.html`.
- Synthesis/judgment is done by the **main thread on Opus** (`research-report` always runs on Opus; see CLAUDE.md).

**HTML hard rules**:
- **Light & dark background modes**: an in-page toggle button (top-right) plus following the system `prefers-color-scheme`; define both palettes with CSS variables (`:root` light + `[data-theme="dark"]`/media query dark), and set an explicit `background` on `body`. Persist the choice in `localStorage` (wrapped in try/catch).
- Responsive: readable at phone width (~400px), ≥16px side gutter, no horizontal page scroll (wide tables and charts scroll inside their own containers).
- Readability: clear typographic hierarchy; tabular-nums for table and axis figures; inline-SVG charts.

### Step 4: Build and Deliver
1. Run `python {topic}/generate_report.py` to produce `{title-slug}.html`; screenshot and check the layout in light mode, dark mode and at phone width.
2. **Delivery (hard rule)**: **hand the user a one-click downloadable file** — deliver the HTML via `SendUserFile` (`display="attach"` download card). **Do NOT use the Artifact / web-deploy feature to publish it.** In a local CLI the file already sits in `{topic}/`; state the path and let the user open it directly.

## Output
- `{topic}/generate_report.py` (and optionally `build_report_content.py`) - rendering script and narrative text (regenerable, not committed)
- `{topic}/{title-slug}.html` - narrative report (HTML with light/dark toggle; regenerable, not committed)
