"""Blender MCP Bridge Addon.

This addon creates a socket server inside Blender that receives
commands from the MCP server and executes them in Blender's context.
"""

bl_info = {
    "name": "Blender MCP Bridge",
    "author": "CaiD Team",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Socket server for AI-assisted 3D modeling",
    "category": "Development",
}

import bpy
import json
import socket
import threading
import math
import tempfile
import base64
from pathlib import Path

# Global server instance
_server = None
_server_thread = None


class BlenderMCPServer:
    """Socket server for Blender modeling operations."""
    
    def __init__(self, host: str = "localhost", port: int = 9876):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
        
    def start(self):
        """Start the socket server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)
        self.running = True
        print(f"Blender MCP Server started on {self.host}:{self.port}")
        
    def stop(self):
        """Stop the socket server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        print("Blender MCP Server stopped")
        
    def serve(self):
        """Main server loop."""
        while self.running:
            try:
                client, addr = self.server_socket.accept()
                self._handle_client(client)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"Server error: {e}")
                    
    def _handle_client(self, client: socket.socket):
        """Handle a client connection."""
        try:
            # Receive data
            data = b""
            while True:
                chunk = client.recv(4096)
                if not chunk:
                    break
                data += chunk
                if data.endswith(b"\n"):
                    break
                    
            if data:
                # Parse command
                command = json.loads(data.decode("utf-8"))
                
                # Execute in main thread via timer
                result = {"pending": True}
                
                def execute():
                    nonlocal result
                    result = self._execute_tool(command)
                    return None  # Don't repeat
                    
                bpy.app.timers.register(execute, first_interval=0.0)
                
                # Wait for result (with timeout)
                import time
                timeout = 30.0
                start = time.time()
                while result.get("pending") and (time.time() - start) < timeout:
                    time.sleep(0.1)
                    
                if result.get("pending"):
                    result = {"success": False, "error": "Timeout waiting for execution"}
                    
                # Send response
                response = json.dumps(result) + "\n"
                client.sendall(response.encode("utf-8"))
                
        except Exception as e:
            error_response = json.dumps({"success": False, "error": str(e)}) + "\n"
            client.sendall(error_response.encode("utf-8"))
        finally:
            client.close()
            
    def _execute_tool(self, command: dict) -> dict:
        """Execute a modeling tool."""
        try:
            tool_name = command.get("tool")
            args = command.get("arguments", {})
            
            handler = getattr(self, f"_tool_{tool_name}", None)
            if handler:
                result = handler(args)
                return {"success": True, "result": result}
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ===== Tool Implementations =====
    
    def _tool_create_primitive(self, args: dict) -> dict:
        """Create a primitive mesh."""
        shape = args["shape"]
        name = args.get("name", shape)
        location = tuple(args.get("location", [0, 0, 0]))
        size = args.get("size", 1)
        
        if shape == "Cube":
            bpy.ops.mesh.primitive_cube_add(size=size * 2, location=location)
        elif shape == "Sphere":
            bpy.ops.mesh.primitive_uv_sphere_add(radius=size, location=location)
        elif shape == "Cylinder":
            bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size * 2, location=location)
        elif shape == "Cone":
            bpy.ops.mesh.primitive_cone_add(radius1=size, depth=size * 2, location=location)
        elif shape == "Torus":
            bpy.ops.mesh.primitive_torus_add(major_radius=size, minor_radius=size * 0.3, location=location)
        elif shape == "Plane":
            bpy.ops.mesh.primitive_plane_add(size=size * 2, location=location)
        else:
            raise ValueError(f"Unknown shape: {shape}")
            
        obj = bpy.context.active_object
        obj.name = name
        
        return {"object": obj.name, "type": shape}
    
    def _tool_extrude_faces(self, args: dict) -> dict:
        """Extrude selected faces."""
        obj_name = args["object_name"]
        depth = args["depth"]
        select_all = args.get("select_all", False)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        # Set active and select
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Enter edit mode
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="FACE")
        
        if select_all:
            bpy.ops.mesh.select_all(action="SELECT")
            
        # Extrude
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": (0, 0, depth)}
        )
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {"object": obj_name, "extruded_depth": depth}
    
    def _tool_inset_faces(self, args: dict) -> dict:
        """Inset selected faces."""
        obj_name = args["object_name"]
        thickness = args["thickness"]
        depth = args.get("depth", 0)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="FACE")
        
        bpy.ops.mesh.inset(thickness=thickness, depth=depth)
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {"object": obj_name, "inset_thickness": thickness}
    
    def _tool_bevel_edges(self, args: dict) -> dict:
        """Bevel selected edges."""
        obj_name = args["object_name"]
        width = args["width"]
        segments = args.get("segments", 1)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action="SELECT")
        
        bpy.ops.mesh.bevel(offset=width, segments=segments)
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {"object": obj_name, "bevel_width": width}
    
    def _tool_loop_cut(self, args: dict) -> dict:
        """Add edge loop(s)."""
        obj_name = args["object_name"]
        cuts = args.get("cuts", 1)
        edge_index = args.get("edge_index", 0)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        
        bpy.ops.mesh.loopcut_slide(
            MESH_OT_loopcut={"number_cuts": cuts, "edge_index": edge_index}
        )
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {"object": obj_name, "cuts": cuts}
    
    def _tool_add_modifier(self, args: dict) -> dict:
        """Add a modifier to an object."""
        obj_name = args["object_name"]
        mod_type = args["modifier_type"]
        params = args.get("params", {})
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        mod = obj.modifiers.new(name=mod_type, type=mod_type)
        
        # Apply params
        if mod_type == "SUBSURF":
            mod.levels = params.get("levels", 2)
            mod.render_levels = params.get("render_levels", 2)
        elif mod_type == "MIRROR":
            mod.use_axis = (
                params.get("x", True),
                params.get("y", False),
                params.get("z", False)
            )
        elif mod_type == "ARRAY":
            mod.count = params.get("count", 2)
            mod.relative_offset_displace = (
                params.get("offset_x", 1),
                params.get("offset_y", 0),
                params.get("offset_z", 0)
            )
        elif mod_type == "BEVEL":
            mod.width = params.get("width", 0.1)
            mod.segments = params.get("segments", 1)
        elif mod_type == "SOLIDIFY":
            mod.thickness = params.get("thickness", 0.1)
        elif mod_type == "BOOLEAN":
            other_obj = bpy.data.objects.get(params.get("object", ""))
            if other_obj:
                mod.object = other_obj
                mod.operation = params.get("operation", "DIFFERENCE")
                
        return {"object": obj_name, "modifier": mod.name}
    
    def _tool_apply_modifier(self, args: dict) -> dict:
        """Apply a modifier."""
        obj_name = args["object_name"]
        mod_name = args["modifier_name"]
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod_name)
        
        return {"object": obj_name, "applied": mod_name}
    
    def _tool_select_geometry(self, args: dict) -> dict:
        """Select geometry elements."""
        obj_name = args["object_name"]
        mode = args["mode"]
        action = args["action"]
        indices = args.get("indices", [])
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type=mode)
        
        if action == "SELECT_ALL":
            bpy.ops.mesh.select_all(action="SELECT")
        elif action == "DESELECT_ALL":
            bpy.ops.mesh.select_all(action="DESELECT")
        elif action == "INVERT":
            bpy.ops.mesh.select_all(action="INVERT")
        elif action == "SELECT_INDICES":
            # Need to access mesh data directly
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
            
            mesh = obj.data
            if mode == "VERT":
                for i in indices:
                    if i < len(mesh.vertices):
                        mesh.vertices[i].select = True
            elif mode == "EDGE":
                for i in indices:
                    if i < len(mesh.edges):
                        mesh.edges[i].select = True
            elif mode == "FACE":
                for i in indices:
                    if i < len(mesh.polygons):
                        mesh.polygons[i].select = True
                        
            bpy.ops.object.mode_set(mode="EDIT")
            
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {"object": obj_name, "selection_mode": mode, "action": action}
    
    def _tool_transform_object(self, args: dict) -> dict:
        """Transform an object."""
        obj_name = args["object_name"]
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        if "location" in args:
            obj.location = tuple(args["location"])
        if "rotation" in args:
            # Convert degrees to radians
            rot = args["rotation"]
            obj.rotation_euler = (
                math.radians(rot[0]),
                math.radians(rot[1]),
                math.radians(rot[2])
            )
        if "scale" in args:
            obj.scale = tuple(args["scale"])
            
        return {"object": obj_name, "transformed": True}
    
    def _tool_delete_object(self, args: dict) -> dict:
        """Delete an object."""
        obj_name = args["object_name"]
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
            
        bpy.data.objects.remove(obj, do_unlink=True)
        
        return {"deleted": obj_name}
    
    def _tool_get_objects(self, args: dict) -> dict:
        """List all scene objects."""
        objects = []
        for obj in bpy.data.objects:
            obj_info = {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
            }
            if obj.type == "MESH":
                obj_info["vertices"] = len(obj.data.vertices)
                obj_info["faces"] = len(obj.data.polygons)
            objects.append(obj_info)
            
        return {"objects": objects}
    
    def _tool_get_screenshot(self, args: dict) -> dict:
        """Capture viewport screenshot."""
        width = args.get("width", 800)
        height = args.get("height", 600)
        
        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            filepath = f.name
            
        # Set render settings
        scene = bpy.context.scene
        old_res_x = scene.render.resolution_x
        old_res_y = scene.render.resolution_y
        old_filepath = scene.render.filepath
        
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        scene.render.filepath = filepath
        
        # Render viewport
        bpy.ops.render.opengl(write_still=True)
        
        # Restore settings
        scene.render.resolution_x = old_res_x
        scene.render.resolution_y = old_res_y
        scene.render.filepath = old_filepath
        
        # Read and encode image
        with open(filepath, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
            
        Path(filepath).unlink()
        
        return {"image_base64": image_data, "width": width, "height": height}
    
    def _tool_execute_code(self, args: dict) -> dict:
        """Execute arbitrary Python code."""
        code = args["code"]
        
        exec_globals = {"bpy": bpy}
        exec_locals = {}
        
        exec(code, exec_globals, exec_locals)
        
        return {"executed": True}
    
    def _tool_spin(self, args: dict) -> dict:
        """Spin/revolve geometry around an axis (lathe operation)."""
        obj_name = args["object_name"]
        angle_deg = args.get("angle", 360)
        steps = args.get("steps", 12)
        axis = args.get("axis", "Z")
        center = tuple(args.get("center", [0, 0, 0]))
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
        
        # Set active and enter edit mode
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        
        # Convert angle to radians (Blender spin uses radians)
        angle_rad = math.radians(angle_deg)
        
        # Set axis tuple
        if axis == "X":
            axis_vec = (1, 0, 0)
        elif axis == "Y":
            axis_vec = (0, 1, 0)
        else:  # Z
            axis_vec = (0, 0, 1)
        
        # Perform spin operation
        bpy.ops.mesh.spin(
            steps=steps,
            angle=angle_rad,
            center=center,
            axis=axis_vec
        )
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "angle": angle_deg,
            "steps": steps,
            "axis": axis,
        }
    
    def _tool_screw_modifier(self, args: dict) -> dict:
        """Add a screw modifier for helix/spiral geometry."""
        obj_name = args["object_name"]
        screw_offset = args.get("screw_offset", 1)
        angle_deg = args.get("angle", 360)
        iterations = args.get("iterations", 2)
        steps = args.get("steps", 16)
        axis = args.get("axis", "Z")
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
        
        # Add screw modifier
        mod = obj.modifiers.new(name="Screw", type="SCREW")
        
        # Configure modifier (angle in radians per API docs)
        mod.angle = math.radians(angle_deg)
        mod.screw_offset = screw_offset
        mod.iterations = iterations
        mod.steps = steps
        mod.render_steps = steps
        mod.axis = axis
        mod.use_smooth_shade = True
        
        return {
            "object": obj_name,
            "modifier": mod.name,
            "screw_offset": screw_offset,
            "angle": angle_deg,
            "iterations": iterations,
        }
    
    def _tool_create_spiral(self, args: dict) -> dict:
        """Create a spiral/helix curve."""
        turns = args.get("turns", 2)
        steps = args.get("steps", 24)
        radius_start = args.get("radius_start", 1)
        radius_end = args.get("radius_end", 1)
        height = args.get("height", 2)
        direction = args.get("direction", "COUNTER_CLOCKWISE")
        
        # Calculate points for spiral
        total_steps = int(turns * steps)
        points = []
        
        for i in range(total_steps + 1):
            t = i / total_steps  # 0 to 1
            angle = t * turns * 2 * math.pi
            
            # Apply direction
            if direction == "CLOCKWISE":
                angle = -angle
            
            # Interpolate radius
            radius = radius_start + (radius_end - radius_start) * t
            
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = t * height
            
            points.append((x, y, z))
        
        # Create curve data
        curve_data = bpy.data.curves.new(name="Spiral", type="CURVE")
        curve_data.dimensions = "3D"
        
        # Create spline
        spline = curve_data.splines.new(type="POLY")
        spline.points.add(len(points) - 1)  # -1 because one point exists by default
        
        for i, (x, y, z) in enumerate(points):
            spline.points[i].co = (x, y, z, 1)  # w=1 for NURBS weight
        
        # Create object
        curve_obj = bpy.data.objects.new("Spiral", curve_data)
        bpy.context.collection.objects.link(curve_obj)
        bpy.context.view_layer.objects.active = curve_obj
        curve_obj.select_set(True)
        
        return {
            "object": curve_obj.name,
            "turns": turns,
            "height": height,
            "radius_start": radius_start,
            "radius_end": radius_end,
            "points": len(points),
        }
    
    def _tool_curve_to_mesh(self, args: dict) -> dict:
        """Convert a curve to mesh geometry."""
        obj_name = args["object_name"]
        bevel_depth = args.get("bevel_depth", 0)
        bevel_resolution = args.get("bevel_resolution", 4)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
        
        if obj.type != "CURVE":
            raise ValueError(f"Object {obj_name} is not a curve (type: {obj.type})")
        
        # Set bevel before conversion (creates tube/pipe geometry)
        if bevel_depth > 0:
            obj.data.bevel_depth = bevel_depth
            obj.data.bevel_resolution = bevel_resolution
        
        # Select and make active
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        
        # Convert to mesh
        bpy.ops.object.convert(target="MESH")
        
        mesh_obj = bpy.context.active_object
        
        return {
            "object": mesh_obj.name,
            "vertices": len(mesh_obj.data.vertices),
            "faces": len(mesh_obj.data.polygons),
            "converted_from": "CURVE",
        }
    
    # === HIGH-PRIORITY MESH TOOLS FOR 3D PRINTING ===
    
    def _tool_fill_holes(self, args: dict) -> dict:
        """Fill holes in mesh."""
        obj_name = args["object_name"]
        sides = args.get("sides", 0)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        
        # Select boundary edges
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold(extend=False, use_wire=False, 
                                          use_boundary=True, use_multi_face=False,
                                          use_non_contiguous=False, use_verts=False)
        
        # Fill holes
        if sides > 0:
            bpy.ops.mesh.fill_holes(sides=sides)
        else:
            bpy.ops.mesh.fill_holes()
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "filled": True,
        }
    
    def _tool_bridge_edges(self, args: dict) -> dict:
        """Bridge two edge loops."""
        obj_name = args["object_name"]
        edge_indices_1 = args["edge_indices_1"]
        edge_indices_2 = args["edge_indices_2"]
        segments = args.get("segments", 1)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="EDGE")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        
        # Select edge indices
        mesh = obj.data
        all_indices = edge_indices_1 + edge_indices_2
        for i in all_indices:
            if i < len(mesh.edges):
                mesh.edges[i].select = True
        
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.bridge_edge_loops(number_cuts=segments)
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "segments": segments,
            "bridged": True,
        }
    
    def _tool_subdivide_mesh(self, args: dict) -> dict:
        """Subdivide mesh geometry."""
        obj_name = args["object_name"]
        cuts = args.get("cuts", 1)
        smoothness = args.get("smoothness", 0)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.subdivide(number_cuts=cuts, smoothness=smoothness)
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "cuts": cuts,
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }
    
    def _tool_merge_vertices(self, args: dict) -> dict:
        """Merge vertices in mesh."""
        obj_name = args["object_name"]
        merge_type = args.get("merge_type", "BY_DISTANCE")
        threshold = args.get("threshold", 0.0001)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        
        if merge_type == "BY_DISTANCE":
            bpy.ops.mesh.remove_doubles(threshold=threshold)
        elif merge_type == "CENTER":
            bpy.ops.mesh.merge(type="CENTER")
        elif merge_type == "AT_FIRST":
            bpy.ops.mesh.merge(type="FIRST")
        elif merge_type == "AT_LAST":
            bpy.ops.mesh.merge(type="LAST")
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "merge_type": merge_type,
            "vertices": len(obj.data.vertices),
        }
    
    def _tool_export_stl(self, args: dict) -> dict:
        """Export object to STL for 3D printing."""
        obj_name = args["object_name"]
        file_path = args["file_path"]
        ascii_format = args.get("ascii", False)
        apply_modifiers = args.get("apply_modifiers", True)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
        
        # Deselect all, select target
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        # Export
        bpy.ops.export_mesh.stl(
            filepath=file_path,
            use_selection=True,
            ascii=ascii_format,
            use_mesh_modifiers=apply_modifiers,
        )
        
        import os
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        return {
            "object": obj_name,
            "file": file_path,
            "size_bytes": file_size,
            "ascii": ascii_format,
        }
    
    def _tool_get_mesh_stats(self, args: dict) -> dict:
        """Get mesh statistics for validation."""
        obj_name = args["object_name"]
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        mesh = obj.data
        
        # Basic stats
        stats = {
            "object": obj_name,
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": sum(len(p.vertices) - 2 for p in mesh.polygons),
        }
        
        # Check for non-manifold geometry
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="DESELECT")
        bpy.ops.mesh.select_non_manifold()
        
        # Count non-manifold elements
        bpy.ops.object.mode_set(mode="OBJECT")
        non_manifold_verts = sum(1 for v in mesh.vertices if v.select)
        
        stats["non_manifold_vertices"] = non_manifold_verts
        stats["is_manifold"] = non_manifold_verts == 0
        stats["is_watertight"] = non_manifold_verts == 0
        
        # Bounding box
        bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
        dimensions = obj.dimensions
        stats["dimensions"] = [round(d, 4) for d in dimensions]
        
        return stats
    
    def _tool_knife_cut(self, args: dict) -> dict:
        """Cut through mesh with a knife line."""
        obj_name = args["object_name"]
        cut_start = args["cut_start"]
        cut_end = args["cut_end"]
        cut_through = args.get("cut_through", True)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        
        # Use bisect as a programmatic knife alternative
        plane_co = ((cut_start[0] + cut_end[0])/2, 
                    (cut_start[1] + cut_end[1])/2, 
                    (cut_start[2] + cut_end[2])/2)
        
        # Calculate plane normal from cut direction
        import mathutils
        start_v = mathutils.Vector(cut_start)
        end_v = mathutils.Vector(cut_end)
        cut_dir = (end_v - start_v).normalized()
        
        # Use perpendicular as normal
        if abs(cut_dir.z) < 0.9:
            plane_no = cut_dir.cross(mathutils.Vector((0, 0, 1)))
        else:
            plane_no = cut_dir.cross(mathutils.Vector((1, 0, 0)))
        plane_no.normalize()
        
        bpy.ops.mesh.bisect(
            plane_co=plane_co,
            plane_no=tuple(plane_no),
            use_fill=False,
            clear_inner=False,
            clear_outer=False,
        )
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "cut_start": cut_start,
            "cut_end": cut_end,
        }
    
    def _tool_assign_material(self, args: dict) -> dict:
        """Create and assign a material to an object."""
        obj_name = args["object_name"]
        mat_name = args["material_name"]
        color = args.get("color", [0.8, 0.8, 0.8])
        metallic = args.get("metallic", 0)
        roughness = args.get("roughness", 0.5)
        
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            raise ValueError(f"Object not found: {obj_name}")
        
        # Create or get material
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(name=mat_name)
        
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Metallic"].default_value = metallic
            bsdf.inputs["Roughness"].default_value = roughness
        
        # Assign to object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
        
        return {
            "object": obj_name,
            "material": mat_name,
            "color": color,
        }
    
    def _tool_fillet_edges(self, args: dict) -> dict:
        """Apply rounded fillet to edges using bevel with high profile."""
        obj_name = args["object_name"]
        radius = args["radius"]
        segments = args.get("segments", 4)
        edge_indices = args.get("edge_indices", [])
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="EDGE")
        
        if edge_indices:
            # Select specific edges
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
            mesh = obj.data
            for i in edge_indices:
                if i < len(mesh.edges):
                    mesh.edges[i].select = True
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            # Select all edges
            bpy.ops.mesh.select_all(action="SELECT")
        
        # Apply fillet using bevel with profile=1.0 (rounded)
        bpy.ops.mesh.bevel(
            offset=radius,
            offset_type="OFFSET",
            segments=segments,
            profile=1.0,  # Rounded fillet profile
            affect="EDGES"
        )
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "radius": radius,
            "segments": segments,
            "edges_filleted": len(edge_indices) if edge_indices else "all",
        }
    
    def _tool_chamfer_edges(self, args: dict) -> dict:
        """Apply flat chamfer to edges using bevel with linear profile."""
        obj_name = args["object_name"]
        size = args["size"]
        edge_indices = args.get("edge_indices", [])
        
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            raise ValueError(f"Mesh object not found: {obj_name}")
        
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_mode(type="EDGE")
        
        if edge_indices:
            # Select specific edges
            bpy.ops.mesh.select_all(action="DESELECT")
            bpy.ops.object.mode_set(mode="OBJECT")
            mesh = obj.data
            for i in edge_indices:
                if i < len(mesh.edges):
                    mesh.edges[i].select = True
            bpy.ops.object.mode_set(mode="EDIT")
        else:
            # Select all edges
            bpy.ops.mesh.select_all(action="SELECT")
        
        # Apply chamfer using bevel with profile=0.5 (flat/linear)
        bpy.ops.mesh.bevel(
            offset=size,
            offset_type="OFFSET",
            segments=1,  # Single segment for flat chamfer
            profile=0.5,  # Linear profile for chamfer
            affect="EDGES"
        )
        
        bpy.ops.object.mode_set(mode="OBJECT")
        
        return {
            "object": obj_name,
            "size": size,
            "edges_chamfered": len(edge_indices) if edge_indices else "all",
        }


