# Offline test suite

## Sub-features
- Unit and integration tests built on the deterministic models (`tests/models/test_test_models.py`, `tests/agents/*`, `tests/run/test_local.py`, `tests/run/test_cli_integration.py`).

## How to get to it (user POV)
A contributor runs `pytest -n auto`.

## Driving it with suite.sh
`suite.sh` should give `553 passed, 61 skipped` (545 at 04d809ce, plus the 8 CLI tests). To target an area: `suite.sh tests/agents -k limit`.

## Gotchas
- The 61 skips are docker/podman/singularity (unavailable), programbench (not installed), and API-key tests. A skip count that changes with no new tests means an environment change, not a pass.
- `tests/run/test_local.py` patches `configure_if_first_time`, the litellm class, and the prompts. `tests/run/test_mini_cli_offline.py` covers the unpatched CLI subprocess path with the same scenarios drive.sh uses.
