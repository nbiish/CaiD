"""XML-RPC Server for FreeCAD MCP Bridge.

This module implements the RPC server that runs inside FreeCAD,
receiving tool calls from the MCP server and executing them.

IMPORTANT: All FreeCAD operations are dispatched to the main GUI thread
to avoid crashes on macOS where GUI operations must run on the main thread.
"""

import json
import threading
import queue
from xmlrpc.server import SimpleXMLRPCServer
from typing import Any

# FreeCAD imports (available when running inside FreeCAD)
try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    import Sketcher
    from PySide2 import QtCore
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False


class MainThreadDispatcher(QtCore.QObject):
    """Dispatches function calls to the main Qt thread."""
    
    execute_signal = QtCore.Signal(object, object)
    
    def __init__(self):
        super().__init__()
        self.result_queue = queue.Queue()
        self.execute_signal.connect(self._execute_in_main_thread)
    
    def _execute_in_main_thread(self, func, args):
        """Called on the main thread to execute the function."""
        try:
            result = func(*args)
            self.result_queue.put(("success", result))
        except Exception as e:
            self.result_queue.put(("error", str(e)))
    
    def dispatch(self, func, *args, timeout=30):
        """Dispatch a function to run on the main thread and wait for result."""
        # Emit signal to trigger execution on main thread
        self.execute_signal.emit(func, args)
        
        # Wait for result
        try:
            status, result = self.result_queue.get(timeout=timeout)
            if status == "success":
                return result
            else:
                raise RuntimeError(result)
        except queue.Empty:
            raise RuntimeError("Timeout waiting for main thread execution")


