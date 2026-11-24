# 07_GodotSteam与多人API

- agent 类型：`web-search-agent`
- 模型：Sonnet
- 负责的 item：GodotSteam_And_SteamMultiplayerPeer, Godot4_High_Level_Multiplayer_API, Disconnect_Reconnect_Late_Join
- agent id：`a0501956d0b58a6d0`

## 首轮调研（2026-11-23 16:53 UTC）

### 派发的任务

````text
## 任务
依次调研以下3个item，每个item输出一个结构化JSON。每完成一个item就立即写出它的JSON并运行验证，再开始下一个（中途中断时已完成的item不会丢失）。

### Item 1
调研 name: GodotSteam_And_SteamMultiplayerPeer
category: Godot技术栈
description: GodotSteam（GDExtension/预编译模块版）与 SteamMultiplayerPeer（expressobits 版 vs godotsteam 官方版）的成熟度、与 Godot 4.3–4.6 的版本兼容矩阵、维护活跃度/维护者数量、已知 bug（create_host 静默失败、不支持 channels/mesh）、是否依赖 Lobby、文档与示例质量。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/GodotSteam_And_SteamMultiplayerPeer.json

### Item 2
调研 name: Godot4_High_Level_Multiplayer_API
category: Godot技术栈
description: Godot 4 高层多人 API：RPC（@rpc 注解、可靠/不可靠、channel）、MultiplayerSynchronizer/MultiplayerSpawner、multiplayer authority、可见性过滤、带宽与性能实测、局限（星型拓扑、无内建预测/插值/换主）、4.x 版本间破坏性改动。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot4_High_Level_Multiplayer_API.json

### Item 3
调研 name: Disconnect_Reconnect_Late_Join
category: Godot技术栈
description: 房主离线检测、断线重连与中途加入（不换主档的基础）：server_disconnected/peer_disconnected 信号、Steam.getLobbyOwner 与 Lobby 房主变更回调、优雅散局与回大厅、中途加入时的全量状态同步、客户端掉线后重进恢复、超时与心跳设计，在 Godot+Steam 下的实现方式与坑。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Disconnect_Reconnect_Late_Join.json

## 字段定义
读取 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/GodotSteam_And_SteamMultiplayerPeer.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot4_High_Level_Multiplayer_API.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Disconnect_Reconnect_Late_Join.json

## 验证
每个JSON写出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml -j {output_path_i}
全部item验证通过后才算完成任务。
````

### 工具调用（20 次）

- `Bash` cat /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml; ls ~/.claude/agents/web-search-modules/ ~/.claude/skills/research/; date +%Y-%m-%d
- `ToolSearch` select:WebSearch,WebFetch
- `Read` /root/.claude/agents/web-search-modules/general-web.md
- `Read` /root/.claude/agents/web-search-modules/github-debug.md
- `WebSearch` SteamMultiplayerPeer godotsteam expressobits GDExtension Godot 4.4 4.5 compatibility
- `WebFetch` https://github.com/expressobits/steam-multiplayer-peer
- `WebFetch` https://godotsteam.com/classes/steam_multiplayer_peer/
- `WebFetch` https://github.com/GodotSteam/GodotSteam
- `WebSearch` GodotSteam SteamMultiplayerPeer official godotsteam 4.x create_host lobby "MultiplayerPeer" channels not supported issue
- `WebSearch` Godot 4 MultiplayerSynchronizer MultiplayerSpawner limitations bandwidth visibility interpolation 4.4 4.5 breaking changes
- `WebSearch` Godot 4 multiplayer late join reconnect server_disconnected host disconnect Steam lobby owner changed GodotSteam lobby_chat_update
- `WebFetch` https://forum.godotengine.org/t/create-host-with-godotsteam-server-fails-silently/137023
- `WebFetch` https://pandaqi.pages.dev/blog/tutorials/online-multiplayer/handling-disconnects-and-reconnects/
- `WebFetch` https://docs.godotengine.org/en/stable/tutorials/networking/high_level_multiplayer.html
- `WebFetch` https://brogolem35.github.io/rollback-with-godotsteam/
- `WebFetch` https://codeberg.org/godotsteam/godotsteam
- `WebFetch` https://godotsteam.com/tutorials/multiplayer_peer/
- `WebSearch` godotsteam MultiplayerPeer repository lobby required "SteamMultiplayerPeer" godotsteam multiplayer peer README host_with_lobby
- `WebSearch` Godot 4 MultiplayerSynchronizer bandwidth benchmark players entities KB/s ENet no interpolation prediction host migration
- `Bash` mkdir -p /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results /tmp/claude-0/-home-user-Deep-Research-skills/7db2bb83-98ca-5144-bdc1-6310ffab2ec1/s…

