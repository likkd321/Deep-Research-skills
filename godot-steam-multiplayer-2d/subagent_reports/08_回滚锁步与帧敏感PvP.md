# 08_回滚锁步与帧敏感PvP

- agent 类型：`web-search-agent`
- 模型：Sonnet
- 负责的 item：Godot_Rollback_Prediction_Plugins, Deterministic_Lockstep_And_Turn_Based, Case_Frame_Sensitive_PvP_Small
- agent id：`a35aec40bd89a4a5a`

## 首轮调研（2026-11-23 16:55 UTC）

### 派发的任务

````text
## 任务
依次调研以下3个item，每个item输出一个结构化JSON。每完成一个item就立即写出它的JSON并运行验证，再开始下一个（中途中断时已完成的item不会丢失）。

### Item 1
调研 name: Godot_Rollback_Prediction_Plugins
category: 帧敏感同步
description: Godot 预测/回滚/延迟补偿插件：netfox（含 noray）、Godot Rollback Netcode（Snopek）、Delta Rollback、SG Physics 2D 定点物理；成熟度、与 SteamMultiplayerPeer 兼容性、支持人数、实际商用案例、学习曲线。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Rollback_Prediction_Plugins.json

### Item 2
调研 name: Deterministic_Lockstep_And_Turn_Based
category: 帧不敏感同步
description: 确定性锁步与指令/回合型联机（三国志式）：lockstep 原理、低频指令同步、文明/全面战争/战棋类做法、Godot 中的确定性问题（浮点/物理非确定）与规避（自写逻辑、定点数）、desync 检测与调试；帧不敏感游戏是否根本不需要锁步、直接用房主权威状态同步更简单。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Deterministic_Lockstep_And_Turn_Based.json

### Item 3
调研 name: Case_Frame_Sensitive_PvP_Small
category: 业界案例
description: 案例：帧敏感 PvP/派对小人数 P2P 独立游戏——Stick Fight、Duck Game、Bopl Battle、洞穴探险2、Rivals of Aether、Boomerang Fu、Brawlhalla 早期等：网络架构（回滚/延迟/房主权威）、引擎、人数、玩家对网络的口碑与差评。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Case_Frame_Sensitive_PvP_Small.json

## 字段定义
读取 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Rollback_Prediction_Plugins.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Deterministic_Lockstep_And_Turn_Based.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Case_Frame_Sensitive_PvP_Small.json

## 验证
每个JSON写出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml -j {output_path_i}
全部item验证通过后才算完成任务。
````

### 工具调用（37 次）

