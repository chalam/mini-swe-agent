"""PSTACK PROTOTYPE (not product code): mine git history for recurring fix classes.

Usage: python prototypes/pstack/mine_history.py [--list CLASS]
Reproduces every number in prototypes/pstack/PLAN.md section "Evidence".
"""

import re
import subprocess
import sys
from collections import Counter

CLASSES = {
    "config_resolution": r"config|override|env var|setdefault|default value|preference|ignored|not used|reload|"
    r"equals sign|override key|cost.limit.*(0|zero)|accept 0|integer notation|discoverable|instance_spec",
    "limits_accounting": r"cost|limit|n_calls|call count|count of|counting|overcount|time limit|wall.clock|kill",
    "message_shape": r"content|string|message|serializ|thinking|cache.control|tool.?call|'command'|args|"
    r"response api|newline|stdout as final|submission",
    "template_vars": r"template|undefined|f-string|working_dir|processor",
    "interactive_ui": r"textual|interactive|human mode|confirm|yolo|scroll|highlight|auto.follow|command palette|"
    r"shortcut|mode switch|switching|progress|inspector|visual mode|exit-immediately|banner",
    "env_backends": r"environment|docker|singularity|apptainer|bubblewrap|contree|modal|swerex|process group|bashrc|"
    r"container",
    "encoding": r"utf|unicode|ansi|emoji|null byte|non-utf",
    "concurrency": r"race|thread|shared config|interruptible|keyboardinterrupt",
    "exit_and_errors": r"exception|exit.status|exit_status|retry|retries|reraise|errors in __init__|"
    r"result variable|on_instance_end|abort",
    "packaging_cli": r"dependencies|__init__ files|import paths|imports|invokation|invocation|option flag|"
    r"pre-commit|-v attribute",
}

FIX = re.compile(r"^(fix|hotfix)\b|^revert", re.I)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def commits() -> list[tuple[str, str, list[str]]]:
    out = git("log", "--format=@@%h|%s", "--name-only")
    result = []
    for block in out.split("@@")[1:]:
        head, *files = block.strip().split("\n")
        sha, subject = head.split("|", 1)
        result.append((sha, subject, [f for f in files if f]))
    return result


def sibling_count(files: list[str], kind: str) -> int:
    pat = {
        "models": r"models/(?!__init__|utils/|test_models)[a-z_]+_model\.py$",
        "environments": r"environments/(extra/)?(?!__init__)[a-z_]+\.py$",
    }[kind]
    return len({f for f in files if re.search(pat, f)})


def main() -> None:
    allc = commits()
    fixes = [c for c in allc if FIX.search(c[1])]
    print(f"total commits: {len(allc)}  fix/revert commits: {len(fixes)}")
    counts = Counter()
    members: dict[str, list[str]] = {k: [] for k in CLASSES}
    unclassified = []
    for sha, subject, _files in fixes:
        hit = False
        for name, pat in CLASSES.items():
            if re.search(pat, subject, re.I):
                counts[name] += 1
                members[name].append(f"{sha} {subject}")
                hit = True
        if not hit:
            unclassified.append(f"{sha} {subject}")
    print("\nfix classes (multi-label, subject regex):")
    for name, n in counts.most_common():
        print(f"  {n:4d}  {name}")
    print(f"  {len(unclassified):4d}  (unclassified)")

    with_tests = sum(any(f.startswith("tests/") for f in files) for _, _, files in fixes)
    print(f"\nfix commits that touch tests/: {with_tests}/{len(fixes)}")
    for kind in ("models", "environments"):
        multi = [(s, subj, sibling_count(fs, kind)) for s, subj, fs in fixes if sibling_count(fs, kind) >= 2]
        print(f"fix commits touching >=2 sibling {kind} implementations: {len(multi)}")
    allmulti = [(s, subj, sibling_count(fs, "models")) for s, subj, fs in allc if sibling_count(fs, "models") >= 3]
    print(f"all commits touching >=3 sibling model implementations: {len(allmulti)}")

    if "--list" in sys.argv:
        name = sys.argv[sys.argv.index("--list") + 1]
        print("\n".join(unclassified if name == "unclassified" else members[name]))


if __name__ == "__main__":
    main()
