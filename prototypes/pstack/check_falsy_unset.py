"""PSTACK PROTOTYPE (not product code): lint for `x or UNSET` on CLI options where 0/0.0 is a legal value.

Past mistake it catches: `cost_limit or UNSET` silently dropped `--cost-limit 0` (fixed twice: #575, #825).
Usage: python prototypes/pstack/check_falsy_unset.py FILE...   (exit 1 on findings)
"""

import ast
import sys
from pathlib import Path

NUMERIC = ("int", "float")


def findings(source: str, filename: str) -> list[str]:
    out = []
    for fn in ast.walk(ast.parse(source)):
        if not isinstance(fn, ast.FunctionDef):
            continue
        numeric = {
            a.arg for a in fn.args.args if a.annotation and any(t in ast.unparse(a.annotation) for t in NUMERIC)
        }
        for node in ast.walk(fn):
            if (
                isinstance(node, ast.BoolOp)
                and isinstance(node.op, ast.Or)
                and isinstance(node.values[-1], ast.Name)
                and node.values[-1].id == "UNSET"
                and isinstance(node.values[0], ast.Name)
                and node.values[0].id in numeric
            ):
                name = node.values[0].id
                out.append(
                    f"{filename}:{node.lineno}: `{name} or UNSET` drops a legal 0 value. "
                    f"Use `{name} if {name} is not None else UNSET`."
                )
    return out


if __name__ == "__main__":
    results = [f for p in sys.argv[1:] for f in findings(Path(p).read_text(), p)]
    print("\n".join(results) or "ok")
    sys.exit(1 if results else 0)
