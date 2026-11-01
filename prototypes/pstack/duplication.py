"""PSTACK PROTOTYPE (not product code): measure copy-paste across sibling implementations.

Answers the open question "would one shared query()/execute() skeleton absorb the provider/backend classes,
or do they genuinely differ?" Usage: python prototypes/pstack/duplication.py
"""

import ast
import difflib
import importlib
import inspect
import os
import textwrap

os.environ.setdefault("MSWEA_SILENT_STARTUP", "1")

from minisweagent.environments import _ENVIRONMENT_MAPPING  # noqa: E402
from minisweagent.models import _MODEL_CLASS_MAPPING  # noqa: E402


def load(path: str):
    module, name = path.rsplit(".", 1)
    try:
        return getattr(importlib.import_module(module), name)
    except ImportError as e:
        print(f"  skip {path}: {e}")
        return None


def method_src(cls, name: str) -> str | None:
    fn = cls.__dict__.get(name)
    return ast.unparse(ast.parse(textwrap.dedent(inspect.getsource(fn)))) if fn else None


def report(title: str, mapping: dict[str, str], methods: list[str], reference: str) -> None:
    classes = {k: c for k, v in mapping.items() if (c := load(v))}
    print(f"\n## {title} (reference: {reference})")
    for m in methods:
        ref = method_src(classes[reference], m)
        own = {k: method_src(c, m) for k, c in classes.items()}
        defined = [k for k, s in own.items() if s]
        identical = [k for k in defined if own[k] == ref]
        ratios = {k: difflib.SequenceMatcher(None, ref or "", own[k]).ratio() for k in defined if k != reference}
        print(f"{m}: defined in {len(defined)}/{len(classes)} classes; byte-identical to reference: {len(identical)}")
        for k, r in sorted(ratios.items(), key=lambda kv: -kv[1]):
            print(f"    {k:22s} similarity {r:.2f}")


report(
    "Model classes",
    _MODEL_CLASS_MAPPING,
    ["query", "format_observation_messages", "serialize", "_calculate_cost"],
    "litellm",
)
report("Environment classes", _ENVIRONMENT_MAPPING, ["_check_finished", "execute", "serialize"], "local")
