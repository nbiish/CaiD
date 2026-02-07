# Missing Essential FreeCAD Modeling Tools

This document outlines 15 essential tools missing from the current FreeCAD MCP server implementation. Adding these would significantly improve the system's capability for mechanical engineering and parametric design tasks.

## 1. Constraints & Sketching (Parametric Core)
*   **tool_name**: `add_sketch_constraint`
    *   **description**: Adds a geometric or dimensional constraint to a sketch. This is essential for creating robust, parametric models rather than just static shapes. Without this, sketches are liable to break when parameters change.
    *   **key_parameters**: `sketch_name` (string), `constraint_type` (enum: "Horizontal", "Vertical", "DistanceX", "DistanceY", "Distance", "Radius", "Diameter", "Coincident", "Tangent", "Parallel", "Perpendicular"), `geometry_indices` (list of integers), `value` (number, optional for dimensional constraints).
    *   **priority**: **High**

*   **tool_name**: `project_external_geometry`
    *   **description**: Projects edges or vertices from existing 3D solids onto the sketch plane. This is critical for referencing previously created geometry (e.g., centering a hole on a parent feature).
    *   **key_parameters**: `sketch_name` (string), `target_object` (string), `subelement_name` (string, e.g., "Edge1").
    *   **priority**: **High**

## 2. Boolean Operations (Part Construction)
*   **tool_name**: `boolean_operation`
    *   **description**: Performs boolean operations between two or more shapes. This allows for complex constructive solid geometry (CSG).
    *   **key_parameters**: `operation` (enum: "Union", "Difference", "Intersection"), `base_object` (string), `tool_objects` (list of strings).
    *   **priority**: **High**

## 3. Patterning & Mirroring (Drafting)
*   **tool_name**: `linear_pattern`
    *   **description**: Creates a linear array of a feature (like a Pad or Pocket) or a solid.
    *   **key_parameters**: `object_name` (string), `direction` (vector or edge reference), `length` (number), `occurrences` (integer).
    *   **priority**: **Medium**

*   **tool_name**: `polar_pattern`
    *   **description**: Creates a circular/polar array of a feature or solid around an axis. Essential for flanges, gears, and wheels.
    *   **key_parameters**: `object_name` (string), `axis` (vector or line reference), `angle` (number, usually 360), `occurrences` (integer).
    *   **priority**: **Medium**

*   **tool_name**: `mirror_object`
    *   **description**: Mirrors a feature or body across a plane.
    *   **key_parameters**: `object_name` (string), `plane` (enum: "XY", "XZ", "YZ" or custom plane reference).
    *   **priority**: **Medium**

## 4. Assembly & Placement
*   **tool_name**: `transform_object`
    *   **description**: Moves or rotates an object in 3D space by modifying its Placement property. Essential for positioning parts in a multi-body assembly or simple arrangement.
    *   **key_parameters**: `object_name` (string), `translation` (vector: [x, y, z]), `rotation_axis` (vector), `rotation_angle` (number).
    *   **priority**: **High**

*   **tool_name**: `create_assembly_container`
    *   **description**: Creates a standard Part container (App::Part) to group related bodies or objects. This facilitates hierarchical assembly structures (e.g., Sub-assemblies).
    *   **key_parameters**: `name` (string), `parent_name` (string, optional).
    *   **priority**: **Medium**

*   **tool_name**: `add_assembly_constraint`
    *   **description**: Adds a topological constraint between two parts (e.g., aligning planes, concentric axes). This enables "smart" assembly where parts snap together.
    *   **key_parameters**: `object1` (string), `subelement1` (string), `object2` (string), `subelement2` (string), `constraint_type` (enum: "PlaneAlignment", "AxialAlignment").
    *   **priority**: **Medium**

## 5. Advanced Modeling & Surfacing
*   **tool_name**: `loft_sketches`
    *   **description**: Creates a solid or surface by lofting through a series of profile sketches. Used for organic shapes or complex transitions.
    *   **key_parameters**: `sketch_names` (list of strings), `solid` (boolean).
    *   **priority**: **Medium**

*   **tool_name**: `create_thickness`
    *   **description**: Creates a hollowed-out solid (thick solid) from a base solid, leaving selected faces open. Commonly used for creating enclosures or plastic parts.
    *   **key_parameters**: `object_name` (string), `face_names` (list of strings to remove), `thickness` (number), `direction` (enum: "Inward", "Outward").
    *   **priority**: **Medium**

*   **tool_name**: `create_datum_plane`
    *   **description**: Creates a datum plane reference geometry. Crucial for creating sketches on angles, offsets, or relative to other geometry where standard XY/XZ/YZ planes are insufficient.
    *   **key_parameters**: `reference_object` (string), `attachment_mode` (string), `offset` (number).
    *   **priority**: **High**

## 6. Import & Interoperability
*   **tool_name**: `import_file`
    *   **description**: Imports external CAD geometry (STEP, IGES, BREP) or meshes (STL) into the current document. Essential for working with vendor parts or legacy data.
    *   **key_parameters**: `file_path` (string), `file_type` (optional, usually inferred from extension).
    *   **priority**: **High**

## 7. Inspection & Helper Tools
*   **tool_name**: `get_face_names`
    *   **description**: Identifying faces blindly is difficult for an LLM. This tool returns a list of faces with their centroids, areas, or normal vectors to help the LLM select the correct face for operations like Sketching or Filleting.
    *   **key_parameters**: `object_name` (string).
    *   **priority**: **High**

*   **tool_name**: `measure_distance`
    *   **description**: Measures distance between two topological entities (points, edges, faces). Useful for verification or deriving dimensions for subsequent features.
    *   **key_parameters**: `object1` (string), `subelement1` (string), `object2` (string), `subelement2` (string).
    *   **priority**: **Medium**
