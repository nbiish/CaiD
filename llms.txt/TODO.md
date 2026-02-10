# TODO

> Keep tasks atomic and testable.

## In Progress

- [ ] Test STL export after Blender reload (Blender 5.0 fix applied)
- [ ] Complex assembly demo combining FreeCAD + Blender

## Backlog

- [ ] UV mapping tools for Blender (uv_unwrap)
- [ ] Geometry nodes support for Blender
- [ ] Add loft_sketches tool for FreeCAD
- [ ] Assembly workflow (create_assembly_container, add_assembly_constraint)
- [ ] Model validation/error checking tools
- [ ] Undo/redo support

## Completed

### Session 2026-02-10: Blender Engineering Integration ✅

#### Blender MCP
- [x] **Manual Start Workaround**: Created `blender_debug_start.py` to bypass addon installation issues.
- [x] **Engineering Tools Verified**: `create_primitive`, `join` (boolean), `bevel_modifier`, `export_stl`.
- [x] **Parametric Model**: MODELED "Chamfered Bolt" solely via Python script.
- [x] **Status**: Alpha (Verified)

### Session 2026-02-07: FreeCAD Baseline ✅

#### FreeCAD MCP
- [x] **Status**: Stable (v0.2.0)
- [x] **Model**: Heltec WiFi LoRa 32 V4 Case (Base + Lid + Snap-fits + Text)
- [x] **Tools**: Primitives, threads, booleans, fillets, screenshots.

## Tool Count

| MCP | Tools | Status |
|-----|-------|--------|
| FreeCAD | 23 | ✅ Stable |
| Blender | 25 | ✅ Alpha |
| **Total** | **48** | |

## Engineering Models Created

| Model | Platform | Features |
|-------|----------|----------|
| Heltec V4 Case | FreeCAD | Complex assembly, snap-fits, text |
| Chamfered Bolt | Blender | Boolean union, bevel modifier, clean topo |

## Next Up: Advanced Tooling Docs
- [ ] Enhance `FREECAD_RESOURCES.md` (Best practices)
- [ ] Enhance `BLENDER_RESOURCES.md` (Engineering patterns)
- [ ] Project cleanup (Remove OpenSCAD)
