# -*- coding: utf-8 -*-
"""每格“速览”：展示型、白话、几分钟看懂难易与要点。（可再生物，不入库）"""
import html
E = html.escape

def _k(c):
    return c["mode"], c["lat"], c["mig"], c["n"]

def _split(s):
    return [x.strip() for x in s.split("；") if len(x.strip()) >= 8]

# ---------- 1. 这格是什么样的游戏 ----------
def game_picture(c):
    m, l, g, n = _k(c)
    kind = {("PVE", "帧不敏感"): "大家一起打电脑的策略/回合/卡牌/塔防类：比如几个人合力守城、一起打牌闯关。节奏慢，比的是脑子不是手速。",
            ("PVE", "帧敏感"): "大家一起打电脑的实时动作类：比如一起搬东西逃生、一起打怪的横版动作（致命公司、R.E.P.O. 那种感觉）。操作要跟手。",
            ("PVP", "帧不敏感"): "玩家互相较劲的回合/心理战/派对类：比如骗子酒馆、狼人杀、卡牌对战。拼的是策略和演技，不拼反应。",
            ("PVP", "帧敏感"): "玩家互相对打的实时动作类：比如派对乱斗、平台对战（Stick Fight 那种）。差几十毫秒就能决定输赢。"}[(m, l)]
    size = "一局 4–6 人，一个小队的规模。" if n == 0 else "一局 7–12 人，一大桌人，更像热闹的派对。"
    leave = ["房主一走，这局就结束，大家回大厅（进度不丢）。",
             "房主一走，画面停几秒，换一个人当房主，接着玩。",
             "房主一走，几乎察觉不到，自动换人继续。"][g]
    return kind, size, leave

# ---------- 2. 推荐怎么做（比喻 + 一句技术） ----------
def analogy(c):
    m, l, g, n = _k(c)
    if l == "帧不敏感":
        a = "像网上下棋：只有房主手里那盘是“正式棋盘”。大家把要走的棋告诉房主，房主落子后通知所有人；每人手里还有一份棋盘抄本，随时能对上。"
    elif m == "PVE":
        a = "像几个人一起搬家：每个人管好自己的脚步（自己算自己的移动，所以操作不卡），家具放哪、怪物怎么动，由房主一个人统一指挥。"
    else:
        a = "像街头篮球自己吹哨：谁出手谁说进没进（射手优先），房主只看看离不离谱。因为你不在意作弊，这样最简单，也最不容易让人觉得“我明明躲开了”。"
    b = ["", "房主离开时，就像打牌时庄家临时离席：大家先停手，指定下一位当庄家，把桌面照原样摆好再接着打。",
         ("房主离开时，就像接力赛里早就站好位置的替补：每个人都有一份完整记录，庄家一不出声，排第一的替补立刻接手。" if l == "帧不敏感"
          else "房主离开时，就像飞机上的副驾驶：副驾驶一直跟着同步在飞，机长一倒下他马上接手。")][g]
    s = "" if n == 0 else "人多以后，房主就像同时给 11 个人打电话，上传更吃紧，也更容易有人掉线。"
    return "".join(x for x in (a, b, s) if x)

# ---------- 3. 玩家会感受到什么 ----------
def player_feel(c):
    m, l, g, n = _k(c)
    out = []
    if l == "帧不敏感":
        out.append(("操作手感", "延迟 100–200ms 也基本感觉不到，全球玩家一起玩都没问题。"))
    elif m == "PVE":
        out.append(("操作手感", "自己的角色零延迟、很跟手；看队友和怪物会有约 0.1 秒的延后，但画面是平滑的。"))
    else:
        out.append(("操作手感", "自己操作跟手，但房主有天然的 0 延迟优势；跨洲对打时“我明明打中了”的争议会比较多。"))
    out.append(("房主离开时", ["弹出“房主已离开”，回到大厅；这局的经验奖励已经存好，想继续就重新开一局。",
                              "画面冻结，显示“正在更换房主…”。房主主动退出约 3–6 秒，掉线约 6–15 秒，然后倒计时继续。"
                              + ("可能回退到 1–5 秒前的状态。" if l == "帧敏感" else "回合制几乎不回档。"),
                              ("最多一下 0.3–1 秒的停顿，大多数玩家察觉不到。" if l == "帧不敏感"
                               else "一眨眼的停顿（作者实测约 0.2 秒），前提是热备库在真实网络下够稳定。")][g]))
    out.append(("进房方式", "房间列表里能看到全球等待中的房间，也能输房间码或直接接受 Steam 好友邀请。"))
    if n == 1:
        out.append(("人多的代价", "人越多越容易有人掉线：12 人局每局“至少有一人掉线”的概率约 31%（6 人约 17%）。" + ("" if l == "帧不敏感" else "房主网络差时全场都会卡。")))
    return out

