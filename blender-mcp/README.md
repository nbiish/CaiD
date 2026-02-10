# Blender MCP Server

AI-assisted 3D mesh modeling via Model Context Protocol.

> ✅ **Live Tested**: Core tools verified (2026-02-07) | **Focus**: Engineering/Modeling

## Features

- Create and manipulate 3D meshes in Blender
- **Engineering focus**: Chamfers, bevels, precision modeling
- Non-destructive modifiers (subdivision, mirror, array)
- STL export for 3D printing (Blender 5.0 compatible)
- Screenshot capture for visual feedback

## Installation

### Blender Addon

Copy `addon/BlenderMCP/` to your Blender addons folder:

- **macOS**: `~/Library/Application Support/Blender/5.0/scripts/addons/`
- **Linux**: `~/.config/blender/5.0/scripts/addons/`
- **Windows**: `%APPDATA%\Blender Foundation\Blender\5.0\scripts\addons\`

Then in Blender:
1. **Edit → Preferences → Add-ons**
2. Search for "MCP" and enable **"Blender MCP Bridge"**
3. Open **Sidebar (N key) → MCP tab → Start Server**

### MCP Server

```bash
cd blender-mcp
uv sync
uv run blender-mcp
```

## Claude Desktop Configuration

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

## Tools (25 Total)

### Primitives & Objects
| Tool | Description | Status |
|------|-------------|--------|
| `create_primitive` | Cube, Sphere, Cylinder, Cone, Torus, Plane | ✅ |
| `get_objects` | List scene objects with vertex/face counts | ✅ |
| `delete_object` | Remove object from scene | ✅ |
| `transform_object` | Move, Rotate, Scale | ✅ |

### Mesh Editing
| Tool | Description | Status |
|------|-------------|--------|
| `extrude_faces` | Extrude selected faces | ✅ |
| `inset_faces` | Inset selected faces | ✅ |
| `bevel_edges` | Bevel selected edges (chamfer) | ✅ |
| `loop_cut` | Add edge loops | ✅ |
| `knife_cut` | Cut through geometry | ✅ |

### Modifiers
| Tool | Description | Status |
|------|-------------|--------|
| `add_modifier` | Subdivision, Mirror, Array, Boolean | ✅ |
| `apply_modifier` | Bake modifier to mesh | ✅ |

### Spiral/Helix (Engineering)
| Tool | Description | Status |
|------|-------------|--------|
| `spin` | Revolve geometry (lathe operation) | ✅ |
| `screw_modifier` | Helix/spiral extrusion | ✅ |
| `create_spiral` | Spiral/helix curve | ✅ |
| `curve_to_mesh` | Convert curve to mesh | ✅ |

### Edge Finishing (Engineering)
| Tool | Description | Status |
|------|-------------|--------|
| `fillet_edges` | Rounded fillet on edges | ✅ |
| `chamfer_edges` | Flat chamfer on edges | ✅ |

### Mesh Repair
| Tool | Description | Status |
|------|-------------|--------|
| `fill_holes` | Fill gaps in mesh | ✅ |
| `bridge_edges` | Bridge two edge loops | ✅ |
| `subdivide_mesh` | Increase mesh detail | ✅ |
| `merge_vertices` | Clean topology | ✅ |
| `get_mesh_stats` | Mesh validation stats | ✅ |

### Export & Materials
| Tool | Description | Status |
|------|-------------|--------|
| `export_stl` | STL for 3D printing (Blender 5.0+) | ✅ |
| `assign_material` | Create and assign materials | ✅ |
| `get_screenshot` | Capture viewport render | ✅ |

## Engineering Example

```python
# Create M8 bolt shank with chamfered edges
create_primitive(shape="Cylinder", name="M8_Shank", size=0.4)
bevel_edges(object_name="M8_Shank", width=0.05, segments=2)

# Create chamfered alignment peg
create_primitive(shape="Cylinder", name="ChamferPeg", size=0.3, location=[2, 0, 0])
bevel_edges(object_name="ChamferPeg", width=0.1, segments=1)

# Create mounting bracket
create_primitive(shape="Cube", name="MountBracket", size=1, location=[-2, 0, 0])
extrude_faces(object_name="MountBracket", depth=0.5, select_all=True)

# Export for 3D printing
export_stl(object_name="M8_Shank", file_path="/path/to/m8_shank.stl")
```

## Architecture

```
┌─────────────────┐     stdio      ┌──────────────────┐
│  Claude/Client  │ ◄────────────► │  blender-mcp     │
│     (MCP)       │                │  (Python server) │
└─────────────────┘                └────────┬─────────┘
                                            │ Socket
                                            │ :9876
                                   ┌────────▼─────────┐
                                   │  Blender Addon   │
                                   │  (MCP Bridge)    │
                                   └──────────────────┘
```

## License

MIT
