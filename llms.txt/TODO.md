# TODO

> Keep tasks atomic and testable.

## In Progress

- [ ] Integration tests with actual FreeCAD/Blender installations
- [ ] UV mapping tools for Blender (uv_unwrap)
- [ ] Geometry nodes support for Blender
- [ ] Add loft_sketches tool for FreeCAD

## Backlog

- [ ] Assembly workflow (create_assembly_container, add_assembly_constraint)
- [ ] Sculpting mode for Blender
- [ ] Model validation/error checking tools
- [ ] Undo/redo support

## Completed

### Phase 3: High-Priority Tools (Current Session)
- [x] `boolean_operation` - Union/Difference/Intersection for FreeCAD
- [x] `import_file` - STEP/STL/IGES import for FreeCAD  
- [x] `export_stl` - 3D print export (both MCPs)
- [x] `get_face_names` / `get_edge_names` - Geometry introspection
- [x] `linear_pattern` / `polar_pattern` - Array tools
- [x] `mirror_object` - Symmetry creation
- [x] `measure_distance` - Distance measurement
- [x] `add_sketch_constraint` - Parametric constraints
- [x] `fill_holes` / `bridge_edges` - Mesh repair (Blender)
- [x] `subdivide_mesh` / `merge_vertices` - Mesh editing (Blender)
- [x] `knife_cut` - Mesh cutting (Blender)
- [x] `get_mesh_stats` - Mesh validation (Blender)
- [x] `fillet_edges` / `chamfer_edges` - Edge finishing (Blender)
- [x] `assign_material` - Material assignment (Blender)

### Phase 2: Helix & Spiral Tools
- [x] `create_helix` - Helix/spiral path for FreeCAD
- [x] `create_thread` - Screw threads (metric/imperial) for FreeCAD
- [x] `sweep_along_path` - Profile sweep for FreeCAD
- [x] `revolve_sketch` - Lathe operation for FreeCAD
- [x] `spin` - Blender lathe operation
- [x] `screw_modifier` - Blender helix extrusion
- [x] `create_spiral` - Blender spiral curve
- [x] `curve_to_mesh` - Curve conversion for Blender

### Phase 1: Core Implementation
- [x] FreeCAD MCP server (stdio transport)
- [x] Blender MCP server (stdio transport)
- [x] FreeCAD addon (XML-RPC bridge on port 9875)
- [x] Blender addon (Socket server on port 9876)
- [x] Create/Pad/Pocket sketches
- [x] Primitive shapes (Box, Cylinder, Sphere, etc.)
- [x] Edge operations (fillet, chamfer for FreeCAD)
- [x] Modifiers (subdivision, mirror, array, boolean)
- [x] Screenshot capture
- [x] STEP export

## Tool Count Summary

| MCP | Tools |
|-----|-------|
| FreeCAD | 23 |
| Blender | 25 |
| **Total** | **48** |