### 交回的报告

3个item的JSON已写出，并分别通过 validate_json.py（覆盖率100%）。

文件：
- /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/GodotSteam_And_SteamMultiplayerPeer.json
- /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Godot4_High_Level_Multiplayer_API.json
- /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Disconnect_Reconnect_Late_Join.json

核心发现：
1. **GodotSteam / SteamMultiplayerPeer**
   - expressobits 版：GDExtension，不支持 channels（作者已移出计划），不依赖 Lobby（其 demo 用 GodotSteam Lobby）。作者 2025-12 起暂停开发并推荐 GodotSteam。Asset Library 条目标 Godot 4.4（0.2.5），README 徽章显示 0.2.3，Godot 4.3/4.5/4.6 没有官方兼容确认。
   - GodotSteam：主仓已迁到 Codeberg，GitHub 仓于 2026-11-10 归档。Codeberg 页面显示有 307 次提交和 19 个 open issue，近期提交频繁，最近一次在 2026-11-09，可见的主力提交者只有 Gramps 一人。SDK 1.65 对应 GodotSteam 4.21 及以上，兼容说明提到 Godot 4.7 有断点。
   - 已知 bug：Godot 4.6 论坛有一帖报告 godotsteam_server 下 `create_host` 静默失败，无人回复，只被建议去 Codeberg 提 issue。GodotSteam issue 列表里另有一条：peer 调用 close() 后无法加入另一个 Lobby。
   - 官方版的 Lobby 依赖与 mesh 问题：没取到官方文档（godotsteam.com 返回 403）。论坛有人调用 `create_lobby`，说明官方版可能与 Lobby 绑定，但未证实。mesh 方面，True P2P 只能走旧 Steam 网络 API 收发原始包，用不了 RPC。
   - 相关的 64 位 Steam ID 与 Godot 32 位 authority 截断问题，来自第三方教程。
2. **Godot 4 高层多人 API**
   - 已确认的：`@rpc` 默认等价 `@rpc("authority","call_remote","reliable",0)`；`transfer_channel` 必须是最后一个参数；同路径双端声明；晚加入会出现 "Node not found"；释放玩家节点会断开其他同步（issue #100873）。
   - 没找到权威来源的：官方带宽基准、4.x 各版本间破坏性改动的清单。唯一的量化数据是一篇二手博客的估算：4 人合作约 30 个实体、30Hz 时每玩家约 100-180 Kbps，方法未核实。网络分析器只统计高层 API 字节，会低估实际流量。
3. **断线、重连与中途加入**
   - 全部要自写，没有现成插件。
   - 要点：close() 前先逐个断开，否则 `peer_disconnected` 可能不触发；先 `set_public_visibility(false)` 再销毁节点；服务器通过 RPC 推全量快照，客户端等 spawned 信号后再应用；重连用计时器加重进 Lobby。
   - 没找到的：Steam 房主变更回调的专门实现案例，以及超时、心跳的具体数值。

主要不确定项（均已在各 JSON 的 uncertain 数组中标注）：
- `architecture_codes`：没拿到用户全景表，三个 item 都只能写通用对应。
- 量化数据：缺人数、带宽、延迟的权威实测。
- `case_studies`：未检索到可核实的商业游戏案例，三个 item 都标了不确定。
- `godot_integration_status`：Godot 4.3-4.6 逐版本兼容矩阵在三个 item 里都不完整。
- Steam 相关的费用和 SDR 中继归属，没有官方原文复核。

另外，部分来源页面显示的版本号（Godot 4.7.x、GodotSteam 4.24）与我已有知识不符，可能是抓取摘要有误，建议 `research-report` 阶段二次核实。本次检索主要靠 WebSearch 和 WebFetch，没有读 GitHub issue 原文。