# ---------- 4. 难度拆解 ----------
def breakdown(c):
    m, l, g, n = _k(c)
    rows = [("大厅与房间列表", 1.5, "Steam 自带房间列表、邀请和房间码，Claude 很熟，约 1 周搞定。")]
    rows.append(("同步", 1.5, "只传“指令”和结果，像传纸条，最简单。") if l == "帧不敏感" else
                ("同步", 3, "要让别人的角色平滑移动、处理“两人抢同一个东西”，需要你亲自调手感。") if m == "PVE" else
                ("同步", 4, "对打要判定谁打中谁，还有房主延迟优势，最考验手感和规则设计。"))
    leave = {0: (1.5, "只要做到体面散场、进度不丢，很简单。"),
             1: (3, "要自己写“选新房主、重连、恢复状态”。好在人人都有完整副本，搬起来不难。") if l == "帧不敏感" else
                (4, "实时状态要定期存快照，迁移时会回退几秒；GTFO、Warframe 这类大作也常在这里翻车。"),
             2: (4, "要绕开 Godot 自带的联机框架自己管消息，还要处理“两个人同时当房主”这类怪问题。") if l == "帧不敏感" else
                (5, "要把整个游戏逻辑改写成纯数据并接热备库，是最难的一类工程。")}[g]
    rows.append(("房主离开", leave[0], leave[1]))
    rows.append(("人数", 1.5, "小队规模，带宽和掉线压力都小。") if n == 0 else
                ("人数", 2.5, "带宽不是问题，难在凑人和掉线概率翻倍。") if l == "帧不敏感" else
                ("人数", 3.5, "房主上传压力约按人数平方增长，必须做带宽优化，建议先上 8 人。"))
    rows.append(("对抗与凑人", 1.5, "合作玩家很宽容，也不用凑对手。") if m == "PVE" else
                ("对抗与凑人", 3, "要凑齐对手、提前定好怒退和掉线怎么算。") if l == "帧不敏感" else
                ("对抗与凑人", 4, "要凑对手、按地区组房，还要处理命中争议。"))
    t = 2 + (1 if g else 0) + (1 if g == 2 and l == "帧敏感" else 0) + (0.5 if l == "帧敏感" else 0) + 0.5 * n
    t = min(t, 5)
    txt = "要两台电脑真机测试，上线头几周一定会修网络 bug。"
    if g:
        txt += "换主还要反复做“随机杀掉房主”的故障测试，以后每加新内容都要重测。"
    rows.append(("测试与上线维护", t, txt))
    return rows

def _tone(v):
    return ("good", "轻松") if v <= 2.5 else ("warn", "有挑战") if v <= 3.5 else ("bad", "很难")

# ---------- 5. 好处 / 坑 ----------
def pros_list(c):
    m, l, g, n = _k(c)
    out = ["不用租服务器，每月成本 0 元；上线后也不会因为“服务器出事”而停服。"]
    out.append("网络要求很低：普通家用宽带绰绰有余，全球玩家一起玩也基本没延迟问题。" if l == "帧不敏感" else
               "手感好：每个人自己的操作零延迟，不需要最难的“回滚”技术。" if m == "PVE" else
               "代码路线清楚：房主型 + 射手优先判定，Claude 写得出来。")
    out.append(["最省事：房主离开只要体面散场，这正是 Claude 最拿手的代码。",
                "房主走了不散局，玩家体验比“直接散场”好很多。",
                "体验最好：玩家几乎察觉不到换了房主。"][g])
    out.append("最容易凑满房，同类游戏的先例也最多。" if n == 0 else "人多热闹，适合派对、社交类玩法。")
    out += _split(c["pros"])
    return _dedupe(out)

def cons_list(c):
    m, l, g, n = _k(c)
    out = ["只有 Steam 玩家能联机；上线头几周到几个月一定要修网络 bug（同类 Godot 游戏都经历过）。"]
    out.append(["房主一掉线整局就结束，所以单局最好控制在 15–30 分钟以内。",
                "要从第一天起按“可存档”的方式写代码；做得半成功的换主（回档、丢东西、卡住）比直接散场更招骂。",
                "要绕开 Godot 自带的联机框架自己管消息，属于最难调的分布式问题，Claude 很难一次写对。"][g])
    if l == "帧敏感":
        out.append("手感和带宽都要调；房主网络差会卡全场，要引导网最好的人当房主。")
    if m == "PVP":
        out.append("必须凑齐对手，小众游戏的冷启动最难；还要提前定好怒退规则。" if l == "帧不敏感" else
                   "房主有天然的延迟优势，命中判定容易起争议；还要凑齐对手、按地区组房。")
    if n == 1:
        out.append("凑满 7–12 个同时在线的人很难；人多也更容易有人掉线（每局约 31%）。")
    out += _split(c["cons"])
    return _dedupe(out)

