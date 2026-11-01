# Feature map: mini-swe-agent (offline)

| Feature | File | Harness |
|---|---|---|
| Local agent run (`mini`) with text-based and tool-call models | [mini-run.md](mini-run.md) | drive.sh |
| Cost and step limits | [limits.md](limits.md) | drive.sh |
| Config specs and overrides (`-c file`, `-c key=value`, CLI flags) | [config.md](config.md) | drive.sh |
| Trajectory inspector (`mini-extra inspector`) | [inspector.md](inspector.md) | inspect.sh (tmux) |
| Offline test suite | [test-suite.md](test-suite.md) | suite.sh |

If a feature needs docker, podman, or an API key, list it here as unverifiable. Don't drop it from the map:
- swebench, swebench-single, and programbench runners (docker/podman)
- container environments: docker, singularity, bubblewrap, swerex, modal, contree
- live provider calls (tests/test_fire.py)
