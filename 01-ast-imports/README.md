# Module 01: AST Imports

**Goal:** list every import in a Python file, with enough context to know how much each one matters.

## Why `ast` and not a regex

`import x` inside a docstring, a comment or a string is not an import; a regex cannot tell. The
standard library already contains Python's real parser. `ast.parse(source)` returns a tree, and
`ast.NodeVisitor` walks it. We override only `visit_Import` and `visit_ImportFrom`, plus a few
visitors that track where we are.

## The three shapes

- `import a.b as c` is an `Import` node with `alias.name == "a.b"`
- `from a.b import x, y` is `ImportFrom(module="a.b", names=[x, y], level=0)`
- `from ..up import z` is `ImportFrom(module="up", level=2)`; `from . import s` has `module=None`, `level=1`

Relative imports are only *names* until module 02 resolves them against a file's location.

## Context matters

The same `import` statement means different things depending on where it sits, so the visitor keeps
a stack of tags:

- `if TYPE_CHECKING:` gives `type_only` (never executed; harmless in a cycle)
- `try: ... except ImportError` or any other `if` gives `conditional` (an optional dependency)
- inside a `def` gives `lazy` (runs at call time; often how people break cycles)

Later, `impact` and `find_cycles` use these flags to say "this cycle is softened by a lazy import".

## Dynamic imports: record the gap

`importlib.import_module("shop.plugin")` has a literal, so we treat it as an import (flagged `dynamic`).
`importlib.import_module(name)` has a variable: we cannot know the target. We do **not** guess; we
count it. That count travels with every answer from here on, because it is what tells an agent how
much to trust the graph.

## Broken files

`ast.parse` raises `SyntaxError` on a broken file. `collect_imports` lets it propagate; module 02
catches it *at the call site*, records the file as unparsed and carries on. The library does not decide
silently; the layer that knows the context does.

Run it: `python 01-ast-imports/main.py`
