"""Module 01: extract every import from a Python file with the stdlib `ast`.

Run:  python 01-ast-imports/main.py
"""

from __future__ import annotations

import ast
from typing import Any


class ImportCollector(ast.NodeVisitor):
    """Walk a syntax tree and record imports plus the *context* they sit in."""

    def __init__(self) -> None:
        self.imports: list[dict[str, Any]] = []
        self.dynamic: list[int] = []  # line numbers of import_module(<not a literal>)
        self._ctx: list[str] = []

    def _flags(self) -> list[str]:
        return sorted(set(self._ctx))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(
                {"module": alias.name, "level": 0, "names": [], "line": node.lineno, "flags": self._flags()}
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        # `from . import x` has module=None and level=1; `from ..a import b` has level=2.
        self.imports.append(
            {
                "module": node.module or "",
                "level": node.level,
                "names": [a.name for a in node.names],
                "line": node.lineno,
                "flags": self._flags(),
            }
        )

    def _under(self, tag: str, body: list[ast.stmt]) -> None:
        self._ctx.append(tag)
        for stmt in body:
            self.visit(stmt)
        self._ctx.pop()

    def visit_If(self, node: ast.If) -> None:
        is_tc = isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
        self._under("type_only" if is_tc else "conditional", node.body)
        self._under("conditional", node.orelse)

    def visit_Try(self, node: ast.Try) -> None:
        self._under("conditional", node.body)
        for handler in node.handlers:
            self._under("conditional", handler.body)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._under("lazy", node.body)

    def visit_Call(self, node: ast.Call) -> None:
        f = node.func
        name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
        if name in ("import_module", "__import__"):
            arg = node.args[0] if node.args else None
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                self.imports.append(
                    {"module": arg.value, "level": 0, "names": [], "line": node.lineno,
                     "flags": [*self._flags(), "dynamic"]}
                )  # fmt: skip
            else:
                # The honest answer: we cannot know. Record it so the user sees the gap.
                self.dynamic.append(node.lineno)
        self.generic_visit(node)


def collect_imports(source: str) -> tuple[list[dict[str, Any]], list[int]]:
    """Return (imports, dynamic_lines). Raises SyntaxError for broken files - callers decide what to do."""
    collector = ImportCollector()
    collector.visit(ast.parse(source))
    return collector.imports, collector.dynamic


SAMPLE = '''
import os, json as j
from shop.models import Item, Order
from . import sibling
from ..up import thing
import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from shop.types import Alias

try:
    import ujson
except ImportError:
    ujson = None


def go(name):
    from shop.lazy import heavy
    importlib.import_module("shop.plugin")
    return importlib.import_module(name)
'''


if __name__ == "__main__":
    imports, dynamic = collect_imports(SAMPLE)
    for i in imports:
        print(f"line {i['line']:>2}: {'.' * i['level']}{i['module']} {i['names']} {i['flags']}")
    print("dynamic (unresolvable) calls on lines:", dynamic)

    by_line = {i["line"]: i for i in imports}
    assert [i["module"] for i in imports if i["level"] == 0 and not i["flags"]] == ["os", "json", "shop.models", "importlib", "typing"]
    assert by_line[4]["names"] == ["sibling"] and by_line[4]["level"] == 1 and by_line[4]["module"] == ""
    assert by_line[5]["level"] == 2 and by_line[5]["module"] == "up"
    assert by_line[10]["flags"] == ["type_only"]
    assert by_line[13]["flags"] == ["conditional"]
    assert by_line[19]["flags"] == ["lazy"]
    assert by_line[20]["flags"] == ["lazy", "dynamic"] and by_line[20]["module"] == "shop.plugin"
    assert dynamic == [21]
    try:
        collect_imports("def (:\n")
    except SyntaxError as e:
        print("syntax error is raised, not swallowed:", e.msg)
    else:
        raise AssertionError("expected SyntaxError")
    print("module 01 OK")
