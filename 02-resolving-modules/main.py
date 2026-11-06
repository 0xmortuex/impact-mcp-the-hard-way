"""Module 02: turn import statements into edges between FILES.

An import names a module ("shop.models"); a graph needs a file ("src/shop/models.py").
This module builds the name -> file index and resolves absolute and relative imports.

Run:  python 02-resolving-modules/main.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT_DEMO = HERE.parent / "demo"


def load(module_dir: str):  # type: ignore[no-untyped-def]
    """Import another module's main.py by directory name (dir names start with digits)."""
    path = HERE.parent / module_dir / "main.py"
    spec = importlib.util.spec_from_file_location("m_" + module_dir.replace("-", "_"), path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


m01 = load("01-ast-imports")

IGNORED = {".git", "node_modules", "venv", ".venv", "dist", "build", "__pycache__"}


def walk_files(root: Path, suffixes: tuple[str, ...]) -> list[str]:
    """Project-relative POSIX paths of source files, skipping ignored directories."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORED)
        for name in sorted(filenames):
            if name.endswith(suffixes):
                found.append((Path(dirpath) / name).relative_to(root).as_posix())
    return found


class ModuleIndex:
    """Maps dotted module names to files, for every plausible import root.

    A file `src/shop/models.py` is importable as `shop.models` when `src/` is an import
    root (src layout) and as `src.shop.models` when the project root is one. We register
    both; resolution simply asks "is this name in the index?".
    """

    def __init__(self, files: list[str]) -> None:
        roots = [""] + (["src"] if any(f.startswith("src/") for f in files) else [])
        self.names: dict[str, str] = {}
        for f in files:
            for root in roots:
                if root and not f.startswith(root + "/"):
                    continue
                parts = (f[len(root) + 1 :] if root else f)[:-3].split("/")
                if parts[-1] == "__init__":  # a package is its __init__.py
                    parts = parts[:-1]
                if parts:
                    self.names.setdefault(".".join(parts), f)
        self.tops = {n.split(".")[0] for n in self.names}

    def resolve(self, importer: str, imp: dict) -> list[str]:
        """Files this import statement depends on (possibly several for `from x import a, b`)."""
        if imp["level"] == 0:
            base = self.names.get(imp["module"]) if imp["module"] else None
            prefix = imp["module"]
            lookup = lambda name: self.names.get(f"{prefix}.{name}" if prefix else name)  # noqa: E731
        else:
            # Relative: start at the importer's directory, go up level-1 times.
            d = importer.rpartition("/")[0]
            for _ in range(imp["level"] - 1):
                d = d.rpartition("/")[0]
            target = "/".join(p for p in (d, imp["module"].replace(".", "/")) if p)
            files = set(self.names.values())
            base = next((c for c in (f"{target}.py", f"{target}/__init__.py") if c in files), None)
            lookup = lambda name: next(  # noqa: E731
                (c for c in (f"{target}/{name}.py", f"{target}/{name}/__init__.py") if c in files), None
            )
        out: list[str] = []
        for name in imp["names"]:
            sub = lookup(name)  # `from shop import pricing` really imports the *module* pricing
            if sub and sub != importer:
                out.append(sub)
            elif base and base != importer and base not in out:
                out.append(base)
        if not imp["names"] and base:
            out.append(base)
        return out


def python_edges(root: Path):  # type: ignore[no-untyped-def]
    """Return (edges, unresolved, external, dynamic) for all .py files under root."""
    files = walk_files(root, (".py",))
    index = ModuleIndex(files)
    edges: list[tuple[str, str, int, list[str]]] = []
    unresolved: list[tuple[str, int, str]] = []
    external: dict[str, int] = {}
    dynamic: list[tuple[str, int]] = []
    for f in files:
        try:
            imports, dyn = m01.collect_imports((root / f).read_text(encoding="utf-8"))
        except SyntaxError:
            unresolved.append((f, 0, "<syntax error: file skipped>"))
            continue
        dynamic += [(f, ln) for ln in dyn]
        for imp in imports:
            targets = index.resolve(f, imp)
            for t in targets:
                edges.append((f, t, imp["line"], imp["flags"]))
            if not targets:
                top = imp["module"].split(".")[0]
                if imp["level"] or top in index.tops:
                    # Looks like OUR code but nothing matched: this is a gap in the graph.
                    unresolved.append((f, imp["line"], "." * imp["level"] + imp["module"]))
                else:
                    external[top] = external.get(top, 0) + 1  # stdlib / third-party: not our files
    return edges, unresolved, external, dynamic


if __name__ == "__main__":
    edges, unresolved, external, dynamic = python_edges(ROOT_DEMO)
    for e in edges:
        print(f"{e[0]} -> {e[1]}  (line {e[2]}) {e[3]}")
    print("unresolved:", unresolved, "| external:", external, "| dynamic:", dynamic)

    assert {(s, d) for s, d, *_ in edges} == {
        ("src/shop/__init__.py", "src/shop/cart.py"),
        ("src/shop/cart.py", "src/shop/pricing.py"),
        ("src/shop/cart.py", "src/shop/models.py"),
        ("src/shop/pricing.py", "src/shop/models.py"),
        ("src/shop/models.py", "src/shop/pricing.py"),
        ("src/shop/cli.py", "src/shop/__init__.py"),
        ("tests/test_cart.py", "src/shop/cart.py"),
    }
    assert unresolved == [] and external == {"json": 1, "importlib": 1}
    assert dynamic == [("src/shop/dyn.py", 5)]
    print("module 02 OK")
