# impact-mcp, The Hard Way

Build an MCP server that answers **"what depends on this file, and what breaks if I change it?"**
for Python and JavaScript/TypeScript projects. No graph library, no TypeScript compiler, no
network. Python's `ast`, a small tokenizer, and a few hundred lines of graph code.

At the end you will have built a minimal version of [impact-mcp](https://github.com/0xmortuex/impact-mcp)
yourself, and you will know the two things that decide whether such a tool is trustworthy:
**resolving import names to files**, and **being honest about what the graph cannot see**.

## Why this exists

"Find usages" in an editor works on one language server's view of the world. An AI agent that is
about to edit a file needs something simpler and more portable: the import graph, the tests that
reach a file through it, and a clear statement of how much of the graph is guesswork. Getting that
right is mostly about edge cases, not algorithms:

- `from pkg import mod` imports a *module*, not a name
- `import()` and `importlib.import_module(x)` with a variable cannot be resolved, and must not be guessed
- an `import x from 'y'` inside a string or comment is not an import
- a cycle detector that recurses will crash on a 1,000-file chain

## Modules

| # | Module | What you build |
|---|--------|----------------|
| 01 | [AST Imports](01-ast-imports/) | Extract every import from Python with `ast`, including TYPE_CHECKING, try/except, lazy and dynamic imports |
| 02 | [Resolving Modules](02-resolving-modules/) | Turn module names into files: the name index, src layouts, relative imports, `from pkg import submodule` |
| 03 | [Scanning JS](03-scanning-js/) | A tokenizer-first import scanner for JS/TS and Node-style file resolution |
| 04 | [Graph and Closure](04-graph-and-closure/) | One graph for both languages, forward and reverse edges, transitive dependents by depth |
| 05 | [Cycles with Tarjan](05-cycles-with-tarjan/) | Strongly connected components, iteratively, and the shortest cycle to show a human |
| 06 | [Impact and Tests](06-impact-and-tests/) | Blast radius, tests that reach a file, entry points, risk, and the honesty line |
| 07 | [MCP Wrapper and Testing](07-mcp-wrapper-and-testing/) | Wrap it in an MCP server and test it over real stdio |

Each module has `README.md` (concepts and design decisions), `main.py` (runnable, checks itself with
`assert`), and `break-it.md` (challenges that break your own code). `demo/` is a small Python +
TypeScript project with a known graph (two cycles, one dynamic import) that every module is checked against.

## How to use it

```
pip install -r requirements.txt     # just mcp and anyio
python verify.py                    # runs every module for real
python 02-resolving-modules/main.py
```

Modules import earlier ones by path, so run them from anywhere. Python 3.10+.

MIT licensed.
