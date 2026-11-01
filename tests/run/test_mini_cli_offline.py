"""Run the real `mini` entry point in a subprocess against deterministic scenario configs (no API key, no mocks)."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCENARIOS = Path(__file__).parent.parent / "test_data" / "cli_scenarios"
MINI = Path(sys.executable).parent / "mini"


def run_mini(tmp_path: Path, scenario: str, *args: str) -> tuple[subprocess.CompletedProcess, dict, Path]:
    work = tmp_path / "work"
    work.mkdir()
    traj = tmp_path / "run.traj.json"
    env = {k: v for k, v in os.environ.items() if not k.startswith("MSWEA_") and not k.endswith("_API_KEY")}
    env |= {"MSWEA_CONFIGURED": "1", "MSWEA_SILENT_STARTUP": "1", "MSWEA_GLOBAL_CONFIG_DIR": str(tmp_path / "cfg")}
    cmd = [str(MINI), "-c", "mini.yaml", "-c", str(SCENARIOS / f"{scenario}.yaml"), "-t", "offline", "-y"]
    result = subprocess.run(
        [*cmd, "--exit-immediately", "-o", str(traj), *args],
        cwd=work,
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Traceback" not in result.stdout + result.stderr
    return result, json.loads(traj.read_text()), work


@pytest.mark.parametrize(
    ("scenario", "args", "exit_status", "api_calls", "cost", "side_effect"),
    [
        ("submit", (), "Submitted", 2, 1.0, ("proof.txt", "hello-from-verify\n")),
        ("toolcall", (), "Submitted", 2, 1.0, ("proof.txt", "toolcall-ok\n")),
        ("cost_limit", ("-l", "3"), "LimitsExceeded", 2, 4.0, ("calls.txt", "one\ntwo\n")),
        ("cost_limit", ("-l", "0"), "Submitted", 4, 6.0, ("calls.txt", "one\ntwo\nthree\n")),
        ("cost_limit", ("-l", "0", "-c", "agent.step_limit=1"), "LimitsExceeded", 1, 2.0, ("calls.txt", "one\n")),
        ("cost_limit", ("-c", "agent.cost_limit=0", "-l", "3"), "LimitsExceeded", 2, 4.0, ("calls.txt", "one\ntwo\n")),
    ],
)
def test_mini_cli_offline(tmp_path, scenario, args, exit_status, api_calls, cost, side_effect):
    _, traj, work = run_mini(tmp_path, scenario, *args)
    assert traj["info"]["exit_status"] == exit_status
    assert traj["info"]["model_stats"] == {"instance_cost": cost, "api_calls": api_calls}
    assert (work / side_effect[0]).read_text() == side_effect[1]


def test_mini_cli_offline_submission_and_message_shape(tmp_path):
    _, text, _ = run_mini(tmp_path, "submit")
    assert text["info"]["submission"] == "verify-ok\n"
    assert [m["role"] for m in text["messages"]] == ["system", "user", "assistant", "user", "assistant", "exit"]
    (tmp_path / "tc").mkdir()
    _, tool, _ = run_mini(tmp_path / "tc", "toolcall")
    assert [m["role"] for m in tool["messages"]] == ["system", "user", "assistant", "tool", "assistant", "tool", "exit"]
    assert [m["tool_call_id"] for m in tool["messages"] if m["role"] == "tool"] == ["call_1", "call_2"]


def test_mini_cli_offline_config_override_reaches_trajectory(tmp_path):
    _, traj, _ = run_mini(tmp_path, "submit", "-c", "agent.step_limit=7", "-c", "model.cost_per_call=0.25")
    assert traj["info"]["config"]["agent"]["step_limit"] == 7
    assert traj["info"]["config"]["model"]["cost_per_call"] == 0.25
    assert traj["info"]["config"]["model_type"] == "minisweagent.models.test_models.DeterministicModel"
