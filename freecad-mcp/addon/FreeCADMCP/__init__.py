"""FreeCAD MCP Addon - XML-RPC bridge for AI-assisted modeling.

This addon creates an XML-RPC server inside FreeCAD that receives
commands from the MCP server and executes them in FreeCAD's context.
"""

bl_info = {
    "name": "FreeCAD MCP Bridge",
    "author": "CaiD Team",
    "version": (0, 1, 0),
    "freecad": "0.21",
    "location": "View > Panels > MCP Bridge",
    "description": "XML-RPC server for AI-assisted CAD modeling",
    "category": "Development",
}
