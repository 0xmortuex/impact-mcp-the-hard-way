"""Module 05: find import cycles with Tarjan's strongly-connected-components algorithm.

A cycle exists exactly when a set of files can all reach each other: a strongly connected
component (SCC) with more than one member. Tarjan finds all SCCs in one pass, O(files + edges).
Then, for each SCC, a BFS finds the *shortest* cycle to show a human.

The implementation is iterative on purpose: a recursive DFS dies with RecursionError on a
chain of ~1000 files, and real repos have those.

Run:  python 05-cycles-with-tarjan/main.py
"""

from __future__ import annotations

import importlib.util
import sys
from collections import deque
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


m04 = load("04-graph-and-closure")


def tarjan(nodes: list[str], succ: dict[str, list[str]]) -> list[list[str]]:
    """Strongly connected components with more than one node."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    result: list[list[str]] = []
    counter = 0
    for root in nodes:
        if root in index:
            continue
        work = [(root, 0)]  # (node, next neighbour position): an explicit call stack
        while work:
            v, i = work.pop()
            if i == 0:
                index[v] = low[v] = counter
                counter += 1
                stack.append(v)
                on_stack.add(v)
            descended = False
            nbrs = succ.get(v, [])
            while i < len(nbrs):
                w = nbrs[i]
                i += 1
                if w not in index:
                    work.append((v, i))  # come back to v after w finishes
                    work.append((w, 0))
                    descended = True
                    break
                if w in on_stack:
                    low[v] = min(low[v], index[w])
            if descended:
                continue
            if low[v] == index[v]:  # v is the root of an SCC: pop it off the stack
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1:
                    result.append(sorted(comp))
            if work:  # finished v: tell the parent
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
    return sorted(result)


def shortest_cycle(comp: list[str], succ: dict[str, list[str]]) -> list[str]:
    """Shortest cycle inside one SCC, as [a, b, ..., a]."""
    members = set(comp)
    best: list[str] | None = None
    for start in comp:
        prev = {start: None}
        queue = deque([start])
        found = None
        while queue and found is None:
            cur = queue.popleft()
            for nxt in succ.get(cur, []):
                if nxt == start:
                    found = cur
                    break
                if nxt in members and nxt not in prev:
                    prev[nxt] = cur
                    queue.append(nxt)
        if found is None:
            continue
        path = [found]
        while prev[path[-1]] is not None:  # walk predecessors back to the start
            path.append(prev[path[-1]])
        path.reverse()  # start ... found
        cycle = [*path, start]
        if best is None or len(cycle) < len(best):
            best = cycle
    assert best is not None
    return best


if __name__ == "__main__":
    # Hand-made graph first: a 3-cycle, a 2-cycle sharing nothing, and a tail.
    succ = {"a": ["b"], "b": ["c"], "c": ["a", "d"], "d": ["e"], "e": ["d"], "f": ["a"]}
    comps = tarjan(sorted(succ), succ)
    print(comps)
    assert comps == [["a", "b", "c"], ["d", "e"]]
    assert shortest_cycle(["a", "b", "c"], succ) == ["a", "b", "c", "a"]
    # a long loop with a short one hiding inside: the short one is what we should print
    tangled = {"p": ["q"], "q": ["r", "p"], "r": ["s"], "s": ["p"]}
    assert shortest_cycle(["p", "q", "r", "s"], tangled) in (["p", "q", "p"], ["q", "p", "q"])

    # 5000-file chain closed into one big cycle: must not blow the recursion limit.
    big = {f"n{i}": [f"n{(i + 1) % 5000}"] for i in range(5000)}
    assert [len(c) for c in tarjan(sorted(big), big)] == [5000]

    g = m04.build_graph(HERE.parent / "demo")
    cycles = tarjan(sorted(g.nodes), g.out)
    for comp in cycles:
        print("cycle:", " -> ".join(shortest_cycle(comp, g.out)))
    assert cycles == [
        ["src/shop/models.py", "src/shop/pricing.py"],
        ["web/src/app.ts", "web/src/util.ts"],
    ]
    print("module 05 OK")
