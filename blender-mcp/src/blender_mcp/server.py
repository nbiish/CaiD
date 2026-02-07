"""Blender MCP Server implementation.

This server provides tools for AI-assisted 3D mesh modeling in Blender.
Communication with Blender happens via TCP sockets to the Blender addon.
"""

import json
import os
import socket
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Configuration
BLENDER_HOST = os.environ.get("BLENDER_HOST", "localhost")
BLENDER_PORT = int(os.environ.get("BLENDER_PORT", "9876"))


def send_to_blender(command: dict) -> dict:
    """Send a command to Blender via socket and return response."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((BLENDER_HOST, BLENDER_PORT))
            sock.settimeout(30.0)
            
            # Send command as JSON
            message = json.dumps(command) + "\n"
            sock.sendall(message.encode("utf-8"))
            
            # Receive response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if response.endswith(b"\n"):
                    break
                    
            return json.loads(response.decode("utf-8"))
            
    except ConnectionRefusedError:
        return {"success": False, "error": "Cannot connect to Blender. Ensure Blender is running with the MCP addon enabled."}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Initialize MCP server
server = Server("blender-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available Blender modeling tools."""
    return [
        Tool(
            name="create_primitive",
            description="Create a primitive mesh (Cube, UV Sphere, Cylinder, Cone, Torus, Plane)",
            inputSchema={
                "type": "object",
                "properties": {
                    "shape": {
                        "type": "string",
                        "enum": ["Cube", "Sphere", "Cylinder", "Cone", "Torus", "Plane"],
                        "description": "Type of primitive mesh",
                    },
                    "name": {
                        "type": "string",
                        "description": "Object name",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Location [x, y, z]",
                        "default": [0, 0, 0],
                    },
                    "size": {
                        "type": "number",
                        "description": "Size/scale of primitive",
                        "default": 1,
                    },
                },
                "required": ["shape"],
            },
        ),
        Tool(
            name="extrude_faces",
            description="Extrude selected faces along their normals",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "depth": {
                        "type": "number",
                        "description": "Extrusion distance",
                    },
                    "select_all": {
                        "type": "boolean",
                        "description": "Select all faces first",
                        "default": False,
                    },
                },
                "required": ["object_name", "depth"],
            },
        ),
        Tool(
            name="inset_faces",
            description="Inset selected faces",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "thickness": {
                        "type": "number",
                        "description": "Inset thickness",
                    },
                    "depth": {
                        "type": "number",
                        "description": "Inset depth",
                        "default": 0,
                    },
                },
                "required": ["object_name", "thickness"],
            },
        ),
        Tool(
            name="bevel_edges",
            description="Bevel selected edges",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "width": {
                        "type": "number",
                        "description": "Bevel width",
                    },
                    "segments": {
                        "type": "integer",
                        "description": "Number of bevel segments",
                        "default": 1,
                    },
                },
                "required": ["object_name", "width"],
            },
        ),
        Tool(
            name="loop_cut",
            description="Add edge loop(s) to mesh",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "cuts": {
                        "type": "integer",
                        "description": "Number of cuts",
                        "default": 1,
                    },
                    "edge_index": {
                        "type": "integer",
                        "description": "Edge index to cut through",
                        "default": 0,
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="add_modifier",
            description="Add a modifier to an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "modifier_type": {
                        "type": "string",
                        "enum": ["SUBSURF", "MIRROR", "ARRAY", "BEVEL", "SOLIDIFY", "BOOLEAN"],
                        "description": "Type of modifier",
                    },
                    "params": {
                        "type": "object",
                        "description": "Modifier-specific parameters",
                    },
                },
                "required": ["object_name", "modifier_type"],
            },
        ),
        Tool(
            name="apply_modifier",
            description="Apply (bake) a modifier to mesh geometry",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "modifier_name": {
                        "type": "string",
                        "description": "Name of modifier to apply",
                    },
                },
                "required": ["object_name", "modifier_name"],
            },
        ),
        Tool(
            name="select_geometry",
            description="Select vertices, edges, or faces",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to select in",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["VERT", "EDGE", "FACE"],
                        "description": "Selection mode",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["SELECT_ALL", "DESELECT_ALL", "INVERT", "SELECT_INDICES"],
                        "description": "Selection action",
                    },
                    "indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Indices to select (for SELECT_INDICES)",
                    },
                },
                "required": ["object_name", "mode", "action"],
            },
        ),
        Tool(
            name="transform_object",
            description="Move, rotate, or scale an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to transform",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "New location [x, y, z]",
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Rotation in degrees [x, y, z]",
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Scale [x, y, z]",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="delete_object",
            description="Delete an object from the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to delete",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="get_objects",
            description="List all objects in the scene",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_screenshot",
            description="Capture a screenshot of the viewport",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "Image width",
                        "default": 800,
                    },
                    "height": {
                        "type": "integer",
                        "description": "Image height",
                        "default": 600,
                    },
                },
            },
        ),
        Tool(
            name="execute_code",
            description="Execute arbitrary Python code in Blender (advanced)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Python code to execute (has access to bpy module)",
                    },
                },
                "required": ["code"],
            },
        ),
        Tool(
            name="spin",
            description="Spin/revolve selected geometry around an axis (lathe operation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to spin",
                    },
                    "angle": {
                        "type": "number",
                        "description": "Spin angle in degrees (360 for full revolution)",
                        "default": 360,
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Number of steps in the revolution",
                        "default": 12,
                    },
                    "axis": {
                        "type": "string",
                        "enum": ["X", "Y", "Z"],
                        "description": "Axis to spin around",
                        "default": "Z",
                    },
                    "center": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Center point [x, y, z]",
                        "default": [0, 0, 0],
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="screw_modifier",
            description="Add a screw modifier (helix/spiral extrusion along axis)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to modify",
                    },
                    "screw_offset": {
                        "type": "number",
                        "description": "Screw offset distance per revolution",
                        "default": 1,
                    },
                    "angle": {
                        "type": "number",
                        "description": "Total rotation angle in degrees",
                        "default": 360,
                    },
                    "iterations": {
                        "type": "integer",
                        "description": "Number of screw turns",
                        "default": 2,
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Steps per revolution",
                        "default": 16,
                    },
                    "axis": {
                        "type": "string",
                        "enum": ["X", "Y", "Z"],
                        "description": "Screw axis",
                        "default": "Z",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="create_spiral",
            description="Create a spiral/helix curve",
            inputSchema={
                "type": "object",
                "properties": {
                    "turns": {
                        "type": "number",
                        "description": "Number of spiral turns",
                        "default": 2,
                    },
                    "steps": {
                        "type": "integer",
                        "description": "Points per turn (smoothness)",
                        "default": 24,
                    },
                    "radius_start": {
                        "type": "number",
                        "description": "Starting radius",
                        "default": 1,
                    },
                    "radius_end": {
                        "type": "number",
                        "description": "Ending radius (same as start for uniform helix)",
                        "default": 1,
                    },
                    "height": {
                        "type": "number",
                        "description": "Total height of spiral",
                        "default": 2,
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["CLOCKWISE", "COUNTER_CLOCKWISE"],
                        "description": "Spiral direction",
                        "default": "COUNTER_CLOCKWISE",
                    },
                },
            },
        ),
        Tool(
            name="curve_to_mesh",
            description="Convert a curve to mesh geometry",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Curve object to convert",
                    },
                    "bevel_depth": {
                        "type": "number",
                        "description": "Bevel depth (pipe radius)",
                        "default": 0,
                    },
                    "bevel_resolution": {
                        "type": "integer",
                        "description": "Bevel resolution (smoothness)",
                        "default": 4,
                    },
                },
                "required": ["object_name"],
            },
        ),
        # === HIGH-PRIORITY MESH TOOLS FOR 3D PRINTING ===
        Tool(
            name="fill_holes",
            description="Fill holes/gaps in mesh by creating faces on boundary edges",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object to fill",
                    },
                    "sides": {
                        "type": "integer",
                        "description": "Maximum sides of hole to fill (0 = all)",
                        "default": 0,
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="bridge_edges",
            description="Bridge two edge loops to create connecting faces",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object",
                    },
                    "edge_indices_1": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "First edge loop indices",
                    },
                    "edge_indices_2": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Second edge loop indices",
                    },
                    "segments": {
                        "type": "integer",
                        "description": "Number of bridge segments",
                        "default": 1,
                    },
                },
                "required": ["object_name", "edge_indices_1", "edge_indices_2"],
            },
        ),
        Tool(
            name="subdivide_mesh",
            description="Subdivide mesh geometry to increase detail",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object to subdivide",
                    },
                    "cuts": {
                        "type": "integer",
                        "description": "Number of cuts per edge",
                        "default": 1,
                    },
                    "smoothness": {
                        "type": "number",
                        "description": "Smooth factor (0-1)",
                        "default": 0,
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="merge_vertices",
            description="Merge selected or nearby vertices",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object",
                    },
                    "merge_type": {
                        "type": "string",
                        "enum": ["CENTER", "AT_FIRST", "AT_LAST", "BY_DISTANCE"],
                        "description": "How to merge vertices",
                        "default": "BY_DISTANCE",
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Distance threshold for BY_DISTANCE mode",
                        "default": 0.0001,
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="export_stl",
            description="Export object to STL for 3D printing",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to export",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Output STL file path",
                    },
                    "ascii": {
                        "type": "boolean",
                        "description": "ASCII format vs binary",
                        "default": False,
                    },
                    "apply_modifiers": {
                        "type": "boolean",
                        "description": "Apply modifiers before export",
                        "default": True,
                    },
                },
                "required": ["object_name", "file_path"],
            },
        ),
        Tool(
            name="get_mesh_stats",
            description="Get mesh statistics for validation (vertices, faces, manifold status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object to analyze",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="knife_cut",
            description="Cut through mesh geometry with a line",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object to cut",
                    },
                    "cut_start": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Start point [x, y, z]",
                    },
                    "cut_end": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "End point [x, y, z]",
                    },
                    "cut_through": {
                        "type": "boolean",
                        "description": "Cut through entire mesh",
                        "default": True,
                    },
                },
                "required": ["object_name", "cut_start", "cut_end"],
            },
        ),
        Tool(
            name="assign_material",
            description="Create and assign a material to an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to assign material to",
                    },
                    "material_name": {
                        "type": "string",
                        "description": "Name for the material",
                    },
                    "color": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "RGB color values [0-1, 0-1, 0-1]",
                        "default": [0.8, 0.8, 0.8],
                    },
                    "metallic": {
                        "type": "number",
                        "description": "Metallic factor (0-1)",
                        "default": 0,
                    },
                    "roughness": {
                        "type": "number",
                        "description": "Roughness factor (0-1)",
                        "default": 0.5,
                    },
                },
                "required": ["object_name", "material_name"],
            },
        ),
        Tool(
            name="fillet_edges",
            description="Apply rounded fillet to selected edges (smooth radius)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object to fillet",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Fillet radius",
                    },
                    "segments": {
                        "type": "integer",
                        "description": "Number of segments for smoothness (higher = smoother)",
                        "default": 4,
                    },
                    "edge_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Edge indices to fillet (empty = all edges)",
                        "default": [],
                    },
                },
                "required": ["object_name", "radius"],
            },
        ),
        Tool(
            name="chamfer_edges",
            description="Apply flat chamfer/bevel to selected edges (angled cut)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Mesh object to chamfer",
                    },
                    "size": {
                        "type": "number",
                        "description": "Chamfer size (width)",
                    },
                    "edge_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Edge indices to chamfer (empty = all edges)",
                        "default": [],
                    },
                },
                "required": ["object_name", "size"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a Blender modeling tool."""
    command = {
        "tool": name,
        "arguments": arguments,
    }
    
    result = send_to_blender(command)
    
    if result.get("success"):
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    else:
        return [TextContent(
            type="text",
            text=f"Error: {result.get('error', 'Unknown error')}"
        )]


def main():
    """Run the Blender MCP server."""
    import asyncio
    
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