def _dedupe(xs):
    seen, out = set(), []
    for x in xs:
        key = x[:14]
        if key in seen:
            continue
        seen.add(key); out.append(x)
    return out

# ---------- 6. Claude vs 你 ----------
def claude_vs_you(c):
    m, l, g, n = _k(c)
    cl = ["Steam 大厅、房间列表、邀请、房间码这些“标准件”。",
          "房主说了算的基础同步和 RPC 调用。",
          "房主离开时体面回大厅、写本地存档。"]
    if l == "帧敏感":
        cl.append("插值、客户端自己算移动这类常见写法（手感要你来调）。")
    if g == 1:
        cl.append("快照存取、换主流程的骨架代码（对不对要你真机验证）。")
    if g == 2:
        cl.append("心跳、投票这些单个模块；但整体在各种掉线组合下是否可靠，它很难保证。")
    you = ["定下“每样东西由谁说了算”，写成文档让 Claude 照着写。",
           "用两台电脑做真机测试，学会看联机日志找问题。",
           "锁定 Godot 和 GodotSteam 的版本，把对应版本的文档喂给 Claude。"]
    if l == "帧敏感":
        you.append("亲自试玩调手感：插值多长、延迟多少能接受。")
    if g:
        you.append("反复做故障测试，判断换主到底可不可靠，敢不敢上线。")
    if m == "PVP":
        you.append("定规则：怒退、掉线、命中判定怎么算，并在游戏里讲清楚。")
    if n == 1:
        you.append("找人做 7–12 人的大人数测试（凑不齐可用无界面客户端模拟）。")
    return cl, you

# ---------- 7. 必做清单 ----------
def must_do(c):
    m, l, g, n = _k(c)
    out = ["强制走 Steam 中继，大厅搜索设为“全球”，用版本号过滤房间。",
           "房主一走就体面回大厅，经验奖励提前存好。"]
    if g:
        out.append("从第一天起：所有状态都能存档、每个物体有固定编号、不把状态藏在物理和动画里。")
    if g == 1:
        out.append("先只做“房主主动退出时交接”（约 1 周，覆盖大多数情况），崩溃迁移之后再补。")
    if g == 2:
        out.append("先做好秒级换主当兜底，再上无感换主。")
    if l == "帧敏感":
        out.append("大厅显示 ping，引导网络最好的人当房主。")
    if m == "PVP":
        out.append("开局前写清楚怒退和掉线怎么算。")
    if n == 1:
        out.append("先把人数上限定在 8 人，稳定后再开到 12。")
    out.append("游戏单人也要完整可玩，联机出问题时还有退路。")
    return out

# ---------- 8. 退路 ----------
def fallback(c):
    m, l, g, n = _k(c)
    chain = []
    if g == 2:
        chain.append("无感换主做不稳 → 改成秒级换主（停几秒并提示）")
    if g >= 1:
        chain.append("秒级换主也不稳 → 改成“房主走就体面散场”")
    if n == 1:
        chain.append("人多卡顿 → 上限降到 8 人")
    if l == "帧敏感" and m == "PVP":
        chain.append("对打争议太多 → 改成帧不敏感玩法，或改为合作 PVE")
    chain.append("联机整体不顺 → 先保证单人可玩，用 Steam 远程同乐（最多 4 人、只需房主有游戏）兜底")
    return c["alt"], chain

# ---------- 9. 如果我是你 ----------
LV_RANK = {"top": 0, "ok": 1, "meh": 2, "no": 3}

def advice(c, cells, mig_names, num_names, level_names):
    lvl = c["level"]
    base = {"top": "放心做。这是首款游戏最稳的落点，照着必做清单走就行。",
            "ok": "可以做。难点集中在上面标红、标黄的几项，照着必做清单走，问题不大。",
            "meh": "能做，但会比较吃力。更稳的走法是先做一个更简单的相邻格子，上线跑稳了再升级到这一格。",
            "no": "不建议用第一款游戏碰这一格。如果玩法允许，建议改成下面这个更好做的组合。"}[lvl]
    alt_txt = ""
    if lvl in ("meh", "no"):
        m, l, g, n = _k(c)
        cands = [x for x in cells if sum([x["mode"] != m, x["lat"] != l, x["mig"] != g, x["n"] != n]) == 1]
        best = min(cands, key=lambda x: (LV_RANK[x["level"]], x["diff"]))
        fmt = lambda x: (f'#{x["id"]}（{x["mode"]} × {x["lat"]} × {mig_names[x["mig"]]} × {num_names[x["n"]]}，'
                         f'结论“{level_names[x["level"]]}”，难度 {x["diff"]:g}/5、胜率 {x["win"]}）')
        if LV_RANK[best["level"]] < LV_RANK[lvl]:
            alt_txt = f'只改一个条件的话，推荐 {fmt(best)}。'
        if LV_RANK[best["level"]] >= 2:
            dist = lambda x: sum([x["mode"] != m, x["lat"] != l, x["mig"] != g, x["n"] != n])
            good = min((x for x in cells if LV_RANK[x["level"]] <= 1), key=lambda x: (dist(x), x["diff"]))
            alt_txt += f'想要稳妥的话，离这格最近的“可行”组合是 {fmt(good)}，要改 {dist(good)} 个条件。'

    return base, alt_txt, c["note"]

