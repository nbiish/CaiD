# CaiD - PRD (Product Requirements Document)

## Project Overview

- **Name:** CaiD (CAD AI Design)
- **Version:** 0.4.0
- **Description:** Three MCP servers for AI-assisted 3D modeling
- **Purpose:** Enable LLMs to create/edit 3D models via FreeCAD, Blender, and OpenSCAD
- **UX:** MCP servers (CLI/programmatic integration)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   AI Client     │     │   AI Client     │
│ (Claude, etc.)  │     │ (Claude, etc.)  │
└────────┬────────┘     └────────┬────────┘
         │ MCP                   │ MCP
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  freecad-mcp    │     │  blender-mcp    │
│  (Python/uv)    │     │  (Python/uv)    │
└────────┬────────┘     └────────┬────────┘
         │ XML-RPC               │ Socket
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│ FreeCAD Addon   │     │ Blender Addon   │
│ (GUI Bridge)    │     │ (GUI Bridge)    │
└─────────────────┘     └─────────────────┘
```

## Components

### 1. freecad-mcp (4 tools) - ✅ STABLE / PROVEN (v0.2.0)
Code-first approach. Scripting reference: `llms.txt/FREECAD_RESOURCES.md`
**Success Story**: Fully modeled parametric Heltec V4 Case (Base + Lid + Snap-fits + Text) entirely via MCP.

| Tool | Description |
|------|-------------|
| `execute_code` | Execute Python code in FreeCAD |
| `get_model_info` | Get objects and dimensions |
| `get_selection` | Get selected faces/edges/objects |
| `get_screenshot` | Capture 3D viewport image |

### 2. blender-mcp (25 tools) - ✅ ALPHA (Verified)
**Focus**: Engineering, Parametric Modeling, and Bevels/Chamfers (Code-First).
Scripting reference: `llms.txt/BLENDER_RESOURCES.md`
**Success Story**: Manually injected server via script, verified connection, and parametrically modeled a chamfered bolt with clean topology.

| Category | Tools |

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


## Short-term Goals

> READ `llms.txt/TODO.md`

## Codebase Requirements

> READ `llms.txt/RULES.md`