# ===== Blender Addon Registration =====

class MCP_PT_Panel(bpy.types.Panel):
    """Panel for MCP server control."""
    bl_label = "MCP Bridge"
    bl_idname = "MCP_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MCP"
    
    def draw(self, context):
        layout = self.layout
        
        global _server
        if _server and _server.running:
            layout.label(text=f"Server running on port {_server.port}")
            layout.operator("mcp.stop_server", text="Stop Server")
        else:
            layout.label(text="Server not running")
            layout.operator("mcp.start_server", text="Start Server")


class MCP_OT_StartServer(bpy.types.Operator):
    """Start MCP server."""
    bl_idname = "mcp.start_server"
    bl_label = "Start MCP Server"
    
    def execute(self, context):
        global _server, _server_thread
        
        if _server is None:
            _server = BlenderMCPServer()
            _server.start()
            _server_thread = threading.Thread(target=_server.serve, daemon=True)
            _server_thread.start()
            
        return {"FINISHED"}


class MCP_OT_StopServer(bpy.types.Operator):
    """Stop MCP server."""
    bl_idname = "mcp.stop_server"
    bl_label = "Stop MCP Server"
    
    def execute(self, context):
        global _server, _server_thread
        
        if _server:
            _server.stop()
            _server = None
            _server_thread = None
            
        return {"FINISHED"}


classes = [
    MCP_PT_Panel,
    MCP_OT_StartServer,
    MCP_OT_StopServer,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # Auto-start server
    bpy.app.timers.register(lambda: bpy.ops.mcp.start_server() or None, first_interval=1.0)


def unregister():
    global _server
    if _server:
        _server.stop()
        _server = None
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
