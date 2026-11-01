#!/usr/bin/env bash
# Drive the Textual trajectory inspector in a private tmux session and capture screens.
# Usage: inspect.sh <run.traj.json>   (screens land next to the trajectory: inspector-*.txt)
set -uo pipefail
source "$(dirname "$0")/_common.sh"
traj="$(realpath "$1")"; ev="$(dirname "$traj")"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/verify-mswea.XXXXXX"); echo "dir $scratch" >> "$STATE_FILE"
sess="verify-mswea-insp-$$"; echo "tmux $sess" >> "$STATE_FILE"
tmux new-session -d -s "$sess" -x 160 -y 45 "$(declare -f offline_env); VENV=$VENV; offline_env $scratch mini-extra inspector $(printf %q "$traj"); echo INSPECTOR_EXITED=\$?; sleep 30"
wait_for() { for _ in $(seq 1 40); do tmux capture-pane -p -t "$sess" | grep -q "$1" && return 0; sleep 0.25; done; return 1; }
wait_for "Step" || { tmux capture-pane -p -t "$sess" > "$ev/inspector-FAILED.txt"; echo "inspector never rendered; see $ev/inspector-FAILED.txt"; tmux kill-session -t "$sess"; exit 1; }
sleep 0.5; tmux capture-pane -p -t "$sess" > "$ev/inspector-0-first.txt"
tmux send-keys -t "$sess" '$'; sleep 0.8; tmux capture-pane -p -t "$sess" > "$ev/inspector-1-last.txt"
tmux send-keys -t "$sess" q; wait_for "INSPECTOR_EXITED=" ; tmux capture-pane -p -t "$sess" > "$ev/inspector-2-quit.txt"
tmux kill-session -t "$sess" 2>/dev/null
grep -o "INSPECTOR_EXITED=[0-9]*" "$ev/inspector-2-quit.txt"; ls "$ev"/inspector-*.txt
