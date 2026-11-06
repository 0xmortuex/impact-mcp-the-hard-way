# Break it: Module 04

1. Remove the visited check in `reach` (`if nxt not in depth`). Run it on `web/src/app.ts`. What happens, and why does a cycle cause it?
2. `reach` stops expanding at `max_depth`. Change `==` to `>` and look at the result for depth 1. What went wrong?
3. Add an edge from a file to itself (`from . import x` where `x` is a name in the same `__init__.py`). Should it be an edge? What would it do to the cycle detector in module 05?
4. Make `add_edge` allow duplicates. Which query result changes?
5. Add a file that is only imported by a test. Is it a "dead-code candidate"? What should the tool say?
