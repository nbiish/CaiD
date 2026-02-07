"""FreeCAD MCP Addon - Module initialization.

This file is loaded by FreeCAD at startup for non-GUI initialization.
The RPC server is started with a delay to ensure FreeCAD is fully loaded.
"""

import FreeCAD
from PySide2 import QtCore  # Use PySide2 for Qt timer (FreeCAD's Qt binding)


def _start_mcp_server():
    """Start the MCP server after FreeCAD is ready."""
    try:
        from FreeCADMCP import rpc_server
        rpc_server.start_server()
        FreeCAD.Console.PrintMessage("FreeCADMCP: MCP Bridge started on localhost:9875\n")
    except Exception as e:
        FreeCAD.Console.PrintError(f"FreeCADMCP: Failed to start MCP Bridge: {e}\n")


# Start server after a short delay to let FreeCAD fully initialize
FreeCAD.Console.PrintMessage("FreeCADMCP: Loading MCP Bridge addon (will start in 2 seconds)...\n")
QtCore.QTimer.singleShot(2000, _start_mcp_server)
