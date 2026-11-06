# Break it: Module 05

1. Replace the iterative Tarjan with the recursive textbook version. At what chain length does the 5,000-node test crash?
2. Delete the `if w in on_stack` branch. Does the test on the hand-made graph still pass? Build a graph where it matters.
3. Find the shortest cycle through a file that is *reachable from* a cycle but not in one. What does your code do?
4. Make a self-import (`a -> a`). Tarjan reports components of size > 1 only. Should a self-loop count as a cycle? Decide, then implement it.
5. Skip edges flagged `type_only` when building `succ`. Does the demo's cycle count change? What about a TYPE_CHECKING-only cycle?
