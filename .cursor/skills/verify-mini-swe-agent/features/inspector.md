# Trajectory inspector

## Sub-features
- Opens a `.traj.json` file or a directory of them. Header reads `Trajectory i/N - <file> - Step k/M`.
- Navigation: `l`/`h` steps, `0`/`$` first and last, `L`/`H` trajectories, `r` reasoning, `q` quit.

## How to get to it (user POV)
`mini-extra inspector <path>` (aliases: `inspect`, `i`).

## Driving it with inspect.sh
1. `drive.sh submit` to produce a trajectory.
2. `inspect.sh <ev>/run.traj.json`.

`inspector-0-first.txt` should show `Step 1/3` and the SYSTEM text. `inspector-1-last.txt` should show `Step 3/3`, `EXIT`, and `verify-ok`. `inspector-2-quit.txt` should show `INSPECTOR_EXITED=0`.

## Gotchas
- Needs tmux. The pane is fixed at 160x45, so layout assertions depend on that size.
- `e`/`E` shell out to `jless`, which is not installed. Don't drive those keys.
