# Break it: Module 06

1. Rename `tests/` to `checks/` in the demo. Which tests does `impact` stop finding? Adjust `is_test` and argue whether guessing by directory name is safe.
2. Add a `setup.py` with `if __name__ == "__main__":`. Should it count as an entry point?
3. A file with zero dependents: "dead code" or "entry point"? List three reasons it could be neither.
4. Make `risk` use only the count. Find a project shape where that is misleading (a 3-file chain from `main`).
5. Delete the lower-bound note when `g.dynamic` is non-zero. Write the sentence an agent might then say to a user, and explain why it would be wrong.
