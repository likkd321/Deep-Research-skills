# -*- coding: utf-8 -*-
"""生成讲述式 HTML 报告（可再生物，不入库）。用法：python generate_report.py [结束时间ISO]"""
import html, sys, re, json, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from build_report_content import *  # noqa
from build_overview import render as ov_render
from build_cell_detail import impl_rows, leave_flow, modules, weeks_total, code_pitfalls, tests, maintenance, risks, cases
for _c in CELLS:
    _c["weeks"] = weeks_total(_c) + {19: "（房主型；回滚路线约 10–16 周）", 24: "（仅供参考，不建议做）"}.get(_c["id"], "")

E = html.escape
HERE = Path(__file__).parent

START = dt.datetime(2026, 11, 23, 16, 20, tzinfo=dt.timezone.utc)
END = dt.datetime.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime.now(dt.timezone.utc)
mins = int((END - START).total_seconds() // 60)
CST = dt.timezone(dt.timedelta(hours=8))
fmt = lambda t: t.strftime("%Y-%m-%d %H:%M")

def badge(level):
    ic, lab, st = LEVEL[level]
    return f'<span class="badge st-{st}"><span class="bi" aria-hidden="true">{ic}</span>{lab}</span>'

def _first_num(s):
    """取第一个数或第一个区间的中点，如“4–7 周”→5.5。"""
    m = re.search(r"(\d+(?:\.\d+)?)(?:\s*[–-]\s*(\d+(?:\.\d+)?))?", s)
    if not m: return None
    a = float(m.group(1)); b = float(m.group(2)) if m.group(2) else a
    return (a + b) / 2

def metric(label, value_html, tone, word):
    """评分卡：色条 + 着色数值 + 文字档位（颜色不单独承载含义）。"""
    return (f'<div class="m t-{tone}"><span class="ml">{E(label)}</span>{value_html}'
            f'<em class="mw">{E(word)}</em></div>')

def tone_low_good(v):   # 难度：越低越好
    return ("good", "容易") if v <= 2.5 else ("warn", "适中") if v <= 3.5 else ("bad", "偏难")

def tone_high_good(v, words=("高", "中", "低")):  # 把握/稳定：越高越好
    return ("good", words[0]) if v >= 3.5 else ("warn", words[1]) if v >= 2.5 else ("bad", words[2])

def tone_weeks(s):
    v = _first_num(s)
    if v is None: return ("bad", "难以估计")
    return ("good", "短") if v <= 4.5 else ("warn", "中等") if v <= 8 else ("bad", "长")

def tone_win(s):
    v = 5 if s.strip().startswith("<") else _first_num(s)
    return ("good", "较高") if v >= 60 else ("warn", "中等") if v >= 35 else ("bad", "偏低")

def metrics(c):
    d = tone_low_good(c["diff"]); cl = tone_high_good(c["claude"]); st = tone_high_good(c["stab"], ("稳", "一般", "不稳"))
    wk = tone_weeks(c["weeks"]); wn = tone_win(c["win"])
    return ('<div class="kv">'
            + metric("实现难度", dots(c["diff"]), *d)
            + metric("Claude 把握", dots(c["claude"]), *cl)
            + metric("网络稳定", dots(c["stab"]), *st)
            + metric("网络部分工期", f'<b class="mv">{E(c["weeks"])}</b>', *wk)
            + metric("终局胜率（主观）", f'<b class="mv">{E(c["win"])}</b>', *wn)
            + '</div><p class="kvleg muted"><i class="k t-good"></i>好 <i class="k t-warn"></i>一般 <i class="k t-bad"></i>差（难度、工期越低越好；其余越高越好）</p>')

def dots(v):
    return f'<span class="score" title="{v}/5">{v:g}<small>/5</small></span>'

# ---------------- 图 1：Claude 把握度 ----------------
def chart_claude():
    W, rowh, left, right, top = 640, 34, 250, 40, 14
    H = top + rowh * len(CLAUDE_TASKS) + 34
    pw = W - left - right
    x = lambda v: left + pw * v / 5
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Claude 在各类联机任务上的把握度，1 到 5 分" class="chart">']
    for t in range(6):
        s.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{top-4}" y2="{H-28}" class="grid"/>')
        s.append(f'<text x="{x(t):.1f}" y="{H-12}" class="tick" text-anchor="middle">{t}</text>')
    for i, (name, v, lab) in enumerate(CLAUDE_TASKS):
        y = top + i * rowh
        bw = pw * v / 5
        s.append(f'<text x="{left-10}" y="{y+rowh/2+4:.1f}" class="lab" text-anchor="end">{E(name)}</text>')
        s.append(f'<g class="hit" data-tip="{E(name)}：{lab} / 5">'
                 f'<rect x="{left}" y="{y+4}" width="{pw}" height="{rowh-8}" fill="transparent"/>'
                 f'<path d="M{left},{y+8} h{bw-4:.1f} a4,4 0 0 1 4,4 v{rowh-24} a4,4 0 0 1 -4,4 h-{bw-4:.1f} z" class="bar s1"/></g>')
        s.append(f'<text x="{left+bw+6:.1f}" y="{y+rowh/2+4:.1f}" class="val">{lab}</text>')
    s.append('</svg>')
    rows = "".join(f"<tr><td>{E(n)}</td><td class='num'>{l}</td></tr>" for n, v, l in CLAUDE_TASKS)
    tbl = f'<details class="dt"><summary>查看数据表</summary><table><thead><tr><th>任务</th><th>把握度（1–5）</th></tr></thead><tbody>{rows}</tbody></table></details>'
    return "".join(s) + tbl

# ---------------- 图 2：房主上行带宽 ----------------
def chart_bw():
    W, H, left, right, top, bottom = 640, 310, 48, 16, 34, 64
    pw, ph = W - left - right, H - top - bottom
    vmax = 6
    y = lambda v: top + ph - ph * v / vmax
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="房主上行带宽估算：6 人与 12 人对比" class="chart">']
    for t in range(0, 7):
        s.append(f'<line x1="{left}" x2="{W-right}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="grid"/>')
        s.append(f'<text x="{left-8}" y="{y(t)+4:.1f}" class="tick" text-anchor="end">{t}</text>')
    s.append(f'<text x="{left-8}" y="{top-18}" class="tick" text-anchor="end">Mbps</text>')
    gw = pw / len(BANDWIDTH)
    bw = 46
    for i, (name, a, b, note) in enumerate(BANDWIDTH):
        cx = left + gw * i + gw / 2
        for j, (v, cls, who) in enumerate([(a, "s1", "6 人"), (b, "s2", "12 人")]):
            bx = cx - bw - 1 + j * (bw + 2)
            top_y = y(v); h = ph * v / vmax
            s.append(f'<g class="hit" data-tip="{E(name)} · {who}：约 {v:g} Mbps（{E(note)}）">'
                     f'<rect x="{bx:.1f}" y="{top:.1f}" width="{bw}" height="{ph}" fill="transparent"/>'
                     f'<path d="M{bx:.1f},{y(0):.1f} v-{max(h-4,0):.1f} a4,4 0 0 1 4,-4 h{bw-8} a4,4 0 0 1 4,4 v{max(h-4,0):.1f} z" class="bar {cls}"/></g>')
            s.append(f'<text x="{bx+bw/2:.1f}" y="{top_y-6:.1f}" class="val" text-anchor="middle">{v:g}</text>')
        s.append(f'<text x="{cx:.1f}" y="{H-bottom+20}" class="lab" text-anchor="middle">{E(name)}</text>')
    s.append('</svg>')
    leg = '<div class="legend"><span><i class="sw s1"></i>6 人</span><span><i class="sw s2"></i>12 人</span></div>'
    rows = "".join(f"<tr><td>{E(n)}</td><td class='num'>{a:g}</td><td class='num'>{b:g}</td><td>{E(no)}</td></tr>" for n, a, b, no in BANDWIDTH)
    tbl = f'<details class="dt"><summary>查看数据表</summary><table><thead><tr><th>场景</th><th>6 人（Mbps）</th><th>12 人（Mbps）</th><th>口径</th></tr></thead><tbody>{rows}</tbody></table></details>'
    return leg + "".join(s) + tbl

# ---------------- 24 格 ----------------
def cell_of(mode, lat, mig, n):
    return next(c for c in CELLS if c["mode"] == mode and c["lat"] == lat and c["mig"] == mig and c["n"] == n)

def argue(c):
    """按四个条件逐条给出技术论证（数字与第 3 章口径一致）。"""
    m, l, g, n = c["mode"], c["lat"], c["mig"], c["n"]
    pts = []
    # ① 模式
    if m == "PVE":
        pts.append(("对战模式 · PVE", "没有房主延迟优势、怒退结算和凑对手的问题。玩家对“房主走了就散”的容忍度高，致命公司、深岩银河、Peak 都是房主一走就结束。"))
    elif l == "帧不敏感":
        pts.append(("对战模式 · PVP", "帧不敏感时房主延迟优势几乎可以忽略，主要问题有两个：一是怒退和掉线要有结算规则（判负、不计分或作废本局）；二是必须凑齐对手，冷启动比 PVE 难。"))
    else:
        pts.append(("对战模式 · PVP", "帧敏感时房主 0 延迟、其他人有网络延迟，优势明显（Halo 3 时代 Bungie 也承认“显著”）。命中判定容易起争议，还需要足够大的匹配池才能按地区配对。"))
    # ② 延迟
    if l == "帧不敏感":
        pts.append(("延迟需求 · 帧不敏感", "由房主权威，每秒同步 5–10 次，每个玩家都存一份完整状态。房主上行在 6 人时约 0.12 Mbps，12 人时约 0.45 Mbps。不需要“确定性锁步”，房主权威加指令同步要简单得多（难度约 2 分，锁步要 4–5 分）。"))
    elif m == "PVE":
        pts.append(("延迟需求 · 帧敏感（PVE）", "每个玩家自己算自己的移动，房主管怪物和世界，再加插值让画面平滑。不用回滚，操作零延迟。代价是带宽：原生同步时房主上行 6 人约 1.2 Mbps，12 人约 5.3 Mbps，做量化和差分后 12 人约 1–1.5 Mbps。"))
    else:
        pts.append(("延迟需求 · 帧敏感（PVP）", "只有两条路：一是“房主型”，各自算移动、由房主判定命中，接受房主优势；二是上预测和回滚（netfox，或 1v1、2v2 的确定性回滚）。后者是 Claude 最弱的领域，把握度约 1–2/5，调试不同步也最痛苦。"))
    # ③ 换主
    if g == 0:
        pts.append(("房主离开 · 不换主", "只需要做到“体面回大厅”：自己写心跳检测，房主掉线时全员回大厅并提示原因，本地成长数据已存好。这是 Claude 最拿手的一类代码，把握度约 4/5。代价是房主掉线整局结束，所以单局最好控制在 15–30 分钟以内。"))
    elif g == 1:
        extra = "帧不敏感时人人都存了完整状态，新主几乎可以直接接管，在回合或波次边界迁移就能做到几乎不回档。" if l == "帧不敏感" else "帧敏感时要全员冻结、恢复最近的快照，会回退 1–5 秒。从第一天起就要按“可存档”的方式写：状态不能藏在物理节点和动画里，实体要有稳定 ID。"
        pts.append(("房主离开 · 秒级换主（D2）", "流程是判定房主掉线 → 选新主 → 新主开房、其他人重连 → 恢复快照。时间按段算：判定掉线时 Steam 默认超时 10 秒，可调到 3–5 秒；开房重连官方说法是“几秒”；恢复快照实测约 1.4 秒。合计下来，房主主动退出约 3–6 秒，崩溃约 6–15 秒（推算）。Godot 把房主固定为 1 号，换主必须新建连接、按 Steam ID 重新对号。" + extra))
    else:
        if l == "帧不敏感":
            pts.append(("房主离开 · 无感换主", "做法是“全员副本加继任顺序”：人人存完整状态，自己写心跳（约每 100ms 一次），事先排好继任顺序，房主一静默就由下一位接管，切换 0.3–1 秒，玩家感觉不到。前提是绕开 Godot 高层接口里“1 号永远是房主”的规定，自己管消息；误判掉线和出现两个房主的问题，只能靠测试暴露。"))
        else:
            pts.append(("房主离开 · 无感换主", "需要热备影子（D3）：另一台机器在后台实时跑一份副本，房主一静默就秒切。现成的只有 Godot Understudy：它是 v0.1.0，作者单机测 8 人换主中位约 0.23 秒，但没经过异地真实网络验证。用它要把游戏逻辑改写成能整体存取的纯数据，放弃 Godot 物理节点；作者记录的竞态类 bug 有 40 多条。"))
    # ④ 人数
    if n == 0:
        pts.append(("每局人数 · 4–6 人", "带宽和掉线的压力都小。假设每人每局掉线概率 3%，“至少一人掉线”约 17%。这个人数也最容易凑满房，PVE 合作类的先例几乎都在这个区间。"))
    else:
        pts.append(("每局人数 · 7–12 人", "星型连接下房主上行约按人数的平方增长，“至少一人掉线”从约 17% 升到约 31%，一次散局要影响 11 个人。小众游戏凑齐 7–12 个同时在线的人也很难。先例：WEBFISHING 12 人满房普遍卡顿，致命公司扩人模组的作者建议不超过 8 人。"))
    return "".join(f"<li><b>{E(t)}</b><br>{E(s)}</li>" for t, s in pts)

def neighbors(c):
    m, l, g, n = c["mode"], c["lat"], c["mig"], c["n"]
    alts = [("对战模式", "PVP" if m == "PVE" else "PVE", cell_of("PVP" if m == "PVE" else "PVE", l, g, n)),
            ("延迟需求", "帧敏感" if l == "帧不敏感" else "帧不敏感", cell_of(m, "帧敏感" if l == "帧不敏感" else "帧不敏感", g, n)),
            ("人数", NUM[1 - n], cell_of(m, l, g, 1 - n))]
    for gg in range(3):
        if gg != g:
            alts.append(("房主离开", MIG[gg], cell_of(m, l, gg, n)))
    out = []
    for dim, val, o in alts:
        out.append(f'<li>{E(dim)}改成 <b>{E(val)}</b> → <button type="button" class="go" data-go="{o["id"]}">#{o["id"]} 查看</button> {badge(o["level"])}'
                   f'<span class="muted"> 难度 {o["diff"]:g} · Claude {o["claude"]:g} · 稳定 {o["stab"]:g} · 胜率 {E(o["win"])}</span></li>')
    return "".join(out)

def overview_html(c):
    return ov_render(c, CELLS, MIG, NUM, {k: v[1] for k, v in LEVEL.items()}, badge)

def detail_sections(c):
    h = []
    h.append('<h4 class="dsec" id="s-impl">网络实现方案（技术与架构）</h4><table class="impl"><tbody>'
             + "".join(f'<tr><th>{E(k)}</th><td>{E(v)}</td></tr>' for k, v in impl_rows(c)) + '</tbody></table>')
    steps, timing = leave_flow(c)
    h.append(f'<h4 class="dsec" id="s-flow">房主离开时怎么处理（{E(MIG[c["mig"]])}）</h4><ol class="flow">'
             + "".join(f'<li>{E(s)}</li>' for s in steps) + f'</ol><p class="timing">⏱ {E(timing)}</p>')
    ms = modules(c)
    h.append('<h4 class="dsec" id="s-mod">模块拆分与工期（网络部分，假设单机玩法已完成、由 Claude 写代码）</h4><table class="mods"><thead><tr><th>模块</th><th>内容</th><th>工期</th></tr></thead><tbody>'
             + "".join(f'<tr><td><b>{E(a)}</b></td><td>{E(b)}</td><td class="num">{(f"{lo:g} 周" if lo == hi else f"{lo:g}–{hi:g} 周")}</td></tr>' for a, b, lo, hi in ms)
             + f'<tr class="tot"><td><b>合计</b></td><td>评分卡里的“网络部分工期”即此合计（偏保守，模块间可复用时会更短）</td><td class="num"><b>{E(weeks_total(c))}</b></td></tr></tbody></table>')
    h.append('<h4 class="dsec" id="s-code">编码难点（写代码时最容易出错的地方）</h4><ul class="pit">'
             + "".join(f'<li><span class="tag {"t-claude" if who.startswith("Claude") else "t-you"}">{E(who)}</span>{E(s)}</li>' for who, s in code_pitfalls(c)) + '</ul>')
    h.append('<h4 class="dsec" id="s-test">测试方法</h4><ul class="plain">' + "".join(f'<li>{E(s)}</li>' for s in tests(c)) + '</ul>')
    h.append('<h4 class="dsec" id="s-mnt">上线后的维护难点与低维护做法</h4><ul class="plain">' + "".join(f'<li>{E(s)}</li>' for s in maintenance(c)) + '</ul>')
    h.append('<h4 class="dsec" id="s-risk">风险与降级方案</h4><table class="mods"><thead><tr><th>风险</th><th>怎么兜底</th></tr></thead><tbody>'
             + "".join(f'<tr><td><b>{E(a)}</b></td><td>{E(b)}</td></tr>' for a, b in risks(c)) + '</tbody></table>')
    h.append('<h4 class="dsec" id="s-case">可参考的先例</h4><ul class="plain">' + "".join(f'<li>{E(s)}</li>' for s in cases(c)) + '</ul>')
    return "".join(h)

def grid():
    # ---- 条件筛选器 ----
    groups = [("mode", "A（对战模式）", ["PVE", "PVP"], ["合作打电脑", "玩家对战"]),
              ("lat", "B（延迟需求）", ["帧不敏感", "帧敏感"], ["三国志式", "马里奥式"]),
              ("mig", "C（房主离开时）", MIG, ["散局回大厅", "停几秒换人", "几乎无感"]),
              ("n", "D（每局人数）", NUM, ["小队", "中等规模"])]
    out = ['<form id="picker" class="picker" onsubmit="return false"><div class="xrow">']
    for key, label, opts, hints in groups:
        out.append(f'<label class="xcell"><span class="xhead">{E(label)}</span><select name="{key}" aria-label="{E(label)}">'
                   '<option value="" selected>请选择</option>')
        for i, (o, h) in enumerate(zip(opts, hints)):
            val = o if key in ("mode", "lat") else str(i)
            out.append(f'<option value="{E(val)}">{E(o)}（{E(h)}）</option>')
        out.append('</select></label>')
    out.append('<div class="xcell xbtn"><span class="xhead">&nbsp;</span><button id="confirm" type="button" disabled>确认</button></div>'
               '</div><p id="pickhint" class="muted">还需选择 4 项条件</p></form>')
    out.append('<div id="detail" class="detail" aria-live="polite"></div>')
    # 预渲染详情模板
    for c in CELLS:
        out.append(f'<template id="t{c["id"]}"><div class="dhead"><span class="cid">#{c["id"]}</span>'
                   f'<b>{c["mode"]} × {c["lat"]} × {MIG[c["mig"]]} × {NUM[c["n"]]}</b>{badge(c["level"])}</div>'
                   f'<p class="dnote">{E(c["note"])}</p>'
                   + metrics(c) +
                   '<nav class="dnav">本格目录：<a href="#" data-s="s-ev">速览</a><a href="#" data-s="s-impl">网络实现方案</a><a href="#" data-s="s-flow">房主离开流程</a><a href="#" data-s="s-mod">模块与工期</a><a href="#" data-s="s-code">编码难点</a><a href="#" data-s="s-test">测试</a><a href="#" data-s="s-mnt">上线维护</a><a href="#" data-s="s-risk">风险与降级</a><a href="#" data-s="s-case">先例</a><a href="#" data-s="s-arg">技术论证</a></nav>'
                   '<h4 class="dsec" id="s-ev">一眼看懂这一格（速览）</h4>'
                   + overview_html(c) +
                   '<p class="more muted">↓ 以下是给需要细节时查阅的技术长文</p>'
                   + detail_sections(c) +
                   '<h4 class="dsec" id="s-arg">技术论证：四个条件在这一格里各自意味着什么</h4>'
                   f'<ol class="argue">{argue(c)}</ol>'
                   '<h4 class="dsec">如果只改一个条件</h4>'
                   f'<ul class="nb">{neighbors(c)}</ul></template>')
    def tcell(v, tone_fn):
        tone, word = tone_fn(v)
        return f'<td class="num tv t-{tone}" title="{E(word)}">{E(v if isinstance(v, str) else f"{v:g}")}</td>'
    rows = "".join(
        f'<tr data-mode="{c["mode"]}" data-lat="{c["lat"]}" data-mig="{MIG[c["mig"]]}" data-n="{NUM[c["n"]]}" data-level="{LEVEL[c["level"]][1]}">'
        f'<td class="num">{c["id"]}</td><td>{c["mode"]}</td><td>{c["lat"]}</td><td>{MIG[c["mig"]]}</td><td>{NUM[c["n"]]}</td>'
        f'<td>{badge(c["level"])}</td><td>{E(c["method"])}</td><td>{E(c["pros"])}</td><td>{E(c["cons"])}</td><td>{E(c["tech"])}</td>'
        + tcell(c["diff"], tone_low_good) + tcell(c["claude"], tone_high_good)
        + tcell(c["stab"], lambda v: tone_high_good(v, ("稳", "一般", "不稳"))) + tcell(c["weeks"], tone_weeks) + tcell(c["win"], tone_win)
        + '</tr>'
        for c in CELLS)
    def fth(label, key, opts):
        o = "".join(f'<option value="{E(x)}">{E(x)}</option>' for x in opts)
        return f'<th class="fh"><span>{label}</span><select data-col="{key}" aria-label="筛选{label}"><option value="">全部</option>{o}</select></th>'
    cols = [2.5, 5, 5.5, 6, 5.5, 6.5, 13.5, 12, 12, 10.5, 3.5, 4, 3.5, 4.5, 5.5]
    colg = "<colgroup>" + "".join(f'<col style="width:{w}%">' for w in cols) + "</colgroup>"
    out.append('<details class="dt wide" open><summary>24 格完整对照表（表头下拉可筛选）</summary>'
               '<p class="muted ftip">在“模式 / 延迟 / 换主 / 人数 / 结论”的表头下拉框里筛选，例如只看“可行”。<span id="fcount">显示 24 / 24 行</span> <button type="button" id="freset" class="go">清除筛选</button></p>'
               '<div class="scroll"><table class="full" id="fulltbl">' + colg + '<thead><tr><th>#</th>'
               + fth("模式", "mode", ["PVE", "PVP"]) + fth("延迟", "lat", ["帧不敏感", "帧敏感"])
               + fth("换主", "mig", MIG) + fth("人数", "n", NUM)
               + fth("结论", "level", [v[1] for v in LEVEL.values()])
               + '<th>推荐方式</th><th>利</th><th>弊</th><th>技术要求</th>'
               '<th>难度</th><th>Claude</th><th>稳定</th><th>工期</th><th>胜率</th></tr></thead><tbody>' + rows + '</tbody></table></div></details>')
    return "".join(out)

counts = {k: sum(1 for c in CELLS if c["level"] == k) for k in LEVEL}

def refs():
    out = []
    for g, items in REFS:
        lis = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a><span class="muted"> · {E(src)}</span></li>' for t, u, src in items)
        out.append(f'<div class="refg"><h4>{E(g)}</h4><ul>{lis}</ul></div>')
    return "".join(out)

CSS = r"""
:root{color-scheme:light;--good-t:#006300;--warning-t:#8a5300;--critical-t:#b02a2a;--violet:#6250d6;--bg:#f7f6f2;--surface-1:#fcfcfb;--surface-2:#f0efec;--line:#e2e0da;--text-primary:#0b0b0b;--text-secondary:#52514e;--muted:#7a7972;
--accent:#2a78d6;--series-1:#2a78d6;--series-2:#eb6834;--good:#0ca30c;--warning:#fab219;--critical:#d03b3b;--good-bg:#e7f5e7;--warning-bg:#fff4dc;--critical-bg:#fbe6e6;--code:#efeee9}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--bg:#121211;--surface-1:#1a1a19;--surface-2:#242422;--line:#33332f;--text-primary:#f0efec;--text-secondary:#c3c2b7;--muted:#8f8e86;
--accent:#3987e5;--series-1:#3987e5;--series-2:#d95926;--good-bg:#16301a;--warning-bg:#3a2f12;--critical-bg:#3a1b1b;--good-t:#5fd35f;--warning-t:#fab219;--critical-t:#ff8a8a;--violet:#9085e9;--code:#2a2a27}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#121211;--surface-1:#1a1a19;--surface-2:#242422;--line:#33332f;--text-primary:#f0efec;--text-secondary:#c3c2b7;--muted:#8f8e86;
--accent:#3987e5;--series-1:#3987e5;--series-2:#d95926;--good-bg:#16301a;--warning-bg:#3a2f12;--critical-bg:#3a1b1b;--good-t:#5fd35f;--warning-t:#fab219;--critical-t:#ff8a8a;--violet:#9085e9;--code:#2a2a27}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text-primary);font:16px/1.75 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:24px 16px 64px}
header.top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
h1{font-size:clamp(22px,4.6vw,32px);line-height:1.3;margin:8px 0 4px}h2{font-size:22px;margin:48px 0 12px;padding-top:8px;border-top:1px solid var(--line)}
h3{font-size:17px;margin:24px 0 8px}h4{margin:0 0 8px;font-size:15px}
p{margin:10px 0}.sub{color:var(--text-secondary);margin:0}.muted{color:var(--muted);font-size:13px}
a{color:var(--accent)}code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:.9em}
#theme{flex:none;border:1px solid var(--line);background:var(--surface-1);color:var(--text-primary);border-radius:999px;padding:6px 14px;font-size:14px;cursor:pointer}
.card{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.answer{font-size:18px;line-height:1.7;border-left:4px solid var(--accent)}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:16px 0}
.stat{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:14px}
.stat b{display:block;font-size:26px;line-height:1.2;font-variant-numeric:tabular-nums}.stat span{display:block;color:var(--text-secondary);font-size:14px;margin-top:4px}
.stat small{color:var(--muted);font-size:12px}
nav.toc ol{margin:6px 0;padding-left:22px}nav.toc a{text-decoration:none}
.callout{background:var(--surface-2);border-radius:10px;padding:12px 16px;margin:14px 0}
.chartbox{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:14px;margin:16px 0;overflow-x:auto;position:relative}
.chartbox h4{margin-bottom:2px}.chart{width:100%;min-width:520px;height:auto;display:block;margin-top:8px}
.chart .grid{stroke:var(--line);stroke-width:1}.chart .tick{fill:var(--muted);font-size:12px;font-variant-numeric:tabular-nums}
.chart .lab{fill:var(--text-secondary);font-size:13px}.chart .val{fill:var(--text-primary);font-size:12px;font-variant-numeric:tabular-nums}
.chart .bar{stroke:var(--surface-1);stroke-width:2}.chart .s1{fill:var(--series-1)}.chart .s2{fill:var(--series-2)}
.chart .hit:hover .bar,.chart .hit:focus .bar{opacity:.85}
.legend{display:flex;flex-wrap:wrap;gap:14px;align-items:center;font-size:13px;color:var(--text-secondary);margin:6px 0}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}.sw.s1{background:var(--series-1)}.sw.s2{background:var(--series-2)}
#tip{position:fixed;pointer-events:none;background:var(--text-primary);color:var(--surface-1);font-size:13px;padding:6px 10px;border-radius:6px;max-width:300px;opacity:0;transition:opacity .1s;z-index:9}
details.dt{margin-top:8px;font-size:14px}details.dt summary{cursor:pointer;color:var(--accent)}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.scroll{overflow-x:auto}
details.wide{--ww:min(1760px,calc(100vw - 48px));width:var(--ww);margin-left:calc((100% - var(--ww)) / 2)}
table.full{table-layout:fixed;min-width:1100px;font-size:13px;line-height:1.55}
table.full th{position:sticky;top:0;background:var(--surface-2);z-index:1;vertical-align:bottom;white-space:nowrap}
table.full td{word-break:break-word}table.full td:nth-child(-n+5){white-space:nowrap}
table.full tbody tr:hover{background:var(--surface-2)}
table.full .badge{font-size:12px;padding:0 6px}
th.fh span{display:block}th.fh select{width:100%;margin-top:4px;font:inherit;font-size:12px;font-weight:400;color:var(--text-primary);background:var(--surface-1);border:1px solid var(--line);border-radius:4px;padding:2px 2px}
th.fh select.set{background:var(--warning-bg);border-color:var(--warning);font-weight:700}
table.full td.tv{font-weight:700;color:var(--tt);border-left:3px solid var(--tc);white-space:normal;word-break:break-word}
.ftip{margin:6px 0}#fcount{margin-left:8px;color:var(--text-primary);font-weight:600}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:13px;font-weight:600;padding:1px 8px;border-radius:999px;border:1px solid;white-space:nowrap}
.bi{font-size:12px}
.st-good{--c:var(--good);--cb:var(--good-bg)}.st-warning{--c:var(--warning);--cb:var(--warning-bg)}.st-critical{--c:var(--critical);--cb:var(--critical-bg)}
.badge.st-good,.badge.st-warning,.badge.st-critical{border-color:var(--c);background:var(--cb);color:var(--text-primary)}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}
.f{border:1px solid var(--line);background:var(--surface-1);color:var(--text-primary);border-radius:999px;padding:5px 12px;font-size:14px;cursor:pointer}
.f.on{background:var(--accent);border-color:var(--accent);color:#fff}
.lv{gap:10px}
.blocks{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px;margin:12px 0}
.blk{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:12px}
.blk.hide{display:none}
table.mx th{font-size:13px;color:var(--text-secondary);font-weight:600;border:0;padding:4px}table.mx td{border:0;padding:4px}
table.mx th[scope=row]{white-space:nowrap;vertical-align:middle}
.cell{width:100%;text-align:left;border:1px solid var(--line);border-left:4px solid var(--c);background:var(--surface-1);color:var(--text-primary);border-radius:8px;padding:6px 8px;cursor:pointer;display:flex;flex-direction:column;gap:2px;font:inherit}
.cell:hover,.cell.sel{background:var(--cb)}.cell .badge{align-self:flex-start}
.cid{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;margin-right:6px}
.mini{font-size:12px;color:var(--text-secondary);line-height:1.4;font-variant-numeric:tabular-nums}
.detail:empty{display:none}.detail{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:6px 0 14px}
.dhead{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.dnote{color:var(--text-secondary)}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px;margin:8px 0}
.kv>.m{background:var(--surface-2);border-radius:8px;padding:8px 10px 8px 12px;border-left:4px solid var(--tc);position:relative}
.kv .ml{display:block;font-size:12px;color:var(--muted)}
.kv .mw{display:inline-block;font-style:normal;font-size:12px;font-weight:700;color:var(--tt);background:var(--tb);border-radius:999px;padding:0 8px;margin-top:4px}
.kv .m .score,.kv .m .mv{color:var(--tt)}.kv .mv{display:block;font-size:17px;line-height:1.4}
.t-good{--tc:var(--good);--tt:var(--good-t);--tb:var(--good-bg)}.t-warn{--tc:var(--warning);--tt:var(--warning-t);--tb:var(--warning-bg)}.t-bad{--tc:var(--critical);--tt:var(--critical-t);--tb:var(--critical-bg)}
.kvleg{margin:2px 0 0;font-size:12px}.kvleg .k{display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--tc);margin:0 3px 0 8px;vertical-align:-1px}.kvleg .k:first-child{margin-left:0}
dl.ev dt{display:inline-block;padding:1px 10px;border-radius:6px;margin-top:12px}
.d-rec{color:var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent)}
.d-alt{color:var(--text-secondary);background:var(--surface-2)}
.d-pro{color:var(--good-t);background:var(--good-bg)}.d-con{color:var(--critical-t);background:var(--critical-bg)}
.d-tec{color:var(--violet);background:color-mix(in srgb,var(--violet) 12%,transparent)}
.kv span.score,.score{display:inline;font-size:20px;font-weight:700;color:var(--text-primary);font-variant-numeric:tabular-nums}.score small{font-size:12px;color:var(--muted);font-weight:400}
dl{margin:8px 0}dt{font-weight:700;margin-top:8px;font-size:14px}dd{margin:2px 0 0;color:var(--text-secondary)}
ol.route{padding-left:22px}ol.route li{margin:8px 0}
.refg ul{margin:4px 0 14px;padding-left:20px}.refg li{margin:3px 0;font-size:14px}
.meta dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 14px;margin:0}.meta dt{margin:0;color:var(--muted);font-weight:400}.meta dd{margin:0;color:var(--text-primary)}
.picker{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:14px 16px;margin:14px 0}
.picker fieldset{border:0;margin:0 0 12px;padding:0;min-width:0}.picker legend{font-weight:700;font-size:15px;margin-bottom:6px;padding:0}
.seg{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.seg label{position:relative;cursor:pointer}.seg input{position:absolute;opacity:0;width:1px;height:1px}
.seg span{display:block;border:1px solid var(--line);border-radius:10px;padding:8px 12px;background:var(--bg);transition:border-color .1s,background .1s}
.seg span b{display:block;font-size:15px}.seg span small{display:block;font-size:12px;color:var(--muted);line-height:1.4}
.seg label:hover span{border-color:var(--accent)}
.seg input:checked+span{border-color:var(--accent);background:var(--surface-2);box-shadow:inset 0 0 0 1px var(--accent)}
.seg input:focus-visible+span{outline:2px solid var(--accent);outline-offset:2px}
.xrow{display:grid;grid-template-columns:repeat(4,minmax(0,1fr)) auto;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--surface-1)}
.xcell{display:flex;flex-direction:column;min-width:0;border-right:1px solid var(--line)}.xcell:last-child{border-right:0}
.xhead{font-size:13px;color:var(--text-secondary);padding:6px 10px;background:var(--surface-2);border-bottom:1px solid var(--line);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.xcell select{appearance:none;-webkit-appearance:none;border:0;border-radius:0;margin:0;width:100%;min-width:0;font:inherit;font-size:14px;color:var(--muted);padding:9px 30px 9px 10px;cursor:pointer;
background:var(--surface-1) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18'%3E%3Crect width='18' height='18' rx='3' fill='%231baf7a'/%3E%3Cpath d='M5 7l4 4 4-4' fill='none' stroke='white' stroke-width='2'/%3E%3C/svg%3E") no-repeat right 8px center}
.xcell select.set{color:var(--text-primary);font-weight:600;background-color:var(--warning-bg)}
.xcell select:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.xcell select option{color:var(--text-primary);background:var(--surface-1);font-weight:400}
.xbtn{justify-content:stretch}.xbtn #confirm{border-radius:0;height:100%;padding:0 22px}
#pickhint{margin:8px 2px 0}
@media (max-width:720px){.xrow{grid-template-columns:repeat(2,minmax(0,1fr))}.xcell{border-bottom:1px solid var(--line)}.xcell:nth-child(2n){border-right:0}
.xbtn{grid-column:1/-1;border-bottom:0}.xbtn .xhead{display:none}.xbtn #confirm{padding:11px}}
#confirm{border:0;background:var(--accent);color:#fff;font:inherit;font-weight:700;border-radius:10px;padding:10px 22px;cursor:pointer;white-space:nowrap}
#confirm:disabled{background:var(--surface-2);color:var(--muted);cursor:not-allowed}
.dsec{margin:18px 0 6px;font-size:15px;padding-top:10px;border-top:1px dashed var(--line)}
ol.argue{padding-left:22px;margin:4px 0}ol.argue li{margin:8px 0;color:var(--text-secondary)}ol.argue b{color:var(--text-primary)}
ul.nb{padding-left:20px;margin:4px 0}ul.nb li{margin:6px 0;font-size:14px}
.go{border:1px solid var(--accent);background:transparent;color:var(--accent);border-radius:6px;padding:0 8px;font:inherit;font-size:13px;cursor:pointer}

.ov{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px}
.ovc{background:var(--surface-1);border:1px solid var(--line);border-radius:12px;padding:14px 18px;min-width:0}
.ovc.hero,.ovc.wide{grid-column:1/-1}
.ovh{font-weight:700;font-size:16px;margin-bottom:6px;color:var(--text-primary)}
.ovc p{margin:6px 0;color:var(--text-secondary)}.ovc ul,.ovc ol{margin:4px 0;padding-left:20px}.ovc li{margin:6px 0;color:var(--text-secondary)}
.ovc.hero{border-left:4px solid var(--accent)}.ovc.hero p{color:var(--text-primary);font-size:16px}
.diffline{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:center;margin-top:10px;padding:8px 12px;border-radius:8px;background:var(--tb);color:var(--tt)}
.diffline .st{letter-spacing:2px;font-size:18px;color:var(--tt)}.diffline .muted{color:var(--text-secondary)}
.analogy{font-size:16px;color:var(--text-primary)!important}
.tech{font-size:14px;border-top:1px dashed var(--line);padding-top:8px}
dl.feel{margin:0}dl.feel dt{font-weight:700;margin-top:8px;color:var(--text-primary);font-size:14px}dl.feel dd{margin:2px 0 0;color:var(--text-secondary)}
.bk{display:grid;grid-template-columns:130px minmax(0,1fr) 64px;grid-template-areas:"n b w" ". t t";gap:2px 12px;align-items:center;margin:12px 0}
.bkn{grid-area:n;font-weight:700;color:var(--text-primary)}.bkbar{grid-area:b;height:12px;background:var(--surface-2);border-radius:6px;overflow:hidden}
.bkbar i{display:block;height:100%;background:var(--tc);border-radius:6px}.bkw{grid-area:w;font-size:13px;font-weight:700;color:var(--tt)}
.bkt{grid-area:t;font-size:14px;color:var(--text-secondary)}
.ovc.pros{border-top:4px solid var(--good)}.ovc.cons{border-top:4px solid var(--critical)}
ul.chk{list-style:none;padding-left:0}ul.chk li{padding-left:26px;position:relative}ul.chk li::before{content:"☐";position:absolute;left:2px;color:var(--accent);font-weight:700}
ol.fb li{margin:4px 0}
.ovc.adv{border-left:4px solid var(--accent);background:color-mix(in srgb,var(--accent) 7%,var(--surface-1))}.ovc.adv p b{color:var(--text-primary)}
.more{margin:18px 0 0;text-align:center}
@media (max-width:720px){.ov{grid-template-columns:1fr}.bk{grid-template-columns:92px minmax(0,1fr) 52px;grid-template-areas:"n b w" "t t t"}}
h2.first{margin-top:28px;border-top:0}
#picker,#detail{--wb:min(1280px,calc(100vw - 48px));width:var(--wb);margin-left:calc((100% - var(--wb)) / 2)}
@media (max-width:720px){#picker,#detail{width:auto;margin-left:0}}
.dnav{display:flex;flex-wrap:wrap;gap:6px 4px;align-items:center;font-size:13px;color:var(--muted);margin:10px 0 0}
.dnav a{border:1px solid var(--line);border-radius:999px;padding:1px 10px;text-decoration:none;background:var(--surface-1)}
.dnav a:hover{border-color:var(--accent)}
table.impl th{width:150px;white-space:nowrap;color:var(--text-primary);background:var(--surface-2);font-weight:700}
table.impl td,table.mods td{color:var(--text-secondary)}table.impl th,table.impl td,table.mods td,table.mods th{padding:8px 10px}
table.mods thead th{background:var(--surface-2)}table.mods tr.tot td{border-top:2px solid var(--line);color:var(--text-primary)}
ol.flow{padding-left:24px;margin:4px 0}ol.flow li{margin:6px 0;color:var(--text-secondary)}
.timing{display:inline-block;background:var(--warning-bg);color:var(--warning-t);font-weight:700;border-radius:8px;padding:4px 12px;margin:4px 0}
ul.pit{list-style:none;padding:0;margin:4px 0}ul.pit li{margin:7px 0;color:var(--text-secondary)}
.tag{display:inline-block;font-size:12px;font-weight:700;border-radius:6px;padding:0 8px;margin-right:8px}
.tag.t-claude{color:var(--critical-t);background:var(--critical-bg)}.tag.t-you{color:var(--accent);background:color-mix(in srgb,var(--accent) 12%,transparent)}
ul.plain{padding-left:20px;margin:4px 0}ul.plain li{margin:6px 0;color:var(--text-secondary)}
.detail{padding:18px 22px}
@media (max-width:520px){.meta dl{grid-template-columns:1fr}.answer{font-size:16px}}
"""

JS = r"""
(function(){
var root=document.documentElement,btn=document.getElementById('theme');
function cur(){return root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}
function lab(){btn.textContent=cur()==='dark'?'☀ 白天模式':'☾ 深色模式'}
try{var s=localStorage.getItem('theme');if(s)root.setAttribute('data-theme',s)}catch(e){}
lab();btn.onclick=function(){var n=cur()==='dark'?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){};lab()};
var tip=document.getElementById('tip');
document.querySelectorAll('.hit').forEach(function(g){g.setAttribute('tabindex','0');
 g.addEventListener('mousemove',function(e){tip.textContent=g.dataset.tip;tip.style.opacity=1;tip.style.left=Math.min(e.clientX+12,innerWidth-310)+'px';tip.style.top=(e.clientY+14)+'px'});
 g.addEventListener('mouseleave',function(){tip.style.opacity=0});
 g.addEventListener('focus',function(){var r=g.getBoundingClientRect();tip.textContent=g.dataset.tip;tip.style.opacity=1;tip.style.left=Math.min(r.left,innerWidth-310)+'px';tip.style.top=(r.bottom+6)+'px'});
 g.addEventListener('blur',function(){tip.style.opacity=0});});
var det=document.getElementById('detail'),form=document.getElementById('picker'),ok=document.getElementById('confirm'),hint=document.getElementById('pickhint');
var MAP=__MAP__,KEYS=['mode','lat','mig','n'],NAMES={mode:'对战模式',lat:'延迟需求',mig:'房主离开时',n:'每局人数'};
function sel(){var r={};KEYS.forEach(function(k){var e=form.querySelector('select[name="'+k+'"]');if(e&&e.value!=='')r[k]=e.value});return r}
function upd(){var s=sel(),miss=KEYS.filter(function(k){return !(k in s)});ok.disabled=miss.length>0;
 hint.textContent=miss.length?('还需选择：'+miss.map(function(k){return NAMES[k]}).join('、')):'已选好，点确认查看';
 form.querySelectorAll('select').forEach(function(s){s.classList.toggle('set',s.value!=='')});}
form.addEventListener('change',function(e){if(e.target.tagName==='SELECT')e.target.classList.toggle('set',e.target.value!=='');upd()});upd();
function show(id){det.innerHTML='';det.appendChild(document.getElementById('t'+id).content.cloneNode(true));
 det.querySelectorAll('.dnav a').forEach(function(a){a.onclick=function(e){e.preventDefault();var s=det.querySelector('#'+a.dataset.s);if(s)s.scrollIntoView({behavior:'smooth',block:'start'})}});
 det.querySelectorAll('[data-go]').forEach(function(a){a.onclick=function(){pick(a.dataset.go)}});}
ok.onclick=function(){var s=sel();show(MAP[[s.mode,s.lat,s.mig,s.n].join('|')])};
function pick(id){var c=INV[id];KEYS.forEach(function(k,i){var e=form.querySelector('select[name="'+k+'"]');if(e)e.value=c[i]});upd();show(id)}
var INV={};Object.keys(MAP).forEach(function(k){INV[MAP[k]]=k.split('|')});
pick(1);hint.textContent='默认展示首推组合 #1，改选条件后点确认即可';
var tb=document.getElementById('fulltbl'),fc=document.getElementById('fcount');
function tf(){var f={};tb.querySelectorAll('thead select').forEach(function(s){if(s.value)f[s.dataset.col]=s.value;s.classList.toggle('set',!!s.value)});var n=0;
 tb.querySelectorAll('tbody tr').forEach(function(r){var ok=Object.keys(f).every(function(k){return r.dataset[k]===f[k]});r.hidden=!ok;if(ok)n++});fc.textContent='显示 '+n+' / 24 行';}
tb.querySelector('thead').addEventListener('change',tf);document.getElementById('freset').onclick=function(){tb.querySelectorAll('thead select').forEach(function(s){s.value=''});tf()};
})();
"""

BODY = """
<header class="top"><div><p class="muted">深度调研报告 · 2026-11</p><h1>{title}</h1><p class="sub">{sub}</p></div>
<button id="theme" type="button">☾ 深色模式</button></header>

<h2 id="c5" class="first">24 种情况评估器（主表）</h2>
<p class="muted">这是报告的主体：选好四个条件就能看到那一格的完整评估。下方是 24 格总表；推导过程、案例和建议在后面的章节。</p>
<p>综合 19 个调研方向的证据，每格给出推荐方式、备选、利弊、技术要求，以及难度、Claude 把握度、网络稳定性（各 1–5 分）。另有两项估算：</p>
<ul>
<li><b>网络部分工期</b>：假设单机玩法已经做完，由 Claude 写代码。</li>
<li><b>终局胜率</b>：做出来、上线稳定、不用天天维护的主观概率，不含市场成败。</li>
</ul>
<p>难度是 5 分最难；把握度和稳定性是 5 分最好。</p>
<p><b>用法：</b>像表格表头一样，在下面一排四个下拉框（A–D）里各选一项，点“确认”，就会出现这一格的评估，包括评分、推荐方式、利弊、技术要求，以及四个条件各自的技术论证。最后还会列出“只改一个条件”会落到哪一格，可以一键跳过去对比。打开页面时默认展示首推组合 #1。下方是全部 24 格的汇总表，表头的下拉框可以筛选，比如只看“可行”的格子。</p>
{grid}


<div class="card answer"><b>一句话答案：</b>能做，但成败几乎取决于你选哪一格。24 种情况里，<b>{top} 格首推、{ok} 格可行、{meh} 格勉强、{no} 格不建议</b>。最稳的是 <b>PVE 合作 × 帧不敏感 × 不换主 × 4–6 人</b>。凡是“帧敏感 PVP 加 7–12 人”或“帧敏感加无感换主”的组合，都不要押在第一款游戏上。决定难度的头号因素是<b>换主</b>，人数的影响其实最小。</div>

<div class="stats">
<div class="stat"><b>$0 / 月</b><span>Steam 大厅加中继网络（SDR）做联机，不需要租服务器</span><small>另有一次性上架费 $100，收入满 $1000 返还</small></div>
<div class="stat"><b>约 30 秒</b><span>房主拔网线后，Steam 才通知其他人“房主走了”</span><small>社区实测个例；所以掉线检测必须自己写心跳</small></div>
<div class="stat"><b>4 → 1 分</b><span>Claude 的把握度：从“大厅加房主同步”降到“无感换主”</span><small>满分 5；把握度看架构复杂度，人数影响很小</small></div>
<div class="stat"><b>5.3 Mbps</b><span>12 人、帧敏感、原生同步不优化时，房主需要的上行带宽</span><small>公式估算；优化后约 1–1.5，帧不敏感约 0.45</small></div>
</div>

<nav class="card toc"><b>这份报告怎么讲</b><ol>
<li style="list-style:none;margin-left:-22px"><a href="#c5">↑ 24 种情况评估器与总表（页面最上方）</a></li>
<li><a href="#c1">Steam 免费送了你哪些联机零件</a></li>
<li><a href="#c2">Godot 这一侧：零件接得上，但房主固定是 1 号</a></li>
<li><a href="#c3">四个开关，难度分别从哪来</a></li>
<li><a href="#c4">Claude 能替你扛多少</a></li>
<li><a href="#c6">上线以后：哪些格子做完就不太用管</a></li>
<li><a href="#c7">我的建议：一条低风险的升级路线</a></li>
</ol></nav>

<h2 id="c1">1. Steam 免费送了你哪些联机零件</h2>
<p><b>问题：</b>不租服务器，光靠 Steam 能撑起一款联机游戏吗？<b>答案：能，而且你要的房间列表它也自带。</b></p>
<p>可以把 Steam 想成一家免费出借场地和传话员的会所：</p>
<ul>
<li><b>大厅（Lobby）就是房间列表。</b>可以建房、搜房、按条件过滤，在房间上贴“模式、版本、人数”这类标签，直接显示“等待中的房间”。每个大厅最多 250 人。房主走了，Steam 会自动指定一位新房主，但它只转交房主这个身份，不会帮你搬游戏进度。</li>
<li><b>中继网络（SDR, Steam Datagram Relay）是传话员。</b>所有数据经 Valve 的中继节点转发，玩家不用设端口转发，IP 也被隐藏。对 Steam 游戏不另收费：这是业界共识，Valve 文档里没写价格。Valve 公开的节点配置里有中国大陆节点（阿里云成都、北京、上海，腾讯云广州）。不过这份配置是用 CS2 查到的，第三方游戏能不能分到这些节点还没证实。</li>
<li><b>另外还有：</b>好友邀请、“加入游戏”、Rich Presence（好友列表里显示你在玩什么），以及免费的 Playtest（独立 AppID，可以做联机公测）。</li>
</ul>
<div class="callout"><b>两个来自真实案例的坑，必须提前填上：</b><br>
① WEBFISHING（Godot 加 GodotSteam）上线头几个月，补丁里反复修大厅问题：活跃房间超过 50 个就搜不到、房间码“距离太远连不上”、旧版本房间混在列表里。原因是 Steam 的大厅搜索默认只找同区和邻近区。面向全球玩家，要把距离过滤设成 Worldwide，并把版本号写进大厅标签做过滤。<br>
② Buckshot Roulette（Godot）开放公共大厅时，官方让玩家自己做端口转发。这说明它没有强制走中继。你要强制所有连接走 SDR，就能免掉这类求助。</div>
<p>代价也要知道：Steam 联机只限 Steam 玩家；同一台电脑不能同时登两个 Steam 账号来自测。这就引出下一个问题：Godot 怎么接上这些零件。</p>

<h2 id="c2">2. Godot 这一侧：零件接得上，但房主固定是 1 号</h2>
<p><b>问题：</b>Godot 能顺畅用上 Steam 联机吗？<b>答案：能接上，但“换主”这件事引擎完全不管。</b></p>
<p>负责接线的是社区插件 <b>GodotSteam</b>。它自带 SteamMultiplayerPeer，能把 Steam 连接接到 Godot 的高层多人接口上（RPC 远程调用、MultiplayerSynchronizer 状态同步等）。效果是你可以像写局域网游戏一样写 Steam 联机，这是 Claude 最熟悉的写法。现状有三点要知道：</p>
<ul>
<li><b>主仓已迁到 Codeberg，更新很频繁。</b>2026 年 7–11 月发了约 9 个版本，多数带接口改名或删除。最新是 4.24（2026-11），支持 Godot 4.4+。结论是锁死版本，不追新。另一个独立的 expressobits 版已停更，不要用。</li>
<li><b>一个已修好的漏洞。</b>4.17–4.23.2 版里，任何玩家都能冒充房主，4.24 已修复。你不在意开挂，但这个洞也能被用来捣乱，所以至少用 4.24。</li>
<li><b>真正的坎：房主永远是 1 号。</b>Godot 的高层接口规定房主是 peer 1，没有“把 1 号交给别人”的接口。房主一断，连接对象直接关闭，同步生成的角色和物体也跟着消失。引擎层面要求自动换主的提案（#7912）从 2023 年挂到现在，没人接。</li>
</ul>
<div class="callout"><b>打个比方：</b>Godot 的牌桌只认“1 号座位是庄家”，庄家一离席，整张桌子就散了。所谓换主，其实是另开一桌，再把每个人的牌原样摆回去：新建连接、按 Steam ID 重新对号、恢复游戏状态。要么照这个思路自己写（秒级换主，D2），要么干脆绕开 Godot 的牌桌，自己管消息（无感换主，D3/D4）。</div>
<p>值得一提的是 2026 年 10 月出现的 <b>Understudy</b>，一个 Godot 热备换主库。作者在单机上测 8 人换主，切换中位数约 0.23 秒，几乎无缝。但它是 v0.1.0，零评价，没经过异地真实网络验证。作者自称代码由 Claude 在他指导下写成，这说明 Claude 加上强测试能做出这种东西，但前提是一个有经验的人在把关。</p>

<h2 id="c3">3. 四个开关，难度分别从哪来</h2>
<p>你的 24 格由四个开关组成。它们对难度的影响很不一样，从大到小依次是：<b>换主 &gt; 帧敏感 &gt; PVE/PVP &gt; 人数</b>。</p>

<h3>开关一：换主（影响最大）</h3>
<ul>
<li><b>不换主</b>：房主一走，全员体面地回大厅，本地成长数据已存好、不会丢。这个“体面回大厅”在每一格都必须做，是所有方案的地基。</li>
<li><b>秒级换主（D2）</b>：分四步，判定房主掉线 → 选新主 → 新主开房、其他人重连 → 恢复快照。时间按段算：
 <ul>
 <li>判定掉线：Steam 默认连接超时 10 秒，可以调到 3–5 秒；房主主动退出则接近 0 秒。</li>
 <li>开房和重连：官方说法是“几秒”。</li>
 <li>恢复快照：一篇论文的实测（Unity + Mirror + Steam）约 1.4 秒。</li>
 </ul>
 合计下来，我推算房主主动退出时停顿约 3–6 秒，崩溃时约 6–15 秒。</li>
<li><b>无感换主</b>：帧不敏感时可行。做法是人人都存一份完整状态，自己写心跳检测，事先排好继任顺序，切换 0.3–1 秒，玩家感觉不到。帧敏感就要上热备影子（D3），代价是把游戏逻辑改写成能整体存取的纯数据，放弃 Godot 的物理节点。</li>
</ul>
<p>为什么换主最难？因为它出错的方式最难看。骗子酒馆（Liar's Bar）2024 年 11 月加入换主后，一两个月里玩家持续反馈崩溃、白屏、规则错乱（左轮显示“22/6 发”）。GTFO、Warframe 的玩家也长期吐槽换主后丢装备、卡交互。<b>换主做得半成功，比干净地散局更招差评。</b>还有一点：拔网线时 Steam 要约 30 秒才转移大厅房主，所以绝不能靠它来判断房主掉线。</p>

<h3>开关二：帧敏感还是不敏感（最大的分水岭）</h3>
<p><b>帧不敏感（三国志式）</b>最省事：由房主权威，每秒同步 5–10 次，人人存一份完整状态，换主几乎白送。顺带澄清一个常见误会：这类游戏<b>不需要“确定性锁步”</b>。房主权威加指令同步要简单得多，我估计难度约 2 分，锁步要 4–5 分。</p>
<p><b>帧敏感 PVE（马里奥式手感）</b>有一个关键捷径。你说不在意开挂，那就可以让每个玩家自己算自己的移动，房主只管怪物和世界，再加插值让画面平滑。这样不用回滚，操作零延迟。致命公司、R.E.P.O.、雨中冒险 2 都是这一类。</p>
<p><b>帧敏感 PVP</b>最难，只有两条路：要么接受房主有延迟优势（Halo 3 时代 Bungie 自己也承认这种优势“显著”），要么上预测和回滚。后者是 Claude 最弱、调试最痛苦的领域。</p>

<h3>开关三：PVE 还是 PVP</h3>
<p>帧不敏感时，两者的技术差别其实不大，差在三件事：</p>
<ul>
<li><b>房主延迟优势</b>：只在 PVP 里构成问题。</li>
<li><b>怒退和掉线</b>：PVP 要提前定好结算规则（判负、不计分或作废本局）。</li>
<li><b>凑对手</b>：PVP 必须有人对打，冷启动更难。</li>
</ul>
<p>PVE 玩家对“房主走了就散”的容忍度高得多：致命公司、深岩银河、Peak 都是房主一走就结束，玩家基本能接受。</p>

<h3>开关四：4–6 人还是 7–12 人（影响最小，但会放大其他问题）</h3>
<ul>
<li><b>带宽</b>：星型连接下，房主上行带宽约按人数的平方增长。帧不敏感时，12 人也只要约 0.45 Mbps，不是问题。帧敏感时，如果不优化，12 人要约 5.3 Mbps，弱上行的房主会卡全场。</li>
<li><b>掉线</b>：假设每人每局掉线概率 3%，“至少一人掉线”的概率在 6 人局约 17%，12 人局约 31%。</li>
<li><b>凑人</b>：小众游戏凑齐 7–12 个同时在线的人，比技术还难。</li>
</ul>
<p>案例也印证了这一点：WEBFISHING 12 人满房普遍卡顿，致命公司扩人模组的作者建议不超过 8 人。7–12 人社交推理游戏的成功作（Among Us、鹅鸭杀）都用了自家服务器。</p>
<div class="chartbox"><h4>房主上行带宽估算：6 人 vs 12 人（Mbps）</h4><p class="muted">按“(人数−1) × 每秒快照数 × 每包大小”估算的 2D 典型值，非实测；悬停可看口径</p>{chart_bw}</div>

<h2 id="c4">4. Claude 能替你扛多少</h2>
<p><b>问题：</b>你懂语法、写得少，Claude 能把联机代码写对吗？<b>答案：简单架构写得很好，越往换主和回滚走越靠不住。</b></p>
<ul>
<li><b>写基础 GDScript 已经不是瓶颈。</b>在一个独立基准里（15 个 GDScript 任务，Godot 4.7.2），Claude Opus 5.5 和 Sonnet 5.5 都是 15 题全部一次做对。但这个基准不含联机任务，目前也没有任何针对 AI 写 Godot 联机代码的受控评测。</li>
<li><b>把握度跟着架构复杂度走，几乎不随人数变。</b>下图是各类任务的把握度分数，综合了实测反馈与开发者经验，属主观评分。</li>
</ul>
<div class="chartbox"><h4>Claude 在各类联机任务上的把握度（1–5）</h4><p class="muted">主观评分；悬停可看分值</p>{chart_claude}</div>
<p><b>典型错误：</b></p>
<ul>
<li><code>@rpc</code> 漏写 <code>any_peer</code> 或 <code>call_local</code>。</li>
<li>在 <code>_ready</code> 里设置 authority，时机不对。</li>
<li>两端节点路径不一致；中途加入时报 “Node not found”。</li>
<li>混用两套 SteamMultiplayerPeer 的接口。</li>
<li>把 64 位的 Steam ID 当成 peer_id 用。</li>
<li>不计带宽地高频同步一切。</li>
</ul>
<p><b>最根本的短板是：Claude 能写出来，但验不出来。</b>Steam 联机不能在一台机器上用两个账号测，时序类 bug 只能靠真机日志去抓。补位办法有四个：</p>
<ul>
<li><b>传输层做成可切换</b>：本机多开时走 ENet，正式上线走 Steam，开源示例 cooties 就是这个结构。这样 Claude 能在本机反复“写、测、修”。</li>
<li><b>定期真机测</b>：每隔一段时间，用两台电脑跑一次真正的 Steam 联机。</li>
<li><b>喂资料</b>：把 GodotSteam 的源码和文档直接提供给 Claude，并在项目的 CLAUDE.md 里列出禁用的 Godot 3 写法。</li>
<li><b>库的 bug 自己报</b>：GodotSteam 维护者禁止用 AI 写的 issue 和 PR，Godot 在 2026 年 7 月也收紧了 AI 贡献政策。遇到库 bug，要用自己的话写报告。</li>
</ul>
<p>对你来说，必须自己扛的是三件事：<b>看懂联机日志、做真机联调、拍板架构</b>。逐行写代码可以交给 Claude。</p>

<h2 id="c6">5. 上线以后：哪些格子做完就不太用管</h2>
<p><b>问题：</b>零服务器方案上线后，会不会天天维护？<b>答案：头几周到几个月一定会修，之后会安静下来，因为根本没有服务器会“宕机”。</b></p>
<p>三款 Godot 零服务器联机游戏的官方补丁记录，说明了问题出在哪：</p>
<ul>
<li><b>WEBFISHING</b>：连续修大厅搜索、房间码、旧版本混入、不同步，后来又加了踢人、封禁、拉黑。</li>
<li><b>Buckshot Roulette</b>：修了玩家在抓道具、装填时掉线导致的卡死。</li>
<li><b>Dome Keeper</b>：联机不开公共大厅，只用加入码和好友邀请。2026 年的补丁大多是重连后状态异常。</li>
</ul>
<p>共同点是：<b>问题全出在自家代码和 Steam 配置上，都是可修的；没有一款因为“服务器”出事而停服。</b>按组合看上线后的稳定性，我的判断是：</p>
<ul>
<li>PVE、帧不敏感、不换主，加上强制走中继和版本过滤：约 <b>4/5</b>。</li>
<li>帧敏感，或 7–12 人：约 3/5。</li>
<li>加了秒级换主：初期 2.5–3/5，打磨后 3.5/5。</li>
<li>无感换主，或帧敏感 PVP：约 2/5。</li>
</ul>
<div class="callout"><b>低维护清单（全部是 Claude 擅长的确定性代码）：</b>
<ul>
<li>强制走 SDR；大厅搜索设为 Worldwide；版本号写进大厅并做过滤；清理“幽灵大厅”。</li>
<li>自己写心跳和超时，房主掉线时全员回大厅并提示原因。</li>
<li>做日志一键上传。</li>
<li>锁定 Godot 和 GodotSteam 的版本。</li>
<li>保证游戏单人也完整可玩。</li>
<li>用 Steam 远程同乐（Remote Play Together）兜底：最多 4 人，只需房主拥有游戏，一行网络代码都不用写。</li>
</ul></div>
<p><b>商业现实也要心里有数</b>（第三方估算，口径不一）：</p>
<ul>
<li>2025 年 Steam 新游戏里，只有约 8% 毛收入超过 10 万美元，约三分之二不到 1000 美元。</li>
<li>合作游戏只占发行量的 5–6%，却占销量的 36–46%。这是供给少、需求大的品类，对你有利。</li>
<li>多人游戏的在线人数最终会稳定在首发峰值的约 6%。所以房间列表要做成“有房就显示”，把好友邀请和房间码作为主入口，不要指望公共匹配。</li>
</ul>

<h2 id="c7">6. 我的建议：一条低风险的升级路线</h2>
<p>我判断你“终局胜率”最高的走法，是<b>先落在第 1 格，同时按“以后能换主”的规矩写代码，再一格一格往上升</b>：</p>
<ol class="route">
<li><b>先做单人能玩的核心玩法</b>。这是冷启动和联机故障的双重保险。</li>
<li><b>上第 1 格</b>（PVE × 帧不敏感 × 不换主 × 4–6 人），网络部分约 {w1}，包括：
 <ul><li>大厅和房间列表（Worldwide 过滤、版本号过滤）、好友邀请。</li>
 <li>强制走 SDR。</li>
 <li>房主权威同步。</li>
 <li>体面回大厅，成长数据存本地并同步 Steam Cloud。</li></ul></li>
<li><b>从第一天起守三条纪律</b>：
 <ul><li>所有游戏状态都能序列化。</li>
 <li>实体用稳定 ID。</li>
 <li>不把状态藏在物理节点和动画里。</li></ul>
 守住这三条，以后加换主不用推倒重来；后期改造的成本大约会翻倍。</li>
<li><b>补“优雅交接”</b>：房主主动退出时，先把最终快照发出去、把大厅房主转给继任者，再离开。约 1 周，能覆盖大多数主动离开的情况。</li>
<li><b>看玩家反馈，再决定要不要做崩溃迁移</b>，也就是第 3 格的完整 D2。</li>
<li><b>如果玩法离不开手感</b>，就走第 7 格：每人自己算移动、房主管世界。人数从 4 起步，验证后再扩到 8。</li>
<li><b>如果一定要做 PVP</b>，选第 15 格：帧不敏感、回合边界换主，走骗子酒馆的路线。定位成好友派对，不做竞技排位。</li>
</ol>

<div class="card"><h3 style="margin-top:0">一页总结</h3><ul>
<li>Steam 加 GodotSteam 足够做零服务器联机，房间列表自带。要强制走中继、大厅搜索设 Worldwide、做版本过滤。</li>
<li>难度主要来自换主和帧敏感，人数的影响最小。帧不敏感时，连无感换主都是可以讨论的。</li>
<li>Claude 擅长大厅、同步、回大厅，把握度约 4/5；换主、回滚、时序调试是它的短板，约 1–2/5。你要负责真机联调和架构拍板。</li>
<li>首作落点是第 1 格，次选是第 7、13、15 格。所有帧敏感 PVP 的 7–12 人格、所有帧敏感的无感换主格，都不建议。</li>
</ul></div>
<p><b>接下来值得盯的信号：</b></p>
<ul>
<li>GodotSteam 新版本的接口变动。</li>
<li>Understudy 是否出现跨网实测和真实用户。</li>
<li>Photon Fusion 的 Godot 版是否转正式版（目前是预览版，官方不建议生产使用）。</li>
<li>Godot 换主提案 #7912 有没有进展。</li>
<li>你自己 Playtest 的三项数据：房主掉线率、跨区连接失败率、等房时长。</li>
</ul>

<div class="callout"><b>阅读说明：</b>
<ul>
<li>胜率、工期、把握度都是基于证据的主观判断。</li>
<li>带宽是公式估算，换主总停顿是分段推算，都不是实测。</li>
<li>销量和收入数据来自第三方估算，口径不一。</li>
<li>中国大陆的 SDR 节点能否用于第三方游戏，尚未证实。</li>
<li>帧敏感 PVP 小游戏（Stick Fight、Duck Game 等）几乎没有公开的一手网络资料，相关格子置信度较低。</li>
</ul>
完整来源与各方向明细保存在调研中间文件（results/*.json）里。</div>

<div class="card meta"><h3 style="margin-top:0">制作信息</h3><dl>
<dt>起始问题</dt><dd>个人开发者首款 Steam 联机 2D 游戏，用 Godot 加 Claude 编程，尽量只用 Steam 自带联机、不租服务器。按 PVE/PVP × 帧敏感/不敏感 × 不换主/秒级/无感换主 × 4–6/7–12 人共 24 种情况，评估可选方式、利弊、难度、技术要求、Claude 把握度与上线后稳定性。补充约束：不在意开挂、成长数据存本地、需要房间列表、玩家遍布全球。</dd>
<dt>主模型</dt><dd>Claude Opus 5.5（claude-opus-5-5，从会话中查询所得）</dd>
<dt>使用的 skill</dt><dd><code>research</code> → <code>research-deep</code> → <code>research-report</code>。子 agent 包括：
 <ul><li>补充框架：1 个 <code>web-search-agent</code>（Sonnet）。</li>
 <li>深度调研：5 组 <code>web-search-agent-deep</code>（Opus，effort high），5 组 <code>web-search-agent</code>（Sonnet，effort medium）。</li>
 <li>每批结束后唤醒原 agent 定向补深 7 次。</li></ul></dd>
<dt>执行模式</dt><dd>标准（甜点区）· 19 个调研方向 · 10 个子 agent · 最大并行 3</dd>
<dt>制作时间</dt><dd>{start_utc} — {end_utc} UTC（北京时间 {start_cst} — {end_cst}），跨度约 {hrs} 小时（其中调研与补深约 45 分钟完成，其余为会话中断等待）</dd>
</dl></div>

<h2 id="refs">核心参考网页</h2>
<p class="muted">精选的高价值网页，以官方文档、源码、官方公告等一手来源为主；不是全量来源列表。</p>
{refs}
"""

def main():
    body = BODY.format(title=E(TITLE), sub=E(SUBTITLE), top=counts["top"], ok=counts["ok"], meh=counts["meh"], no=counts["no"],
                       chart_bw=chart_bw(), chart_claude=chart_claude(), grid=grid(), refs=refs(), hrs=round(mins / 60, 1), w1=CELLS[0]["weeks"],
                       start_utc=fmt(START), end_utc=fmt(END), start_cst=fmt(START.astimezone(CST)), end_cst=fmt(END.astimezone(CST)))
    doc = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{E(TITLE)}</title><style>{CSS}</style></head><body><div class="wrap">{body}</div><div id="tip" role="tooltip"></div>'
           f'<script>{JS.replace("__MAP__", json.dumps({"|".join([c["mode"], c["lat"], str(c["mig"]), str(c["n"])]): c["id"] for c in CELLS}, ensure_ascii=False))}</script></body></html>')
    slug = re.sub(r'[\\/:*?"<>|]+', '', TITLE).replace('：', '-').replace(' + ', '+').replace(' ', '')
    out = HERE / f"{slug}.html"
    out.write_text(doc, encoding="utf-8")
    print(out)

