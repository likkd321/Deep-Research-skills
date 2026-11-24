# 子 agent 交回的数据

每个文件对应一个子 agent：先是派发给它的任务，然后按轮次列出它调用的工具（搜索词 / 读取的网址），最后是它交回主线程的报告原文。
“补深”轮次是主线程在批次结束后唤醒原 agent 做的定向补充。原始对话记录（含工具返回内容）在 `raw/` 下，为 gzip 压缩的 JSONL。

| 文件 | agent 类型 | 模型 | 负责的 item |
|---|---|---|---|
| [00_补充框架.md](00_补充框架.md) | `web-search-agent` | Sonnet | Step 2 补充 items 与字段 |
| [01_无感换主.md](01_无感换主.md) | `web-search-agent-deep` | Opus | Seamless_Host_Migration_D3_D4 |
| [02_秒级换主D2.md](02_秒级换主D2.md) | `web-search-agent-deep` | Opus | D2_Snapshot_Host_Migration |
| [03_Claude能力.md](03_Claude能力.md) | `web-search-agent-deep` | Opus | Claude_Godot_Netcode_Capability |
| [04_长期稳定与终局胜率.md](04_长期稳定与终局胜率.md) | `web-search-agent-deep` | Opus | Long_Term_Stability_Endgame_Odds |
| [05_承载力与7-12人案例.md](05_承载力与7-12人案例.md) | `web-search-agent-deep` | Opus | Home_Host_Capacity_And_Scaling, Case_7_12_Player_Indies |
| [06_Steamworks与补充方案.md](06_Steamworks与补充方案.md) | `web-search-agent` | Sonnet | Steamworks_Networking_Suite, Free_Supplementary_Services, Steam_Policy_And_Matchmaking_Cold_Start |
| [07_GodotSteam与多人API.md](07_GodotSteam与多人API.md) | `web-search-agent` | Sonnet | GodotSteam_And_SteamMultiplayerPeer, Godot4_High_Level_Multiplayer_API, Disconnect_Reconnect_Late_Join |
| [08_回滚锁步与帧敏感PvP.md](08_回滚锁步与帧敏感PvP.md) | `web-search-agent` | Sonnet | Godot_Rollback_Prediction_Plugins, Deterministic_Lockstep_And_Turn_Based, Case_Frame_Sensitive_PvP_Small |
| [09_PVE案例与PvP公平.md](09_PVE案例与PvP公平.md) | `web-search-agent` | Sonnet | Case_PVE_Coop_P2P_Indies, P2P_PvP_Fairness_Basics |
| [10_Godot商业作品与测试.md](10_Godot商业作品与测试.md) | `web-search-agent` | Sonnet | Godot_Steam_Commercial_Titles, Netcode_Testing_And_Reference_Impl |
