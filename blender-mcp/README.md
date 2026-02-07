# Blender MCP Server

AI-assisted 3D mesh modeling via Model Context Protocol.

## Features

- Create and manipulate 3D meshes in Blender
- Mesh editing (extrude, bevel, inset, loop cut)
- Non-destructive modifiers (subdivision, mirror, array)
- Object transformations
- Screenshot capture for visual feedback

## Installation

### Blender Addon

1. Open Blender → Edit → Preferences → Add-ons
2. Click "Install..." and select `addon/BlenderMCP/__init__.py`
3. Enable "Development: Blender MCP Bridge"

Or copy `addon/BlenderMCP/` to:
- **macOS**: `~/Library/Application Support/Blender/4.0/scripts/addons/`
- **Linux**: `~/.config/blender/4.0/scripts/addons/`
- **Windows**: `%APPDATA%\Blender Foundation\Blender\4.0\scripts\addons\`

### MCP Server

```bash
cd blender-mcp
uv sync
uv run blender-mcp
```

## Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "blender": {
      "command": "uv",
      "args": ["--directory", "/path/to/CaiD/blender-mcp", "run", "blender-mcp"]
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLENDER_HOST` | localhost | Blender socket host |
| `BLENDER_PORT` | 9876 | Blender socket port |

## Tools

| Tool | Description |
|------|-------------|
| `create_primitive` | Cube, UV Sphere, Cylinder, Cone, Torus, Plane |
| `extrude_faces` | Extrude selected faces |
| `inset_faces` | Inset selected faces |
| `bevel_edges` | Bevel selected edges |
| `loop_cut` | Add edge loops |
| `add_modifier` | Subdivision, Mirror, Array, Boolean |
| `apply_modifier` | Bake modifier to mesh |
| `spin` | Revolve geometry around axis (lathe operation) |
| `screw_modifier` | Add screw modifier for helix/spiral extrusion |
| `create_spiral` | Create spiral/helix curve |
| `curve_to_mesh` | Convert curve to mesh with optional bevel |
| `fillet_edges` | Apply rounded fillet to edges (smooth radius) |
| `chamfer_edges` | Apply flat chamfer to edges (angled cut) |
| `fill_holes` | Fill gaps in mesh by creating faces on boundary edges |
| `bridge_edges` | Bridge two edge loops to create connecting faces |
| `subdivide_mesh` | Subdivide mesh geometry to increase detail |
| `merge_vertices` | Merge nearby or selected vertices |
| `export_stl` | Export object to STL for 3D printing |
| `get_mesh_stats` | Get mesh validation stats (vertices, manifold status) |
| `knife_cut` | Cut through mesh geometry with a line |
| `assign_material` | Create and assign a material to an object |
| `select_geometry` | Select vertices/edges/faces |
| `transform_object` | Move, Rotate, Scale |
| `delete_object` | Remove object from scene |
| `get_objects` | List scene objects |
| `get_screenshot` | Capture viewport render |

## License

MIT