# ---------- 渲染 ----------
def stars(v):
    k = max(1, min(5, round(v)))
    return "★" * k + "☆" * (5 - k)

def render(c, cells, mig_names, num_names, level_names, badge):
    kind, size, leave = game_picture(c)
    tone_all = _tone(c["diff"])
    h = []
    h.append('<div class="ov">')
    # hero
    h.append(f'<div class="ovc hero"><div class="ovh">🎮 这格是什么样的游戏</div><p>{E(kind)}</p><p>{E(size)}{E(leave)}</p>'
             f'<div class="diffline t-{tone_all[0]}"><span class="st">{stars(c["diff"])}</span><b>整体难度 {c["diff"]:g}/5 · {tone_all[1]}</b>'
             f'<span class="muted">（终局胜率约 {E(c["win"])}，网络部分约 {E(c["weeks"])}）</span></div></div>')
    # 推荐怎么做 + 玩家体感
    h.append(f'<div class="ovc"><div class="ovh">🛠 推荐怎么做</div><p class="analogy">{E(analogy(c))}</p>'
             f'<p class="tech"><b>技术上一句话：</b>{E(c["method"])}</p></div>')
    h.append('<div class="ovc"><div class="ovh">👀 玩家会感受到什么</div><dl class="feel">'
             + "".join(f'<dt>{E(k)}</dt><dd>{E(v)}</dd>' for k, v in player_feel(c)) + '</dl></div>')
    # 难度拆解
    rows = breakdown(c)
    bars = []
    for name, v, txt in rows:
        tn, word = _tone(v)
        bars.append(f'<div class="bk"><div class="bkn">{E(name)}</div><div class="bkbar"><i class="t-{tn}" style="width:{v/5*100:.0f}%"></i></div>'
                    f'<div class="bkw t-{tn}">{word}</div><div class="bkt">{E(txt)}</div></div>')
    h.append('<div class="ovc wide"><div class="ovh">📊 难度拆解：难在哪、不难在哪</div>' + "".join(bars) + '</div>')
    # 好处 / 坑
    h.append('<div class="ovc pros"><div class="ovh">👍 好处</div><ul>' + "".join(f'<li>{E(x)}</li>' for x in pros_list(c)) + '</ul></div>')
    h.append('<div class="ovc cons"><div class="ovh">⚠️ 坑和代价</div><ul>' + "".join(f'<li>{E(x)}</li>' for x in cons_list(c)) + '</ul></div>')
    # Claude vs 你
    cl, you = claude_vs_you(c)
    h.append(f'<div class="ovc"><div class="ovh">🤖 Claude 能帮你写的（把握度 {c["claude"]:g}/5）</div><ul>' + "".join(f'<li>{E(x)}</li>' for x in cl) + '</ul></div>')
    h.append('<div class="ovc"><div class="ovh">🙋 你自己要扛的</div><ul>' + "".join(f'<li>{E(x)}</li>' for x in you) + '</ul></div>')
    # 必做 + 退路
    h.append('<div class="ovc"><div class="ovh">✅ 必做清单</div><ul class="chk">' + "".join(f'<li>{E(x)}</li>' for x in must_do(c)) + '</ul></div>')
    alt, chain = fallback(c)
    h.append(f'<div class="ovc"><div class="ovh">🪂 退路</div><p><b>备选方案：</b>{E(alt)}</p><ol class="fb">'
             + "".join(f'<li>{E(x)}</li>' for x in chain) + '</ol></div>')
    # 建议
    base, alt_txt, note = advice(c, cells, mig_names, num_names, level_names)
    h.append(f'<div class="ovc wide adv"><div class="ovh">💡 如果我是你</div><p><b>{E(base)}</b> {E(alt_txt)}</p><p class="muted">一句话结论：{E(note)}</p></div>')
    h.append('</div>')
    return "".join(h)