- `Bash` cat /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml; ls ~/.claude/agents/web-search-modules/ ~/.claude/skills/research/; date +%F
- `ToolSearch` select:WebSearch,WebFetch
- `Read` /root/.claude/agents/web-search-modules/general-web.md
- `Read` /root/.claude/agents/web-search-modules/github-debug.md
- `WebSearch` netfox Godot rollback netcode noray latest version Godot 4.5 4.6
- `WebSearch` Godot Rollback Netcode Snopek SteamMultiplayerPeer commercial games Delta Rollback SG Physics 2D
- `WebFetch` https://github.com/foxssake/netfox
- `WebFetch` https://foxssake.github.io/netfox/latest/faq/
- `WebFetch` https://gitlab.com/snopek-games/godot-rollback-netcode
- `WebSearch` netfox GodotSteam SteamMultiplayerPeer rollback compatible github issue
- `WebFetch` https://brogolem35.github.io/rollback-with-godotsteam/
- `WebFetch` https://forum.godotengine.org/t/can-you-use-godotsteam-netfox-connection-syncing/142914
- `WebSearch` netfox release v1.x changelog 2026 Godot 4.5 4.6 rollback
- `WebSearch` games using Godot Rollback Netcode Snopek Steam released "rollback" Godot game Steam
- `WebFetch` https://medium.com/@david.dehaene/delta-rollback-new-optimizations-for-rollback-netcode-7d283d56e54b
- `WebSearch` SG Physics 2D Godot fixed-point deterministic physics GDExtension Godot 4 status
- `WebSearch` Snopek godot-rollback-netcode Retro Tank Party rollback players max Godot 4 version 1.0 release
- `Bash` sed -n 1,80p ~/.claude/skills/research/validate_json.py; ls /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/ /home/user/Deep-Research-skills/godot-st…
- `Write` /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot_Rollback_Prediction_Plugins.json
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d && python ~/.claude/skills/research/validate_json.py -f fields.yaml -j results/Godot_Rollback_Pred…
- `WebSearch` lockstep deterministic networking turn-based strategy desync detection checksum Civilization Total War multiplayer architecture
- `WebSearch` Godot deterministic lockstep floating point determinism fixed-point math multiplayer RTS
- `WebSearch` Civilization VI multiplayer how it works host authoritative or lockstep; Total War multiplayer lockstep deterministic; Age of Empires lockstep 1500 archers
- `WebFetch` https://godotengine.org/asset-library/asset/5234
- `WebFetch` https://gafferongames.com/post/deterministic_lockstep/
- `WebSearch` Civilization multiplayer "out of sync" lockstep each client simulates game rules turn-based desync cause
- `WebSearch` turn-based strategy game multiplayer authoritative host vs lockstep which is simpler indie developer Godot
- `WebFetch` https://medium.com/@treeform/dont-use-lockstep-in-rts-games-b40f3dd6fddb
- `Write` /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Deterministic_Lockstep_And_Turn_Based.json
- `WebSearch` Stick Fight The Game netcode Unity networking host lag complaints Landfall
- `WebSearch` Bopl Battle netcode rollback Unity Landfall Steam reviews lag multiplayer
- `WebSearch` Rivals of Aether rollback netcode Steam Rivals 2 GGPO Brawlhalla netcode rollback history Boomerang Fu online
- `WebSearch` Spelunky 2 online multiplayer netcode rollback Steam reviews lag
- `WebSearch` Duck Game online netcode lag host Steam; Boomerang Fu online netcode complaints
- `WebSearch` Brawlhalla netcode architecture rollback server Blue Mammoth Adobe Air early P2P history
- `Write` /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Case_Frame_Sensitive_PvP_Small.json
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d && for f in Deterministic_Lockstep_And_Turn_Based Case_Frame_Sensitive_PvP_Small; do python ~/.cla…

### 交回的报告

All 3 items are written and each passed validate_json.py with 35/35 fields (100%). Item 3 rests on thin evidence and should be treated as a lead, not a finding.

Files, all in /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/:
- Godot_Rollback_Prediction_Plugins.json
- Deterministic_Lockstep_And_Turn_Based.json
- Case_Frame_Sensitive_PvP_Small.json

**Item 1, Godot rollback plugins**
- **netfox:**
  - v1.35.3 dated 2026-06-25 (Godot store listing); about 1.1k GitHub stars.
  - Its FAQ says Godot 4.x is supported and it builds on the Godot multiplayer API, so any peer should work. It does not mention Steam.
  - It does not require deterministic physics, but warns RTS-scale entity counts are a poor fit for rollback.
  - netfox.noray needs a noray server. The free test instance is for prototyping only, which conflicts with the zero-server goal.
  - A forum thread suggests Steam for the connection and netfox for syncing, but nobody has confirmed it works.
- **Snopek Godot Rollback Netcode:**
  - The Godot 4 version is still labelled 1.0.0-alpha, with Godot 4.2 as the listed target.
  - A tutorial by brogolem35 (updated 2026-09 for Godot 4.7) uses it with Steam. Relayed mode works with SteamMultiplayerPeer and RPC. True P2P needs a custom adapter and a replacement for `multiplayer_authority`, because Steam IDs are 64-bit. Steam P2P also does not catch corrupted packets, so the author added a SHA256 checksum.
  - Retro Tank Party (2-4 players) is the only confirmed user with a stated player count.
- **SG Physics 2D:** the newest Godot 4 release found is v1.0.0-alpha13 from 2023-07, with no later activity.
- **Delta Rollback:** the Medium article returned 403, so I only have search snippets.
- **Not found:** no commercial Steam games with player counts and reviews, and no 4.3-4.6 compatibility statements.

**Item 2, lockstep and turn-based**
- Lockstep sends only inputs, so bandwidth depends on input size rather than entity count. Desync detection is per-tick state checksums plus input hashes, with per-system checksums to find the first divergence (Gaffer on Games, Age of Empires "1500 Archers" paper).
- GDQuest says Godot is not deterministic by default because physics uses floats. A forum answer says not to rely on NavigationServer2D being deterministic.
- Klotho is a C#/.NET asset for deterministic multiplayer in Godot 4.4+ (v0.14.0, 32.32 fixed-point, lockstep and rollback, marked "Community").
- My conclusion is that frame-insensitive games do not need lockstep. Host-authoritative command and state sync is simpler (difficulty 2/5 versus 4-5/5), and second-level host migration can use a snapshot at each turn boundary.
- **Weak spot:** I found no first-hand source for Civilization or Total War netcode. Civ desync evidence is only player-forum reports.

