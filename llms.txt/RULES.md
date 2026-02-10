# RULES.md

> CAD AI Design Interface standards and conventions

## Project Overview

**CaiD** (CAD AI Design) provides AI-assisted 3D modeling through MCP servers for FreeCAD and Blender.

## MCP Server Architecture

| Server | Port | Protocol | Focus |
|--------|------|----------|-------|
| Server | Port | Protocol | Focus |
|--------|------|----------|-------|
| FreeCAD MCP | 9875 | XML-RPC | Parametric CAD, engineering |
| Blender MCP | 9876 | Socket | Mesh modeling, organic shapes |

## Tool Naming Conventions

### FreeCAD Tools (23)

**Document Management**
- `create_document` – Initialize new FreeCAD project
- `get_objects` – List all document objects with metadata

**Geometry Creation**
- `create_primitive` – Generate Box, Cylinder, Sphere, Cone, Torus
- `create_sketch` – Define 2D profile with lines, arcs, rectangles
- `create_helix` – Generate spiral/coil path for springs, threads
- `create_thread` – Generate metric/imperial screw thread geometry

**Solid Operations**
- `pad_sketch` – Extrude sketch profile into solid (add material)
- `pocket_sketch` – Cut sketch profile into solid (remove material)
- `revolve_sketch` – Rotate profile around axis (lathe operation)
- `sweep_along_path` – Extrude profile along curve path
- `boolean_operation` – Union/Difference/Intersection CSG ops

**Edge Finishing**
- `fillet_edges` – Apply rounded radius to selected edges
- `chamfer_edges` – Apply angled flat cut to selected edges

**Pattern & Symmetry**
- `linear_pattern` – Create linear array of features
- `polar_pattern` – Create circular array around axis
- `mirror_object` – Reflect object across plane

**Constraints & Parameters**
- `add_sketch_constraint` – Apply dimensional/geometric constraints
- `set_parameter` – Update spreadsheet-driven parameters
- `measure_distance` – Calculate distance between geometry

**Geometry Inspection**
- `get_face_names` – List faces with area, surface type
- `get_edge_names` – List edges with length, curve type

**Import/Export**
- `import_file` – Load STEP, IGES, STL, BREP files
- `export_step` – Save to STEP format for CAD exchange
- `export_stl` – Save to STL for 3D printing
- `get_screenshot` – Capture current viewport as PNG

### Blender Tools (25)

**Scene Management**
- `create_primitive` – Generate Cube, Sphere, Cylinder, Cone, Torus, Plane
- `get_objects` – List scene objects with vertex/face counts
- `delete_object` – Remove object from scene
- `transform_object` – Apply Move, Rotate, Scale transforms

**Mesh Editing**
- `extrude_faces` – Extend selected faces outward
- `inset_faces` – Create inward offset of selected faces
- `bevel_edges` – Apply chamfer or rounded bevel to edges
- `loop_cut` – Add subdivision edge loops
- `knife_cut` – Cut through mesh with line tool
- `select_geometry` – Select vertices, edges, or faces

**Modifiers**
- `add_modifier` – Add Subdivision, Mirror, Array, Boolean modifier
- `apply_modifier` – Bake modifier permanently to mesh

**Spiral & Helix**
- `spin` – Revolve geometry around axis (lathe)
- `screw_modifier` – Apply spiral/helix extrusion
- `create_spiral` – Generate spiral curve primitive
- `curve_to_mesh` – Convert curve to mesh with bevel

**Edge Finishing**
- `fillet_edges` – Apply smooth rounded edge transition
- `chamfer_edges` – Apply flat angled edge transition

**Mesh Repair**
- `fill_holes` – Close open boundary edges
- `bridge_edges` – Connect two edge loops with faces
- `subdivide_mesh` – Increase mesh density uniformly
- `merge_vertices` – Combine nearby or overlapping vertices
- `get_mesh_stats` – Report manifold status, vertex/face counts

**Export & Materials**
- `export_stl` – Save to STL for 3D printing (Blender 5.0+)
- `assign_material` – Create and assign material with color
- `get_screenshot` – Capture viewport render as PNG

## 3D Printing Best Practices

### Design for Manufacturing

1. **Manifold Geometry** – Ensure watertight, closed meshes
2. **45° Overhang Rule** – Avoid supports where possible
3. **Wall Thickness** – Minimum 0.8mm (FDM), 0.5mm (SLA)
4. **Chamfers on Bed Edges** – 0.3mm prevents first-layer splay
5. **Thread Pitch** – Use ≥1.0mm pitch for printable threads

### Tool Selection

| Task | FreeCAD | Blender |
|------|---------|---------|
| Precise engineering | ✅ Primary | ❌ |
| Screw threads | ✅ `create_thread` | ❌ |
| Organic shapes | ❌ | ✅ Primary |
| Mesh repair | ❌ | ✅ `fill_holes` |
| Modifiers | ❌ | ✅ `add_modifier` |
| Code-driven Design | ⚠️ Python | ⚠️ Python |

## Code Standards

- Match existing codebase style
- SOLID, DRY, KISS, YAGNI principles
- Small, focused changes over rewrites
- Never create dummy/placeholder code
- Verify facts via web search
