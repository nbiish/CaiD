# Missing Essential Blender MCP Tools for 3D Modeling

Based on analysis of current tools (create_primitive, extrude_faces, inset_faces, bevel_edges, loop_cut, add_modifier, spin, screw_modifier, create_spiral, curve_to_mesh, select_geometry, transform_object), here are 10 essential missing tools for comprehensive 3D modeling:

| Tool Name | Description | Parameters | Priority |
|-----------|-------------|------------|----------|
| knife_cut | Cut mesh geometry with a knife tool to create new edges and faces | object_name (string), cut_points (array of [x,y,z] coordinates), cut_type (enum: "EXACT", "DIFFERENCE") | High |
| bridge_edges | Bridge two sets of selected edges to create connecting faces | object_name (string), edge_indices (array of integers), segments (integer), profile (float) | High |
| fill_holes | Fill selected boundary edges to create faces | object_name (string), edge_indices (array of integers), use_beauty (boolean) | High |
| sculpt_mode | Enter sculpting mode and apply sculpting brushes | object_name (string), brush_type (enum: "DRAW", "SMOOTH", "PINCH", "INFLATE"), strength (float), radius (float), location (array of 3 floats) | High |
| uv_unwrap | Unwrap mesh for UV mapping | object_name (string), method (enum: "ANGLE_BASED", "CONFORMAL", "LIGHTMAP_PACK"), margin (float) | Medium |
| assign_material | Assign material to selected faces or entire object | object_name (string), material_name (string), face_indices (array of integers, optional) | Medium |
| add_curve | Create various types of curves (Bezier, NURBS, etc.) | curve_type (enum: "BEZIER", "NURBS", "POLY"), points (array of [x,y,z] coordinates), name (string) | Medium |
| geometry_nodes | Apply geometry node modifiers for procedural modeling | object_name (string), node_group_name (string), parameters (object) | Low |
| subdivide_mesh | Subdivide mesh geometry to increase detail | object_name (string), cuts (integer), smoothness (float), quadify (boolean) | High |
| merge_vertices | Merge selected vertices at center or at first/last location | object_name (string), merge_type (enum: "CENTER", "AT_FIRST", "AT_LAST"), threshold (float) | Medium |