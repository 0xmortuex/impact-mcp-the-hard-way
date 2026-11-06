"""Module 07: test the server the way a client uses it - a real subprocess over stdio.

Unit tests of the functions are not enough: the MCP layer decides what an agent can see
(tool names, schemas, which errors survive). So this module launches server.py as a child
process, performs the real MCP handshake, lists the tools, and calls them.

Run:  python 07-mcp-wrapper-and-testing/main.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

HERE = Path(__file__).resolve().parent
DEMO = HERE.parent / "demo"


async def run() -> None:
    params = StdioServerParameters(command=sys.executable, args=[str(HERE / "server.py"), "--dir", str(DEMO)])
    async with stdio_client(params) as (read, write), ClientSession(read, write) as session:
        init = await session.initialize()
        assert init.server_info.name == "impact-lite"
        names = {t.name for t in (await session.list_tools()).tools}
        print("tools:", sorted(names))
        assert names == {"project_map", "dependents", "impact", "find_cycles"}

        res = await session.call_tool("impact", {"path": "src/shop/pricing.py"})
        text = res.content[0].text
        print(text)
        assert not res.is_error
        assert "tests/test_cart.py" in text and "src/shop/cli.py [console script]" in text

        res = await session.call_tool("dependents", {"path": "src/shop/models.py", "depth": 1})
        assert "src/shop/cart.py" in res.content[0].text and "src/shop/cli.py" not in res.content[0].text

        res = await session.call_tool("find_cycles", {})
        assert "web/src/app.ts -> web/src/util.ts -> web/src/app.ts" in res.content[0].text

        # An expected failure must reach the agent as a readable message, not a bare "error".
        res = await session.call_tool("impact", {"path": "src/shop/nope.py"})
        print("error text:", res.content[0].text)
        assert res.is_error and "not a scanned file" in res.content[0].text


if __name__ == "__main__":
    asyncio.run(run())
    print("module 07 OK")