main()

MCSS = """
body{font-size:16px}.wrap{max-width:640px;padding:14px 14px 48px}
#picker,#detail{width:auto!important;margin-left:0!important}
.picker{padding:10px}.xrow{grid-template-columns:1fr!important}.xcell{border-right:0!important;border-bottom:1px solid var(--line)}
.xbtn{grid-column:auto!important}.xbtn .xhead{display:none}.xbtn #confirm{padding:14px;font-size:17px;border-radius:0}
.xcell select{font-size:16px;padding:12px 34px 12px 12px}
.kv{grid-template-columns:1fr 1fr}.kv>.m:last-child{grid-column:1/-1}
.ov{grid-template-columns:1fr}.bk{grid-template-columns:88px minmax(0,1fr) 52px;grid-template-areas:"n b w" "t t t"}
.detail{padding:12px 10px}.ovc{padding:12px 12px}.kv>.m{padding:8px 10px}.mhead{display:flex;justify-content:space-between;align-items:center;gap:8px}.mhead h1{font-size:20px;margin:4px 0}
.mfoot{margin-top:20px;font-size:13px;color:var(--muted);text-align:center}
"""

MJS = r"""
(function(){
var root=document.documentElement,btn=document.getElementById('theme');
function cur(){return root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')}
function lab(){btn.textContent=cur()==='dark'?'☀ 白天':'☾ 深色'}
try{var s=localStorage.getItem('theme');if(s)root.setAttribute('data-theme',s)}catch(e){}
lab();btn.onclick=function(){var n=cur()==='dark'?'light':'dark';root.setAttribute('data-theme',n);try{localStorage.setItem('theme',n)}catch(e){};lab()};
var det=document.getElementById('detail'),form=document.getElementById('picker'),ok=document.getElementById('confirm'),hint=document.getElementById('pickhint');
var MAP=__MAP__,KEYS=['mode','lat','mig','n'],NAMES={mode:'对战模式',lat:'延迟需求',mig:'房主离开时',n:'每局人数'};
function sel(){var r={};KEYS.forEach(function(k){var e=form.querySelector('select[name="'+k+'"]');if(e&&e.value!=='')r[k]=e.value});return r}
function upd(){var s=sel(),miss=KEYS.filter(function(k){return !(k in s)});ok.disabled=miss.length>0;
 hint.textContent=miss.length?('还需选择：'+miss.map(function(k){return NAMES[k]}).join('、')):'已选好，点确认查看';
 form.querySelectorAll('select').forEach(function(s){s.classList.toggle('set',s.value!=='')});}
form.addEventListener('change',upd);
function show(id){det.innerHTML='';det.appendChild(document.getElementById('t'+id).content.cloneNode(true));}
ok.onclick=function(){var s=sel();show(MAP[[s.mode,s.lat,s.mig,s.n].join('|')])};
var INV={};Object.keys(MAP).forEach(function(k){INV[MAP[k]]=k.split('|')});
var c=INV[1];KEYS.forEach(function(k,i){var e=form.querySelector('select[name="'+k+'"]');if(e)e.value=c[i]});upd();show(1);
hint.textContent='默认展示首推组合 #1，改选条件后点确认即可';
})();
"""

