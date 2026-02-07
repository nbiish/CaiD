# CaiD - PRD (Product Requirements Document)

## Project Overview

- **Name:** CaiD (CAD AI Design)
- **Version:** 0.3.0
- **Description:** Two MCP servers for AI-assisted 3D modeling
- **Purpose:** Enable LLMs to create/edit 3D models via FreeCAD and Blender
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
│ (Bridge)        │     │ (Bridge)        │
└─────────────────┘     └─────────────────┘
```

## Components

### 1. freecad-mcp (23 tools)
Parametric CAD modeling for mechanical engineering and precise parts.

| Category | Tools |
|----------|-------|
| **Primitives** | `create_primitive`, `create_document` |
| **Sketching** | `create_sketch`, `add_sketch_constraint` |
| **Features** | `pad_sketch`, `pocket_sketch`, `revolve_sketch` |
| **Edges** | `fillet_edges`, `chamfer_edges` |
| **Helix/Thread** | `create_helix`, `create_thread`, `sweep_along_path` |
| **Boolean** | `boolean_operation` (union/difference/intersection) |
| **Patterns** | `linear_pattern`, `polar_pattern`, `mirror_object` |
| **Import/Export** | `import_file`, `export_stl`, `export_step` |
| **Inspection** | `get_face_names`, `get_edge_names`, `measure_distance` |
| **Parameters** | `set_parameter` |
| **Utility** | `get_screenshot`, `get_objects`, `execute_code` |

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

## Short-term Goals

> READ `llms.txt/TODO.md`

## Codebase Requirements

> READ `llms.txt/RULES.md`
