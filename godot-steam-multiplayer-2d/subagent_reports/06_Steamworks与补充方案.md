# 06_Steamworks与补充方案

- agent 类型：`web-search-agent`
- 模型：Sonnet
- 负责的 item：Steamworks_Networking_Suite, Free_Supplementary_Services, Steam_Policy_And_Matchmaking_Cold_Start
- agent id：`aae669f59ad51606e`

## 首轮调研（2026-11-23 16:48 UTC）

### 派发的任务

````text
## 任务
依次调研以下3个item，每个item输出一个结构化JSON。每完成一个item就立即写出它的JSON并运行验证，再开始下一个（中途中断时已完成的item不会丢失）。

### Item 1
调研 name: Steamworks_Networking_Suite
category: Steam能力
description: Steamworks 联机套件全貌：ISteamMatchmaking Lobby（创建/搜索/过滤/房间列表/元数据/人数上限/房主转移）、ISteamNetworkingSockets/Messages、Steam Datagram Relay（SDR）中继与 P2P 打洞、Listen Server 模式、免费范围与带宽限制、全球及中国大陆连通性与延迟、Steam 好友邀请/Join Game/Rich Presence。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Steamworks_Networking_Suite.json

### Item 2
调研 name: Free_Supplementary_Services
category: Steam能力
description: 免费/近免费补充方案及与 Steam 无关的基线：EOS P2P/Lobby、Photon 免费档、W4 Cloud、Noray、Godot 内置 ENet/WebRTC/WebSocket（ENet 需端口转发说明为何需要 SDR）；Steam Cloud/排行榜/统计/成就/库存作为"轻后端"记录玩家成长（配合本地存档）；各自限制与长期免费风险。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Free_Supplementary_Services.json

### Item 3
调研 name: Steam_Policy_And_Matchmaking_Cold_Start
category: Steam能力
description: Steam 平台政策与匹配池冷启动：Steam Networking 仅限 Steam 玩家的影响、上架费与流程、Playtest/Demo 联机测试、玩家 IP 隐私（SDR 隐藏 IP）、Steam Deck；小人数游戏房间列表常空的应对（好友邀请优先、Remote Play Together 兜底、Discord 社群、跨区匹配）。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Steam_Policy_And_Matchmaking_Cold_Start.json

## 字段定义
读取 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Steamworks_Networking_Suite.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Free_Supplementary_Services.json
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Steam_Policy_And_Matchmaking_Cold_Start.json

## 验证
每个JSON写出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml -j {output_path_i}
全部item验证通过后才算完成任务。
````

### 工具调用（24 次）

