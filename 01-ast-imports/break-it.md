# Break it: Module 01

1. Add an `async def` to the sample and put an import inside it. It is missed. Why? (Hint: `visit_FunctionDef` does not cover `AsyncFunctionDef`.) Fix it.
2. Add `import a.b.c`. What does `module` contain? Why is that not the same as "the file imported"?
3. Put `__import__("x")` inside a class body. Is it caught? Is it flagged lazy?
4. Python 3.11 has `try: ... except* E`, an `ast.TryStar`. Does your visitor see imports inside it?
5. Parse a file with a `\x00` byte in it. Which exception do you get, `SyntaxError` or `ValueError`? Handle both.
