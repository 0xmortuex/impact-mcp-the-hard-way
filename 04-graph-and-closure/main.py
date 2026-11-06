"""Module 04: put both languages into one graph and ask "who depends on this?".

The graph stores edges twice (forward and reverse) so both questions are cheap:
  dependencies(f) = what f imports      (forward)
  dependents(f)   = who imports f       (reverse)
Transitive questions are a breadth-first search; BFS gives the *shortest* depth for free.

Run:  python 04-graph-and-closure/main.py
"""

from __future__ import annotations

import importlib.util
import sys
from collections import deque
from dataclasses import dataclass, field
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
m03 = load("03-scanning-js")


@dataclass
class Graph:
    nodes: set[str] = field(default_factory=set)
    out: dict[str, list[str]] = field(default_factory=dict)  # file -> files it imports
    inn: dict[str, list[str]] = field(default_factory=dict)  # file -> files that import it
    # The honesty counters: what the graph could NOT see.
    unresolved: list = field(default_factory=list)
    dynamic: int = 0
    external: dict[str, int] = field(default_factory=dict)

    def add_edge(self, src: str, dst: str) -> None:
        if dst not in self.out.setdefault(src, []):
            self.out[src].append(dst)
            self.inn.setdefault(dst, []).append(src)

    def reach(self, start: str, direction: str, max_depth: int) -> dict[str, int]:
        """BFS. Returns {file: depth}. direction 'in' = dependents, 'out' = dependencies."""
        adj = self.inn if direction == "in" else self.out
        depth = {start: 0}
        queue = deque([start])
        while queue:
            cur = queue.popleft()
            if depth[cur] == max_depth:
                continue
            for nxt in adj.get(cur, ()):
                if nxt not in depth:  # the visited check is what makes cycles harmless
                    depth[nxt] = depth[cur] + 1
                    queue.append(nxt)
        del depth[start]
        return depth

    def confidence(self) -> str:
        return (
            f"Graph confidence: {len(self.nodes)} files | UNRESOLVED imports: {len(self.unresolved)} | "
            f"dynamic non-literal imports: {self.dynamic} | external packages: {len(self.external)}"
        )


def build_graph(root: Path) -> Graph:
    g = Graph()
    g.nodes.update(m02.walk_files(root, (".py",) + m03.JS_SUFFIXES))
    edges, unresolved, external, dynamic = m02.python_edges(root)
    for src, dst, *_ in edges:
        g.add_edge(src, dst)
    g.unresolved += unresolved
    g.dynamic += len(dynamic)
    for k, v in external.items():
        g.external[k] = g.external.get(k, 0) + v
    jedges, junres, jext, jdyn = m03.js_edges(root)
    for src, dst, *_ in jedges:
        g.add_edge(src, dst)
    g.unresolved += junres
    g.dynamic += jdyn
    for k, v in jext.items():
        g.external[k] = g.external.get(k, 0) + v
    return g


if __name__ == "__main__":
    g = build_graph(HERE.parent / "demo")
    print(g.confidence())

    models = "src/shop/models.py"
    d1 = g.reach(models, "in", 1)
    d9 = g.reach(models, "in", 9)
    print("direct dependents of models.py:", d1)
    print("all dependents of models.py   :", d9)
    assert d1 == {"src/shop/cart.py": 1, "src/shop/pricing.py": 1}
    assert d9 == {
        "src/shop/cart.py": 1,
        "src/shop/pricing.py": 1,
        "src/shop/__init__.py": 2,
        "tests/test_cart.py": 2,
        "src/shop/cli.py": 3,
    }
    assert g.reach("src/shop/cli.py", "out", 9) == {
        "src/shop/__init__.py": 1,
        "src/shop/cart.py": 2,
        "src/shop/pricing.py": 3,
        "src/shop/models.py": 3,
    }
    # a cycle must terminate, and a file is never its own dependent
    assert "web/src/app.ts" not in g.reach("web/src/app.ts", "in", 9)
    assert set(g.reach("web/src/lazy.ts", "in", 9)) == {"web/src/app.ts", "web/src/util.ts", "web/src/index.test.ts"}
    assert len(g.unresolved) == 0 and g.dynamic == 1
    print("module 04 OK")
