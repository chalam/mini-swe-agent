# Cost and step limits

## Sub-features
- `-l/--cost-limit N` stops once cost >= N. `-l 0` disables the limit. This regressed twice: #575 and #825.
- `agent.step_limit` (via `-c agent.step_limit=N`).
- A clean stop with non-interactive stdin (#850): exit code 0, `exit_status LimitsExceeded`, no traceback.

## How to get to it (user POV)
`mini -l 3 ...`, or `-c agent.step_limit=1`.

## Driving it with drive.sh
- `drive.sh cost_limit -l 3` should show LimitsExceeded, `api_calls 2`, and `calls.txt` = `one\ntwo`.
- `drive.sh cost_limit -l 0` should show Submitted, `api_calls 4`, and `calls.txt` ending in `three`.
- `drive.sh submit -c agent.step_limit=1` should show LimitsExceeded and `api_calls 1`.

## Gotchas
- The limit counts `extra.cost` from each output, not `cost_per_call`.
- drive.sh unsets `MSWEA_GLOBAL_COST_LIMIT` and `MSWEA_GLOBAL_CALL_LIMIT`. Cover the global limit with a pytest test instead.
