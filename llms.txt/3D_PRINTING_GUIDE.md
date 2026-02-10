# 3D Printing Modeling Guide

> **AI-Assisted CAD for 3D Printing** | FreeCAD + Blender MCP Reference

## Overview

This guide covers best practices for designing 3D-printable models using AI-assisted CAD tools through the FreeCAD and Blender MCP servers.

---

## Core Design Principles

### 1. Solid & Manifold Geometry

| Principle | Description |
|-----------|-------------|
| **Watertight Mesh** | All vertices connected by edges; each edge connects exactly 2 faces |
| **No Open Edges** | Continuous surface with no gaps or holes |
| **Consistent Normals** | All face normals pointing outward |
| **No Intersecting Faces** | Clean boolean operations, no overlapping geometry |

### 2. The 45-Degree Rule

Overhangs up to **45° from vertical** can print without supports. Design with this in mind:
- Use chamfers instead of fillets on downward-facing edges
- Replace 90° overhangs with 45° angled transitions
- Reorient parts to minimize unsupported overhangs

### 3. Wall Thickness Guidelines

| Material/Method | Minimum Wall | Recommended |
|-----------------|--------------|-------------|
| **FDM (PLA/ABS)** | 0.8mm (2× nozzle) | 1.2-1.6mm |
| **FDM Unsupported** | 1.2mm | 1.5-2.0mm |
| **SLA (Resin)** | 0.5mm | 0.8-1.0mm |
| **SLS (Nylon)** | 0.7mm | 1.0mm |

### 4. Chamfers vs Fillets

| Feature | Chamfer | Fillet |
|---------|---------|--------|
| **Shape** | Angled flat cut | Rounded curve |
| **Print Quality** | Better on overhangs | Can sag on overhangs |
| **Support Need** | Often eliminates supports | May still require supports |
| **Use Case** | Assembly edges, bed contact | Stress relief, aesthetics |

**Recommendation**: Use **chamfers** for downward-facing edges and assembly interfaces. Use **fillets** for stress-critical areas and aesthetics.

---

## FreeCAD MCP Tools Reference

### Document & Primitives

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `create_document` | Creates new FreeCAD document | Start fresh for each print project |
| `create_primitive` | Box, Cylinder, Sphere, Cone, Torus | Use as boolean bases |
| `get_objects` | Lists all document objects | Verify no hidden/orphan geometry |

### Sketch-Based Modeling

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `create_sketch` | 2D profile on XY/XZ/YZ plane | Use closed profiles only |
| `pad_sketch` | Extrudes sketch to solid | Symmetric option centers geometry |
| `pocket_sketch` | Cuts into solid | Avoid through-all on thin walls |
| `add_sketch_constraint` | Dimensional/geometric constraints | Fully constrain for parametric edits |

### Edge Operations

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `fillet_edges` | Rounds selected edges with radius | Use on internal corners for strength |
| `chamfer_edges` | Bevels edges with flat angled cut | Use on overhangs and bed contact edges |

### Engineering Features

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `create_helix` | Spiral/helix path | For springs, coils, threads |
| `create_thread` | Metric/imperial screw threads | Use pitch ≥1.0mm for printability |
| `sweep_along_path` | Sweeps profile along curve | Ensure continuous closed profile |
| `revolve_sketch` | Lathe operation around axis | Profile must not cross axis |

### Boolean & Patterns

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `boolean_operation` | Union/Difference/Intersection | Clean up result with mesh check |
| `linear_pattern` | Linear array of features | Use for mounting holes, vents |
| `polar_pattern` | Circular array around axis | Check for minimum gap between copies |
| `mirror_object` | Symmetry across plane | Ensures balanced print warping |

### Export & Validation

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `export_stl` | Binary STL for slicing | Use low tessellation for speed |
| `export_step` | STEP for CAD exchange | Preferred for dimensional accuracy |
| `get_face_names` | Lists faces with properties | Verify surface types |
| `get_edge_names` | Lists edges with lengths | Check for zero-length edges |

---

## Blender MCP Tools Reference

### Primitives & Objects

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `create_primitive` | Cube, Sphere, Cylinder, etc. | Start with quads for clean topology |
| `get_objects` | Scene object list with counts | Verify vertex/face counts |
| `delete_object` | Removes object | Clean up construction geometry |
| `transform_object` | Move/Rotate/Scale | Apply transforms before export |

### Mesh Editing

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `extrude_faces` | Extends selected faces | Creates new geometry |
| `inset_faces` | Insets faces inward | Use for recessed details |
| `bevel_edges` | Chamfers/rounds edges | Segments=1 for print-friendly chamfers |
| `loop_cut` | Adds edge loops | Creates detail control |
| `knife_cut` | Cuts through geometry | Use for creating split lines |

### Modifiers

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `add_modifier` (SUBSURF) | Subdivision surface smoothing | Apply before export for mesh |
| `add_modifier` (MIRROR) | Symmetry modifier | Apply to make manifold |
| `add_modifier` (ARRAY) | Linear/radial copies | Apply before boolean ops |
| `add_modifier` (BOOLEAN) | Union/Difference/Intersect | Use "Exact" mode for clean results |
| `apply_modifier` | Bakes modifier to mesh | Required before STL export |

### Spiral/Helix

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `spin` | Lathe/revolve geometry | Creates revolved solids |
| `screw_modifier` | Helix extrusion | For coils, springs, threads |
| `create_spiral` | Spiral curve primitive | Convert to mesh for printing |
| `curve_to_mesh` | Curve → mesh conversion | Set bevel for solid geometry |

### Mesh Repair

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `fill_holes` | Closes open boundaries | Essential for watertight mesh |
| `bridge_edges` | Connects edge loops | Creates connecting faces |
| `subdivide_mesh` | Increases mesh density | Smooths before print |
| `merge_vertices` | Cleans doubled vertices | Distance=0.0001 for precision |
| `get_mesh_stats` | Manifold/watertight check | Run before every export |

### Export

| Tool | Action | 3D Print Tip |
|------|--------|--------------|
| `export_stl` | STL for 3D printing | Blender 5.0 compatible |
| `assign_material` | Material assignment | Visual reference only |
| `get_screenshot` | Viewport capture | Document your design |

---

## Print-Ready Checklist

### Before Export
- [ ] Check geometry is manifold/watertight
- [ ] Verify wall thickness ≥ 0.8mm
- [ ] Add chamfers to bed-contact edges (0.3mm)
- [ ] Apply all modifiers
- [ ] Recalculate normals (face outward)
- [ ] Apply object transforms (Ctrl+A)

### Export Settings
- [ ] Use binary STL (smaller file)
- [ ] Set correct units (mm)
- [ ] Export selection only
- [ ] Verify scale matches intended size

### Slicer Preparation
- [ ] Orient part to minimize supports
- [ ] Set appropriate layer height
- [ ] Configure infill for strength needs
- [ ] Enable supports for angles >45°

---

## Common Measurements

| Feature | Minimum | Recommended |
|---------|---------|-------------|
| Wall thickness | 0.8mm | 1.2mm |
| Chamfer for bed edge | 0.3mm | 0.5mm |
| Thread pitch (M8) | 1.0mm | 1.25mm |
| Thread pitch (M10) | 1.25mm | 1.5mm |
| Thread pitch (M12) | 1.5mm | 1.75mm |
| Bolt flat section | 1/3 diameter | - |
| Alignment peg chamfer | 1mm | 2mm |
| Clearance for fit | +0.2mm | +0.3mm |
