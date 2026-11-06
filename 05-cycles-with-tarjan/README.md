# Module 05: Cycles with Tarjan

**Goal:** find every import cycle, and show each as a short, readable loop.

## What a cycle is

Files `a` and `b` are in a cycle if `a` can reach `b` and `b` can reach `a`. Group every file with
the files it mutually reaches: these groups are the **strongly connected components** (SCCs). Any SCC
with more than one file is a tangle; a lone file is not.

## Tarjan in one pass

Run a depth-first search, giving each node an `index` (visit order) and a `low` link (the lowest
index reachable from its subtree through a back edge). When a node finishes with `low == index`, it
is the root of an SCC: pop the stack down to it. O(files + edges).

## Iterative, on purpose

The textbook version is recursive. Python's default recursion limit is 1000, and a repo with a
1,000-file import chain is real. We keep our own `work` stack of `(node, next neighbour position)`
pairs instead of using the call stack. The test closes a 5,000-node chain into a ring to prove it.

## The shortest cycle

An SCC of 40 files is useless to print. The user wants one concrete loop to break. For each member, BFS
over edges that stay inside the SCC until we come back to the start; keep the shortest result. For
large SCCs the real server caps the number of starting points.

## Not every cycle is a bug

A cycle through an `if TYPE_CHECKING:` import or a function-level (lazy) import works fine at runtime.
The real server prints which edges in the cycle carry those flags, from the context tracking built in
module 01.

Run it: `python 05-cycles-with-tarjan/main.py`
