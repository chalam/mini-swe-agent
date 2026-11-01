# Config specs and overrides

## Sub-features
- `-c` accepts builtin names (`mini.yaml`), file paths, and `key=value` (dotted keys, values that contain `=`). Specs merge recursively in order.
- CLI flags (`-m`, `--model-class`, `-l`, `-y`, `--exit-immediately`, `-o`) override the `-c` specs.
- Setting any `-c` drops the default `mini.yaml`, as documented in `--help`.

## How to get to it (user POV)
`mini -c mini.yaml -c agent.step_limit=5 -c model.model_kwargs.temperature=0`

## Driving it with drive.sh
- `drive.sh submit -c agent.step_limit=1` proves a key=value override reaches the agent (LimitsExceeded, `api_calls 1`).
- To prove a merged value, read it from the trajectory: `python -c "import json;print(json.load(open('<ev>/run.traj.json'))['info']['config']['agent']['step_limit'])"`.

## Gotchas
- The config cluster has 26 fix commits in history (UTF-8 reads #892, empty keys #883, multiple `=` b6705754, env config ignored #700). Re-run these drives after touching `config/__init__.py`, `utils/serialize.py`, or `run/mini.py`.
- `cost_limit: 0` and similar falsy-but-legal values: `prototypes/pstack/check_falsy_unset.py <files>` lints for `x or UNSET`.