class FreeCADMCPServer:
    """XML-RPC server for FreeCAD modeling operations."""
    
    def __init__(self, host: str = "localhost", port: int = 9875):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.dispatcher = None
        
    def start(self):
        """Start the RPC server in a background thread."""
        # Create dispatcher on the main thread
        self.dispatcher = MainThreadDispatcher()
        
        self.server = SimpleXMLRPCServer(
            (self.host, self.port),
            allow_none=True,
            logRequests=False
        )
        self.server.register_function(self.execute_tool, "execute_tool")
        
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"FreeCAD MCP Server started on {self.host}:{self.port}")
        
    def stop(self):
        """Stop the RPC server."""
        if self.server:
            self.server.shutdown()
            self.server = None
            print("FreeCAD MCP Server stopped")
    
    def _run_on_main_thread(self, func, *args):
        """Run a function on the main GUI thread."""
        if self.dispatcher:
            return self.dispatcher.dispatch(func, *args)
        else:
            # Fallback: direct execution (may crash on macOS)
            return func(*args)
            
    def execute_tool(self, tool_name: str, arguments_json: str) -> str:
        """Execute a modeling tool and return the result as JSON."""
        try:
            args = json.loads(arguments_json)
            
            # Route to appropriate handler
            handler = getattr(self, f"_tool_{tool_name}", None)
            if handler:
                # Execute on main thread to avoid GUI crashes
                result = self._run_on_main_thread(handler, args)
                return json.dumps({"success": True, "result": result})
            else:
                return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})
                
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    # ===== Tool Implementations =====
    
    def _tool_execute_code(self, args: dict[str, Any]) -> dict:
        """Execute arbitrary Python code in FreeCAD."""
        code = args.get("code", "")
        if not code.strip():
            return {"output": ""}
        
        import io
        import sys
        
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        try:
            exec(code, {"__builtins__": __builtins__, "App": App, "FreeCAD": App, 
                        "Gui": Gui, "FreeCADGui": Gui, "Part": Part, "Sketcher": Sketcher})
            output = buffer.getvalue()
            return {"output": output if output else "OK"}
        except Exception as e:
            return {"output": f"Error: {e}"}
        finally:
            sys.stdout = old_stdout
    
    def _tool_get_model_info(self, args: dict[str, Any]) -> dict:
        """Get objects and dimensions from current document."""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}
        
        obj_name = args.get("object_name", "")
        info = {"document": doc.Name, "objects": []}
        
        for obj in doc.Objects:
            if obj_name and obj.Name != obj_name:
                continue
            obj_info = {"name": obj.Name, "type": obj.TypeId}
            if hasattr(obj, "Shape"):
                bb = obj.Shape.BoundBox
                obj_info["dimensions"] = {
                    "length": round(bb.XMax - bb.XMin, 3),
                    "width": round(bb.YMax - bb.YMin, 3),
                    "height": round(bb.ZMax - bb.ZMin, 3),
                    "volume": round(obj.Shape.Volume, 3),
                }
            info["objects"].append(obj_info)
        
        return info

    def _tool_create_document(self, args: dict[str, Any]) -> dict:
        """Create a new FreeCAD document."""
        name = args.get("name", "Untitled")
        doc = App.newDocument(name)
        return {"document": doc.Name}
    
    def _tool_create_primitive(self, args: dict[str, Any]) -> dict:
        """Create a primitive shape."""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument("Untitled")
            
        shape_type = args.get("shape", "Box")
        params = args.get("params", {})
        name = args.get("name", shape_type)
        
        if shape_type == "Box":
            obj = doc.addObject("Part::Box", name)
            obj.Length = params.get("Length", 10)
            obj.Width = params.get("Width", 10)
            obj.Height = params.get("Height", 10)
        elif shape_type == "Cylinder":
            obj = doc.addObject("Part::Cylinder", name)
            obj.Radius = params.get("Radius", 5)
            obj.Height = params.get("Height", 10)
        elif shape_type == "Sphere":
            obj = doc.addObject("Part::Sphere", name)
            obj.Radius = params.get("Radius", 5)
        elif shape_type == "Cone":
            obj = doc.addObject("Part::Cone", name)
            obj.Radius1 = params.get("Radius1", 5)
            obj.Radius2 = params.get("Radius2", 0)
            obj.Height = params.get("Height", 10)
        elif shape_type == "Torus":
            obj = doc.addObject("Part::Torus", name)
            obj.Radius1 = params.get("Radius1", 10)
            obj.Radius2 = params.get("Radius2", 2)
        else:
            raise ValueError(f"Unknown shape type: {shape_type}")
            
        doc.recompute()
        return {"object": obj.Name, "type": shape_type}
    
    def _tool_create_sketch(self, args: dict[str, Any]) -> dict:
        """Create a 2D sketch."""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument("Untitled")
            
        plane = args.get("plane", "XY")
        geometry = args.get("geometry", [])
        
        # Create sketch
        sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
        
        # Set sketch plane
        if plane == "XY":
            sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(0, 0, 0, 1))
        elif plane == "XZ":
            sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(1, 0, 0), 90))
        elif plane == "YZ":
            sketch.Placement = App.Placement(App.Vector(0, 0, 0), App.Rotation(App.Vector(0, 1, 0), 90))
        
        # Add geometry
        for geo in geometry:
            geo_type = geo.get("type", "")
            params = geo.get("params", {})
            
            if geo_type == "line":
                start = App.Vector(params.get("start", [0, 0])[0], params.get("start", [0, 0])[1], 0)
                end = App.Vector(params.get("end", [10, 0])[0], params.get("end", [10, 0])[1], 0)
                sketch.addGeometry(Part.LineSegment(start, end))
            elif geo_type == "circle":
                center = App.Vector(params.get("center", [0, 0])[0], params.get("center", [0, 0])[1], 0)
                radius = params.get("radius", 5)
                sketch.addGeometry(Part.Circle(center, App.Vector(0, 0, 1), radius))
            elif geo_type == "rectangle":
                x = params.get("x", 0)
                y = params.get("y", 0)
                w = params.get("width", 10)
                h = params.get("height", 10)
                # Add four lines for rectangle
                sketch.addGeometry(Part.LineSegment(App.Vector(x, y, 0), App.Vector(x + w, y, 0)))
                sketch.addGeometry(Part.LineSegment(App.Vector(x + w, y, 0), App.Vector(x + w, y + h, 0)))
                sketch.addGeometry(Part.LineSegment(App.Vector(x + w, y + h, 0), App.Vector(x, y + h, 0)))
                sketch.addGeometry(Part.LineSegment(App.Vector(x, y + h, 0), App.Vector(x, y, 0)))
            elif geo_type == "arc":
                center = App.Vector(params.get("center", [0, 0])[0], params.get("center", [0, 0])[1], 0)
                radius = params.get("radius", 5)
                start_angle = params.get("start_angle", 0) * 3.14159 / 180
                end_angle = params.get("end_angle", 90) * 3.14159 / 180
                sketch.addGeometry(Part.ArcOfCircle(Part.Circle(center, App.Vector(0, 0, 1), radius), start_angle, end_angle))
        
        doc.recompute()
        return {"sketch": sketch.Name, "geometry_count": len(geometry)}
    
    def _tool_pad_sketch(self, args: dict[str, Any]) -> dict:
        """Extrude a sketch (PartDesign Pad)."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        sketch_name = args.get("sketch_name", "Sketch")
        length = args.get("length", 10)
        symmetric = args.get("symmetric", False)
        
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch not found: {sketch_name}")
        
        # Check if we have a Body, if not create one
        body = None
        for obj in doc.Objects:
            if obj.TypeId == "PartDesign::Body":
                body = obj
                break
        
        if not body:
            body = doc.addObject("PartDesign::Body", "Body")
        
        # Move sketch into body if not already
        if sketch not in body.Group:
            body.addObject(sketch)
        
        # Create pad
        pad = doc.addObject("PartDesign::Pad", "Pad")
        pad.Profile = sketch
        pad.Length = length
        pad.Symmetric = symmetric
        body.addObject(pad)
        
        doc.recompute()
        return {"pad": pad.Name, "length": length}
    
    def _tool_pocket_sketch(self, args: dict[str, Any]) -> dict:
        """Cut into a solid using a sketch (PartDesign Pocket)."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        sketch_name = args.get("sketch_name", "Sketch")
        depth = args.get("depth", 10)
        through_all = args.get("through_all", False)
        
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch not found: {sketch_name}")
        
        # Find the body
        body = None
        for obj in doc.Objects:
            if obj.TypeId == "PartDesign::Body":
                body = obj
                break
        
        if not body:
            raise ValueError("No Body found for pocket operation")
        
        # Create pocket
        pocket = doc.addObject("PartDesign::Pocket", "Pocket")
        pocket.Profile = sketch
        if through_all:
            pocket.Type = 1  # Through All
        else:
            pocket.Length = depth
        body.addObject(pocket)
        
        doc.recompute()
        return {"pocket": pocket.Name, "depth": depth if not through_all else "through_all"}
    
    def _tool_fillet_edges(self, args: dict[str, Any]) -> dict:
        """Apply fillet to selected edges."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        radius = args.get("radius", 1)
        edges = args.get("edges", [])
        
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        # Create fillet
        fillet = doc.addObject("Part::Fillet", f"{object_name}_Fillet")
        fillet.Base = obj
        
        # Set edges to fillet
        edge_list = []
        if edges:
            for edge_name in edges:
                edge_num = int(edge_name.replace("Edge", ""))
                edge_list.append((edge_num, radius, radius))
        else:
            # Fillet all edges
            for i in range(1, len(obj.Shape.Edges) + 1):
                edge_list.append((i, radius, radius))
        
        fillet.Edges = edge_list
        obj.Visibility = False
        doc.recompute()
        
        return {"fillet": fillet.Name, "radius": radius, "edges": len(edge_list)}
    
    def _tool_chamfer_edges(self, args: dict[str, Any]) -> dict:
        """Apply chamfer to selected edges."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        size = args.get("size", 1)
        edges = args.get("edges", [])
        
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        # Create chamfer
        chamfer = doc.addObject("Part::Chamfer", f"{object_name}_Chamfer")
        chamfer.Base = obj
        
        # Set edges to chamfer
        edge_list = []
        if edges:
            for edge_name in edges:
                edge_num = int(edge_name.replace("Edge", ""))
                edge_list.append((edge_num, size, size))
        else:
            # Chamfer all edges
            for i in range(1, len(obj.Shape.Edges) + 1):
                edge_list.append((i, size, size))
        
        chamfer.Edges = edge_list
        obj.Visibility = False
        doc.recompute()
        
        return {"chamfer": chamfer.Name, "size": size, "edges": len(edge_list)}
    
    def _tool_get_objects(self, args: dict[str, Any]) -> dict:
        """List all objects in the current document."""
        doc = App.ActiveDocument
        if not doc:
            return {"objects": [], "document": None}
            
        objects = []
        for obj in doc.Objects:
            obj_info = {
                "name": obj.Name,
                "label": obj.Label,
                "type": obj.TypeId,
            }
            objects.append(obj_info)
            
        return {"document": doc.Name, "objects": objects}
    
    def _tool_create_helix(self, args: dict[str, Any]) -> dict:
        """Create a helix/spiral path."""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument("Untitled")
            
        pitch = args.get("pitch", 5)
        height = args.get("height", 20)
        radius = args.get("radius", 10)
        angle = args.get("angle", 0)
        left_handed = args.get("left_handed", False)
        
        # Create helix using Part module
        helix = doc.addObject("Part::Helix", "Helix")
        helix.Pitch = pitch
        helix.Height = height
        helix.Radius = radius
        helix.Angle = angle
        helix.LocalCoord = 1 if left_handed else 0
        
        doc.recompute()
        return {"helix": helix.Name, "pitch": pitch, "height": height, "radius": radius}
    
    def _tool_create_thread(self, args: dict[str, Any]) -> dict:
        """Create a screw thread."""
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument("Untitled")
            
        diameter = args.get("diameter", 10)
        pitch = args.get("pitch", 1.5)
        length = args.get("length", 20)
        internal = args.get("internal", False)
        thread_type = args.get("thread_type", "metric")
        
        # Create helix for thread path
        helix = doc.addObject("Part::Helix", "ThreadHelix")
        helix.Pitch = pitch
        helix.Height = length
        helix.Radius = diameter / 2
        
        # Create thread profile sketch
        sketch = doc.addObject("Sketcher::SketchObject", "ThreadProfile")
        
        # Simple triangular thread profile
        h = pitch * 0.866  # Thread height for 60-degree angle
        if internal:
            # Internal thread (nut)
            sketch.addGeometry(Part.LineSegment(
                App.Vector(diameter/2, 0, 0),
                App.Vector(diameter/2 + h, pitch/2, 0)
            ))
            sketch.addGeometry(Part.LineSegment(
                App.Vector(diameter/2 + h, pitch/2, 0),
                App.Vector(diameter/2, pitch, 0)
            ))
            sketch.addGeometry(Part.LineSegment(
                App.Vector(diameter/2, pitch, 0),
                App.Vector(diameter/2, 0, 0)
            ))
        else:
            # External thread (bolt)
            sketch.addGeometry(Part.LineSegment(
                App.Vector(diameter/2, 0, 0),
                App.Vector(diameter/2 - h, pitch/2, 0)
            ))
            sketch.addGeometry(Part.LineSegment(
                App.Vector(diameter/2 - h, pitch/2, 0),
                App.Vector(diameter/2, pitch, 0)
            ))
            sketch.addGeometry(Part.LineSegment(
                App.Vector(diameter/2, pitch, 0),
                App.Vector(diameter/2, 0, 0)
            ))
        
        doc.recompute()
        return {
            "helix": helix.Name,
            "profile": sketch.Name,
            "diameter": diameter,
            "pitch": pitch,
            "length": length,
            "type": "internal" if internal else "external"
        }
    
    def _tool_sweep_along_path(self, args: dict[str, Any]) -> dict:
        """Sweep a profile along a path."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        profile_name = args.get("profile_name")
        path_name = args.get("path_name")
        solid = args.get("solid", True)
        
        profile = doc.getObject(profile_name)
        path = doc.getObject(path_name)
        
        if not profile:
            raise ValueError(f"Profile not found: {profile_name}")
        if not path:
            raise ValueError(f"Path not found: {path_name}")
        
        # Create sweep
        sweep = doc.addObject("Part::Sweep", "Sweep")
        sweep.Sections = [profile]
        sweep.Spine = (path, ["Edge1"])
        sweep.Solid = solid
        
        doc.recompute()
        return {"sweep": sweep.Name}
    
    def _tool_revolve_sketch(self, args: dict[str, Any]) -> dict:
        """Revolve a sketch around an axis."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        sketch_name = args.get("sketch_name")
        axis = args.get("axis", "Z")
        angle = args.get("angle", 360)
        
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch not found: {sketch_name}")
        
        # Determine axis vector
        if axis == "X":
            axis_vec = App.Vector(1, 0, 0)
        elif axis == "Y":
            axis_vec = App.Vector(0, 1, 0)
        else:
            axis_vec = App.Vector(0, 0, 1)
        
        # Create revolution
        rev = doc.addObject("Part::Revolution", "Revolution")
        rev.Source = sketch
        rev.Axis = axis_vec
        rev.Base = App.Vector(0, 0, 0)
        rev.Angle = angle
        rev.Solid = True
        
        doc.recompute()
        return {"revolution": rev.Name, "angle": angle}
    
    def _tool_set_parameter(self, args: dict[str, Any]) -> dict:
        """Update a parameter in a spreadsheet."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        name = args.get("name")
        value = args.get("value")
        
        # Find or create spreadsheet
        spreadsheet = None
        for obj in doc.Objects:
            if obj.TypeId == "Spreadsheet::Sheet":
                spreadsheet = obj
                break
        
        if not spreadsheet:
            spreadsheet = doc.addObject("Spreadsheet::Sheet", "Parameters")
        
        # Set the parameter
        spreadsheet.set(name, str(value))
        spreadsheet.setAlias(name, name)
        
        doc.recompute()
        return {"parameter": name, "value": value}
    
    def _tool_export_step(self, args: dict[str, Any]) -> dict:
        """Export model to STEP format."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        filepath = args.get("filepath")
        objects = args.get("objects", [])
        
        if objects:
            export_objects = [doc.getObject(name) for name in objects if doc.getObject(name)]
        else:
            export_objects = [obj for obj in doc.Objects if hasattr(obj, "Shape")]
        
        if not export_objects:
            raise ValueError("No objects to export")
        
        Part.export(export_objects, filepath)
        return {"filepath": filepath, "objects": len(export_objects)}
    
    def _tool_get_screenshot(self, args: dict[str, Any]) -> dict:
        """Capture a screenshot of the current view."""
        width = args.get("width", 800)
        height = args.get("height", 600)
        
        # Get active view
        view = Gui.ActiveDocument.ActiveView
        if not view:
            raise ValueError("No active view")
        
        # Capture to temp file
        import tempfile
        import os
        import base64
        
        fd, filepath = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        
        view.saveImage(filepath, width, height, "White")
        
        # Read and encode
        with open(filepath, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        os.unlink(filepath)
        
        return {"image": image_data, "width": width, "height": height, "format": "png"}
    
    # ===== Additional Tools =====
    
    def _tool_boolean_operation(self, args: dict[str, Any]) -> dict:
        """Perform boolean operation between shapes."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        operation = args.get("operation", "union")
        base_name = args.get("base_object")
        tool_names = args.get("tool_objects", [])
        
        base = doc.getObject(base_name)
        if not base:
            raise ValueError(f"Base object not found: {base_name}")
        
        tools = []
        for name in tool_names:
            obj = doc.getObject(name)
            if obj:
                tools.append(obj)
        
        if not tools:
            raise ValueError("No tool objects found")
        
        if operation == "union":
            result = doc.addObject("Part::MultiFuse", "Union")
            result.Shapes = [base] + tools
        elif operation == "difference":
            result = doc.addObject("Part::Cut", "Cut")
            result.Base = base
            result.Tool = tools[0]
        elif operation == "intersection":
            result = doc.addObject("Part::MultiCommon", "Intersection")
            result.Shapes = [base] + tools
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        doc.recompute()
        return {"result": result.Name, "operation": operation}
    
    def _tool_import_file(self, args: dict[str, Any]) -> dict:
        """Import CAD file."""
        filepath = args.get("file_path")
        file_type = args.get("file_type", "auto")
        
        doc = App.ActiveDocument
        if not doc:
            doc = App.newDocument("Imported")
        
        if file_type == "auto":
            ext = filepath.lower().split(".")[-1]
            file_type = ext
        
        if file_type in ["step", "stp"]:
            Part.insert(filepath, doc.Name)
        elif file_type in ["iges", "igs"]:
            Part.insert(filepath, doc.Name)
        elif file_type == "stl":
            import Mesh
            Mesh.insert(filepath, doc.Name)
        elif file_type == "brep":
            Part.insert(filepath, doc.Name)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        doc.recompute()
        return {"imported": filepath, "document": doc.Name}
    
    def _tool_export_stl(self, args: dict[str, Any]) -> dict:
        """Export object to STL."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        file_path = args.get("file_path")
        ascii_format = args.get("ascii", False)
        
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        import Mesh
        
        if hasattr(obj, "Shape"):
            mesh = Mesh.Mesh(obj.Shape.tessellate(0.1))
        else:
            mesh = obj.Mesh
        
        mesh.write(file_path)
        return {"file_path": file_path, "object": object_name}
    
    def _tool_get_face_names(self, args: dict[str, Any]) -> dict:
        """Get face names from an object."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        faces = []
        if hasattr(obj, "Shape"):
            for i, face in enumerate(obj.Shape.Faces, 1):
                faces.append({
                    "name": f"Face{i}",
                    "area": face.Area,
                    "type": face.Surface.__class__.__name__
                })
        
        return {"object": object_name, "faces": faces}
    
    def _tool_get_edge_names(self, args: dict[str, Any]) -> dict:
        """Get edge names from an object."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        edges = []
        if hasattr(obj, "Shape"):
            for i, edge in enumerate(obj.Shape.Edges, 1):
                edges.append({
                    "name": f"Edge{i}",
                    "length": edge.Length,
                    "type": edge.Curve.__class__.__name__
                })
        
        return {"object": object_name, "edges": edges}
    
    def _tool_linear_pattern(self, args: dict[str, Any]) -> dict:
        """Create linear array of objects."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        direction = args.get("direction", [1, 0, 0])
        occurrences = args.get("occurrences", 3)
        length = args.get("length", 30)
        
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        # Create array
        array = doc.addObject("Part::FeaturePython", f"{object_name}_Array")
        
        # For now, use draft array
        import Draft
        array_obj = Draft.make_ortho_array(
            obj,
            App.Vector(direction[0], direction[1], direction[2]) * (length / (occurrences - 1)),
            occurrences
        )
        
        doc.recompute()
        return {"array": array_obj.Name if array_obj else "Array", "occurrences": occurrences}
    
    def _tool_polar_pattern(self, args: dict[str, Any]) -> dict:
        """Create circular array around axis."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        occurrences = args.get("occurrences", 6)
        angle = args.get("angle", 360)
        axis = args.get("axis", "Z")
        center = args.get("center", [0, 0, 0])
        
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        import Draft
        
        # Determine axis vector
        if axis == "X":
            axis_vec = App.Vector(1, 0, 0)
        elif axis == "Y":
            axis_vec = App.Vector(0, 1, 0)
        else:
            axis_vec = App.Vector(0, 0, 1)
        
        array_obj = Draft.make_polar_array(
            obj,
            occurrences,
            angle,
            App.Vector(center[0], center[1], center[2]),
            axis_vec
        )
        
        doc.recompute()
        return {"array": array_obj.Name if array_obj else "PolarArray", "occurrences": occurrences}
    
    def _tool_mirror_object(self, args: dict[str, Any]) -> dict:
        """Mirror an object across a plane."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object_name = args.get("object_name")
        plane = args.get("plane", "XY")
        
        obj = doc.getObject(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")
        
        # Create mirrored copy
        mirror = doc.addObject("Part::Mirroring", f"{object_name}_Mirror")
        mirror.Source = obj
        
        if plane == "XY":
            mirror.Normal = App.Vector(0, 0, 1)
        elif plane == "XZ":
            mirror.Normal = App.Vector(0, 1, 0)
        elif plane == "YZ":
            mirror.Normal = App.Vector(1, 0, 0)
        
        doc.recompute()
        return {"mirror": mirror.Name, "plane": plane}
    
    def _tool_measure_distance(self, args: dict[str, Any]) -> dict:
        """Measure distance between objects/elements."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        object1 = args.get("object1")
        object2 = args.get("object2")
        subelement1 = args.get("subelement1", "")
        subelement2 = args.get("subelement2", "")
        
        obj1 = doc.getObject(object1)
        obj2 = doc.getObject(object2)
        
        if not obj1 or not obj2:
            raise ValueError("Objects not found")
        
        shape1 = obj1.Shape
        shape2 = obj2.Shape
        
        if subelement1:
            shape1 = getattr(obj1.Shape, subelement1)
        if subelement2:
            shape2 = getattr(obj2.Shape, subelement2)
        
        distance = shape1.distToShape(shape2)[0]
        
        return {"distance": distance, "unit": "mm"}
    
    def _tool_add_sketch_constraint(self, args: dict[str, Any]) -> dict:
        """Add constraint to sketch."""
        doc = App.ActiveDocument
        if not doc:
            raise ValueError("No active document")
            
        sketch_name = args.get("sketch_name")
        constraint_type = args.get("constraint_type")
        geometry_indices = args.get("geometry_indices", [])
        value = args.get("value", None)
        
        sketch = doc.getObject(sketch_name)
        if not sketch:
            raise ValueError(f"Sketch not found: {sketch_name}")
        
        constraint_id = None
        
        if constraint_type == "Horizontal":
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Horizontal", geometry_indices[0]))
        elif constraint_type == "Vertical":
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Vertical", geometry_indices[0]))
        elif constraint_type == "Distance" and value is not None:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Distance", geometry_indices[0], value))
        elif constraint_type == "DistanceX" and value is not None:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("DistanceX", geometry_indices[0], value))
        elif constraint_type == "DistanceY" and value is not None:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("DistanceY", geometry_indices[0], value))
        elif constraint_type == "Radius" and value is not None:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Radius", geometry_indices[0], value))
        elif constraint_type == "Coincident" and len(geometry_indices) >= 2:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Coincident", 
                geometry_indices[0], 1, geometry_indices[1], 1))
        elif constraint_type == "Tangent" and len(geometry_indices) >= 2:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Tangent", 
                geometry_indices[0], geometry_indices[1]))
        elif constraint_type == "Parallel" and len(geometry_indices) >= 2:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Parallel", 
                geometry_indices[0], geometry_indices[1]))
        elif constraint_type == "Perpendicular" and len(geometry_indices) >= 2:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Perpendicular", 
                geometry_indices[0], geometry_indices[1]))
        elif constraint_type == "Equal" and len(geometry_indices) >= 2:
            constraint_id = sketch.addConstraint(Sketcher.Constraint("Equal", 
                geometry_indices[0], geometry_indices[1]))
        else:
            raise ValueError(f"Unknown or incomplete constraint: {constraint_type}")
        
        doc.recompute()
        return {"constraint_id": constraint_id, "type": constraint_type}


# Global server instance
_server = None


def start_server(host: str = "localhost", port: int = 9875):
    """Start the FreeCAD MCP server."""
    global _server
    if _server is None:
        _server = FreeCADMCPServer(host, port)
        _server.start()
    return _server


def stop_server():
    """Stop the FreeCAD MCP server."""
    global _server
    if _server:
        _server.stop()
        _server = None


def is_running():
    """Check if the server is running."""
    return _server is not None


# NOTE: Server is started via Init.py with a delay, not at import time
# To start manually in FreeCAD Python console:
#   from FreeCADMCP import rpc_server
#   rpc_server.start_server()
