# Module 04: Graph and Closure

**Goal:** one graph over both languages, and the transitive question "who depends on this?".

## Two adjacency maps

For each edge `a imports b` we store `out[a] += b` and `inn[b] += a`. Dependencies walk `out`;
dependents walk `inn`. Same BFS, different map. Building both at insert time costs memory but makes
every query cheap, which is the right trade for a tool answering many small questions about one graph.

## Why BFS

Breadth-first search yields each file at its *shortest* distance, which is exactly what "grouped by
depth" means: depth 1 are the direct importers, depth 2 import those, and so on. The `depth` map
doubles as the visited set, which is also what makes **cycles harmless**: a file already seen is
never queued again.

## The honesty counters live in the graph

`unresolved`, `dynamic` and `external` are fields of `Graph`, and every answer prints
`Graph confidence: ...`. This is a design decision, not decoration: an agent cannot tell
"nothing depends on this" from "something depends on this through an import I could not follow" unless
the tool says so.

## Rebuild or cache?

The tutorial rebuilds per call. The real server also walks the tree on every call (so answers are
always fresh), but caches *parse results* keyed on each file's mtime and size, outside the repo.
Parsing is the expensive part; edges are cheap to recompute.

Run it: `python 04-graph-and-closure/main.py`
