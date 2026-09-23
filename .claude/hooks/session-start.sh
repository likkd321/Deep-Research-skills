#!/bin/bash
# SessionStart hook（仅 Claude Code on the web / 云端会话）：
# 把本仓库的 research skills、web-search agent 与策略模块装进 ~/.claude，
# 并确保 pyyaml 可用——新开的云端会话即可直接 /research、/research-deep、/research-report，
# 无需每次手动 cp。幂等：重复执行结果相同。
#
# 语言：默认装中文版 skills；设 RESEARCH_SKILLS_LANG=en 则装英文版（两者同名，只能二选一）。
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
LANG_VARIANT="${RESEARCH_SKILLS_LANG:-zh}"
SKILLS_SRC="$REPO/skills/research-$LANG_VARIANT"
SKILLS_DIR="$HOME/.claude/skills"
AGENTS_DIR="$HOME/.claude/agents"

if [ ! -d "$SKILLS_SRC" ]; then
  echo "session-start: 找不到 $SKILLS_SRC，跳过安装" >&2
  exit 0
fi

mkdir -p "$SKILLS_DIR" "$AGENTS_DIR"

# skills：research / research-add-items / research-add-fields / research-deep / research-report
for d in "$SKILLS_SRC"/*/; do
  name="$(basename "$d")"
  rm -rf "${SKILLS_DIR:?}/$name"
  cp -r "$d" "$SKILLS_DIR/$name"
done

# web-search agent（检索型 effort medium / 深度判断型 effort high）+ 策略模块（agent 正文会从 ~/.claude/agents/web-search-modules/ 读取模块）
for agent in web-search-agent web-search-agent-deep; do
  cp "$REPO/agents/$agent.md" "$AGENTS_DIR/$agent.md"
done
rm -rf "$AGENTS_DIR/web-search-modules"
cp -r "$REPO/agents/web-search-modules" "$AGENTS_DIR/web-search-modules"

# validate_json.py 依赖 pyyaml
if ! python3 -c "import yaml" >/dev/null 2>&1; then
  python3 -m pip install --quiet pyyaml
fi

echo "session-start: 已安装 research-$LANG_VARIANT skills 与 web-search agent 到 ~/.claude" >&2
