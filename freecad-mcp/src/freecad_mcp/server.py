"""FreeCAD MCP Server implementation.

This server provides tools for AI-assisted parametric 3D modeling in FreeCAD.
Communication with FreeCAD happens via XML-RPC to the FreeCAD addon.
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


# Initialize MCP server
server = Server("freecad-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available FreeCAD modeling tools."""
    return [
        Tool(
            name="create_document",
            description="Create a new FreeCAD document",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Document name",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="create_primitive",
            description="Create a primitive shape (Box, Cylinder, Sphere, Cone, Torus)",
            inputSchema={
                "type": "object",
                "properties": {
                    "shape": {
                        "type": "string",
                        "enum": ["Box", "Cylinder", "Sphere", "Cone", "Torus"],
                        "description": "Type of primitive shape",
                    },
                    "name": {
                        "type": "string",
                        "description": "Object name",
                    },
                    "params": {
                        "type": "object",
                        "description": "Shape parameters (e.g., Length, Width, Height for Box)",
                    },
                },
                "required": ["shape"],
            },
        ),
        Tool(
            name="create_sketch",
            description="Create a 2D sketch for parametric modeling",
            inputSchema={
                "type": "object",
                "properties": {
                    "plane": {
                        "type": "string",
                        "enum": ["XY", "XZ", "YZ"],
                        "description": "Sketch plane",
                        "default": "XY",
                    },
                    "geometry": {
                        "type": "array",
                        "description": "List of geometry elements (lines, circles, arcs)",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "params": {"type": "object"},
                            },
                        },
                    },
                },
            },
        ),
        Tool(
            name="pad_sketch",
            description="Extrude a sketch to create a solid (PartDesign Pad)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sketch_name": {
                        "type": "string",
                        "description": "Name of sketch to extrude",
                    },
                    "length": {
                        "type": "number",
                        "description": "Extrusion length in mm",
                    },
                    "symmetric": {
                        "type": "boolean",
                        "description": "Extrude symmetrically",
                        "default": False,
                    },
                },
                "required": ["sketch_name", "length"],
            },
        ),
        Tool(
            name="pocket_sketch",
            description="Cut into a solid using a sketch (PartDesign Pocket)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sketch_name": {
                        "type": "string",
                        "description": "Name of sketch to cut",
                    },
                    "depth": {
                        "type": "number",
                        "description": "Cut depth in mm",
                    },
                    "through_all": {
                        "type": "boolean",
                        "description": "Cut through entire solid",
                        "default": False,
                    },
                },
                "required": ["sketch_name"],
            },
        ),
        Tool(
            name="fillet_edges",
            description="Apply fillet (rounded) to selected edges",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to fillet",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Fillet radius in mm",
                    },
                    "edges": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Edge names to fillet (e.g., ['Edge1', 'Edge2'])",
                    },
                },
                "required": ["object_name", "radius"],
            },
        ),
        Tool(
            name="chamfer_edges",
            description="Apply chamfer (bevel) to selected edges",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to chamfer",
                    },
                    "size": {
                        "type": "number",
                        "description": "Chamfer size in mm",
                    },
                    "edges": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Edge names to chamfer",
                    },
                },
                "required": ["object_name", "size"],
            },
        ),
        Tool(
            name="set_parameter",
            description="Update a parameter in the spreadsheet for parametric design",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Parameter name/alias",
                    },
                    "value": {
                        "type": ["number", "string"],
                        "description": "New parameter value",
                    },
                },
                "required": ["name", "value"],
            },
        ),
        Tool(
            name="export_step",
            description="Export the model to STEP format",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Output file path (.step)",
                    },
                    "objects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Object names to export (empty for all)",
                    },
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="get_screenshot",
            description="Capture a screenshot of the current FreeCAD view",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {
                        "type": "integer",
                        "description": "Image width in pixels",
                        "default": 800,
                    },
                    "height": {
                        "type": "integer",
                        "description": "Image height in pixels",
                        "default": 600,
                    },
                },
            },
        ),
        Tool(
            name="get_objects",
            description="List all objects in the current document",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="execute_code",
            description="Execute arbitrary Python code in FreeCAD (advanced)",
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
            name="create_helix",
            description="Create a helix/spiral path (for springs, coils, threads)",
            inputSchema={
                "type": "object",
                "properties": {
                    "pitch": {
                        "type": "number",
                        "description": "Distance between turns in mm",
                    },
                    "height": {
                        "type": "number",
                        "description": "Total height of helix in mm",
                    },
                    "radius": {
                        "type": "number",
                        "description": "Radius of helix in mm",
                    },
                    "angle": {
                        "type": "number",
                        "description": "Cone angle in degrees (0 for cylinder, >0 for cone)",
                        "default": 0,
                    },
                    "left_handed": {
                        "type": "boolean",
                        "description": "Left-handed helix (counter-clockwise)",
                        "default": False,
                    },
                },
                "required": ["pitch", "height", "radius"],
            },
        ),
        Tool(
            name="create_thread",
            description="Create a screw thread on a cylindrical object",
            inputSchema={
                "type": "object",
                "properties": {
                    "diameter": {
                        "type": "number",
                        "description": "Major diameter of thread in mm",
                    },
                    "pitch": {
                        "type": "number",
                        "description": "Thread pitch (distance between threads) in mm",
                    },
                    "length": {
                        "type": "number",
                        "description": "Thread length in mm",
                    },
                    "internal": {
                        "type": "boolean",
                        "description": "Internal thread (nut) vs external (bolt)",
                        "default": False,
                    },
                    "thread_type": {
                        "type": "string",
                        "enum": ["metric", "imperial", "trapezoidal"],
                        "description": "Thread profile type",
                        "default": "metric",
                    },
                },
                "required": ["diameter", "pitch", "length"],
            },
        ),
        Tool(
            name="sweep_along_path",
            description="Sweep a profile along a path (e.g., circle along helix for spring)",
            inputSchema={
                "type": "object",
                "properties": {
                    "profile_name": {
                        "type": "string",
                        "description": "Name of sketch/shape to sweep",
                    },
                    "path_name": {
                        "type": "string",
                        "description": "Name of path (helix, wire, edge) to sweep along",
                    },
                    "solid": {
                        "type": "boolean",
                        "description": "Create solid (True) or shell (False)",
                        "default": True,
                    },
                },
                "required": ["profile_name", "path_name"],
            },
        ),
        Tool(
            name="revolve_sketch",
            description="Revolve a sketch around an axis (lathe operation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sketch_name": {
                        "type": "string",
                        "description": "Name of sketch to revolve",
                    },
                    "angle": {
                        "type": "number",
                        "description": "Revolution angle in degrees (360 for full)",
                        "default": 360,
                    },
                    "axis": {
                        "type": "string",
                        "enum": ["X", "Y", "Z"],
                        "description": "Axis to revolve around",
                        "default": "Z",
                    },
                },
                "required": ["sketch_name"],
            },
        ),
        # === HIGH-PRIORITY TOOLS FOR 3D PRINTING WORKFLOW ===
        Tool(
            name="boolean_operation",
            description="Perform boolean operation (union/difference/intersection) between shapes",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["union", "difference", "intersection"],
                        "description": "Boolean operation type",
                    },
                    "base_object": {
                        "type": "string",
                        "description": "Name of base object",
                    },
                    "tool_objects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Names of objects to combine with base",
                    },
                },
                "required": ["operation", "base_object", "tool_objects"],
            },
        ),
        Tool(
            name="import_file",
            description="Import CAD file (STEP, IGES, STL, BREP) into document",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to file to import",
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["step", "iges", "stl", "brep", "auto"],
                        "description": "File format (auto-detected if not specified)",
                        "default": "auto",
                    },
                },
                "required": ["file_path"],
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
                        "description": "ASCII format (larger file) vs binary",
                        "default": False,
                    },
                },
                "required": ["object_name", "file_path"],
            },
        ),
        Tool(
            name="get_face_names",
            description="Get list of faces with their properties for geometry introspection",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to inspect",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="get_edge_names",
            description="Get list of edges with their properties for geometry introspection",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to inspect",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="linear_pattern",
            description="Create linear array of a feature or object",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to pattern",
                    },
                    "direction": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Direction vector [x, y, z]",
                    },
                    "length": {
                        "type": "number",
                        "description": "Total length of pattern in mm",
                    },
                    "occurrences": {
                        "type": "integer",
                        "description": "Number of copies (including original)",
                    },
                },
                "required": ["object_name", "direction", "occurrences"],
            },
        ),
        Tool(
            name="polar_pattern",
            description="Create circular array around an axis",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to pattern",
                    },
                    "axis": {
                        "type": "string",
                        "enum": ["X", "Y", "Z"],
                        "description": "Rotation axis",
                        "default": "Z",
                    },
                    "center": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Center point [x, y, z]",
                        "default": [0, 0, 0],
                    },
                    "angle": {
                        "type": "number",
                        "description": "Total angle in degrees",
                        "default": 360,
                    },
                    "occurrences": {
                        "type": "integer",
                        "description": "Number of copies (including original)",
                    },
                },
                "required": ["object_name", "occurrences"],
            },
        ),
        Tool(
            name="mirror_object",
            description="Mirror an object across a plane",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to mirror",
                    },
                    "plane": {
                        "type": "string",
                        "enum": ["XY", "XZ", "YZ"],
                        "description": "Mirror plane",
                        "default": "XY",
                    },
                },
                "required": ["object_name"],
            },
        ),
        Tool(
            name="measure_distance",
            description="Measure distance between two points, edges, or faces",
            inputSchema={
                "type": "object",
                "properties": {
                    "object1": {
                        "type": "string",
                        "description": "First object name",
                    },
                    "subelement1": {
                        "type": "string",
                        "description": "Subelement (e.g., 'Face1', 'Edge1', 'Vertex1')",
                        "default": "",
                    },
                    "object2": {
                        "type": "string",
                        "description": "Second object name",
                    },
                    "subelement2": {
                        "type": "string",
                        "description": "Subelement on second object",
                        "default": "",
                    },
                },
                "required": ["object1", "object2"],
            },
        ),
        Tool(
            name="add_sketch_constraint",
            description="Add constraint to sketch geometry (horizontal, vertical, distance, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sketch_name": {
                        "type": "string",
                        "description": "Sketch to constrain",
                    },
                    "constraint_type": {
                        "type": "string",
                        "enum": ["Horizontal", "Vertical", "Distance", "DistanceX", "DistanceY",
                                 "Radius", "Diameter", "Coincident", "Tangent", "Parallel",
                                 "Perpendicular", "Equal", "Symmetric", "Fixed"],
                        "description": "Type of constraint",
                    },
                    "geometry_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Geometry indices to constrain (0-based)",
                    },
                    "value": {
                        "type": "number",
                        "description": "Value for dimensional constraints",
                    },
                },
                "required": ["sketch_name", "constraint_type", "geometry_indices"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute a FreeCAD modeling tool."""
    try:
        client = get_rpc_client()
        
        # Call the corresponding RPC method
        result = client.execute_tool(name, json.dumps(arguments))
        result_data = json.loads(result)
        
        if result_data.get("success"):
            return [TextContent(type="text", text=json.dumps(result_data, indent=2))]
        else:
            return [TextContent(
                type="text",
                text=f"Error: {result_data.get('error', 'Unknown error')}"
            )]
            
    except ConnectionRefusedError:
        return [TextContent(
            type="text",
            text="Error: Cannot connect to FreeCAD. Ensure FreeCAD is running with the MCP addon enabled."
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


def main():
    """Run the FreeCAD MCP server."""
    import asyncio
    
    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
