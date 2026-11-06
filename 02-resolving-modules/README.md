# Module 02: Resolving Modules

**Goal:** turn "this file imports `shop.models`" into "this file depends on `src/shop/models.py`".

## The index

A graph needs files, not names. We build `dotted name -> file` once:

- `src/shop/models.py` is importable as `shop.models` if `src/` is an import root (the *src layout*), and as `src.shop.models` if the project root is.
- `shop/__init__.py` *is* the package `shop`: strip `__init__` from the name.

We register the file under every plausible root and let lookups decide. This avoids parsing
`pyproject.toml` for package configuration, and it is why the real server also treats `src/` and any
directory with a `pyproject.toml` as import roots.

## `from pkg import name` is two questions

`from shop import pricing` could mean "the function `pricing` in `shop/__init__.py`" or "the module
`shop/pricing.py`". Python tries the attribute first and falls back to the submodule; statically we
check the submodule index first, because a file named `pricing.py` is far more likely than a name
collision. If it is a submodule, the edge goes to `pricing.py`, not to `__init__.py`.

## Relative imports

`from .pricing import total` in `src/shop/cart.py`: start at the importer's directory (`src/shop`),
go up `level - 1` directories, append the module path, then look for `<path>.py` or `<path>/__init__.py`.
No index needed; it is pure path arithmetic.

## Three kinds of "not found"

When nothing matches, the statement lands in exactly one bucket:

1. **external**: the top-level name (`json`, `requests`) is not one of ours. Not a gap.
2. **unresolved**: it *looks* like ours (relative, or the top-level name is a project package) but no file matched. That is a hole in the graph and is reported.
3. **dynamic**: from module 01.

The distinction between 1 and 2 is the whole point. Without it, a typo'd internal import is
silently treated like `import numpy`.

## What this tutorial skips (the real server does it)

Namespace packages (directories without `__init__.py`), `__all__`, wildcard imports, ambiguity between
several roots, case-insensitive file systems, and `.gitignore`.

Run it: `python 02-resolving-modules/main.py`
