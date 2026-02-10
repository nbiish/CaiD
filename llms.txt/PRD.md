# CaiD - PRD (Product Requirements Document)

## Project Overview

- **Name:** CaiD (CAD AI Design)
- **Version:** 0.4.0
- **Description:** Three MCP servers for AI-assisted 3D modeling
- **Purpose:** Enable LLMs to create/edit 3D models via FreeCAD, Blender, and OpenSCAD
- **UX:** MCP servers (CLI/programmatic integration)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Client     │     │   AI Client     │     │   AI Client     │
│ (Claude, etc.)  │     │ (Claude, etc.)  │     │ (Claude, etc.)  │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │ MCP                   │ MCP                   │ MCP
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  freecad-mcp    │     │  blender-mcp    │     │  openscad-mcp   │
│  (Python/uv)    │     │  (Python/uv)    │     │  (Python/uv)    │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │ XML-RPC               │ Socket                │ subprocess
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ FreeCAD Addon   │     │ Blender Addon   │     │ OpenSCAD CLI    │
│ (GUI Bridge)    │     │ (GUI Bridge)    │     │ (Headless)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Components

### 1. freecad-mcp (2 tools)
Code-first approach. Scripting reference: `llms.txt/FREECAD_RESOURCES.md`

| Tool | Description |
|------|-------------|
| `execute_code` | Execute Python code in FreeCAD |
| `get_model_info` | Get objects and dimensions |

### 2. blender-mcp (25 tools)
Mesh modeling for organic shapes, game assets, and creative 3D.

| Category | Tools |
|----------|-------|
| **Primitives** | `create_primitive` |
| **Mesh Editing** | `extrude_faces`, `inset_faces`, `loop_cut`, `subdivide_mesh` |
| **Edges** | `bevel_edges`, `fillet_edges`, `chamfer_edges` |
| **Helix/Spiral** | `spin`, `screw_modifier`, `create_spiral`, `curve_to_mesh` |
| **Mesh Repair** | `fill_holes`, `bridge_edges`, `merge_vertices` |
| **Cutting** | `knife_cut` |
| **Modifiers** | `add_modifier`, `apply_modifier` |
| **Materials** | `assign_material` |
| **Selection** | `select_geometry` |
| **Transform** | `transform_object`, `delete_object` |
| **Export** | `export_stl` |
| **Inspection** | `get_mesh_stats`, `get_objects`, `get_screenshot` |

### 3. openscad-mcp (1 tool)
Code-first approach. Scripting reference: `llms.txt/OPENSCAD_RESOURCES.md`

| Tool | Description |
|------|-------------|
| `execute_scad` | Execute OpenSCAD code, export STL |

## Short-term Goals

> READ `llms.txt/TODO.md`

## Codebase Requirements

> READ `llms.txt/RULES.md`

