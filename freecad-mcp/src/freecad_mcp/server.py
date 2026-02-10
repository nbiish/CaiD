"""FreeCAD MCP Server - Code-First Approach.

2 tools: execute_code, get_model_info
See llms.txt/FREECAD_RESOURCES.md for scripting patterns.
"""

import json
import os
import xmlrpc.client
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Configuration
FREECAD_HOST = os.environ.get("FREECAD_HOST", "localhost")
FREECAD_PORT = int(os.environ.get("FREECAD_PORT", "9875"))


def get_rpc_client() -> xmlrpc.client.ServerProxy:
    """Get XML-RPC client connected to FreeCAD addon."""
    return xmlrpc.client.ServerProxy(f"http://{FREECAD_HOST}:{FREECAD_PORT}")


server = Server("freecad-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Minimal toolset: code execution + model info."""
    return [
        Tool(
            name="execute_code",
            description="Execute Python code in FreeCAD. See FREECAD_RESOURCES.md for patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="get_model_info",
            description="Get objects and dimensions from current document",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Specific object (optional, empty for all)",
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute tool via XML-RPC to FreeCAD."""
    try:
        client = get_rpc_client()

        if name == "execute_code":
            result = client.execute_tool("execute_code", json.dumps(arguments))
            result_data = json.loads(result)
            if result_data.get("success"):
                output = result_data.get("result", {})
                # The addon returns {"output": "..."} — extract the string
                if isinstance(output, dict):
                    output = output.get("output", str(output))
                return [TextContent(type="text", text=str(output))]
            return [TextContent(type="text", text=f"Error: {result_data.get('error')}")]

        elif name == "get_model_info":
            result = client.execute_tool("get_model_info", json.dumps(arguments))
            result_data = json.loads(result)
            if result_data.get("success"):
                output = result_data.get("result", {})
                return [TextContent(type="text", text=json.dumps(output, indent=2))]
            return [TextContent(type="text", text=f"Error: {result_data.get('error')}")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except ConnectionRefusedError:
        return [TextContent(
            type="text",
            text="Error: Cannot connect to FreeCAD. Ensure FreeCAD is running with MCP addon."
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


def main():
    """Run server."""
    import asyncio

    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
