# pstack plan for mini-swe-agent (offline-only)

Baseline at 04d809ce, branch pstack-setup, Python 3.13, `uv pip install -e '.[dev]'`:
- `pytest -n auto`: 545 passed, 61 skipped, 2 collection errors (contree_sdk, modal not in .[dev])
- the skill's `suite.sh` (same, minus those 2 modules): 545 passed, 61 skipped, 0 failed
- pyright: 140 errors (/workspace/pstack-evidence/pyright-baseline.txt)

## Evidence (reproduce with `python prototypes/pstack/mine_history.py [--list CLASS]`)

| Measure | Count |
|---|---|
| Commits | 1022 |
| Fix or revert commits | 172 |
| Fix commits that touch tests/ | 49 of 172 |
| Fix commits by class | message_shape 40, interactive_ui 36, config_resolution 26, limits_accounting 19, env_backends 19, exit_and_errors 15 |
| Fix commits touching 2 or more sibling model implementations | 11 |
| Fix commits touching 2 or more sibling environment implementations | 12 |
| All commits touching 3 or more model implementations | 47 |

Duplication (`prototypes/pstack/duplication.py`):
- `format_observation_messages` is byte-identical in 7 of 10 model classes.
- `serialize` is identical in 6 of 6 model classes and in 7 of 7 environment classes.
- `_check_finished` is identical in 7 of 7 environment classes.

## Plan, ordered by leverage
1. Make the offline verification skill the definition of done: `.cursor/skills/verify-mini-swe-agent`. (Done.)
2. Add a pytest that runs the real `mini` CLI as a subprocess with the scenario YAMLs (submit, toolcall, cost_limit at `-l 3` and `-l 0`, step_limit). Today the only end-to-end test patches the litellm class, the first-run prompt, and the stdin prompts.
3. Add a contract test parametrized over `_MODEL_CLASS_MAPPING`. It checks `format_message`, `format_observation_messages`, and `serialize` shapes for each of the 3 message formats. This targets the 40 message-shape fixes.
4. Add an environment protocol test over every importable `_ENVIRONMENT_MAPPING` class. It checks the `execute()` keys (`output`, `returncode`, `exception_info`) and the `_check_finished` semantics. This targets #747 and #764.
5. Add a limits table test over (cost_limit, step_limit, per-call cost, parse failure), covering 0 = disabled and the #915 billed-parse-failure case. Add `check_falsy_unset.py` to pre-commit.
6. Add config-merge table tests: `-c` ordering, `key=value` with `=` in the value, empty keys, CLI flags beating `-c`, and UTF-8 reads.
7. Add a pyright ratchet in CI that fails when the count goes above 140.
8. Only after tests 3 and 4 exist, consider folding the byte-identical `serialize`, `_check_finished`, and `format_observation_messages` copies into shared helpers. AGENTS.md favours small polymorphic classes, so this is the lowest-leverage step.
