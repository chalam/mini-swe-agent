#!/usr/bin/env bash
# Remove only what drive.sh/inspect.sh created (listed in the state file). Evidence under $EVIDENCE_ROOT is kept.
source "$(dirname "$0")/_common.sh"
[ -f "$STATE_FILE" ] || { echo "nothing to clean"; exit 0; }
while read -r kind val; do
  case "$kind" in
    dir) [[ "$val" == */verify-mswea.* ]] && rm -rf -- "$val" && echo "removed $val" ;;
    tmux) tmux kill-session -t "$val" 2>/dev/null && echo "killed tmux $val" ;;
  esac
done < "$STATE_FILE"
rm -f "$STATE_FILE"; echo "evidence kept in $EVIDENCE_ROOT"
