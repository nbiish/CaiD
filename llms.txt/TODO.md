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

### Session 2026-02-07: MCP Live Testing ✅

#### FreeCAD MCP
- [x] Fixed macOS thread-safety crash (MainThreadDispatcher)
- [x] Verified 15+ tools (primitives, threads, booleans, fillets)
- [x] Created 3D-printable M8/M10/M12 bolts with flat sections
- [x] Exported STL files to `/exports/`

#### Blender MCP  
- [x] Fixed STL export for Blender 5.0 (`wm.stl_export` API)
- [x] Verified 8+ tools (primitives, modifiers, bevel, extrude)
- [x] Created engineering examples: M8_Shank, ChamferPeg, MountBracket
- [x] Updated README with engineering-focused documentation

### Previous Sessions
- [x] Phase 1-3 tools implemented (48 total)
- [x] FreeCAD/Blender addon structure
- [x] Helix, thread, and spiral tools

## Tool Count

| MCP | Tools | Status |
|-----|-------|--------|
| FreeCAD | 23 | ✅ Tested |
| Blender | 25 | ✅ Tested |
| **Total** | **48** | |

## Engineering Models Created

| Model | Platform | Features |
|-------|----------|----------|
| M8 Bolt (flat) | FreeCAD | 1/3 section cut, hex head |
| M10 Bolt | FreeCAD | Flat section for printing |
| M12 Bolt | FreeCAD | Heavy-duty, flat section |
| ChamferPeg | Blender | Beveled alignment peg |
| M8_Shank | Blender | 2-segment bevel |
| MountBracket | Blender | Extruded cube |
