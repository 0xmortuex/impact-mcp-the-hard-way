# Break it: Module 07

1. Add `print("hello")` at the top of a tool function in `server.py`. Run `main.py`. Why does the session break?
2. Raise `ValueError` instead of `ToolError` in `_check`. What does the client see now?
3. Remove a docstring. Look at the tool list. What does the agent lose?
4. Make `_graph()` cache forever. Edit a file in `demo/` while the server runs. What does the agent see?
5. Call `impact` with `../../etc/passwd`. It fails, but would it fail for the right reason? Add an explicit sandbox check.