def main_mobile():
    g = grid()
    picker = g[g.index('<form id="picker"'):g.index('</form>') + len('</form>')]
    tpls = "".join(
        f'<template id="t{c["id"]}"><div class="dhead"><span class="cid">#{c["id"]}</span>'
        f'<b>{c["mode"]} × {c["lat"]} × {MIG[c["mig"]]} × {NUM[c["n"]]}</b>{badge(c["level"])}</div>'
        f'<p class="dnote">{E(c["note"])}</p>' + metrics(c) + overview_html(c) + '</template>'
        for c in CELLS)
    mtitle = "24 种情况速览（手机版）"
    body = (f'<header class="mhead"><div><p class="muted" style="margin:0">Godot + Claude 做 Steam 联机 2D 游戏</p><h1>{mtitle}</h1></div>'
            f'<button id="theme" type="button">☾ 深色</button></header>'
            '<p class="muted">四个条件各选一项，点“确认”看这一格的速览：难不难、难在哪、要注意什么。</p>'
            + picker + '<div id="detail" class="detail" aria-live="polite"></div>' + tpls
            + '<p class="mfoot">技术细节（网络实现方案、模块工期、编码与维护难点等）见电脑版完整报告。</p>')
    mp = json.dumps({"|".join([c["mode"], c["lat"], str(c["mig"]), str(c["n"])]): c["id"] for c in CELLS}, ensure_ascii=False)
    doc = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f'<title>{mtitle}</title><style>{CSS}{MCSS}</style></head><body><div class="wrap">{body}</div>'
           f'<script>{MJS.replace("__MAP__", mp)}</script></body></html>')
    out = HERE / "24种情况速览-手机版.html"
    out.write_text(doc, encoding="utf-8")
    print(out)

main_mobile()
