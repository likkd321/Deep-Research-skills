#!/usr/bin/env bash
# Regression test for .claude/hooks/session-start.sh (Claude Code on the web bootstrap).
# Runs the hook against a throwaway HOME; never touches the real ~/.claude.
# Run:  bash tests/test_session_start_hook.sh   (exit 0 = all pass)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$ROOT_DIR/.claude/hooks/session-start.sh"
TMP_HOME="$(mktemp -d)"
trap 'rm -rf "$TMP_HOME"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -x "$HOOK" ]] || fail "hook is not executable: $HOOK"

# 1. Outside the web environment the hook is a no-op.
HOME="$TMP_HOME" CLAUDE_CODE_REMOTE="" CLAUDE_PROJECT_DIR="$ROOT_DIR" "$HOOK"
[[ ! -e "$TMP_HOME/.claude" ]] || fail "hook must not install anything when CLAUDE_CODE_REMOTE != true"

# 2. In the web environment it installs skills, agent and modules; running twice is idempotent.
for _ in 1 2; do
  HOME="$TMP_HOME" CLAUDE_CODE_REMOTE=true CLAUDE_PROJECT_DIR="$ROOT_DIR" "$HOOK" 2>/dev/null
done
for s in research research-add-items research-add-fields research-deep research-report; do
  [[ -f "$TMP_HOME/.claude/skills/$s/SKILL.md" ]] || fail "missing skill $s"
  diff -q "$ROOT_DIR/skills/research-zh/$s/SKILL.md" "$TMP_HOME/.claude/skills/$s/SKILL.md" >/dev/null \
    || fail "installed $s differs from skills/research-zh (default must be zh)"
done
[[ -f "$TMP_HOME/.claude/skills/research/validate_json.py" ]] || fail "validate_json.py not installed"
for a in web-search-agent web-search-agent-deep; do
  [[ -f "$TMP_HOME/.claude/agents/$a.md" ]] || fail "$a.md not installed"
done
for m in "$ROOT_DIR"/agents/web-search-modules/*.md; do
  [[ -f "$TMP_HOME/.claude/agents/web-search-modules/$(basename "$m")" ]] || fail "missing module $(basename "$m")"
done

# 3. RESEARCH_SKILLS_LANG=en installs the English variant.
HOME="$TMP_HOME" CLAUDE_CODE_REMOTE=true CLAUDE_PROJECT_DIR="$ROOT_DIR" RESEARCH_SKILLS_LANG=en "$HOOK" 2>/dev/null
diff -q "$ROOT_DIR/skills/research-en/research/SKILL.md" "$TMP_HOME/.claude/skills/research/SKILL.md" >/dev/null \
  || fail "RESEARCH_SKILLS_LANG=en did not install research-en"

# 4. The project-level agents (register both agent types in web sessions) must not drift from agents/.
for a in web-search-agent web-search-agent-deep; do
  diff -q "$ROOT_DIR/agents/$a.md" "$ROOT_DIR/.claude/agents/$a.md" >/dev/null \
    || fail ".claude/agents/$a.md drifted from agents/$a.md — re-copy it"
done

# 5. The two agent types differ only in frontmatter: same methodology body, effort medium vs high.
body() { awk '/^---$/ && n < 2 { n++; next } n >= 2' "$1"; }
[[ "$(body "$ROOT_DIR/agents/web-search-agent.md")" == "$(body "$ROOT_DIR/agents/web-search-agent-deep.md")" ]] \
  || fail "web-search-agent-deep.md body drifted from web-search-agent.md — keep the methodology identical"
grep -qx 'effort: medium' "$ROOT_DIR/agents/web-search-agent.md" || fail "web-search-agent must declare effort: medium"
grep -qx 'effort: high' "$ROOT_DIR/agents/web-search-agent-deep.md" || fail "web-search-agent-deep must declare effort: high"

# 6. settings.json registers the hook.
python3 - "$ROOT_DIR/.claude/settings.json" <<'PY' || fail "settings.json does not register the SessionStart hook"
import json, sys
cfg = json.load(open(sys.argv[1]))
cmds = [h["command"] for g in cfg["hooks"]["SessionStart"] for h in g["hooks"]]
assert any(c.endswith(".claude/hooks/session-start.sh") for c in cmds), cmds
PY

echo "PASS: session-start hook"
