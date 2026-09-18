#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 results/*.json 汇总为深色 HTML 报告（同时输出 markdown 中间产物）。

用法: python generate_report.py
读取: outline.yaml, fields.yaml, results/*.json, synthesis.json(可选)
输出: report.html, report.md
"""
import html
import json
import re
from pathlib import Path

import yaml

BASE = Path(__file__).resolve().parent
OUTLINE = yaml.safe_load((BASE / "outline.yaml").read_text(encoding="utf-8"))
FIELDS = yaml.safe_load((BASE / "fields.yaml").read_text(encoding="utf-8"))
RESULTS_DIR = BASE / "results"
SYNTH_PATH = BASE / "synthesis.json"

# 深色面板 + dataviz 参考调色板的 dark 步进（前三槽通过 all-pairs CVD 校验）
SERIES = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181"]


def slug(text):
    return re.sub(r"[^\w一-鿿]+", "-", str(text)).strip("-").lower()


def is_uncertain(value, name, uncertain_list):
    if name in uncertain_list:
        return True
    if value is None:
        return True
    if isinstance(value, str):
        s = value.strip()
        return not s or "[不确定]" in s
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def load_items():
    """按 outline 的 items 顺序返回 (item_meta, json_data)。"""
    by_name = {}
    for p in sorted(RESULTS_DIR.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        data["_source_file"] = p.name
        by_name[p.stem] = data
    out = []
    for meta in OUTLINE["items"]:
        key = slug_file(meta["name"])
        data = by_name.get(key)
        if data is None:  # 名称对不上时按 name 字段兜底匹配
            for d in by_name.values():
                if str(d.get("name", "")).startswith(meta["name"][:3]):
                    data = d
                    break
        if data is not None:
            out.append((meta, data))
    return out


def slug_file(name):
    return re.sub(r"[^\w一-鿿]+", "_", str(name)).strip("_")


def fmt_value(value, depth=0):
    """把任意 JSON 值格式化为 HTML 片段。"""
    if isinstance(value, str):
        return html.escape(value).replace("\n", "<br>")
    if isinstance(value, (int, float)):
        return html.escape(str(value))
    if isinstance(value, list):
        if not value:
            return ""
        if all(isinstance(v, (str, int, float)) for v in value):
            if len(value) <= 3 and sum(len(str(v)) for v in value) < 120:
                return html.escape(" ; ".join(str(v) for v in value))
            return "<ul class='v-list'>" + "".join(
                f"<li>{html.escape(str(v))}</li>" for v in value) + "</ul>"
        parts = []
        for v in value:
            if isinstance(v, dict):
                inner = " <span class='sep'>|</span> ".join(
                    f"<span class='k'>{html.escape(str(k))}</span> {fmt_value(vv, depth+1)}"
                    for k, vv in v.items())
                parts.append(f"<li>{inner}</li>")
            else:
                parts.append(f"<li>{fmt_value(v, depth+1)}</li>")
        return "<ul class='v-list'>" + "".join(parts) + "</ul>"
    if isinstance(value, dict):
        rows = "".join(
            f"<div class='kv'><span class='k'>{html.escape(str(k))}</span>"
            f"<span class='v'>{fmt_value(v, depth+1)}</span></div>"
            for k, v in value.items())
        return f"<div class='kv-block'>{rows}</div>"
    return html.escape(str(value))


def fmt_value_md(value):
    if isinstance(value, str):
        return value.replace("\n", " ")
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if all(isinstance(v, (str, int, float)) for v in value):
            return " ; ".join(str(v) for v in value)
        return " ; ".join(
            ", ".join(f"{k}: {vv}" for k, vv in v.items()) if isinstance(v, dict) else str(v)
            for v in value)
    if isinstance(value, dict):
        return " ; ".join(f"{k}: {fmt_value_md(v)}" for k, v in value.items())
    return str(value)


def score_num(raw):
    """从 '8.5/10 — 理由' 里抽出数值。"""
    if raw is None:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", str(raw))
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)", str(raw))
    return float(m.group(1)) if m else None


# ---------------------------------------------------------------- 图表组件
def bar_group(title, subtitle, rows, maxv, unit="", note=""):
    """rows: [(label, [(series_name, value, color), ...])]"""
    out = [f"<figure class='fig'><figcaption><h4>{html.escape(title)}</h4>"]
    if subtitle:
        out.append(f"<p class='sub'>{html.escape(subtitle)}</p>")
    out.append("</figcaption><div class='bars'>")
    for label, series in rows:
        out.append(f"<div class='bar-row'><div class='bar-label'>{html.escape(label)}</div>"
                   "<div class='bar-track'>")
        for sname, val, color in series:
            if val is None:
                continue
            pct = max(0.0, min(100.0, val / maxv * 100))
            out.append(
                f"<div class='bar' style='--w:{pct:.1f}%;--c:{color}' "
                f"title='{html.escape(sname)}: {val}{unit}'>"
                f"<span class='bar-fill'></span>"
                f"<span class='bar-val'>{val}{unit}</span></div>")
        out.append("</div></div>")
    out.append("</div>")
    if note:
        out.append(f"<p class='note'>{html.escape(note)}</p>")
    out.append("</figure>")
    return "".join(out)


def legend(names):
    chips = "".join(
        f"<span class='chip'><i style='background:{SERIES[i % len(SERIES)]}'></i>{html.escape(n)}</span>"
        for i, n in enumerate(names))
    return f"<div class='legend'>{chips}</div>"


def prob_chart(entries):
    """entries: [(name, low, mid, high)] — 胜率区间点图。"""
    out = ["<figure class='fig'><figcaption><h4>办公 AI Agent 赛道终局胜率</h4>"
           "<p class='sub'>圆点为中性情景，横杠为悲观→乐观区间</p></figcaption>"
           "<div class='probs'>"]
    for i, (name, low, mid, high) in enumerate(entries):
        c = SERIES[i % len(SERIES)]
        out.append(
            f"<div class='prob-row'><div class='bar-label'>{html.escape(name)}</div>"
            f"<div class='prob-track'>"
            f"<span class='prob-range' style='left:{low}%;width:{max(high-low,0.5)}%;--c:{c}'></span>"
            f"<span class='prob-dot' style='left:{mid}%;--c:{c}' title='中性情景 {mid}%'></span>"
            f"</div><div class='prob-val'>{mid}%<small>{low}–{high}%</small></div></div>")
    out.append("<div class='prob-axis'>"
               + "".join(f"<span style='left:{v}%'>{v}%</span>" for v in (0, 20, 40, 60, 80, 100))
               + "</div></div></figure>")
    return "".join(out)


# ---------------------------------------------------------------- 渲染
def render():
    items = load_items()
    synth = json.loads(SYNTH_PATH.read_text(encoding="utf-8")) if SYNTH_PATH.exists() else {}
    topic = OUTLINE["topic"]
    date = OUTLINE.get("date", "")
    categories = FIELDS["fields"]
    field_desc = {f["name"]: f.get("description", "")
                  for flist in categories.values() for f in flist}

    H = []
    H.append(HEAD.replace("{{TITLE}}", html.escape(topic)))
    H.append(f"<header class='hero'><p class='eyebrow'>Deep Research · {html.escape(date)}"
             f" · 时间窗口 {html.escape(OUTLINE.get('time_range',''))}</p>"
             f"<h1>{html.escape(topic)}</h1>")
    if synth.get("headline"):
        H.append(f"<p class='lede'>{html.escape(synth['headline'])}</p>")
    H.append("</header><main>")

    # 执行摘要
    if synth.get("summary_blocks"):
        H.append("<section id='summary'><h2>执行摘要</h2>")
        for b in synth["summary_blocks"]:
            H.append(f"<div class='callout'><h3>{html.escape(b['title'])}</h3>"
                     f"<div>{b['body']}</div></div>")
        H.append("</section>")

    # 关键指标卡
    if synth.get("stat_tiles"):
        H.append("<section id='stats'><h2>三家基本盘</h2><div class='tiles'>")
        for i, t in enumerate(synth["stat_tiles"]):
            c = SERIES[i % len(SERIES)]
            metrics = "".join(
                f"<div class='tile-metric'><span class='m-label'>{html.escape(m['label'])}</span>"
                f"<span class='m-value'>{html.escape(str(m['value']))}</span></div>"
                for m in t.get("metrics", []))
            H.append(f"<div class='tile' style='--c:{c}'><h3>{html.escape(t['name'])}</h3>"
                     f"<p class='tile-sub'>{html.escape(t.get('subtitle',''))}</p>{metrics}</div>")
        H.append("</div></section>")

    # 评分图
    if synth.get("scorecard"):
        sc = synth["scorecard"]
        names = sc["players"]
        rows = [(d["dimension"],
                 [(names[i], d["scores"][i], SERIES[i % len(SERIES)]) for i in range(len(names))])
                for d in sc["dimensions"]]
        H.append("<section id='scorecard'><h2>全维度打分</h2>")
        H.append(legend(names))
        H.append(bar_group("各维度评分（1–10）", sc.get("subtitle", ""), rows, 10.0,
                           note=sc.get("note", "")))
        H.append(score_table(names, sc["dimensions"]))
        H.append("</section>")

    # 胜率
    if synth.get("win_probability"):
        wp = synth["win_probability"]
        H.append("<section id='endgame'><h2>终局胜率预测</h2>")
        if wp.get("intro"):
            H.append(f"<div class='callout'><div>{wp['intro']}</div></div>")
        H.append(prob_chart([(e["name"], e["low"], e["mid"], e["high"]) for e in wp["entries"]]))
        for e in wp["entries"]:
            H.append(f"<div class='reason'><h4>{html.escape(e['name'])} · {e['mid']}%</h4>"
                     f"<div>{e['rationale']}</div></div>")
        H.append("</section>")

    # 能力维度框架
    if synth.get("capability_framework"):
        cf = synth["capability_framework"]
        H.append("<section id='capability'><h2>做办公 AI Agent 需要的能力维度</h2>")
        if cf.get("intro"):
            H.append(f"<div class='callout'><div>{cf['intro']}</div></div>")
        for tier in cf["tiers"]:
            H.append(f"<h3 class='tier tier-{tier['level']}'>{html.escape(tier['title'])}</h3>"
                     "<div class='cap-grid'>")
            for c in tier["items"]:
                H.append(f"<div class='cap'><h4>{html.escape(c['name'])}</h4>"
                         f"<p>{html.escape(c['what'])}</p>"
                         f"<p class='cap-why'>{html.escape(c.get('why',''))}</p></div>")
            H.append("</div>")
        H.append("</section>")

    # 目录
    H.append("<section id='toc'><h2>调研对象明细</h2><ol class='toc'>")
    for meta, data in items:
        sid = slug(meta["name"])
        summ = " · ".join(
            f"{k}: {html.escape(str(v))}" for k, v in (synth.get("toc_summary", {})
                                                       .get(meta["name"], {}) or {}).items())
        H.append(f"<li><a href='#{sid}'>{html.escape(meta['name'])}</a>"
                 f"<span class='toc-tag'>{html.escape(meta['category'])}</span>"
                 + (f"<span class='toc-sum'>{summ}</span>" if summ else "") + "</li>")
    H.append("</ol></section>")

    # 每个 item 的详情
    for meta, data in items:
        sid = slug(meta["name"])
        uncertain_list = data.get("uncertain", []) or []
        H.append(f"<section class='item' id='{sid}'><h2>{html.escape(meta['name'])}"
                 f"<span class='toc-tag'>{html.escape(meta['category'])}</span></h2>")
        for cat, flist in categories.items():
            body = []
            for f in flist:
                nm = f["name"]
                val = data.get(nm)
                if is_uncertain(val, nm, uncertain_list):
                    continue
                body.append(
                    f"<div class='field'><div class='f-name' title='{html.escape(field_desc.get(nm,''))}'>"
                    f"{html.escape(nm)}</div><div class='f-val'>{fmt_value(val)}</div></div>")
            if body:
                H.append(f"<details open class='cat'><summary>{html.escape(cat)}</summary>"
                         + "".join(body) + "</details>")
        extra = [k for k in data
                 if k not in field_desc and k not in ("uncertain", "_source_file", "sources")]
        if extra:
            H.append("<details class='cat'><summary>其他信息</summary>" + "".join(
                f"<div class='field'><div class='f-name'>{html.escape(k)}</div>"
                f"<div class='f-val'>{fmt_value(data[k])}</div></div>"
                for k in extra if not is_uncertain(data[k], k, uncertain_list)) + "</details>")
        if data.get("sources"):
            H.append("<details class='cat'><summary>信息来源</summary>"
                     f"<div class='field'><div class='f-val'>{fmt_value(data['sources'])}</div></div>"
                     "</details>")
        if uncertain_list:
            H.append("<p class='unc'>未能核实/已跳过的字段：" +
                     html.escape("、".join(uncertain_list)) + "</p>")
        H.append("</section>")

    if synth.get("method"):
        H.append(f"<section id='method'><h2>方法论与局限</h2><div class='callout'>"
                 f"<div>{synth['method']}</div></div></section>")

    H.append("</main><footer><p>由 deep-research-skills 工作流生成 · "
             f"{html.escape(date)} · 分数为绝对锚点分并经主线程横向校准</p></footer>")
    H.append(TAIL)
    (BASE / "report.html").write_text("".join(H), encoding="utf-8")

    # markdown 中间产物
    M = [f"# {topic}", "", f"> Deep Research · {date} · 时间窗口 {OUTLINE.get('time_range','')}", ""]
    if synth.get("headline"):
        M += [synth["headline"], ""]
    M += ["## 目录", ""]
    for i, (meta, data) in enumerate(items, 1):
        M.append(f"{i}. [{meta['name']}](#{slug(meta['name'])}) — {meta['category']}")
    M.append("")
    for meta, data in items:
        uncertain_list = data.get("uncertain", []) or []
        M += [f"## {meta['name']}", ""]
        for cat, flist in categories.items():
            lines = []
            for f in flist:
                nm = f["name"]
                val = data.get(nm)
                if is_uncertain(val, nm, uncertain_list):
                    continue
                lines.append(f"- **{nm}**: {fmt_value_md(val)}")
            if lines:
                M += [f"### {cat}", ""] + lines + [""]
    (BASE / "report.md").write_text("\n".join(M), encoding="utf-8")
    print(f"[ok] report.html / report.md 已生成，items={len(items)}")


def score_table(names, dims):
    head = "".join(f"<th>{html.escape(n)}</th>" for n in names)
    rows = []
    for d in dims:
        cells = "".join(
            f"<td><b>{s}</b></td>" if s == max(x for x in d['scores'] if x is not None)
            else f"<td>{s}</td>" for s in d["scores"])
        rows.append(f"<tr><th class='row-h'>{html.escape(d['dimension'])}"
                    f"<small>权重 {d.get('weight','-')}</small></th>{cells}</tr>")
    return (f"<table class='score-table'><thead><tr><th>维度</th>{head}</tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table>")


HEAD = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{TITLE}}</title>
<style>
:root{color-scheme:dark;
 --bg:#141413;--surface:#1a1a19;--surface-2:#232321;--line:#33332f;
 --text:#ffffff;--text-2:#c3c2b7;--muted:#8a897f;
 --s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;
 --radius:12px;--maxw:1080px}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
 font:16px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif;
 -webkit-font-smoothing:antialiased}
main,header.hero,footer{max-width:var(--maxw);margin:0 auto;padding:0 16px}
.hero{padding-top:56px;padding-bottom:24px;border-bottom:1px solid var(--line);margin-bottom:8px}
.eyebrow{color:var(--muted);font-size:13px;letter-spacing:.04em;margin:0 0 10px;text-transform:uppercase}
h1{font-size:clamp(26px,4.4vw,40px);line-height:1.25;margin:0 0 14px;letter-spacing:-.01em}
.lede{color:var(--text-2);font-size:17px;margin:0;max-width:74ch}
h2{font-size:22px;margin:44px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--line);
 display:flex;align-items:center;gap:10px;flex-wrap:wrap}
h3{font-size:17px;margin:22px 0 10px}
h4{font-size:15px;margin:0 0 6px}
p{margin:0 0 10px}
a{color:var(--s1);text-decoration:none}a:hover{text-decoration:underline}
.callout{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--s1);
 border-radius:var(--radius);padding:16px 18px;margin:0 0 14px}
.callout h3{margin-top:0}
.callout ul{margin:6px 0 0;padding-left:20px}.callout li{margin:4px 0}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
.tile{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--c);
 border-radius:var(--radius);padding:16px}
.tile h3{margin:0 0 2px;font-size:18px}
.tile-sub{color:var(--muted);font-size:13px;margin:0 0 12px}
.tile-metric{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-top:1px solid var(--line)}
.m-label{color:var(--text-2);font-size:13px}
.m-value{font-weight:640;font-variant-numeric:tabular-nums;text-align:right}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin:0 0 14px}
.chip{display:flex;align-items:center;gap:7px;color:var(--text-2);font-size:14px}
.chip i{width:11px;height:11px;border-radius:3px;display:inline-block}
.fig{margin:0 0 18px;background:var(--surface);border:1px solid var(--line);
 border-radius:var(--radius);padding:18px}
figcaption h4{margin:0 0 4px;font-size:16px}
figcaption .sub{color:var(--muted);font-size:13px;margin:0 0 14px}
.bar-row{display:grid;grid-template-columns:minmax(96px,168px) 1fr;gap:14px;align-items:center;
 padding:9px 0;border-top:1px solid var(--line)}
.bar-row:first-child{border-top:0}
.bar-label{color:var(--text-2);font-size:13px;line-height:1.35}
.bar-track{display:flex;flex-direction:column;gap:2px}
.bar{display:flex;align-items:center;gap:8px;height:16px}
.bar-fill{height:14px;width:var(--w);background:var(--c);border-radius:0 4px 4px 0;
 min-width:2px;transition:filter .15s}
.bar:hover .bar-fill{filter:brightness(1.22)}
.bar-val{font-size:12px;color:var(--text-2);font-variant-numeric:tabular-nums}
.note{color:var(--muted);font-size:12.5px;margin:12px 0 0}
.score-table{width:100%;border-collapse:collapse;margin-top:16px;font-size:14px}
.score-table th,.score-table td{border:1px solid var(--line);padding:9px 11px;text-align:center}
.score-table thead th{background:var(--surface-2);font-size:13px}
.score-table .row-h{text-align:left;color:var(--text-2);font-weight:520}
.score-table .row-h small{display:block;color:var(--muted);font-weight:400;font-size:11.5px}
.score-table td{font-variant-numeric:tabular-nums;color:var(--text-2)}
.score-table td b{color:var(--text)}
.probs{margin-top:8px;position:relative}
.prob-row{display:grid;grid-template-columns:minmax(96px,168px) 1fr 86px;gap:14px;align-items:center;
 padding:13px 0;border-top:1px solid var(--line)}
.prob-row:first-child{border-top:0}
.prob-track{position:relative;height:16px}
.prob-track:before{content:"";position:absolute;left:0;right:0;top:7px;height:2px;background:var(--surface-2)}
.prob-range{position:absolute;top:6px;height:4px;background:var(--c);opacity:.42;border-radius:4px}
.prob-dot{position:absolute;top:2px;width:12px;height:12px;margin-left:-6px;border-radius:50%;
 background:var(--c);box-shadow:0 0 0 2px var(--surface)}
.prob-val{text-align:right;font-variant-numeric:tabular-nums;font-weight:640}
.prob-val small{display:block;color:var(--muted);font-weight:400;font-size:11.5px}
.prob-axis{position:relative;height:18px;margin-left:calc(min(168px,26%) + 14px);margin-right:100px}
.prob-axis span{position:absolute;transform:translateX(-50%);color:var(--muted);font-size:11px}
.reason{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
 padding:14px 16px;margin:0 0 10px}
.reason h4{color:var(--text)}
.reason ul{margin:6px 0 0;padding-left:20px}
.tier{display:inline-block;padding:5px 12px;border-radius:999px;font-size:14px;margin:22px 0 12px}
.tier-1{background:rgba(57,135,229,.16);color:#8fbdf3;border:1px solid rgba(57,135,229,.4)}
.tier-2{background:rgba(25,158,112,.16);color:#6fd0ad;border:1px solid rgba(25,158,112,.4)}
.tier-3{background:rgba(217,89,38,.14);color:#e79b79;border:1px solid rgba(217,89,38,.38)}
.cap-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.cap{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:14px}
.cap h4{color:var(--text)}
.cap p{color:var(--text-2);font-size:14px;margin:0 0 6px}
.cap-why{color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:8px;margin:8px 0 0}
ol.toc{list-style:none;counter-reset:t;padding:0;margin:0}
ol.toc li{counter-increment:t;padding:11px 0;border-top:1px solid var(--line);
 display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
ol.toc li:before{content:counter(t);color:var(--muted);font-variant-numeric:tabular-nums;min-width:18px}
.toc-tag{font-size:11.5px;color:var(--muted);border:1px solid var(--line);
 border-radius:999px;padding:2px 9px}
.toc-sum{color:var(--text-2);font-size:13px}
.item h2{scroll-margin-top:20px}
details.cat{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);
 margin:0 0 10px;overflow:hidden}
details.cat>summary{padding:12px 16px;cursor:pointer;font-weight:620;font-size:15px;
 background:var(--surface-2);list-style:none;display:flex;align-items:center;gap:8px}
details.cat>summary:before{content:"▸";color:var(--muted);transition:transform .15s}
details.cat[open]>summary:before{transform:rotate(90deg)}
details.cat>summary::-webkit-details-marker{display:none}
.field{display:grid;grid-template-columns:minmax(150px,210px) 1fr;gap:16px;padding:13px 16px;
 border-top:1px solid var(--line)}
.f-name{color:var(--s1);font-size:13px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
 word-break:break-word;line-height:1.5}
.f-val{color:var(--text-2);font-size:14.5px;min-width:0;overflow-wrap:anywhere}
.f-val .v-list{margin:0;padding-left:18px}
.f-val .v-list li{margin:3px 0}
.kv-block{display:flex;flex-direction:column;gap:5px}
.kv{display:flex;gap:9px;align-items:baseline}
.kv .k,.f-val .k{color:var(--muted);font-size:12.5px;white-space:nowrap}
.sep{color:var(--line)}
.unc{color:var(--muted);font-size:12.5px;margin:8px 0 0}
footer{border-top:1px solid var(--line);margin-top:56px;padding-top:18px;padding-bottom:48px;
 color:var(--muted);font-size:13px}
@media(max-width:680px){
 .field,.bar-row,.prob-row{grid-template-columns:1fr;gap:6px}
 .prob-row{gap:8px}.prob-val{text-align:left}
 .prob-axis{margin-left:0;margin-right:0}
 .hero{padding-top:36px}
}
</style></head><body>"""

TAIL = "</body></html>"

if __name__ == "__main__":
    render()
