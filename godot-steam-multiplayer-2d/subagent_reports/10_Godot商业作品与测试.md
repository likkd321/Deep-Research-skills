# 10_Godot商业作品与测试

- agent 类型：`web-search-agent`
- 模型：Sonnet
- 负责的 item：Godot_Steam_Commercial_Titles, Netcode_Testing_And_Reference_Impl
- agent id：`a55f6e15a4b72430c`

## 首轮调研（2026-11-23 16:57 UTC）

### 派发的任务

````text
## 任务
依次调研以下2个item，每个item输出一个结构化JSON。每完成一个item就立即写出它的JSON并运行验证，再开始下一个（中途中断时已完成的item不会丢失）。

### Item 1
调研 name: Godot_Steam_Commercial_Titles
category: 业界案例
description: 案例：用 Godot 做 Steam 联机的商业作品——Webfishing、Buckshot Roulette 多人版、Cassette Beasts、Brotato 联机、Halls of Torment 等，以及 2025-2026 新作复盘（如 80.lv Godot 4.6 C# 联机团队复盘）：网络架构、用的插件、口碑与踩坑。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Steam_Commercial_Titles.json

### Item 2
调研 name: Netcode_Testing_And_Reference_Impl
category: 开发工作流
description: 联机测试调试与开源参考实现：Godot 本地多实例调试、延迟/丢包模拟（Clumsy、tc netem）、Steam 双账号测试、desync/状态日志；可供 Claude 参考的开源 Godot+Steam 范例与模板（expressobits 示例、cooties 等）；如何让 Claude 形成"写-测-修"闭环弥补无法真机联调的短板。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Netcode_Testing_And_Reference_Impl.json

## 字段定义
读取 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Steam_Commercial_Titles.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Netcode_Testing_And_Reference_Impl.json

## 验证
每个JSON写出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml -j {output_path_i}
全部item验证通过后才算完成任务。
````

### 工具调用（13 次）

