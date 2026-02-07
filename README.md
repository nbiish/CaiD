# CaiD - CAD AI Design

> Two Model Context Protocol (MCP) servers for AI-assisted 3D modeling

## Overview

CaiD provides AI-powered 3D modeling through two focused MCP servers:

| Server | Application | Focus | Use Case |
|--------|-------------|-------|----------|
| **freecad-mcp** | FreeCAD | Parametric CAD | Engineering, mechanical parts |
| **blender-mcp** | Blender | Mesh modeling | Creative 3D, organic shapes |

## Quick Start

### FreeCAD MCP

```bash
# Install addon in FreeCAD
cp -r freecad-mcp/addon/FreeCADMCP ~/Library/Application\ Support/FreeCAD/Mod/

# Run MCP server
cd freecad-mcp && uv sync && uv run freecad-mcp
```

### Blender MCP

```bash
# Install addon via Blender Preferences > Add-ons > Install
# Or copy manually:
cp -r blender-mcp/addon/BlenderMCP ~/.config/blender/4.0/scripts/addons/

# Run MCP server
cd blender-mcp && uv sync && uv run blender-mcp
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "freecad": {
      "command": "uv",
      "args": ["--directory", "/path/to/CaiD/freecad-mcp", "run", "freecad-mcp"]
    },
    "blender": {
      "command": "uv",
      "args": ["--directory", "/path/to/CaiD/blender-mcp", "run", "blender-mcp"]
    }
  }
}
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Claude    │────▶│ freecad-mcp  │────▶│    FreeCAD     │
│   (LLM)     │     │  (MCP/RPC)   │     │  (GUI/Headless)│
└─────────────┘     └──────────────┘     └────────────────┘
       │
       │            ┌──────────────┐     ┌────────────────┐
       └───────────▶│ blender-mcp  │────▶│    Blender     │
                    │ (MCP/Socket) │     │ (GUI/Background)│
                    └──────────────┘     └────────────────┘
```

## FreeCAD Tools

- `create_document` - New document
- `create_primitive` - Box, Cylinder, Sphere, Cone, Torus
- `create_sketch` - 2D parametric sketch
- `pad_sketch` / `pocket_sketch` - Extrude / Cut
- `fillet_edges` / `chamfer_edges` - Edge operations
- `create_helix` - Spiral path for springs/threads
- `create_thread` - Screw threads (metric, imperial, trapezoidal)
- `sweep_along_path` - Sweep profile along helix
- `revolve_sketch` - Lathe operation
- `set_parameter` - Spreadsheet parameters
- `export_step` - STEP export / `get_screenshot` - Visual feedback

## Blender Tools

- `create_primitive` - Cube, Sphere, Cylinder, Cone, Torus, Plane
- `extrude_faces` / `inset_faces` - Face operations
- `bevel_edges` / `loop_cut` - Edge operations
- `add_modifier` / `apply_modifier` - Subdivision, Mirror, Array, Boolean
- `spin` - Revolve geometry (lathe operation)
- `screw_modifier` - Helix/spiral extrusion
- `create_spiral` - Spiral/helix curve
- `curve_to_mesh` - Convert curve to mesh
- `select_geometry` - Vertex/Edge/Face selection
- `transform_object` - Move, Rotate, Scale
- `get_screenshot` - Visual feedback

## License

MIT
