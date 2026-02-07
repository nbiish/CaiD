"""FreeCAD MCP Addon - GUI initialization.

This file is loaded by FreeCAD at startup and initializes the MCP Bridge.
FreeCAD expects this file for addons that need GUI components.
"""


def InitGui():
    """Initialize the GUI components - called by FreeCAD at startup."""
    import FreeCAD
    FreeCAD.Console.PrintMessage("FreeCADMCP: InitGui called\n")
    # Server starts automatically when rpc_server is imported
