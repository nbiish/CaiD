"""FreeCAD MCP Server — Code-First (4 tools).

Tools: execute_code, get_model_info, get_selection, get_screenshot
See llms.txt/FREECAD_RESOURCES.md for scripting patterns.
"""

import json
import os
import xmlrpc.client
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

# Configuration
FREECAD_HOST = os.environ.get("FREECAD_HOST", "localhost")
FREECAD_PORT = int(os.environ.get("FREECAD_PORT", "9875"))


def get_rpc() -> xmlrpc.client.ServerProxy:
    return xmlrpc.client.ServerProxy(f"http://{FREECAD_HOST}:{FREECAD_PORT}")


server = Server("freecad-mcp")


def _call_addon(tool_name: str, args: dict) -> dict:
    """Call addon via XML-RPC and parse response."""
    client = get_rpc()
    raw = client.execute_tool(tool_name, json.dumps(args))
    return json.loads(raw)


def _extract_text(result_data: dict) -> str:
    """Extract text from addon response, handling nested dicts."""
    if not result_data.get("success"):
        return f"Error: {result_data.get('error', 'Unknown error')}"
    result = result_data.get("result", {})
    if isinstance(result, dict):
        # execute_code returns {"output": "..."}, others return info dicts
        if "output" in result:
            return result["output"]
        return json.dumps(result, indent=2)
    return str(result)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="execute_code",
            description="Execute Python code in FreeCAD. See FREECAD_RESOURCES.md for patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
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
        Tool(
            name="get_selection",
            description="Get currently selected objects/faces/edges in FreeCAD",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_screenshot",
            description="Capture screenshot of FreeCAD 3D viewport",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "default": 800},
                    "height": {"type": "integer", "default": 600},
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    try:
        result_data = _call_addon(name, arguments)

        # Screenshot returns image content
        if name == "get_screenshot" and result_data.get("success"):
            result = result_data.get("result", {})
            if "image_base64" in result:
                return [
                    ImageContent(
                        type="image",
                        data=result["image_base64"],
                        mimeType="image/png",
                    ),
                    TextContent(
                        type="text",
                        text=f"Screenshot: {result.get('width', 800)}x{result.get('height', 600)}px",
                    ),
                ]

        return [TextContent(type="text", text=_extract_text(result_data))]

    except ConnectionRefusedError:
        return [TextContent(
            type="text",
            text="Error: Cannot connect to FreeCAD. Ensure FreeCAD is running with MCP addon.",
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


def main():
    import asyncio

    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
