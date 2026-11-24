# 03_Claude能力

- agent 类型：`web-search-agent-deep`
- 模型：Opus
- 负责的 item：Claude_Godot_Netcode_Capability
- agent id：`a352de6ba60322910`

## 首轮调研（2026-11-23 16:31 UTC）

### 派发的任务

````text
## 任务
调研 name: Claude_Godot_Netcode_Capability
category: AI编程能力
description: Claude 写 Godot 4 联机代码的能力边界：GDScript/Godot 4 训练数据量、Godot 3/4 API 混淆（rpc 注解、MultiplayerSynchronizer 等）、GodotSteam 这种小众库的出错率、Godot MCP / Claude Code 工作流实践、开发者实测反馈（2024-2026）；哪些网络任务 AI 擅长（大厅/RPC/状态同步）哪些不擅长（回滚、确定性、换主、不可复现的时序 bug）；C# vs GDScript 对 Claude 把握度的影响；"懂语法写得少"的开发者在每类方案上需要自己扛的部分。，输出结构化JSON到 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Claude_Godot_Netcode_Capability.json

## 字段定义
读取 /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml 获取所有字段定义

## 输出要求
1. 按fields.yaml定义的字段输出JSON
2. 不确定的字段值标注[不确定]
3. JSON末尾添加uncertain数组，列出所有不确定的字段名
4. 所有字段值必须使用中文输出（调研过程可用英文，但最终JSON值为中文）

## 输出路径
/home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Claude_Godot_Netcode_Capability.json

## 验证
完成JSON输出后，运行验证脚本确保字段完整覆盖：
python ~/.claude/skills/research/validate_json.py -f /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml -j /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Claude_Godot_Netcode_Capability.json
验证通过后才算完成任务。
````

### 工具调用（49 次）

