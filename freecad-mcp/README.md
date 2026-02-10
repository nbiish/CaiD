# FreeCAD MCP Server

Code-first CAD modeling. 4 tools, infinite capability.

> **✅ Success Story**: Modeled [Heltec V4 Case](https://github.com/nbiish/CaiD/result/HeltecV4) parametrically via MCP.

## Tools

| Tool | Description |
|------|-------------|
| `execute_code` | Execute Python in FreeCAD |
| `get_model_info` | Get objects and dimensions |
| `get_selection` | Get selected faces/edges/objects |
| `get_screenshot` | Capture 3D viewport image |

## Scripting Reference

See [FREECAD_RESOURCES.md](../llms.txt/FREECAD_RESOURCES.md) for patterns.

## Install

### 1. MCP Server (Python package)

```bash
cd freecad-mcp && uv sync
```

### 2. FreeCAD Addon

Copy the addon to FreeCAD's Mod directory:

```bash
# Find your Mod path — run in FreeCAD's Python console:
# print(FreeCAD.getUserAppDataDir() + "Mod")

# macOS (standard or external drive install)
cp -r addon/FreeCADMCP ~/Library/Application\ Support/FreeCAD/Mod/

# Linux
cp -r addon/FreeCADMCP ~/.local/share/FreeCAD/Mod/

# Windows
# Copy addon/FreeCADMCP to %APPDATA%/FreeCAD/Mod/
```

### 3. Start the MCP Bridge

> **Required each FreeCAD session.** Paste this in FreeCAD's Python console:

```python
from FreeCADMCP import rpc_server; rpc_server.start_server()
```

You should see: `FreeCAD MCP Server started on localhost:9875`

#### Optional: Create a Startup Macro

To avoid typing the command manually, create a FreeCAD macro:

1. In FreeCAD: **Macro → Macros → Create**
2. Name it `StartMCP.FCMacro`
3. Paste this content:
   ```python
   from FreeCADMCP import rpc_server
   rpc_server.start_server()
   ```
4. Save and run it each session, or assign it to a toolbar button

## MCP Client Config

```json
{
  "mcpServers": {
    "freecad": {
      "command": "uv",
      "args": ["--directory", "/path/to/freecad-mcp", "run", "freecad-mcp"]
    }
  }
}
```

## Architecture

```
MCP Client ←→ server.py (stdio) ←→ XML-RPC ←→ rpc_server.py (inside FreeCAD)
```
