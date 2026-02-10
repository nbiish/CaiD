# FreeCAD MCP Server

Code-first approach. 2 tools, infinite capability.

## Tools

| Tool | Description |
|------|-------------|
| `execute_code` | Execute Python code in FreeCAD |
| `get_model_info` | Get objects and dimensions |

## Scripting Reference

See [FREECAD_RESOURCES.md](../llms.txt/FREECAD_RESOURCES.md) for:
- Part module: primitives, booleans, transforms
- PartDesign: Sketcher, Pad, Pocket, Hole, Fillet
- BoundBox: dimensions, volume, area
- Export: STL, STEP

## Requirements

1. FreeCAD running with MCP addon enabled
2. Addon listening on `localhost:9875`

## Install

```bash
cd freecad-mcp && uv sync
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

## Example

```python
execute_code(code="""
import Part
base = Part.makeBox(80, 40, 10)
hole = Part.makeCylinder(5, 15)
hole.translate(App.Vector(40, 20, -2))
result = base.cut(hole)
Part.show(result)
""")
```
