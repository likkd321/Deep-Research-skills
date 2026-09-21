---
name: research-report
user-invocable: true
description: Summarize deep research results into an HTML report, cover all fields, skip uncertain values, support light/dark mode, deliver as a downloadable file.
allowed-tools: Read, Write, Glob, Bash, AskUserQuestion
---

# Research Report - Summary Report (HTML)

## Trigger
`/research-report`

## Workflow

### Step 1: Locate Results Directory
Find `*/outline.yaml` in current working directory, read topic and output_dir config.

### Step 2: Scan Optional Summary Fields
Read all JSON results, extract fields suitable for TOC display (numeric, short metrics). Use AskUserQuestion:
- Which fields to display in the TOC besides item name? (dynamic options from fields actually present in the JSON)

### Step 3: Generate HTML Report (no longer markdown)
Generate `generate_report.py` in `{topic}/`; it reads all JSON under output_dir + fields.yaml and produces a **single self-contained HTML report**.

**Output & naming (hard rules)**:
- The report is always **HTML**, emitted as **one self-contained `.html` file** (all CSS/JS inlined, no external dependencies).
- **Name the file after the report title**: slugify outline.yaml's `topic` (or a user-specified title) (spaces→`-`, drop special chars), e.g. `google-moat-and-long-runway.html`. Do NOT use a generic name like `report.html`.
- Synthesis/judgment is done by the **main thread on Opus** (`research-report` always runs on Opus; see CLAUDE.md).

**HTML hard rules**:
- **Light & dark background modes**: an in-page toggle button (top-right) plus following the system `prefers-color-scheme`; define both palettes with CSS variables (`:root` light + `[data-theme="dark"]`/media query dark), and set an explicit `background` on `body`. Persist the choice in `localStorage` (wrapped in try/catch).
- Responsive: readable at phone width (~400px), ≥16px side gutter, no horizontal overflow.
- Structure: title + table of contents (anchor links + user-selected summary fields, includes every item) + one section per item (organized by field category).
- Readability: clear typographic hierarchy; tabular-nums for figures; simple inline-SVG charts (theme-aware colors) for cross-item conclusions/scores where useful.

**TOC format**: must include every item; each shows number, name (anchor link), user-selected summary fields.

#### Script Technical Requirements (must follow)
**1. JSON structure compatibility**: support flat (fields at top level) and nested (fields in a category sub-dict). Lookup order: top level → category-mapping key → traverse nested dicts.
**2. Category multi-language mapping**: fields.yaml category names and JSON keys may mix CN/EN — build a bidirectional mapping and adapt to this run's actual categories.
**3. Complex value formatting**: list of dicts → one line each with ` | ` between kv; plain list → comma-join if short, line breaks if long; nested dict → recurse; long text (>100 chars) → break into lines/paragraphs; escape HTML special chars on output.
**4. Extra fields**: fields present in JSON but not in fields.yaml go under "Other"; filter internal keys `_source_file`, `uncertain`, and nested top-level keys.
**5. Uncertain skipping**: skip when the value contains `[uncertain]`, the field name is in the `uncertain` array, or the value is None/empty.

### Step 4: Build and Deliver
1. Run `python {topic}/generate_report.py` to produce `{title-slug}.html`.
2. **Delivery (hard rule)**: **hand the user a one-click downloadable file** — deliver the HTML via `SendUserFile` (`display="attach"` download card). **Do NOT use the Artifact / web-deploy feature to publish it.** In a local CLI the file already sits in `{topic}/`; state the path and let the user open it directly.

## Output
- `{topic}/generate_report.py` - conversion script (regenerable, not committed)
- `{topic}/{title-slug}.html` - summary report (HTML with light/dark toggle; regenerable, not committed)