**Item 3, small PvP case studies**
- Spelunky 2 uses rollback. The PC release launched without online play, the PS4 version had severe lag, and PC players still reported "syncing" hangs in 2023.
- Rivals of Aether had a rollback open beta in 2021, 1v1 only.
- Rivals of Aether 2 reportedly uses SnapNet plus dedicated servers (vendor claim from Edgegap).
- Boomerang Fu has no online play; its developer points players to Steam Remote Play.
- Stick Fight is only guessed to be host-based, from a fan guide. Aggregated reviews mention desync, lag and high ping.
- **Not verified:** Duck Game, Bopl Battle and Brawlhalla's early netcode. Most player counts, engines and host-migration handling are marked [不确定].

Each JSON lists its uncertain fields in the `uncertain` array. `architecture_codes` is marked uncertain in all three because I could not map the plugins to the user's A/B/D codes without their overview table.

## 第 1 次补深（2026-11-23 16:59 UTC）

### 派发的任务

````text
The coordinator sent a message while you were working:
定向补深（只改存疑字段，不要重跑）：
0. 用户全景表架构编码（请据此重写三个item的 architecture_codes 并去掉[不确定]）：A1 状态同步房主·房主走散局；A2 确定性帧同步/回滚·无迁移；A3 幽灵同屏；B1/B2 = A1/A2+云后端；D1 帧同步换发令员；D2 状态快照迁移（暂停选主）；D3 热备影子秒切；D4 各管移动+协调员管共享；D5 网状；C1/C2 云专服；C3 社区自建专服；E1 异步共享。
1. Case_Frame_Sensitive_PvP_Small：用开发者一手（Steam News 补丁说明、开发者访谈/博客/GDC、Reddit 开发者回帖）补：Bopl Battle（据称 Unity + 自写确定性定点物理 + 回滚 + Steam P2P，核实）、Duck Game（在线网络实现与 lag 口碑、人数 4/8）、Stick Fight（Unity、Steam P2P 房主、4 人）、SpeedRunners、Ultimate Chicken Horse、Lethal League Blaze、Brawlhalla 早期（P2P→专服?），每款写引擎/网络方案/人数/换主/网络口碑。至少把 4-5 款写实。
2. Godot_Rollback_Prediction_Plugins：在 netfox GitHub issues/discussions 搜 "steam"/"SteamMultiplayerPeer"，确认是否有人跑通、遇到什么问题；netfox 是否有已上架 Steam 的商业作品。
补完更新三个 JSON 的字段与 uncertain 数组，重新运行 validate_json.py，回报改动。无需 git checkpoint。

Address this before completing your current task.
````

### 工具调用（12 次）

