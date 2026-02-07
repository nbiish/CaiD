# FreeCAD MCP Server

AI-assisted parametric 3D CAD modeling via Model Context Protocol.

## Features

- Create and manage FreeCAD documents
- Parametric modeling with Part/PartDesign workbenches
- Sketch-based design with constraints
- STEP file export
- Screenshot capture for visual feedback

## Installation

### FreeCAD Addon

Copy the `addon/FreeCADMCP/` directory to your FreeCAD Mod folder:

- **macOS**: `~/Library/Application Support/FreeCAD/Mod/`
- **Linux**: `~/.FreeCAD/Mod/` or `~/.local/share/FreeCAD/Mod/`
- **Windows**: `%APPDATA%\FreeCAD\Mod\`

Restart FreeCAD and enable the addon.

### MCP Server

```bash
cd freecad-mcp
uv sync
uv run freecad-mcp
```

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "freecad": {
      "command": "uv",
      "args": ["--directory", "/path/to/CaiD/freecad-mcp", "run", "freecad-mcp"]
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `create_document` | Create a new FreeCAD document |
| `create_primitive` | Create Box, Cylinder, Sphere, Cone, Torus |
| `create_sketch` | Create 2D sketch with constraints |
| `pad_sketch` | Extrude sketch (PartDesign Pad) |
| `pocket_sketch` | Cut into solid (PartDesign Pocket) |
| `fillet_edges` | Round selected edges |
| `chamfer_edges` | Bevel selected edges |
| `set_parameter` | Update spreadsheet parameter |
| `create_helix` | Create helix/spiral path (springs, coils) |
| `create_thread` | Create screw threads (metric, imperial, trapezoidal) |
| `sweep_along_path` | Sweep profile along helix/path |
| `revolve_sketch` | Revolve sketch around axis (lathe) |
| `boolean_operation` | Union/Difference/Intersection between shapes |
| `import_file` | Import STEP, IGES, STL, BREP files |
| `export_stl` | Export to STL for 3D printing |
| `get_face_names` | Get face info for geometry introspection |
| `get_edge_names` | Get edge info for geometry introspection |
| `linear_pattern` | Create linear array of objects |
| `polar_pattern` | Create circular array around axis |
| `mirror_object` | Mirror object across a plane |
| `measure_distance` | Measure distance between geometry |
| `add_sketch_constraint` | Add parametric constraints to sketch |
| `export_step` | Export to STEP format |
| `get_screenshot` | Capture current viewport |

## License

MIT
