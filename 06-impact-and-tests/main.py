"""Module 06: from a graph to an answer - blast radius, tests to run, entry points, risk.

`impact(path)` is the tool an agent will call most. It combines:
  * transitive dependents (module 04),
  * test files among them (a test "covers" a file if it reaches it through imports),
  * entry points among them (a break there shows up at startup),
  * the honesty counters: a graph with unresolved edges gives a LOWER BOUND, and says so.

Run:  python 06-impact-and-tests/main.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(module_dir: str):  # type: ignore[no-untyped-def]
    path = HERE.parent / module_dir / "main.py"
    spec = importlib.util.spec_from_file_location("m_" + module_dir.replace("-", "_"), path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


m02 = load("02-resolving-modules")
m04 = load("04-graph-and-closure")
m05 = load("05-cycles-with-tarjan")


def is_test(path: str) -> bool:
    name = path.rsplit("/", 1)[-1]
    parts = path.split("/")[:-1]
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or re.search(r"\.(test|spec)\.[jt]sx?$", name) is not None
        or any(p in ("tests", "test", "__tests__") for p in parts)
    )


def entry_points(root: Path, files: list[str]) -> dict[str, str]:
    """Guess where execution starts: console scripts, `if __name__` guards, package.json main."""
    eps: dict[str, str] = {}
    index = m02.ModuleIndex([f for f in files if f.endswith(".py")])
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        in_scripts = False
        for line in pyproject.read_text(encoding="utf-8").splitlines():
            if line.startswith("["):
                in_scripts = line.strip() == "[project.scripts]"
            elif in_scripts and (m := re.match(r'\s*[\w-]+\s*=\s*"([\w.]+):', line)):
                target = index.names.get(m.group(1))
                if target:
                    eps[target] = "console script"
    for f in files:
        if f.endswith(".py") and re.search(r"^if __name__ ==", (root / f).read_text(encoding="utf-8"), re.M):
            eps.setdefault(f, "__main__ guard")
    for pj in root.rglob("package.json"):
        main = json.loads(pj.read_text(encoding="utf-8")).get("main")
        if main:
            rel = (pj.parent / main).relative_to(root).as_posix()
            if rel in files:
                eps[rel] = "package.json main"
    return {f: why for f, why in eps.items() if not is_test(f)}


def risk(n_transitive: int, n_files: int, entries: int) -> str:
    share = n_transitive / max(1, n_files)
    if n_transitive >= 25 or share >= 0.15:
        return "HIGH"
    if n_transitive >= 5 or share >= 0.05 or (entries and n_transitive >= 2):
        return "MEDIUM"
    return "LOW"


def impact(root: Path, g, path: str) -> str:  # type: ignore[no-untyped-def]
    if path not in g.nodes:
        raise ValueError(f"{path!r} is not a scanned file; known files start: {sorted(g.nodes)[:3]}")
    reach = g.reach(path, "in", 50)
    eps = entry_points(root, sorted(g.nodes))
    tests = sorted(f for f in reach if is_test(f))
    entries = sorted(f for f in reach if f in eps)
    cycles = m05.tarjan(sorted(g.nodes), g.out)
    in_cycle = any(path in c for c in cycles)
    level = risk(len(reach), len(g.nodes), len(entries))
    lines = [
        f"Impact of changing {path}",
        f"Direct dependents: {sum(1 for d in reach.values() if d == 1)}; transitive: {len(reach)}",
        f"Tests that reach it ({len(tests)}): {', '.join(tests) or 'none'}",
        f"Entry points affected ({len(entries)}): {', '.join(f'{e} [{eps[e]}]' for e in entries) or 'none'}",
        f"Risk: {level}" + (" (file is in an import cycle)" if in_cycle else ""),
    ]
    if g.unresolved or g.dynamic:
        lines.append("NOTE: unresolved/dynamic imports exist, so real dependents may be missing (lower bound).")
    lines.append(g.confidence())
    return "\n".join(lines)


if __name__ == "__main__":
    demo = HERE.parent / "demo"
    g = m04.build_graph(demo)
    files = sorted(g.nodes)
    eps = entry_points(demo, files)
    print("entry points:", eps)
    assert eps == {
        "src/shop/cli.py": "console script",
        "web/src/app.ts": "package.json main",
    }
    assert is_test("tests/test_cart.py") and is_test("web/src/index.test.ts") and not is_test("src/shop/cart.py")

    out = impact(demo, g, "src/shop/models.py")
    print(out)
    assert "Tests that reach it (1): tests/test_cart.py" in out
    assert "src/shop/cli.py [console script]" in out
    assert "(file is in an import cycle)" in out
    assert "lower bound" in out  # the demo has one dynamic import
    assert "Risk: HIGH" in out  # 5 of 11 files (45%) sit downstream

    out = impact(demo, g, "web/src/lazy.ts")
    assert "web/src/index.test.ts" in out and "web/src/app.ts [package.json main]" in out
    try:
        impact(demo, g, "nope.py")
    except ValueError as e:
        print("clear error:", e)
    else:
        raise AssertionError("expected ValueError")
    print("module 06 OK")
