# OpenSCAD MCP Server

Single tool, infinite capability through code.

## Install

```bash
brew install openscad  # macOS
cd openscad-mcp && uv sync
```

## Tool

| Tool | Description |
|------|-------------|
| `execute_scad` | Execute OpenSCAD code. Export STL optional. |

## Usage

```
execute_scad(
  code="difference() { cube(20); cylinder(h=25, r=5); }",
  export="bracket.stl"
)
```

## Scripting Reference

See [OPENSCAD_RESOURCES.md](../llms.txt/OPENSCAD_RESOURCES.md) for:
- Primitives: cube, cylinder, sphere
- Booleans: union, difference, intersection
- Modules: reusable parametric parts
- 3D Printing: holes, channels, chamfers
- BOSL2: screw_hole, threading, rounding
- SolidPython2: Python → SCAD

## Claude Desktop

```json
{
  "mcpServers": {
    "openscad": {
      "command": "uv",
      "args": ["--directory", "/path/to/openscad-mcp", "run", "openscad-mcp"]
    }
  }
}
```