- `Read` /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml
- `Bash` ls ~/.claude/agents/web-search-modules/ ~/.claude/skills/research/ 2>&1; ls /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results 2>&1
- `ToolSearch` select:WebSearch,WebFetch
- `Bash` cd ~/.claude/agents/web-search-modules/; head -c 2500 general-web.md; echo ----; head -c 2000 github-debug.md; python3 -c "import json;d=json.load(open('/home/u…
- `WebSearch` Godot Steam multiplayer commercial game Webfishing netcode GodotSteam postmortem
- `WebSearch` 80.lv Godot 4.6 C# multiplayer Steam game postmortem
- `WebFetch` https://80.lv/articles/indie-team-breaks-down-shipping-multiplayer-game-with-godot-4-6-using-c
- `WebSearch` Buckshot Roulette multiplayer Godot Steam Cassette Beasts Brotato co-op Godot netcode
- `WebSearch` Godot clumsy tc netem multiple instances debug multiplayer; godot steam multiplayer template expressobits cooties github
- `WebSearch` WEBFISHING Godot GodotSteam P2P lobby lamedeveloper Lamedeveloper interview networking
- `WebSearch` Godot 4 "Debug" "Run Multiple Instances" multiplayer test; simulate latency packet loss Clumsy Godot ENet
- `WebSearch` Steam co-op Godot Halls of Torment Brotato online co-op Godot netcode Steam Remote Play Together
- `Bash` mkdir -p /tmp/x; cat > /tmp/claude-0/gen.py <<'EOF' import json R='/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/' U='[不确定]' a={ "name":"Go…

### 交回的报告

两个 item 的 JSON 都已写出，验证脚本显示字段覆盖率 100%（35/35）。

文件路径：
- /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Steam_Commercial_Titles.json
- /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Netcode_Testing_And_Reference_Impl.json

**本次检索的局限（很重要）：**
- 检索深度偏浅，只做了少量 WebSearch 和 1 次 WebFetch。
- Webfishing、Buckshot Roulette 多人版、Cassette Beasts、Brotato、Halls of Torment 的网络架构和人数都没有一手来源。这些条目多数来自我的记忆，或来自 GamingOnLinux 一类二手报道，JSON 里已标"[不确定]"。
- Halls of Torment 没有联机证据，Brotato 是否有在线联机未确认，JSON 里都已说明。
- 80.lv 那篇 Godot 4.6 + C# 复盘讲的游戏是 **Pratfall**（Quad Head，4 人团队，约 6 个月）。该文已抓取到可用的一手信息：
  - 技术栈：Godot 4.6.1 + C#，用 Facepunch.Steamworks 接入 Steam。
  - 网络：开发期自建在 Epic Online Services 上，终版改为 SteamNetworkingSockets，另有自研近距语音。
  - 踩坑：编辑器频繁崩溃、C# GC 问题、Windows Smart App Control 拦截未签名游戏（需付费代码签名）。
  - 文中没有人数、换主、销量和评价的信息。
- Item 2 里，Clumsy 和 netfox NetworkSimulator 有来源支持。netem、cooties 和 Steam Sockets 对本地模拟工具的兼容性，检索没有找到资料，已标"[不确定]"。
- 主要来源：80.lv Pratfall 复盘、Godot 论坛 86334 帖、netfox 文档、expressobits/steam-multiplayer-peer、Malcolm-Q 的 SteamGodotTemplate、Tumblefire 的 devlog。

如需补强，可以让一个 agent 单独去查 Webfishing 和 Buckshot Roulette 的网络实现一手资料。

## 第 1 次补深（2026-11-23 16:59 UTC）

### 派发的任务

````text
The coordinator sent a message while you were working:
定向补深（只改存疑字段，不要重跑）。其他 item 已找到的一手线索，请顺藤摸瓜读原文并写入：
1. Godot_Steam_Commercial_Titles：
 - WEBFISHING（Godot 3.5 + GodotSteam，默认 12 人）：Steam News https://store.steampowered.com/news/app/3146520 （上线 1 月内 ≥6 个网络补丁：>50 活跃大厅搜不到/房间码失效与 Lobby 搜索距离过滤、旧版本服、desync、踢人封禁）；社区 mod 框架 GDWeave/反编译分析中关于其 Steam P2P 包（actor 更新）机制的描述。
 - Buckshot Roulette 多人版：Steam News https://store.steampowered.com/news/app/2835570 （2024-12-10 公共大厅上线、开发者让玩家端口转发 UDP 4379/4380、断线软锁补丁）——判断其网络栈（ENet 直连? GodotSteam?）。
 - Dome Keeper 联机（Godot，线上 ≤8 人，2026-04-13 上线，仅房间码+好友）：GodotFest 2025 演讲 https://media.ccc.de/v/godotfest2025-keeper-to-keepers-adding-multiplayer-to-dome-keeper 的架构要点，Steam News https://store.steampowered.com/news/app/1637320 的 v5.0.x 补丁（重连丢状态、误报满员、开局加入崩溃）。
 - Cassette Beasts（在线 2 人合作的实现方式）、Brotato（是否有在线联机，或仅本地+Remote Play Together）——查官方公告确认。
 - 可再补 1-2 款 2024-2026 Godot 4 + Steam 联机新作（带网络口碑）。
2. Netcode_Testing_And_Reference_Impl：Godot 编辑器"运行多个实例"（Debug > Customize Run Instances，4.3+）的用法；Steam 测试 AppID 480（Spacewar）；同机双 Steam 账号不可行→需两台机/虚拟机/朋友；SDR 走中继时本机 netem/Clumsy 的适用性（对 UDP 出站有效与否）；推荐"传输层可切换 ENet/Steam"让 Claude 本地闭环（参考 JoshuaHieter/multiplayerSteamExample）；cooties 仓库是否仍在、内容是什么。
补完更新两个 JSON 的字段与 uncertain 数组，重新运行 validate_json.py，回报改动。无需 git checkpoint。

Address this before completing your current task.
````

### 工具调用（14 次）

- `WebFetch` https://store.steampowered.com/news/app/3146520
- `WebFetch` https://store.steampowered.com/news/app/2835570
- `WebFetch` https://media.ccc.de/v/godotfest2025-keeper-to-keepers-adding-multiplayer-to-dome-keeper
- `WebFetch` https://store.steampowered.com/news/app/1637320
- `Bash` cd /tmp/claude-0; for r in JoshuaHieter/multiplayerSteamExample; do curl -s https://api.github.com/repos/$r | head -c 600; done; echo; curl -s "https://api.gith…
- `Bash` cd /tmp/claude-0; for a in 3146520 2835570 1637320; do curl -s -m 20 "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=$a&count=60&maxlength=700"…
- `Bash` cd /tmp/claude-0; python3 - <<'EOF' import json,datetime for a,kw in (("3146520",None),("2835570",("multi","lobby","port","disconnect","online","network","co-op…
- `Bash` cd /tmp/claude-0; python3 - <<'EOF' | cut -c1-900 import json,datetime for a,kw in (("3146520",("lobby","network","desync","ban","kick","code")),("2835570",("mu…
- `Bash` cd /tmp/claude-0; python3 - <<'EOF' > out.txt import json,datetime for a in ("3146520","2835570","1637320"): d=json.load(open(f"n{a}.json"))["appnews"]["newsite…
- `Bash` cd /tmp/claude-0; python3 - <<'EOF' | cut -c1-2200 import json,datetime def show(a,titles,n): for i in json.load(open(f"n{a}.json"))["appnews"]["newsitems"]: if…
- `Bash` cd /tmp/claude-0; for a in 1352760 1942280; do :; done python3 - <<'EOF' | cut -c1-3500 import json,datetime def f(a,t,s=0,n=3000): for i in json.load(open(f"n{…
- `Bash` cd /tmp/claude-0; python3 - <<'EOF' | cut -c1-5500 import json def f(a,t,s=0,n=3000): for i in json.load(open(f"n{a}.json"))["appnews"]["newsitems"]: if t in i[…
- `Bash` cd /tmp/claude-0; curl -s "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=1637320&count=100&maxlength=0" | python3 -c " import json,sys,re for …
- `Bash` cat > /tmp/claude-0/upd.py <<'EOF' import json R='/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/' U='[不确定]' def load(n): return json.load(o…

### 交回的报告

两个 JSON 已更新，重新验证均通过（35/35，100%）。路径：/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Steam_Commercial_Titles.json 和 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Netcode_Testing_And_Reference_Impl.json。

**读原文的方式：** 你给的 Steam News 网页和 media.ccc.de 页面抓取下来只有导航壳，没有正文。我改用 Steam 新闻 API（api.steampowered.com/ISteamNews/GetNewsForApp）读到了一手公告全文。

**Item 1 补深的发现：**
- **WEBFISHING：**
  - 1.06（2024-10-12）：修了活跃大厅超过 50 个时搜不到房间、房间码加入失败的问题，旧版本服务器在浏览器里可见但不能加入，并新增封禁。
  - 1.07/1.08：修了仅房间码大厅被公开的问题，以及房间码大厅"距离太远无法连接"的问题。
  - 1.10：踢/封合并为 Boot，新增 Block。
  - 1.11（12-31）：重做大厅浏览器，加 Lobby Tags，大厅类型改为 Unlisted/Private。
  - 1.12（2025-01-01）：修了 lag/desync，并修了"满员加入者被静默加入封禁名单"的 bug。
  - **没找到：** 公告里没有"上线 1 月内至少 6 个网络补丁"这个说法。GDWeave 和反编译分析关于 P2P actor 包的描述没读到原文，标为"[不确定]"。
- **Buckshot Roulette 多人版：**
  - 官方明确说多人是 peer-to-peer，最多 4 人，2024-10-31 上线，Beta 期间无公共匹配。
  - 公共大厅在 2024-12-10 上线，同一公告里让玩家转发 UDP 4379/4380。
  - 补丁修了断线软锁（抓取道具时、装填时）和断线玩家偷道具崩溃。
  - **没找到：** 公告里看不出具体网络栈是 ENet 直连还是 GodotSteam，标为"[不确定]"。
- **Dome Keeper：**
  - 多人 2026-04-13 上线，是本地分屏加在线混合，没有公共大厅，只能用加入码或 Steam 好友。
  - 跨平台走 PlayFab，Steam/LAN 可直连；2026-02-10 做过公开 playtest。
  - v5.0.1 修了重新加入后临时增益变永久，v5.0.3 修了重连后 gamertag 异常和本地玩家断线空指针，v5.0.4 修了 PlayFab 连接失败时不应阻止 Steam/LAN 主机。
  - **没找到：** "重连丢状态、误报满员、开局加入崩溃"这几条，公告里没有。
  - GodotFest 2025 讲座页只有目录，没有架构细节，视频内容没读到。
- **Cassette Beasts：** 2024-05-20 免费多人更新，最多 8 人在线同图探索，另有 1v1 对战和 2 人合作战斗。网络栈未公开。
- **Brotato：** 官方公告确认只有本地最多 4 人合作（Update 1.1，2024-10-25），兼容 Remote Play Together，没有在线联机。
- **额外补的新作：** 没有另补 2024-2026 的新 Godot 4 + Steam 联机作品，只保留了上一轮的 Pratfall。
- **另外修改的字段：** host_migration_support、late_join_and_reconnect_support、nat_traversal_and_relay_behavior、post_launch_stability、maintenance_burden、key_pitfalls、fit_pve_vs_pvp，sources 也加了新来源。
- **uncertain：** 已更新为 quantitative_limits、architecture_codes、estimated_dev_weeks_solo、godot_integration_status、case_studies（WEBFISHING mod 框架细节、Buckshot 网络栈、Cassette Beasts 网络栈、Dome Keeper 讲座内容）。

**Item 2 补深的发现：**
- **cooties：** 仓库还在，地址是 bearlikelion/cooties，MIT 协议。内容是 Godot 平台游戏教程项目，同时支持 Steam Networking Sockets 和 ENet 两种传输，用了 RPC、MultiplayerSpawner、MultiplayerSynchronizer 和远端物理插值。README 链接了作者的 GodotCon'26 演讲。
- **JoshuaHieter/multiplayerSteamExample：** 当前环境访问不了这个仓库，内容未验证，标为"[不确定]"。
- **"传输层可切换 ENet/Steam"：** 我把它作为推荐写入了 test_and_debug_tooling，cooties 正是这种结构。
- **多实例、AppID 480、双账号：**
  - 多实例（Debug > Customize Run Instances）、Steam 测试 AppID 480、同机只能登一个 Steam 账号，这三点来自你的线索。我没有再查官方文档，已按线索写入。
  - 同机双账号不可行，需要两台机器、虚拟机或朋友。
- **netem/Clumsy 对 SDR：** 判断为理论上对本机出站 UDP 有效，但 Steam 可能走回环，netem 要指定真实出口网卡。这是推断，未找到实测资料，已标"[不确定]"。
- **uncertain：** 已更新为 quantitative_limits、host_migration_support、godot_integration_status、estimated_dev_weeks_solo、reference_implementations（JoshuaHieter 仓库未验证）、test_and_debug_tooling（netem/Clumsy 适用性为推断）。
