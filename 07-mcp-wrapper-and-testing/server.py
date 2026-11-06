"""The finished mini server: modules 02-06 behind four MCP tools.

Run it yourself:  python server.py --dir ../demo
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

PARENT = Path(__file__).resolve().parent.parent


def load(module_dir: str):  # type: ignore[no-untyped-def]
    path = PARENT / module_dir / "main.py"
    spec = importlib.util.spec_from_file_location("m_" + module_dir.replace("-", "_"), path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


m04 = load("04-graph-and-closure")
m05 = load("05-cycles-with-tarjan")
m06 = load("06-impact-and-tests")

mcp = MCPServer(
    "impact-lite",
    instructions="Import-graph impact analysis. Call impact(path) before editing a file. "
    "Read the 'Graph confidence' line: unresolved or dynamic imports mean results are a lower bound.",
)
ROOT = Path.cwd()


def _graph():  # type: ignore[no-untyped-def]
    # Rebuilt per call so the answer always reflects the files on disk right now.
    return m04.build_graph(ROOT)


def _check(g, path: str) -> None:  # type: ignore[no-untyped-def]
    # MCPServer only forwards a ToolError's message to the client; any other exception
    # becomes a useless "Error executing tool". So expected failures are ToolErrors.
    if path not in g.nodes:
        raise ToolError(f"{path!r} is not a scanned file. Use a project-relative path such as {sorted(g.nodes)[0]!r}.")


@mcp.tool()
def project_map() -> str:
    """Overview: file count, cycle count, entry points and the graph-confidence line. Start here."""
    g = _graph()
    eps = m06.entry_points(ROOT, sorted(g.nodes))
    cycles = m05.tarjan(sorted(g.nodes), g.out)
    return "\n".join(
        [f"{len(g.nodes)} files; import cycles: {len(cycles)}", *(f"entry: {f} ({w})" for f, w in sorted(eps.items())), g.confidence()]
    )


@mcp.tool()
def dependents(path: str, depth: int = 3) -> str:
    """Who imports `path` (transitively up to `depth`), grouped by depth."""
    g = _graph()
    _check(g, path)
    found = g.reach(path, "in", depth)
    lines = [f"Dependents of {path}: {len(found)}"]
    lines += [f"  depth {d}: {f}" for f, d in sorted(found.items(), key=lambda kv: (kv[1], kv[0]))]
    return "\n".join([*lines, g.confidence()])


@mcp.tool()
def impact(path: str) -> str:
    """Blast radius of changing `path`: dependents, tests that reach it, entry points, risk."""
    g = _graph()
    _check(g, path)
    return m06.impact(ROOT, g, path)


@mcp.tool()
def find_cycles() -> str:
    """Import cycles, each with its shortest loop."""
    g = _graph()
    cycles = m05.tarjan(sorted(g.nodes), g.out)
    lines = [f"Import cycles: {len(cycles)}"]
    lines += [" -> ".join(m05.shortest_cycle(c, g.out)) for c in cycles]
    return "\n".join([*lines, g.confidence()])


def main() -> None:
    global ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".")
    ROOT = Path(ap.parse_args().dir).resolve()
    mcp.run()


if __name__ == "__main__":
    main()
