#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate markdown report from deep-research JSON results.

Reads outline.yaml (item order + topic), fields.yaml (field order + labels),
and every JSON under results/, then emits report.md with a table of contents
(item name + category) plus per-item sections organized by field category.
Skips [不确定] values and fields listed in each JSON's `uncertain` array.
"""
import json
import re
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent
FIELDS_PATH = BASE / "fields.yaml"
OUTLINE_PATH = BASE / "outline.yaml"
RESULTS_DIR = BASE / "results"
REPORT_PATH = BASE / "report.md"

SKIP_KEYS = {"name", "uncertain", "_source_file"}


def load_yaml(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def field_order(fields_yaml):
    """Return list of (category, field_name, description) in fields.yaml order."""
    order = []
    for category, defs in fields_yaml.get("fields", {}).items():
        for d in defs:
            order.append((category, d["name"], d.get("description", "")))
    return order


def anchor(idx, name):
    return f"item-{idx}"


def is_skippable(value):
    if value is None:
        return True
    if isinstance(value, str):
        v = value.strip()
        return v == "" or "[不确定]" in v
    return False


def fmt_value(value):
    if isinstance(value, list):
        # sources or plain lists -> bullet lines
        lines = []
        for it in value:
            if isinstance(it, dict):
                lines.append("- " + " | ".join(f"{k}: {v}" for k, v in it.items()))
            else:
                lines.append(f"- {it}")
        return "\n".join(lines)
    if isinstance(value, dict):
        return "\n".join(f"- **{k}**: {v}" for k, v in value.items())
    text = str(value).strip()
    return text


def main():
    outline = load_yaml(OUTLINE_PATH)
    fields_yaml = load_yaml(FIELDS_PATH)
    topic = outline.get("topic", "调研报告")
    gen_date = outline.get("generated_date", "")
    time_range = outline.get("time_range", "")

    items = outline.get("items", [])
    order = field_order(fields_yaml)
    # label per field name = category
    field_label = {name: cat for cat, name, _ in order}
    field_seq = [name for _, name, _ in order]

    # load results keyed by item name
    results = {}
    for jf in RESULTS_DIR.glob("*.json"):
        with open(jf, encoding="utf-8") as f:
            data = json.load(f)
        results[data.get("name", jf.stem)] = data

    out = []
    out.append(f"# {topic}\n")
    meta = []
    if gen_date:
        meta.append(f"生成日期：{gen_date}")
    if time_range:
        meta.append(f"时间范围：{time_range}")
    if meta:
        out.append(" · ".join(meta) + "\n")
    out.append("> 本报告由仓库 `research-zh` 深度调研 skill 生成："
               "8 个调研 item × 7 个分析维度，每项由独立联网 agent 检索并交叉验证后汇总。\n")

    # ---- TOC ----
    out.append("## 目录\n")
    for i, item in enumerate(items, 1):
        name = item["name"]
        cat = item.get("category", "")
        out.append(f"{i}. [{name}](#{anchor(i, name)})" + (f" — {cat}" if cat else ""))
    out.append("")

    # ---- Sections ----
    for i, item in enumerate(items, 1):
        name = item["name"]
        cat = item.get("category", "")
        data = results.get(name)
        out.append(f'\n<a id="{anchor(i, name)}"></a>')
        out.append(f"## {i}. {name}")
        if cat:
            out.append(f"*分类：{cat}*\n")
        if not data:
            out.append("_（无结果）_\n")
            continue
        uncertain = set(data.get("uncertain", []) or [])
        for fname in field_seq:
            if fname in uncertain:
                continue
            if fname not in data:
                continue
            value = data[fname]
            if is_skippable(value):
                continue
            label = field_label.get(fname, fname)
            out.append(f"### {label}")
            out.append(fmt_value(value) + "\n")
        # extra fields not in fields.yaml
        extras = [k for k in data.keys()
                  if k not in SKIP_KEYS and k not in field_seq]
        if extras:
            out.append("### 其他信息")
            for k in extras:
                if is_skippable(data[k]):
                    continue
                out.append(f"**{k}**: {fmt_value(data[k])}\n")

    REPORT_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"报告已生成: {REPORT_PATH}  ({len(items)} items)")


if __name__ == "__main__":
    main()
