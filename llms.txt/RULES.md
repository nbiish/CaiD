# Rules

## Naming & Comments

- Use descriptive tool names matching CAD terminology
- Document tool parameters with clear descriptions
- Use snake_case for tool names

## Always

- Return structured JSON responses with success/error status
- Include object names in responses for chaining operations
- Validate input parameters before executing
- Call `doc.recompute()` after FreeCAD modifications
- Set mode back to OBJECT after Blender edit operations

## Never

- Leave Blender in EDIT mode after tool execution
- Create orphan objects (always assign to document/scene)
- Use blocking operations that freeze the UI
- Assume object exists without checking

## If

- Edge indices are empty → apply to all edges
- File type is "auto" → detect from extension
- No active document → create one automatically
- Object not found → raise ValueError with descriptive message
