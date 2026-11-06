# Module 06: Impact and Tests

**Goal:** the tool an agent calls before editing: one answer with blast radius, tests, entry points and risk.

## The ingredients

- **Dependents**: module 04, unlimited depth.
- **Tests that reach it.** A test file "covers" a changed file if it imports it directly or through a chain. That is a *superset* of the tests worth running, not proof of coverage, and the output says so. Test files are recognised by name and directory (`test_*.py`, `*.test.ts`, anything under `tests/`).
- **Entry points** are where execution starts: console scripts in `pyproject.toml`, files with `if __name__ == ...`, `package.json` `main`. A change that reaches one can break startup.
- **Risk**: a simple, explainable rule on transitive count and share of the project (HIGH at 25 files or 15%, MEDIUM at 5 or 5%). A score you cannot explain is worse than none.

## The line that matters

If `unresolved` or `dynamic` is non-zero the answer adds "real dependents may be missing (lower bound)".
Without it an agent would read "0 dependents" as safe-to-delete.

## Symbols

The real server also takes `impact(path, symbol)`. The narrowing works by finding files whose import
edge names that symbol, following `__init__.py` re-exports (`from .core import Engine` makes the
package a *re-exporter*), and treating everything further out as an upper bound. That needs the
imported names stored on each edge; module 02's `imp["names"]` is where that starts.

Run it: `python 06-impact-and-tests/main.py`
