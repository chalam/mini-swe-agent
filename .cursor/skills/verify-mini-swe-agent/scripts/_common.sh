# Sourced by the other scripts. Paths are absolute so scripts work from any cwd.
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$SKILL_DIR/../../.." && pwd)"
VENV="$REPO/.venv"
EVIDENCE_ROOT="${VERIFY_EVIDENCE_DIR:-/workspace/verify-evidence}"
STATE_FILE="${TMPDIR:-/tmp}/verify-mswea.state"   # one line per scratch dir / tmux session WE created
# Offline + hermetic: no first-run prompt, no banner, global config isolated per run, no key leakage.
offline_env() {
  env -u OPENAI_API_KEY -u ANTHROPIC_API_KEY -u OPENROUTER_API_KEY -u PORTKEY_API_KEY -u REQUESTY_API_KEY \
      -u MSWEA_MODEL_NAME -u MSWEA_GLOBAL_COST_LIMIT -u MSWEA_GLOBAL_CALL_LIMIT \
      MSWEA_CONFIGURED=1 MSWEA_SILENT_STARTUP=1 MSWEA_GLOBAL_CONFIG_DIR="$1/cfg" PATH="$VENV/bin:$PATH" "${@:2}"
}
