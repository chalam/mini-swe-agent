---
name: verify-mini-swe-agent
description: Prove mini-swe-agent behavior offline by driving the real `mini` CLI (and the `mini-extra inspector` TUI) with the repo's deterministic test models, no API key. Use after any change to agents, models, environments, config merging, limits, or run scripts, before claiming it works.
---

# Verify mini-swe-agent (offline)

Surface: the `mini` CLI (primary), the `mini-extra inspector` Textual TUI, and the Python library. Swebench/programbench runners need docker or podman; this box has neither, so they are out of scope (see Gotchas).

How it stays offline: `model.model_class: deterministic` (`minisweagent.models.test_models.DeterministicModel`) replays the `outputs` list from a YAML scenario, so the real CLI → config merge → agent loop → `LocalEnvironment` → trajectory path runs, and only the LM call is scripted. `drive.sh` unsets every provider key and `MSWEA_MODEL_NAME`, so a run that tries to reach litellm fails loudly instead of spending money.

All helpers live in `scripts/` and work from any cwd. `$S` below means `.cursor/skills/verify-mini-swe-agent/scripts`.

## Launch

`mini` is short-lived, so launch means installing once, then giving every drive its own scratch dir.

```bash
cd <repo> && uv venv .venv && uv pip install -p .venv -e '.[dev]'   # once; ~5 s with a warm uv cache
```

Each `drive.sh` run creates a fresh `/tmp/verify-mswea.XXXXXX/{cfg,work}`. `cfg` is the isolated `MSWEA_GLOBAL_CONFIG_DIR`, so `~/.config/mini-swe-agent/.env` is never read or written, and `work` is the agent's cwd. The run also sets `MSWEA_CONFIGURED=1` to skip the first-run setup prompt, and `-y --exit-immediately </dev/null` so nothing waits on stdin. Several drives can run side by side because nothing is shared.

## Doctor

```bash
$S/doctor.sh      # read-only; exit 0 = worth driving
```

It checks four things: the venv entry points exist, `minisweagent` imports from THIS checkout (catches a stale non-editable install), both deterministic model classes resolve through `get_model_class`, and `mini --help` and `mini-extra inspector --help` run. It also reports leftover scratch from earlier runs.

## Drive

```bash
$S/drive.sh <scenario> [extra mini args]
```

The scenario is a name from `scenarios/` or a path to your own YAML. It runs:
`mini -c mini.yaml -c <scenario> -t "verify scenario <name>" -y --exit-immediately -o <evidence>/run.traj.json [extra args]`

| Scenario | Command | Must show |
|---|---|---|
| `submit` | `drive.sh submit` | `exit_status: Submitted`, `submission: "verify-ok\n"`, `api_calls: 2`, `cost: 1.0`, `proof.txt` in workdir_files |
| `toolcall` | `drive.sh toolcall` | `Submitted`, roles contain `tool` (tool-call message shape), model_type `DeterministicToolcallModel` |
| `cost_limit` | `drive.sh cost_limit -l 3` | `LimitsExceeded`, `api_calls: 2`, `calls.txt` = one,two (call 3 never ran), exit_code 0, no traceback |
| `cost_limit` | `drive.sh cost_limit -l 0` | `0` disables the limit: `Submitted`, `api_calls: 4`, calls.txt has `three` |
| `submit` | `drive.sh submit -c agent.step_limit=1` | `LimitsExceeded`, `api_calls: 1` |

To write a new scenario, copy one from `scenarios/`. Each `outputs` item is `{role: assistant, content, extra: {cost, actions: [{command}]}}`. Toolcall items also need `tool_calls` plus a matching `tool_call_id` in each action. `__WORKDIR__` is replaced with the scratch workdir. Special actions from `test_models._process_test_actions`: `{command: "/sleep 2"}` sleeps, then that output is skipped and the next one replayed. `/warning msg` logs a warning and does the same. There is also `raise`, but YAML cannot carry an exception object, so use pytest for that.

Run the TUI against any trajectory:

```bash
$S/inspect.sh <evidence-dir>/run.traj.json
```

This starts a private tmux session `verify-mswea-insp-<pid>`, waits for `Step` in the header, captures the first screen, presses `$` (last step) and captures again, then presses `q` and checks that `INSPECTOR_EXITED=0` appears.

Tests (offline; provider-key tests self-skip):

```bash
$S/suite.sh [pytest args]
```

This runs `pytest -n auto` without the two modules that need optional deps (see Gotchas). Baseline at 04d809ce: **545 passed, 61 skipped, 0 failed**.

## Evidence

Evidence lives in `${VERIFY_EVIDENCE_DIR:-/workspace/verify-evidence}/<YYYYmmdd-HHMMSS>-<scenario>/`:
- `cmd.txt`: the exact command line
- `scenario.yaml`: the resolved scenario
- `transcript.txt`: the full stdout and stderr of the CLI
- `exit_code`
- `run.traj.json`: the real trajectory file the CLI wrote
- `workdir_files.txt`: every file the agent's commands created, with its contents. This is the side effect, so check it as well as the exit status.
- `summary.json`: exit_status, submission, api_calls, cost, message roles, model_type, and whether the transcript contains a traceback
- `inspector-*.txt`: TUI screen captures, written when you run inspect.sh

Proof standards:
- Drive the CLI, not `main()` with patches. `tests/run/test_local.py` already covers the patched path.
- A claim about limits needs the side-effect file to show that the over-limit command never ran, not just the `exit_status`.
- A claim about message shape needs the roles list or the trajectory messages, not just the transcript.
- For a change in config merging, show the merged value in `run.traj.json` → `info.config`.
- Report the evidence dir path in your answer.

## Cleanup

```bash
$S/cleanup.sh
```

This removes only the scratch dirs and tmux sessions recorded in `/tmp/verify-mswea.state`, the ones our scripts created. It never kills by process name, and it never touches `$VERIFY_EVIDENCE_DIR`. Run it after every failed iteration too.

## Gotchas

- Plain `pytest` collects `tests/environments/extra/test_contree.py` and `test_swerex_modal.py`, which fail with errors because `contree_sdk` and `modal` are not part of `.[dev]`. That gives 545 passed, 61 skipped, **2 errors**. `suite.sh` leaves those two modules out. Install the extras only if your change touches them.
- `tests/run/test_cli_integration.py` shells out to `mini-extra`. Run it with the venv on PATH (suite.sh does this). Without that, 9 tests fail with FileNotFoundError, which looks like a regression and isn't.
- `extra.cost` in each output is what the agent's `cost_limit` counts. `cost_per_call` only feeds GLOBAL_MODEL_STATS. If you leave `extra.cost` out, cost stays 0 and the limit never fires.
- Rich renders observations in `transcript.txt` with the markup stripped. Read `run.traj.json` for the exact observation text.
- Not verifiable here: docker, podman, singularity, bubblewrap, swerex, and modal environments; swebench and programbench batch runs; and the live tests in tests/test_fire.py, which need keys. Say so explicitly when a change touches them.