- `Bash` date +%Y-%m-%d; cat /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/fields.yaml; ls ~/.claude/agents/web-search-modules/; ls /home/user/Deep-Research…
- `ToolSearch` select:WebSearch,WebFetch
- `Bash` cat ~/.claude/agents/web-search-modules/general-web.md ~/.claude/agents/web-search-modules/github-debug.md | head -150; ls /home/user/Deep-Research-skills/godot…
- `WebSearch` Claude Godot 4 GDScript multiplayer code Godot 3 syntax mistakes reddit
- `WebSearch` Godot MCP server Claude Code workflow GDScript 2025
- `WebSearch` LLM GDScript benchmark Godot 4 code generation accuracy
- `WebFetch` https://github.com/flockbay/godot-llm-bench
- `WebFetch` https://recognizingpatterns.substack.com/p/ai-is-the-worst-at-godot-thats-why
- `WebFetch` https://ziva.sh/blogs/claude-godot
- `WebFetch` https://godotlearning.com/blog/ai-write-gdscript-llm-godot
- `WebFetch` https://johnvanscoyoc.itch.io/godot-ai-agent-kit-rules-prompts-workflow-for-cursor-and-claude-code/devlog/1729187/3-godot-4-bugs-ai-writes-that-pass-the-parse-c…
- `WebFetch` https://dev.to/orellanaed/claude-code-for-godot-in-2026-connect-it-to-your-game-and-what-it-builds-37md
- `WebSearch` GodotSteam ChatGPT OR Claude AI wrong function names hallucinate Steam lobby Godot 4
- `WebSearch` AI generated Godot 4 multiplayer code "@rpc" "set_multiplayer_authority" wrong forum
- `WebSearch` vibe coding multiplayer game netcode AI fails rollback desync experience 2025 2026
- `WebFetch` https://dev.to/ziva/7-godot-4-api-calls-your-ai-assistant-still-gets-wrong-3ep6
- `WebFetch` https://gamedevaihub.com/how-to-vibe-code-a-game-the-step-by-step-guide-2026/
- `WebSearch` Claude Code Godot multiplayer devlog Steam P2P "Claude" built lobby rpc experience
- `WebFetch` https://github.com/JoshuaHieter/multiplayerSteamExample
- `WebSearch` Godot Foundation AI generated code contributions policy 2026
- `WebSearch` Godot C# vs GDScript which is better for AI coding assistants Claude
- `WebSearch` SteamMultiplayerPeer create_host create_client signature change GodotSteam 4.x expressobits differences
- `WebSearch` netfox Godot rollback addon AI Claude prompt OR "LLM" usage
- `WebSearch` Godot 4 "@rpc" Godot 3 "remote" "master" "puppet" "remotesync" AI ChatGPT outputs
- `WebSearch` site:reddit.com r/godot AI multiplayer code Claude OR ChatGPT "multiplayer" Godot 4 experience
- `WebFetch` https://godotsteam.com/classes/multiplayer_peer/
- `WebFetch` https://axeghost.offprint.app/a/3mzhxoqpnh423-any-networked-co-player-can-act-as-the-server-in-a-godotsteam-game
- `WebFetch` https://godotsteam.com/tutorials/multiplayer_peer/
- `WebSearch` GodotSteam "AI" policy no AI generated code support Gramps
- `Bash` cd /tmp && gh api repos/GodotSteam/GodotSteam --jq '.pushed_at, .description, .default_branch' 2>&1 | head; gh api repos/GodotSteam/GodotSteam/readme --jq .cont…
- `WebFetch` https://github.com/GodotSteam/GodotSteam
- `WebFetch` https://codeberg.org/godotsteam/godotsteam
- `WebFetch` https://godotsteam.com/changelog/godot4/
- `WebSearch` Godot 4 MultiplayerSynchronizer "Node not found" spawn race condition late join error issue
- `WebSearch` Godot physics not deterministic rollback netcode netfox SG Physics 2D fixed point
- `WebFetch` https://foxssake.github.io/netfox/latest/netfox/tutorials/rollback-caveats/
- `WebFetch` https://www.summerengine.com/blog/best-ai-coding-assistant-for-godot
- `WebSearch` Claude Godot 联机 多人 代码 AI 写 GDScript 经验 Steam
- `WebFetch` https://forum.godotengine.org/t/deciding-on-multiplayer-architecture-for-steam/140817
- `WebSearch` Godot 4.7 release date stable 2026 multiplayer changes
- `WebSearch` Godot MCP run multiple instances multiplayer testing Claude host client two windows logs
- `WebFetch` https://gamedevaihub.com/best-godot-mcp-servers-claude-code/
- `Bash` cd /home/user/Deep-Research-skills/godot-steam-multiplayer-2d; sed -n 80,400p outline.yaml; grep -rn "A1\|B1\|C1\|E1" outline.yaml | head -30
- `WebFetch` https://en.wikipedia.org/wiki/Bow-wow_Battle
- `WebSearch` "Claude" Godot multiplayer itch.io devlog 2026 netcode "host" desync AI wrote
- `Bash` cat ~/.claude/skills/research/validate_json.py | head -60; ls /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/; f=$(ls /home/user/Deep-Resear…
- `Bash` sed -n 60,200p ~/.claude/skills/research/validate_json.py | grep -n "def \|flat\|nested\|category" | head -30
- `Write` /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Claude_Godot_Netcode_Capability.json
- `Bash` python ~/.claude/skills/research/validate_json.py -f godot-steam-multiplayer-2d/fields.yaml -j godot-steam-multiplayer-2d/results/Claude_Godot_Netcode_Capabilit…

### 交回的报告

I wrote the JSON for the item and it passes the validation script: 35 of 35 fields covered, all values in Chinese, with the `uncertain` array at the end. I did not commit it or push it to a research branch.

Output: /home/user/Deep-Research-skills/godot-steam-multiplayer-2d/results/Claude_Godot_Netcode_Capability.json

**Main conclusions**
- **Basic GDScript is no longer the bottleneck.** In the independent godot-llm-bench (15 GDScript tasks run headless on Godot 4.7.2, dated 2026-10-06), Claude Opus 5.5 and Sonnet 5.5 got 15/15 on the first try. Haiku 4.5 got 11/15 first try and 14/15 after one fix. The benchmark has no networking tasks, so these numbers do not carry over to netcode.
- **Godot 3 vs 4 mix-ups have mostly gone away in newer models.** In a ziva.sh test (May 2026), Claude 3.5 Sonnet and GPT-4o still wrote Godot 3 multiplayer code; Opus 4.7 got it right. The risk remains when no version is stated and in thinly documented areas such as netcode.
- **No controlled benchmark exists for AI-written Godot netcode** as of 2026-11. GDScript is not in MultiPL-E either. Most evidence comes from vendor blogs and personal accounts.
- **Confidence scores by task (1–5):**

| Task | Score |
|---|---|
| Steam Lobby, room list, invites | 4 |
| RPC + MultiplayerSynchronizer, host-authoritative sync | 4 |
| No host migration (graceful end, back to lobby) | 4 |
| Late join | 3 |
| Prediction + interpolation | 3 |
| D2 host migration within seconds | 2 |
| Diagnosing timing bugs that won't reproduce | 2 |
| Rollback / deterministic lockstep | 1–2 |
| Seamless host migration | 1 |

  The pattern is that Claude's limits track architectural complexity far more than player count.
- **Typical errors:**
  - `@rpc` missing `any_peer` or `call_local`.
  - Authority set at the wrong time (in `_ready`).
  - Node paths that differ between peers.
  - "Node not found" on late join.
  - GodotSteam version drift: two `SteamMultiplayerPeer` APIs (the expressobits version and the one merged into GodotSteam), and forgetting `run_callbacks`.
  - Using the 64-bit Steam ID as the `peer_id`.
  - Syncing everything at high frequency with no sense of bandwidth. In one second-hand case, an AI-written shooter was unplayable above 10 clients at about 3,000 input messages per second.
- **New facts worth flagging:**
  - The GodotSteam GitHub repo was archived on 2026-11-10 and moved to Codeberg (now 4.24, Steamworks SDK 1.65). This is after Claude's training cutoff.
  - The GodotSteam readme says no LLMs may be used for issues, patches or PRs, and violators may be blocked. Godot itself tightened its rules on AI-written contributions in July 2026. A developer who hits a library bug has to write the report in their own words.
  - A published, unpatched hole in `SteamMultiplayerPeer` (CVE-2026-123017, through v4.23.2) lets any player claim peer ID 1 and act as the server. Claude's default code would not guard against it.
- **Workflow:** Claude Code plus a Godot MCP server can close the write-test-fix loop for logic that isn't timing-sensitive. Steam itself cannot be tested with two clients on one machine and one account. The recommendation is a switchable Steam/local ENet transport layer (as in the JoshuaHieter example) so Claude can iterate on local ENet, with the developer doing periodic two-machine Steam tests.
- **Grid verdict:** feasible only for timing-tolerant play with no host migration. Frame-sensitive PVE is marginal. Frame-sensitive PVP is marginal at 4–6 players and not recommended at 7–12. D2 migration is marginal. Seamless migration is not recommended in any cell.

**Uncertain fields:**
- `architecture_codes`: the source material does not define A/B/C/E precisely; only D1–D4 are certain.
- `estimated_dev_weeks_solo`: no public data exists, so these are estimates.
- `cost_per_month`: Claude subscription prices still need checking.
- `common_claude_errors`: partly inferred from forum reports, with no Claude-specific statistics.
- `case_studies`: Bow-wow Battle's network approach and player count are not confirmed.

## Sources and References
1. godot-llm-bench (first-hand) https://github.com/flockbay/godot-llm-bench
2. recognizingpatterns Substack, 2026-11-16 https://recognizingpatterns.substack.com/p/ai-is-the-worst-at-godot-thats-why
3. ziva.sh Claude vs GPT-4o on Godot 4 APIs https://ziva.sh/blogs/claude-godot
4. godotlearning: where LLMs help and break https://godotlearning.com/blog/ai-write-gdscript-llm-godot
5. AI Godot 4 bugs that pass the parse check https://johnvanscoyoc.itch.io/godot-ai-agent-kit-rules-prompts-workflow-for-cursor-and-claude-code/devlog/1729187/3-godot-4-bugs-ai-writes-that-pass-the-parse-check-real-error-messages-included
6. Claude Code for Godot in 2026 https://dev.to/orellanaed/claude-code-for-godot-in-2026-connect-it-to-your-game-and-what-it-builds-37md
7. Vibe coding guide (AI shooter netcode failure) https://gamedevaihub.com/how-to-vibe-code-a-game-the-step-by-step-guide-2026/
8. Godot MCP server roundup https://gamedevaihub.com/best-godot-mcp-servers-claude-code/
9. Coding-Solo/godot-mcp PR #56 (multiple instances) https://gh.r-mj.com/Coding-Solo/godot-mcp/pull/56
10. JoshuaHieter/multiplayerSteamExample https://github.com/JoshuaHieter/multiplayerSteamExample
11. Hardwire (Claude-written multiplayer kit) https://hardwire-gamedev.itch.io/hardwire-godot-online
12. GodotSteam on Codeberg (no-LLM policy, 4.24) https://codeberg.org/godotsteam/godotsteam
13. GodotSteam peer ID forgery disclosure https://axeghost.offprint.app/a/3mzhxoqpnh423-any-networked-co-player-can-act-as-the-server-in-a-godotsteam-game
14. Godot Forum: Node not Found on late join https://forum.godotengine.org/t/node-not-found-multiplayersynchronizer-on-client-late-joining/137234
15. netfox rollback caveats https://foxssake.github.io/netfox/latest/netfox/tutorials/rollback-caveats/
16. Godot to ban almost all AI coding contributions https://www.gamedeveloper.com/business/godot-to-ban-almost-all-ai-coding-contributions
17. Multiplayer changes in Godot 4.0 report 2 https://godotengine.org/article/multiplayer-changes-godot-4-0-report-2/

The full list of 32 sources is in the JSON's `sources` field.
