"""Module 03: find imports in JavaScript / TypeScript without a JS parser.

A regex over the raw text would match `import x from "y"` inside comments and strings.
So we tokenize first: comments disappear, string literals become single tokens, and only
then do we look for the module syntax.

Run:  python 03-scanning-js/main.py
"""

from __future__ import annotations

import importlib.util
import posixpath
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

TOKEN = re.compile(
    r"""
    (?P<skip>\s+|//[^\n]*|/\*.*?\*/)          # whitespace and comments: dropped
   |(?P<str>'(?:[^'\\\n]|\\.)*'|"(?:[^"\\\n]|\\.)*"|`(?:[^`\\]|\\.)*`)   # string literals
   |(?P<id>[A-Za-z_$][\w$]*)
   |(?P<p>.)
    """,
    re.X | re.S,
)


def tokenize(src: str) -> list[tuple[str, str]]:
    toks = []
    for m in TOKEN.finditer(src):
        kind = m.lastgroup
        if kind == "skip":
            continue
        text = m.group()
        toks.append(("str", text[1:-1]) if kind == "str" else (kind or "p", text))
    return toks


def js_imports(src: str) -> tuple[list[dict], int]:
    """Return (imports, dynamic_count). Each import: {spec, kind, type_only}."""
    t = tokenize(src)
    out: list[dict] = []
    dynamic = 0
    i = 0
    while i < len(t):
        kind, val = t[i]
        after_dot = i > 0 and t[i - 1] == ("p", ".")  # `obj.import(...)` is not the keyword
        if kind == "id" and not after_dot:
            if val in ("import", "export"):
                nxt = t[i + 1] if i + 1 < len(t) else ("p", "")
                if val == "import" and nxt == ("p", "("):  # dynamic import("x")
                    if i + 3 < len(t) and t[i + 2][0] == "str" and t[i + 3] == ("p", ")"):
                        out.append({"spec": t[i + 2][1], "kind": "dynamic", "type_only": False})
                    else:
                        dynamic += 1  # import(variable): cannot know the target
                else:
                    # import ... from "x" | import "x" | export ... from "x": scan to the string
                    type_only = nxt == ("id", "type")
                    j = i + 1
                    while j < len(t) and t[j][0] != "str" and t[j] not in (("p", ";"), ("id", "import")):
                        j += 1
                    if j < len(t) and t[j][0] == "str" and (
                        t[j - 1] == ("id", "from") or j == i + 1  # `from "x"` or bare `import "x"`
                    ):
                        out.append({"spec": t[j][1], "kind": val, "type_only": type_only})
                        i = j
            elif val == "require" and i + 1 < len(t) and t[i + 1] == ("p", "("):
                if i + 3 < len(t) and t[i + 2][0] == "str" and t[i + 3] == ("p", ")"):
                    out.append({"spec": t[i + 2][1], "kind": "require", "type_only": False})
                else:
                    dynamic += 1
        i += 1
    return out, dynamic


JS_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")


def resolve_relative(importer: str, spec: str, files: set[str]) -> str | None:
    """Node-style resolution for './x' and '../x': exact file, + extension, then /index.ext."""
    if not spec.startswith("."):
        return None  # bare specifier: a package (react) - not one of our files in this tutorial
    base = posixpath.normpath(posixpath.join(posixpath.dirname(importer), spec))
    if base in files:
        return base
    for ext in JS_SUFFIXES:
        if base + ext in files:
            return base + ext
    for ext in JS_SUFFIXES:
        if f"{base}/index{ext}" in files:
            return f"{base}/index{ext}"
    return None


def js_edges(root: Path):  # type: ignore[no-untyped-def]
    files = m02.walk_files(root, JS_SUFFIXES)
    fileset = set(files)
    edges, unresolved, external, dynamic = [], [], {}, 0
    for f in files:
        imports, dyn = js_imports((root / f).read_text(encoding="utf-8"))
        dynamic += dyn
        for imp in imports:
            target = resolve_relative(f, imp["spec"], fileset)
            if target:
                edges.append((f, target, imp["kind"], imp["type_only"]))
            elif imp["spec"].startswith("."):
                unresolved.append((f, imp["spec"]))
            else:
                external[imp["spec"]] = external.get(imp["spec"], 0) + 1
    return edges, unresolved, external, dynamic


if __name__ == "__main__":
    src = """
    // import fake from "./comment";
    import React, { useState } from "react";
    import type { T } from './types';
    export { a } from "./a";
    export * from "./b";
    const s = "import nope from './string'";
    const lazy = () => import("./lazy");
    const dyn = (n) => import(n);
    const c = require('./cjs');
    obj.import("./method");
    """
    imports, dyn = js_imports(src)
    print(imports, "dynamic:", dyn)
    assert [i["spec"] for i in imports] == ["react", "./types", "./a", "./b", "./lazy", "./cjs"]
    assert imports[1]["type_only"] and imports[4]["kind"] == "dynamic" and dyn == 1

    edges, unresolved, external, dynamic = js_edges(HERE.parent / "demo")
    for e in edges:
        print(e)
    assert {(s, d) for s, d, *_ in edges} == {
        ("web/src/app.ts", "web/src/util.ts"),
        ("web/src/app.ts", "web/src/lazy.ts"),
        ("web/src/util.ts", "web/src/app.ts"),
        ("web/src/index.test.ts", "web/src/app.ts"),
    }
    assert external == {"react": 1} and unresolved == [] and dynamic == 0
    print("module 03 OK")