## 第 1 次补深（2026-11-23 16:56 UTC）

### 派发的任务

````text
The coordinator sent a message while you were working:
定向补深（只改存疑/冲突字段，不要重跑）。先统一口径——以下是其他item已一手核实的事实，请直接采用并去掉相应[不确定]：
- 版本：Godot 4.6/4.7 是当前全支持版本（官方 release policy），4.5 仅安全修复，≤4.4 EOL；GodotSteam 4.24 于 2026-11-07/08 发布（changelog 含 "Fixed: peer ID claim during setup and bad peer rejection"，修复 4.17–4.23.2 的 peer ID 伪造问题）。这些不是抓取错误。
- GodotSteam 4.x 自带 SteamMultiplayerPeer 源码（Codeberg godot4 分支 godotsteam_multiplayer_peer.cpp，其他 agent 已读）：无 create_mesh；lobby 模式 host_with_lobby/connect_to_lobby 下成员两两建连（事实 mesh），客户端经房主中转默认关闭（4.16.2 起可选）；create_host 固定 peer 1；create_client 每次随机 peer ID；丢失 peer 1 直接 close()；host_with_lobby 要求调用者已是 lobby owner。独立 multiplayerpeer 仓已退役并入主仓。
- Steam 数字（GameNetworkingSockets 源码）：默认连接超时 10000ms（可调），单消息上限 512KB，默认发送速率 256KB/s。Lobby 房主转移：主动 LeaveLobby 即时；拔线约 30s 才收到离开回调（Facepunch.Steamworks issue #765）→ 掉线检测要自建心跳（参考 Godot Understudy 170ms 静默+多数票）。
- 用户全景表架构编码：A1 状态同步房主·房主走散局；A2 确定性帧同步/回滚；A3 幽灵同屏；B1/B2 = A1/A2+云后端；D1 帧同步换发令员；D2 状态快照迁移（暂停选主）；D3 热备影子秒切；D4 各管移动+协调员管共享；D5 网状去中心；C1/C2 云专服；C3 社区自建专服；E1 异步共享。请据此重写三个item的 architecture_codes。
然后补：
1. 真实案例：Godot 用 GodotSteam 的商业联机游戏（WEBFISHING 用 Godot3.5+GodotSteam，上线后多次修大厅/房间码/desync；Dome Keeper 联机 ≤8 人仅房间码+好友，2026 补丁多为重连丢状态；Buckshot Roulette 联机断线软锁补丁）——按你的三个item视角写进 case_studies（可引 Steam News 页 https://store.steampowered.com/news/app/3146520 等）。
2. Godot 高层 API 带宽：再找一手/可复核的实测（Godot 官方博客 multiplayer 文章、GitHub issue 里的带宽测量、netfox/社区 benchmark），找不到就保留二手估算并注明。
3. 心跳/超时的推荐数值与 Lobby 房主变更（LobbyChatUpdate_t / lobby_chat_update 信号、getLobbyOwner 轮询）的 GodotSteam 写法示例来源。
补完更新三个JSON与uncertain数组，重新运行 validate_json.py，回报改动。

Address this before completing your current task.
````

### 工具调用（5 次）

- `WebFetch` https://store.steampowered.com/news/app/3146520
- `WebSearch` Dome Keeper multiplayer patch notes reconnect disconnect fix 2026 Steam
- `WebSearch` netfox Godot bandwidth benchmark MultiplayerSynchronizer bytes per second measured github
- `WebSearch` GodotSteam lobby_chat_update signal getLobbyOwner lobby owner changed example docs
- `Bash` cat > /tmp/claude-0/-home-user-Deep-Research-skills/7db2bb83-98ca-5144-bdc1-6310ffab2ec1/scratchpad/patch.py <<'EOF' import json R="/home/user/Deep-Research-ski…

### 交回的报告

定向补深已完成。三个 JSON 已更新，并重新运行 validate_json.py，全部通过，覆盖率 100%。

只改了存疑/冲突字段，没有重跑调研。

