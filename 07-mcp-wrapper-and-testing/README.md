# Module 07: MCP Wrapper and Testing

**Goal:** expose the analysis as MCP tools and prove it works the way a real client uses it.

## The wrapper is thin

`server.py` registers four functions with `@mcp.tool()`. The function name becomes the tool name, the
docstring becomes the description the agent reads, and the type hints become the input schema. So the
docstrings are product copy: say what the tool answers and when to call it.

## Errors are part of the interface

`MCPServer` forwards only a `ToolError`'s message to the client; any other exception turns into a
generic "Error executing tool". So expected failures (a path that is not in the graph) are raised as
`ToolError` with an instruction: *"Use a project-relative path such as ..."*. Never swallow, never
fall back silently; tell the agent what to do next.

## Sandbox

The server takes `--dir` and answers only about that tree. Everything is read-only: files are opened
for reading and parsed; nothing is imported or executed. The real server also rejects absolute paths
and `..` that leave `--dir`.

## Test the process, not just the functions

`main.py` here launches `server.py` as a child process, performs the real MCP handshake, lists tools
and calls them, including the failure case. It catches what unit tests cannot: a tool that is not
registered, a schema that rejects the arguments, an error text that never reaches the client, stdout
pollution that corrupts the protocol (which is why servers never `print` to stdout).

Run it: `python 07-mcp-wrapper-and-testing/main.py`

## Where to go from here

The real [impact-mcp](https://github.com/0xmortuex/impact-mcp) adds tsconfig and workspace
resolution, `__all__` and re-export-aware `symbol_users`, namespace packages, `.gitignore`, a
persistent parse cache, symlink-loop safety, and exact-edge tests on realistic multi-package projects.
