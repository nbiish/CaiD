"""OpenSCAD MCP Server - Code-First Approach.

Single tool: execute_scad. Use scripting for everything.
See llms.txt/OPENSCAD_RESOURCES.md for patterns.
"""

import os
import tempfile
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from . import scad_builder


server = Server("openscad-mcp")
output_dir = Path(os.environ.get("OPENSCAD_OUTPUT_DIR", "/tmp"))


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Minimal: one tool for all operations."""
    return [
        Tool(
            name="execute_scad",
            description="Execute OpenSCAD code. Returns STL path or SCAD preview.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "OpenSCAD code"},
                    "export": {"type": "string", "description": "Filename for STL export (optional)"},
                },
                "required": ["code"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute OpenSCAD code."""
    if name != "execute_scad":
        return [TextContent(type="text", text=f"Unknown: {name}")]

    code = arguments.get("code", "")
    export_name = arguments.get("export")

    if not code.strip():
        return [TextContent(type="text", text="Error: empty code")]

    try:
        if export_name:
            # Export to STL
            if not export_name.endswith(".stl"):
                export_name += ".stl"
            path = output_dir / export_name
            success, result = scad_builder.render_scad_to_stl(code, str(path))
            if success:
                return [TextContent(type="text", text=f"Exported: {result}")]
            return [TextContent(type="text", text=f"Error: {result}")]
        else:
            # Preview only
            return [TextContent(type="text", text=f"```scad\n{code}\n```")]

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