- `WebSearch` Bopl Battle developers netcode deterministic fixed-point physics rollback Unity Steam
- `WebSearch` Duck Game online netcode Landon Podbielski interview networking 8 players lag
- `WebSearch` SpeedRunners netcode peer to peer lockstep Double Dutch Games online lag; Ultimate Chicken Horse netcode; Lethal League Blaze online netcode
- `WebSearch` Brawlhalla netcode dedicated servers peer-to-peer Blue Mammoth developer blog rollback
- `WebSearch` github foxssake netfox issue discussion steam SteamMultiplayerPeer GodotSteam
- `WebSearch` Bopl Battle "rollback" OR "deterministic" Steam news patch notes netcode Jonas Tyroller Tom Tyroller
- `WebSearch` netfox made game released on Steam Godot rollback netfox commercial release Steam page
- `WebFetch` https://github.com/foxssake/netfox/issues?q=steam
- `WebFetch` https://github.com/foxssake/netfox/discussions?discussions_q=steam
- `WebSearch` Ultimate Chicken Horse online multiplayer Clever Endeavour Games netcode Unity Photon Steam lag reviews
- `WebSearch` SpeedRunners Steam online multiplayer netcode lag complaints Double Dutch Games engine Unity? host peer-to-peer
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results && cat > /tmp/claude-0/upd.py <<'EOF' import json def load(n): return json.load(open(n+'.j…

### 交回的报告

定向补深已做完，三个 JSON 都重新验证通过（各 35/35，100%）。但第 1 点（Case 条目）只补到了二手来源，没拿到开发者一手资料。

**0. architecture_codes**：三个 item 都已按你给的编码重写，并从各自的 uncertain 数组里去掉了该字段。
- Godot_Rollback_Prediction_Plugins：netfox 预测加对账对应 A1 的增强版。Snopek 回滚、Delta Rollback、SG Physics 2D 对应 A2。noray 只是传输层辅助。
- Deterministic_Lockstep_And_Turn_Based：锁步对应 A2，锁步换发令员对应 D1。推荐的房主权威指令加状态同步对应 A1，加上回合边界快照搬家就是 D2。
- Case_Frame_Sensitive_PvP_Small：
  - Stick Fight 是 A1。
  - Spelunky 2、Rivals of Aether、Bopl Battle、Lethal League Blaze 是 A2。
  - Brawlhalla 偏 C1/C2。
  - SpeedRunners 在 A1 与 A2 之间，我标了 [不确定]。
  - 这些案例都没有 D 类换主证据。

**1. Case_Frame_Sensitive_PvP_Small**：case_studies 重写成 10 条，新增 Bopl Battle、Duck Game、SpeedRunners、Ultimate Chicken Horse、Lethal League Blaze，Brawlhalla 改写，并追加 9 个来源。实际写实的有这几款：
- **Lethal League Blaze**：开发者 YinYin 在 Steam 论坛称网络是自研的类 GGPO、零延迟实现。有玩家推断为 P2P 加回滚。口碑混合，有人说超过 2 人的房间总断线。
- **Brawlhalla**：粉丝 wiki 引述开发者，说是服务器型加 GGPO 式回滚，迟到包最多约 7 帧。wiki 没有链原帖，没法核实。所以"早期 P2P 转专服"这个说法没证实，早期架构仍是 [不确定]。
- **SpeedRunners**：2014 年 Steam 论坛玩家说是 P2P，只有一个 peer 多承担些职责。这是玩家说法，不是官方的。
- **Ultimate Chicken Horse**：Wikipedia 称基于 Unity，支持跨平台联机，Steam 英文好评 13,862 条（Overwhelmingly Positive）。具体网络方案没证实。评测对联机延迟的说法混合。
- **Duck Game**：在线最多 8 人，与你给的 4/8 相符。网络实现和 lag 口碑没找到可靠来源。
- **Bopl Battle**：只有侧证。开源克隆 warpzone-gg/bopl-port 描述原作用确定性 Q32.32 定点数物理，克隆自己用 GGRS 回滚。这不是开发者一手资料。Unity 和 Steam P2P 都没核实。
- **Stick Fight**：只有粉丝分析认为是房主型，引擎 Unity 未经一手证实。

Steam News 补丁说明、GDC、开发者访谈、Reddit 开发者回帖这几类一手来源，搜索都没返回 Bopl Battle、Duck Game、SpeedRunners、Ultimate Chicken Horse 的内容。要写实这几款，需要有人直接查 Steam News 或 SteamDB。我已在 risks 字段里注明。

**2. netfox 与 Steam**：补充写进了 godot_integration_status 和 case_studies。
- 在 netfox GitHub issues 里搜 steam，只命中 6 条，标题都不涉及 SteamMultiplayerPeer 或 GodotSteam。只看了标题，没打开正文。Discussions 里只命中 1 条（Showcase your game）。
- 没有任何人报告"用 SteamMultiplayerPeer 跑通"或"跑不通"。仅 issue #432 中维护者转述 multiplayer API 支持 Steam 等传输，这是二手信息。
- 没找到已在 Steam 上架的 netfox 商业作品。README 的 Built with netfox 清单只写"Steam 上即将上线"，清单中的 Bubble Battle、Chrome Carnage 等都没确认上架。
- 顺带发现一条 GodotSteam 风险，来自搜索摘要，没有核对原始公告。它是 CVE-2026-123017，影响 4.17 到 4.23.2，这些版本把 peer ID 1 当服务器，客户端可伪造 RPC，已写入 godot_integration_status。

uncertain 数组已更新，另外两个 item 的该数组只去掉了 architecture_codes。Godot_Rollback_Prediction_Plugins 的数组新增了 case_studies。

文件位置：/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/ 下的 Godot_Rollback_Prediction_Plugins.json、Deterministic_Lockstep_And_Turn_Based.json、Case_Frame_Sensitive_PvP_Small.json。
