# Blender MCP Resources

Reference guide for AI-assisted engineering and 3D design using `blender-mcp`.

## Philosophy
**Code-First Engineering**: We prioritize precise, reproducible Python scripts (`execute_code`) over manual sculpting. 
**Non-Destructive**: Use Modifiers (Boolean, Bevel, Solidify) to keep the history editable, applying them only when necessary (e.g., for export).

## Core API Patterns

### 1. Basic Setup (Python Script)
Always import `bpy` and `bmesh`. Clear scene if starting fresh.

```python
import bpy
import bmesh
import math

# Clear Scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Parameters
L, W, H = 50.0, 30.0, 10.0
```

### 2. Primitives & Transforms
Use `bpy.ops.mesh.primitive_...` or create meshes from data.

```python
# Create Box
bpy.ops.mesh.primitive_cube_add(size=1, location=(0,0,0))
box = bpy.context.active_object
box.name = "MyBox"
box.dimensions = (L, W, H)
# Apply Scale (Critical for modifiers!)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
```

### 3. Boolean Operations (CSG)
The most robust way to drill holes or combine parts.

```python
# Main Object
main_obj = bpy.data.objects["MyBox"]

# Cutter Object
bpy.ops.mesh.primitive_cylinder_add(radius=2.5, depth=H*2)
cutter = bpy.context.active_object
cutter.location = (10, 5, 0)
    
# Boolean Modifier
mod = main_obj.modifiers.new(name="HoleCut", type='BOOLEAN')
mod.object = cutter
mod.operation = 'DIFFERENCE'
# solver='FAST' (worse topology) or 'EXACT' (better)
mod.solver = 'EXACT' 

# Hide Cutter
cutter.display_type = 'WIRE'
cutter.hide_render = True
```

### 4. Bevels & Chamfers
Essential for engineering aesthetics and ergonomics.

**Non-Destructive (Modifier)**:
```python
bevel = main_obj.modifiers.new(name="EdgeBevel", type='BEVEL')
bevel.width = 1.0
bevel.segments = 3 # Roundness (1 = Chamfer)
bevel.limit_method = 'ANGLE' # Only sharp edges
bevel.angle_limit = math.radians(30)
```

**Destructive (Edit Mode / BMesh)**:
Use when you need specific edge selection.
```python
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(main_obj.data)

# Select Edges (e.g., top loop)
for e in bm.edges:
    if e.calc_face_angle() > 0.1: # Sharp edges
        e.select = True

# Bevel Operator
bmesh.ops.bevel(bm, geom=[e for e in bm.edges if e.select], offset=1.0, segments=1)
bmesh.update_edit_mesh(main_obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
```

### 5. Export for Printing
Apply modifiers to ensure geometry is "baked".

```python
# Select Object
bpy.ops.object.select_all(action='DESELECT')
main_obj.select_set(True)
bpy.context.view_layer.objects.active = main_obj

# Export STL
bpy.ops.export_mesh.stl(filepath="/path/to/model.stl", use_selection=True, global_scale=1.0)
```

## Tools Reference
(From `server.py`)

- `create_primitive`: Quick shapes.
- `execute_code`: **Primary tool for complex logic.**
- `bevel_edges`: Direct edge beveling.
- `apply_modifier`: Bake parametric history.
- `get_mesh_stats`: Check for manifold geometry (watertight).

## Best Practices
1. **Apply Scale**: Always `ctrl+A` (in code `transform_apply`) after resizing. Modifiers (Bevel, Boolean) break on non-uniform scale.
2. **Manifold Checks**: For 3D printing, geometry must be watertight. Use `get_mesh_stats` or built-in '3D-Print Toolbox' checks.
3. **Origin Points**: Keep origins sensible (e.g., center or bottom-center) for positioning.
6. **Clean Topology**: Avoid N-gons (>4 vertices) on curved surfaces to prevent shading artifacts.

## Advanced Engineering Patterns

### 1. Precision Booleans (Exact Solver)
For manufacturing, use 'EXACT' solver to handle coplanar faces correctly.

```python
mod = obj.modifiers.new(name="Cut", type='BOOLEAN')
mod.object = cutter
mod.operation = 'DIFFERENCE'
mod.solver = 'EXACT'  # SLOW but ACCURATE
```

### 2. Shrinkwrap (Retopology / Surface Projection)
Project details onto a curved surface (e.g., logo on a cylinder).

```python
shrink = logo_obj.modifiers.new(name="Wrap", type='SHRINKWRAP')
shrink.target = curved_surface_obj
shrink.wrap_method = 'PROJECT'
shrink.use_project_x = False
shrink.use_project_y = False
shrink.use_project_z = True
shrink.use_negative_direction = True
```

### 3. Geometry Nodes (Procedural Parts)
Create parametric threads/gears using node trees (programmatically attached).

```python
# Add Geometry Nodes Modifier
gn = obj.modifiers.new(name="GeoNodes", type='NODES')
# Load existing node group (must be in blend file or appended)
gn.node_group = bpy.data.node_groups.get("ScrewThreadGenerator")
# Set Inputs
gn["Input_2"] = 10.0  # Height
gn["Input_3"] = 1.5   # Pitch
```

### 4. Generative Python (Math Surfaces)
Create complex mathematical shapes (e.g., Gyroids) for lightweight infill.

```python
# Generate Gyroid Surface
verts = []
scale = 0.5
import math
for x in range(20):
    for y in range(20):
        for z in range(20):
            # Gyroid approx: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0
            val = math.sin(x*scale)*math.cos(y*scale) + \
                  math.sin(y*scale)*math.cos(z*scale) + \
                  math.sin(z*scale)*math.cos(x*scale)
            if abs(val) < 0.1:
                verts.append((x*scale, y*scale, z*scale))
# ... create mesh from verts ...
```

### 5. Export Validation (3D Print Toolbox)
Ensure printability before export.

```python
# Select object
bpy.ops.mesh.print3d_check_all()
# Check results in Info panel or properties
# Auto-cleanup non-manifold
bpy.ops.mesh.print3d_clean_non_manifold()
```
