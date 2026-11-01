#!/usr/bin/env bash
# Read-only: is this checkout worth driving? Exit 0 = yes. Never installs or deletes anything.
source "$(dirname "$0")/_common.sh"
fail=0; ok() { echo "OK   $*"; }; bad() { echo "FAIL $*"; fail=1; }
cd "$REPO"
# Importing minisweagent mkdirs and reads the global config dir; point it at a throwaway dir so doctor never touches ~/.config.
export MSWEA_SILENT_STARTUP=1 MSWEA_CONFIGURED=1 MSWEA_GLOBAL_CONFIG_DIR="$(mktemp -d)"; trap 'rm -rf "$MSWEA_GLOBAL_CONFIG_DIR"' EXIT
echo "repo: $REPO  branch: $(git branch --show-current)  head: $(git rev-parse --short HEAD)"
[ -x "$VENV/bin/mini" ] && ok "venv entry points ($VENV/bin/mini)" || bad "no $VENV/bin/mini -> run: uv venv .venv && uv pip install -p .venv -e '.[dev]'"
inst=$("$VENV/bin/python" -c "import minisweagent,pathlib;print(pathlib.Path(minisweagent.__file__).resolve())" 2>&1)
[[ "$inst" == "$REPO/src/"* ]] && ok "minisweagent imports from this checkout ($inst)" || bad "minisweagent resolves to '$inst' (not an editable install of $REPO)"
"$VENV/bin/python" -c "from minisweagent.models import get_model_class as g; g('x','deterministic'); g('x','minisweagent.models.test_models.DeterministicToolcallModel')" 2>/dev/null \
  && ok "deterministic models importable" || bad "deterministic models not importable"
v=$(MSWEA_SILENT_STARTUP=1 "$VENV/bin/python" -c "import minisweagent;print(minisweagent.__version__)" 2>&1) && ok "version $v" || bad "version: $v"
MSWEA_SILENT_STARTUP=1 timeout 20 "$VENV/bin/mini" --help >/dev/null 2>&1 && ok "mini --help" || bad "mini --help"
MSWEA_SILENT_STARTUP=1 timeout 20 "$VENV/bin/mini-extra" inspector --help >/dev/null 2>&1 && ok "mini-extra inspector --help" || bad "mini-extra inspector --help"
command -v tmux >/dev/null && ok "tmux (needed only for the inspector drive)" || echo "WARN no tmux: inspector drive unavailable"
for k in OPENAI_API_KEY ANTHROPIC_API_KEY OPENROUTER_API_KEY; do [ -n "${!k:-}" ] && echo "NOTE $k is set in this shell; drive.sh unsets it anyway (offline only)"; done
[ -s "$STATE_FILE" ] && echo "NOTE leftover scratch from earlier runs listed in $STATE_FILE -> run cleanup.sh"
exit $fail
