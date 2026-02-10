# CaiD - CAD AI Design

> Two Model Context Protocol (MCP) servers for AI-assisted 3D modeling

<div align="center">
  <hr width="50%">
  <h3>Support This Project</h3>
  <table style="border: none; border-collapse: collapse;">
    <tr style="border: none;">
      <td align="center" style="border: none; vertical-align: middle; padding: 20px;">
        <h4>Stripe</h4>
        <img src="qr-stripe-donation.png" alt="Scan to donate" width="180"/>
        <p><a href="https://raw.githubusercontent.com/nbiish/license-for-all-works/8e9b73b269add9161dc04bbdd79f818c40fca14e/qr-stripe-donation.png">Donate via Stripe</a></p>
      </td>
      <td align="center" style="border: none; vertical-align: middle; padding: 20px;">
        <a href="https://www.buymeacoffee.com/nbiish">
          <img src="buy-me-a-coffee.svg" alt="Buy me a coffee" />
        </a>
      </td>
    </tr>
  </table>
  <hr width="50%">
</div>

## Overview

CaiD provides AI-powered 3D modeling through two focused MCP servers:

| Server | Application | Focus | Use Case |
|--------|-------------|-------|----------|
| **freecad-mcp** | FreeCAD | Parametric CAD | Engineering, mechanical parts |
| **blender-mcp** | Blender | Mesh modeling | Creative 3D, organic shapes |

## Quick Start

### FreeCAD MCP

```bash
# Install addon in FreeCAD
cp -r freecad-mcp/addon/FreeCADMCP ~/Library/Application\ Support/FreeCAD/Mod/

# Run MCP server
cd freecad-mcp && uv sync && uv run freecad-mcp
```

### Blender MCP

```bash
# Install addon via Blender Preferences > Add-ons > Install
# Or copy manually:
cp -r blender-mcp/addon/BlenderMCP ~/.config/blender/4.0/scripts/addons/

# Run MCP server
cd blender-mcp && uv sync && uv run blender-mcp
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "freecad": {
      "command": "uv",
      "args": ["--directory", "/path/to/CaiD/freecad-mcp", "run", "freecad-mcp"]
    },
    "blender": {
      "command": "uv",
      "args": ["--directory", "/path/to/CaiD/blender-mcp", "run", "blender-mcp"]
    }
  }
}
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐
│   Claude    │────▶│ freecad-mcp  │────▶│    FreeCAD     │
│   (LLM)     │     │  (MCP/RPC)   │     │  (GUI/Headless)│
└─────────────┘     └──────────────┘     └────────────────┘
       │
       │            ┌──────────────┐     ┌────────────────┐
       └───────────▶│ blender-mcp  │────▶│    Blender     │
                    │ (MCP/Socket) │     │ (GUI/Background)│
                    └──────────────┘     └────────────────┘
```

## FreeCAD Tools

- `create_document` - New document
- `create_primitive` - Box, Cylinder, Sphere, Cone, Torus
- `create_sketch` - 2D parametric sketch
- `pad_sketch` / `pocket_sketch` - Extrude / Cut
- `fillet_edges` / `chamfer_edges` - Edge operations
- `create_helix` - Spiral path for springs/threads
- `create_thread` - Screw threads (metric, imperial, trapezoidal)
- `sweep_along_path` - Sweep profile along helix
- `revolve_sketch` - Lathe operation
- `set_parameter` - Spreadsheet parameters
- `export_step` - STEP export / `get_screenshot` - Visual feedback

## Blender Tools

- `create_primitive` - Cube, Sphere, Cylinder, Cone, Torus, Plane
- `extrude_faces` / `inset_faces` - Face operations
- `bevel_edges` / `loop_cut` - Edge operations
- `add_modifier` / `apply_modifier` - Subdivision, Mirror, Array, Boolean
- `spin` - Revolve geometry (lathe operation)
- `screw_modifier` - Helix/spiral extrusion
- `create_spiral` - Spiral/helix curve
- `curve_to_mesh` - Convert curve to mesh
- `select_geometry` - Vertex/Edge/Face selection
- `transform_object` - Move, Rotate, Scale
- `get_screenshot` - Visual feedback

## Citation

```bibtex
@misc{CaiD2026,
  author/creator/steward = {ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band and enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians},
  title/description = {CaiD},
  type_of_work = {Indigenous digital creation/software incorporating traditional knowledge and cultural expressions},
  year = {2026},
  publisher/source/event = {GitHub repository under tribal sovereignty protections},
  howpublished = {\url{https://github.com/nbiish/CaiD}},
  note = {Authored and stewarded by ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band and enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians. This work embodies Indigenous intellectual property, traditional knowledge systems (TK), traditional cultural expressions (TCEs), and associated data protected under tribal law, federal Indian law, treaty rights, Indigenous Data Sovereignty principles, and international indigenous rights frameworks including UNDRIP. All usage, benefit-sharing, and data governance are governed by the COMPREHENSIVE RESTRICTED USE LICENSE FOR INDIGENOUS CREATIONS WITH TRIBAL SOVEREIGNTY, DATA SOVEREIGNTY, AND WEALTH RECLAMATION PROTECTIONS.}
}
```

## License

Copyright © 2026 ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), a descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band, and an enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians. This work embodies Traditional Knowledge and Traditional Cultural Expressions. All rights reserved.
