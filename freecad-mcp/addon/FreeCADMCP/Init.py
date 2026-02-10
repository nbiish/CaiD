"""FreeCAD MCP Addon — Module initialization.

Starts XML-RPC server after FreeCAD loads.
"""

import FreeCAD

try:
    from PySide6 import QtCore
except ImportError:
    from PySide2 import QtCore


def _start_mcp_server():
    try:
        from FreeCADMCP import rpc_server
        rpc_server.start_server()
        FreeCAD.Console.PrintMessage("FreeCADMCP: MCP Bridge started on localhost:9875\n")
    except Exception as e:
        FreeCAD.Console.PrintError(f"FreeCADMCP: Failed to start: {e}\n")


FreeCAD.Console.PrintMessage("FreeCADMCP: Loading (will start in 2s)...\n")
QtCore.QTimer.singleShot(2000, _start_mcp_server)
