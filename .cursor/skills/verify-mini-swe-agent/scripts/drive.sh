#!/usr/bin/env bash
# Drive the real `mini` CLI offline against a deterministic scenario.
# Usage: drive.sh <scenario-name|path.yaml> [extra mini args, e.g. -l 3 or -c agent.step_limit=1]
# Prints the evidence dir and a JSON summary. Exit code = mini's exit code.
set -uo pipefail
source "$(dirname "$0")/_common.sh"
scen="$1"; shift
[ -f "$scen" ] || scen="$REPO/tests/test_data/cli_scenarios/$scen.yaml"
[ -f "$scen" ] || { echo "no scenario $scen"; exit 2; }
name=$(basename "$scen" .yaml)
scratch=$(mktemp -d "${TMPDIR:-/tmp}/verify-mswea.XXXXXX"); echo "dir $scratch" >> "$STATE_FILE"
mkdir -p "$scratch/cfg" "$scratch/work"
ev="$EVIDENCE_ROOT/$(date +%Y%m%d-%H%M%S)-$name"; mkdir -p "$ev"
cp "$scen" "$ev/scenario.yaml"
cmd=(mini -c mini.yaml -c "$ev/scenario.yaml" -t "verify scenario $name" -y --exit-immediately -o "$ev/run.traj.json" "$@")
printf '%q ' "${cmd[@]}" > "$ev/cmd.txt"; echo >> "$ev/cmd.txt"
( cd "$scratch/work" && offline_env "$scratch" timeout 120 "${cmd[@]}" </dev/null >"$ev/transcript.txt" 2>&1 ); rc=$?
echo "$rc" > "$ev/exit_code"
( cd "$scratch/work" && find . -type f -exec sh -c 'echo "== $1"; head -c 2000 "$1"' _ {} \; ) > "$ev/workdir_files.txt"
"$VENV/bin/python" - "$ev" "$rc" > "$ev/summary.json" <<'PY'
import json, sys
from pathlib import Path
ev, rc = Path(sys.argv[1]), int(sys.argv[2])
t = ev / "run.traj.json"
s = {"exit_code": rc, "traj_written": t.exists()}
if t.exists():
    d = json.loads(t.read_text())
    info = d.get("info", {})
    s |= {"exit_status": info.get("exit_status"), "submission": info.get("submission"),
          "api_calls": info.get("model_stats", {}).get("api_calls"), "cost": info.get("model_stats", {}).get("instance_cost"),
          "roles": [m.get("role") for m in d.get("messages", [])],
          "model_type": info.get("config", {}).get("model_type")}
s["traceback_in_transcript"] = "Traceback (most recent call last)" in (ev / "transcript.txt").read_text()
print(json.dumps(s, indent=1))
PY
echo "evidence: $ev"; cat "$ev/summary.json"
exit $rc