**三个 item 共同的改动**
- `architecture_codes` 已按全景表重写：
  - GodotSteam/SteamMultiplayerPeer：A1 传输层基础，也是 B1 的客户端传输；lobby 模式下成员两两建连，有 D5 的传输基础，但 RPC 仍按 peer 1 星型使用。
  - 高层 API：A1 默认实现层，B1 客户端侧；不提供 A2 回滚（需 netfox 等另做），也没有 D1-D5 换主。
  - 断线/重连/中途加入：A1 房主走散局分支的基础，也是 D2、D3 的前置能力。
- `case_studies` 已写入 WEBFISHING、Dome Keeper、Buckshot Roulette，并统一标注口径：
  - WEBFISHING 的 Steam News 页抓取为空；Dome Keeper 的补丁原文、Buckshot Roulette 的断线软锁补丁，我没有核到。三条的补丁内容都是转述你给的信息，换主处理写的是[不确定]。
  - Dome Keeper 联机在 2026-04-13 上线，线上最多 8 人，这一点已由 Xbox Wire 和 PCGames 核实。
  - 没有其他案例的口碑数据。

**GodotSteam/SteamMultiplayerPeer**
- 已采用你提供的版本口径，并去掉相应的[不确定]：4.6/4.7 全支持，4.5 仅安全修复，≤4.4 EOL；GodotSteam 4.24 修复 4.17–4.23.2 的 peer ID 伪造问题，写进了 pitfalls，建议升级。
- 已写入官方 peer 的行为：无 create_mesh，lobby 模式事实 mesh，create_host 固定 peer 1，create_client 随机 peer ID，host_with_lobby 要求调用者是 lobby owner，独立仓已并入主仓。
- 已写入 Steam 数字（GNS 默认超时 10s、单消息 512KB、默认发送速率 256KB/s）和房主转移口径（拔线约 30s 才收到离开回调）。
- expressobits 版标明为 EOL 版本，不建议新项目采用。
- 仍保留[不确定]的字段：`quantitative_limits`、`player_count_support`、`case_studies`、`cost_per_month`、`tech_requirements`。

**高层 API 带宽**
- 没找到一手可复核的 Spawner/Synchronizer 带宽基准。netfox 文档没有带宽数据，Godot 官方博客也只谈设计。
- 可复核的只有一点：Godot 网络分析器只统计高层 API 载荷字节，会低估实际流量。这是 godot issue #91869 里维护者的说明。
- 保留了二手估算：Godot 4.5 ENet，4 人约 30 个实体 30Hz，每玩家约 100-180Kbps，方法未核实。建议用 Wireshark 自测。
- 4.x 版本间破坏性改动清单仍没拿到权威来源，留作[不确定]，要查各版本 Release notes。

**心跳/超时与房主变更**
- 推荐数值：
  - 掉线检测不能依赖 Lobby 回调，要自建心跳。
  - 心跳间隔约 100ms 量级。
  - 静默约 170ms 判疑似掉线，再多数票确认。
  - 重连窗口 10-30s，超时回大厅。
  - 后两条是经验值，不是官方数值；170ms 加多数票来自你提供的 Godot Understudy，我没有一手核对。
- 房主变更写法：
  - GodotSteam 的 godot4 分支 `godotsteam.cpp` 确实注册了 `Steam.lobby_chat_update`，但它是成员状态变化事件，不是房主变更事件。
  - 没找到房主变更的现成示例。实用做法是在 `lobby_chat_update` 处理函数里重新调用 `Steam.getLobbyOwner(lobby_id)`，与保存的 host id 比较，或定时轮询。这个做法本身是推断，要对照所用 GodotSteam 版本源码确认。
  - 社区例子只在加入后读一次房主（Godot 4.4.1 论坛帖）。

更新后的 `uncertain` 数组：
- GodotSteam_And_SteamMultiplayerPeer：`quantitative_limits`、`player_count_support`、`case_studies`、`cost_per_month`、`tech_requirements`
- Godot4_High_Level_Multiplayer_API：`quantitative_limits`、`player_count_support`、`godot_integration_status`、`case_studies`
- Disconnect_Reconnect_Late_Join：`case_studies`、`tech_requirements`

文件在 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/：
- GodotSteam_And_SteamMultiplayerPeer.json
- Godot4_High_Level_Multiplayer_API.json
- Disconnect_Reconnect_Late_Join.json
