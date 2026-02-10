# FreeCAD MCP Server

Code-first approach. 4 tools, infinite capability.

## Tools

| Tool | Description |
|------|-------------|
| `execute_code` | Execute Python in FreeCAD |
| `get_model_info` | Get objects and dimensions |
| `get_selection` | Get selected faces/edges/objects |
| `get_screenshot` | Capture 3D viewport image |

## Scripting Reference

See [FREECAD_RESOURCES.md](../llms.txt/FREECAD_RESOURCES.md) for patterns:
- Primitives, booleans, transforms
- PartDesign: Sketcher, Pad, Pocket, Fillet
- Selection API (interactive modeling)
- 3D text, snap-fit clips, tolerances

## Requirements

1. FreeCAD running with MCP addon (auto-starts on launch)
2. Addon listens on `localhost:9875`

## Install

```bash
cd freecad-mcp && uv sync
cp -r addon/FreeCADMCP ~/Library/Application\ Support/FreeCAD/Mod/
```

## Claude Desktop

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

## Manual Start (if auto-start fails)

In FreeCAD Python console:
```python
from FreeCADMCP import rpc_server
rpc_server.start_server()
```