- `Bash` cat /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml; ls ~/.claude/agents/web-search-modules/ ~/.claude/skills/research/; ls /home/user/De…
- `ToolSearch` select:WebSearch,WebFetch
- `Read` /root/.claude/agents/web-search-modules/general-web.md
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results; python3 -c " import json;d=json.load(open('Claude_Godot_Netcode_Capability.json'));print(…
- `WebSearch` Steamworks ISteamMatchmaking lobby limits max members 250 RequestLobbyList 50 results lobby data key value size
- `WebSearch` Steam Datagram Relay SDR free China POPs Perfect World relay Shanghai Guangzhou ping
- `WebFetch` https://partner.steamgames.com/doc/api/ISteamMatchmaking
- `WebFetch` https://partner.steamgames.com/doc/features/multiplayer/steamdatagramrelay
- `WebFetch` https://partner.steamgames.com/doc/api/ISteamNetworkingSockets
- `WebSearch` Steam China 蒸汽平台 国区 联机 Steam Networking 延迟 SDR 中国大陆 中继 节点
- `WebSearch` GodotSteam SteamMultiplayerPeer GDExtension Godot 4.4 4.5 version compatibility 2026
- `WebSearch` Epic Online Services P2P free lobbies limits Godot EOS plugin; Photon free tier CCU 20; W4 Cloud Godot pricing; Noray netfox
- `WebSearch` Steam Direct fee $100 recoup $1000 revenue Steam playtest demo multiplayer release 30 days coming soon page
- `WebFetch` https://partner.steamgames.com/doc/features/cloud
- `WebFetch` https://partner.steamgames.com/doc/store/releasing
- `WebFetch` https://partner.steamgames.com/doc/features/playtest
- `WebFetch` https://www.photonengine.com/pun/pricing
- `WebSearch` W4 Cloud Godot free tier pricing lobby matchmaking
- `WebSearch` EOS Lobby interface max members 64 EOS P2P relay free terms Epic Online Services Godot plugin EOSG
- `WebSearch` Steam Remote Play Together Godot game support requirements Steam Deck Godot multiplayer SteamNetworkingSockets
- `WebSearch` Steam Networking Sockets host migration lobby owner left Godot GodotSteam lobby owner change host migration
- `Bash` mkdir -p /tmp/claude-0/s && cat > /tmp/claude-0/s/gen1.py <<'EOF' import json d={} d["name"]="Steamworks_Networking_Suite" d["category"]="Steam能力" d["what_it_is…
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results; python3 - <<'EOF' import json f='Steamworks_Networking_Suite.json';d=json.load(open(f)) d…
- `Bash` cat > /tmp/claude-0/s/gen2.py <<'EOF' import json R='/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/' def dump(n,d): d["name"]=n;d["category…

### 交回的报告

三个 item 的 JSON 都已写出，并分别通过 `validate_json.py`，字段覆盖率均为 100%（35/35）。

输出文件（目录 `/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/`）：
- `Steamworks_Networking_Suite.json`
- `Free_Supplementary_Services.json`
- `Steam_Policy_And_Matchmaking_Cold_Start.json`

**核实过的一手事实（来自 Valve 和 Photon 官方页）**
- **Lobby**：
  - 人数上限 250，键长上限 255 字符。
  - 房主离开后 Steam 自动指派新房主，也可用 `SetLobbyOwner` 手动转让；但只转移大厅所有者，不迁移游戏状态。
  - 房间搜索 20 秒超时。
  - 大厅类型有 Private、FriendsOnly、Public、Invisible 四种。
- **SDR**：官方文档说明中继会隐藏双方 IP、防 DoS。`ConnectP2P` 走中继，`ConnectByIPAddress` 是不经中继的纯 UDP。官方页没写价格，"对开发者免费"是业界共识，不是官方原话。
- **上架与测试**：
  - Steam Direct 费用 100 美元，产品调整后收入达到 1000 美元后回收。
  - 商店页至少"即将推出"2 周，商店页审核 3-5 个工作日。
  - Playtest 免费，使用独立子 AppID，支持联机和好友邀请（认识满 30 天，每人 1/2/3 个名额）。
- **Photon**：PUN 免费档为 20 CCU、60GB/月，且仅限开发用途；付费为一次性 95 美元、100 CCU、12 个月。
- **Steam Cloud**：单次写入上限 100MB，每用户的字节配额和文件数由开发者在后台设置，默认值官方页未给。
- **GodotSteam**：expressobits 的 `steam-multiplayer-peer` 作者在 2025 年 12 月暂停维护，并称功能已并入 GodotSteam 4.x 主分支。

**标 [不确定] 的内容（各 JSON 末尾的 `uncertain` 数组已列出）**
- **中国大陆延迟与 SDR 节点**：只找到加速器厂商 NoPing 的商业博客，没有独立实测，也没有确认国内有 SDR 节点。
- **数值未核实**：
  - Lobby 数据值长度（常见说法是 8192 字节）。
  - 单条消息大小上限。
  - 默认发送速率。
  - Steam Cloud 默认配额。
- **服务限额与价格未核实**：EOS 的 Lobby 人数上限和 P2P 中继限额、W4 Cloud 当前价格和免费档、Photon 的 Godot SDK 价格。
- **Godot 版本兼容**：GodotSteam 与 Godot 4.3-4.6 的兼容矩阵未核实，需以其 Releases 页为准。
- **案例**：没有检索到带网络口碑的 Godot + Steam 具体游戏案例。`case_studies` 只写了少量一般认知，其中 Valheim、Lethal Company 的表述（含 Steam P2P 和房主掉线即结束）是凭印象写的，未逐条核实。
- **全景表编码**：架构编码（A/B/D 类）是按描述推断的。全景表的精确定义不在本次资料中，对应关系可能不准。

## 第 1 次补深（2026-11-23 16:52 UTC）

### 派发的任务

````text
The coordinator sent a message while you were working:
定向补深（只改存疑字段，不要重跑）：
1. 中国大陆/全球 SDR：查 Valve 公开的 SDR 网络配置（如 https://api.steampowered.com/ISteamApps/GetSDRConfig/v1/?appid=730 或 SteamDB/社区整理的 POP 列表），确认是否有中国大陆 POP（如 sha/can/tsn/pwg 等代码）及完美世界合作节点；找独立实测（Reddit/知乎/NGA/Steam 社区）描述大陆玩家走 SDR 联机的延迟与稳定性；跨洲（欧-亚、美-亚）SDR 延迟数量级。
2. 统一口径：主线程已从 GameNetworkingSockets 源码得到 默认连接超时 10000ms、单条消息上限 512KB、默认发送速率 256KB/s（可调）——请直接用这三个数（注明来源 GNS 源码 steamnetworkingsockets 默认配置），并去掉对应的[不确定]。
3. Lobby metadata 值长度上限（8192?）与 lobby 数据键数量限制：查 Steamworks ISteamMatchmaking 文档 k_nMaxLobbyKeyLength / SetLobbyData 说明。
4. EOS：Lobby 人数上限、P2P 中继是否免费/限额、是否要求 Epic 账号（可用 Steam 账号 Connect 登录）；W4 Cloud 当前价格与免费档。
5. Free_Supplementary_Services / Steam_Policy 的 case_studies 中凭印象写的 Valheim、Lethal Company 网络描述请快速核实（Lethal Company = Unity NGO + Facepunch Transport/Steam P2P、房主离开即散局？Valheim = Steam P2P + 可选专服）。
补完更新对应三个 JSON 的字段与 uncertain 数组并重新运行 validate_json.py，回报改动。

Address this before completing your current task.
````

### 工具调用（9 次）

- `WebFetch` https://api.steampowered.com/ISteamApps/GetSDRConfig/v1/?appid=730
- `WebFetch` https://partner.steamgames.com/doc/api/ISteamMatchmaking
- `WebSearch` Lethal Company networking Netcode for GameObjects Facepunch Steam transport host leaves game ends; Valheim Steam P2P dedicated server networking
- `WebSearch` EOS lobby max members 64 limit; EOS P2P relay free usage limits; Epic Account Services not required Connect Interface Steam login external account
- `WebSearch` Valheim networking Steam P2P listen server dedicated server crossplay PlayFab host leaves world
- `WebSearch` SDR 中国大陆 阿里云 腾讯云 POP Steam Datagram Relay 联机 延迟 实测 知乎 OR NGA OR reddit
- `WebFetch` https://w4games.com/pricing
- `WebFetch` https://dev.epicgames.com/docs/game-services/lobbies
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results; python3 - <<'EOF' import json def load(n): return json.load(open(n+'.json')) def save(n,d…

### 交回的报告

定向补深已完成。三个 JSON 都已更新并重新通过 `validate_json.py`，覆盖率均为 35/35，只改了存疑字段。文件在 `/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/` 下：`Steamworks_Networking_Suite.json`、`Free_Supplementary_Services.json`、`Steam_Policy_And_Matchmaking_Cold_Start.json`。

**1. SDR 大陆节点**
- Valve 公开的 `ISteamApps/GetSDRConfig/v1/?appid=730` 列出了大陆 POP：
  - 阿里云：成都 `ctu`、北京 `pek`、上海 `pvg`。
  - 腾讯云：广州 `tgd`。
  - 每个城市另有移动/电信/联通子节点，后缀 `m`/`t`/`u`，例如 `pvgt` 是上海电信。
- 配置里没有 `sha`、`can`、`tsn`、`pwg` 这类代码，也没有"完美世界"命名的节点。大陆节点由阿里云和腾讯云承载。
- 同一份配置里还有 `hkg`、`tyo`、`sgp`、`seo` 等亚洲节点。
- 这份配置是用 CS2（appid 730）查的。第三方 Steamworks 游戏是否能用到这些大陆 POP，没能证实，已标 [不确定]。
- 没找到知乎、NGA、Reddit 上的独立实测。搜到的几乎都是加速器厂商 NoPing 的博客：北京到新加坡约 120-180ms，东京约 50-80ms，香港约 30-50ms，但没有测试方法说明。已按低可信度写入 `latency_profile`、`quantitative_limits` 和 Policy 条目。
- 跨洲延迟只写了经验量级：欧-亚约 150-250ms，美西-亚约 100-180ms，没有出处，已标 [不确定]。

**2. GameNetworkingSockets 数值**
`Steamworks_Networking_Suite.json` 的 `quantitative_limits` 已按主线程口径写入：连接超时 10000ms、单条消息 512KB、默认发送速率 256KB/s（可调），来源注明 GameNetworkingSockets 源码默认配置，对应的 [不确定] 已去掉。

**3. Lobby 元数据**
- 键长 `k_nMaxLobbyKeyLength` 是 255。
- 值长受 `k_cubChatMetadataMax` 限制，ISteamMatchmaking 页只链接到 ISteamFriends，没写数值。8192 只是常见说法，未证实，仍标 [不确定]。
- 键的数量官方没有限制，`SetLobbyData` 和 `SetLobbyMemberData` 两页都没提；键或值超长时返回 false。

**4. EOS 与 W4 Cloud**（已写入 `Free_Supplementary_Services.json`）
- EOS Lobby 最多 64 人，来源是 SynicSugar 插件文档（二手，没拿到 Epic 官方页）；该文档建议 P2P 场景 16 人以内。
- EOS P2P 中继没找到公开的免费额度或限速数字，只能写"官方称无版税/托管费"。
- EOS 不要求 Epic 账号。Connect 接口支持 Device ID 匿名登录，也可以用 Steam 作外部身份提供方登录（SynicSugar 文档和 UE 论坛日志，二手）。
- W4 Cloud 的 `/pricing` 页返回 404，当前价格和免费档仍没核实。

**5. Lethal Company 与 Valheim 案例**
三个 JSON 的 `case_studies` 都已改写，来源都是二手：
- Lethal Company 是 Unity Netcode for GameObjects 加 Facepunch Transport，走 Steam。社区称它不支持换主，房主离开会话即结束。另有模组反馈房主掉线后 Steam 大厅残留，"加入游戏"会报错。
- Valheim 同时有 Steam 后端和 PlayFab 跨平台中继后端，用 `-crossplay` 参数切换。游戏内托管时房主下线世界不可用，也可以用专用服务器。部分说法来自主机商博客，可信度一般。
- 没找到 Godot + Steam 的具体案例。

三个 JSON 的 `sources` 已补上 GetSDRConfig、SynicSugar、Steam 论坛和 Edgegap 的链接，`uncertain` 数组已按上面各点调整。
