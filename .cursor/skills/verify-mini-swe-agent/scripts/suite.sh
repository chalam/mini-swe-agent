#!/usr/bin/env bash
# Offline test suite, excluding the two modules that need optional deps (contree_sdk, modal) not in '.[dev]'.
# Usage: suite.sh [pytest args]   e.g. suite.sh tests/agents -k cost
source "$(dirname "$0")/_common.sh"
cd "$REPO"
scratch=$(mktemp -d "${TMPDIR:-/tmp}/verify-mswea.XXXXXX"); echo "dir $scratch" >> "$STATE_FILE"
offline_env "$scratch" pytest -n auto -q -p no:cacheprovider \
  --ignore=tests/environments/extra/test_contree.py --ignore=tests/environments/extra/test_swerex_modal.py "$@"
