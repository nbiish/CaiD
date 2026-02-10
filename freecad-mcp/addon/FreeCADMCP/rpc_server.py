"""FreeCAD MCP Addon — XML-RPC bridge (4 handlers).

Handlers: execute_code, get_model_info, get_selection, get_screenshot
All FreeCAD operations dispatch to Qt main thread to avoid macOS crashes.
"""

import io
import json
import queue
import sys
import threading
import traceback
from xmlrpc.server import SimpleXMLRPCServer
from typing import Any

# FreeCAD imports
try:
    import FreeCAD as App
    import FreeCADGui as Gui
    import Part
    import Sketcher
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False

# PySide6/PySide2 compatibility
try:
    from PySide6 import QtCore
except ImportError:
    from PySide2 import QtCore


class MainThreadDispatcher(QtCore.QObject):
    """Dispatch function calls to Qt main thread."""

    execute_signal = QtCore.Signal(object, object)

    def __init__(self):
        super().__init__()
        self.result_queue = queue.Queue()
        self.execute_signal.connect(self._run)

    def _run(self, func, args):
        try:
            result = func(*args)
            self.result_queue.put(("ok", result))
        except Exception as e:
            self.result_queue.put(("err", traceback.format_exc()))

    def dispatch(self, func, *args, timeout=30):
        self.execute_signal.emit(func, args)
        try:
            status, result = self.result_queue.get(timeout=timeout)
            if status == "ok":
                return result
            raise RuntimeError(result)
        except queue.Empty:
            raise RuntimeError("Timeout waiting for main thread")


class FreeCADMCPServer:
    """Minimal XML-RPC server for FreeCAD MCP bridge."""

    def __init__(self, host="localhost", port=9875):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.dispatcher = None

    def start(self):
        self.dispatcher = MainThreadDispatcher()
        self.server = SimpleXMLRPCServer(
            (self.host, self.port), allow_none=True, logRequests=False
        )
        self.server.register_function(self.execute_tool, "execute_tool")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        print(f"FreeCAD MCP Server started on {self.host}:{self.port}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server = None
            print("FreeCAD MCP Server stopped")

    def execute_tool(self, tool_name: str, arguments_json: str) -> str:
        """Route tool call to handler, run on main thread."""
        try:
            args = json.loads(arguments_json)
            handler = getattr(self, f"_tool_{tool_name}", None)
            if not handler:
                return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})
            result = self.dispatcher.dispatch(handler, args)
            return json.dumps({"success": True, "result": result})
        except Exception as e:
            return json.dumps({"success": False, "error": traceback.format_exc()})

    # === Tool Handlers ===

    def _tool_execute_code(self, args: dict[str, Any]) -> dict:
        """Execute Python code in FreeCAD with stdout capture."""
        code = args.get("code", "")
        if not code.strip():
            return {"output": ""}

        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = out_buf = io.StringIO()
        sys.stderr = err_buf = io.StringIO()

        try:
            exec(code, {
                "__builtins__": __builtins__,
                "App": App, "FreeCAD": App,
                "Gui": Gui, "FreeCADGui": Gui,
                "Part": Part, "Sketcher": Sketcher,
            })
            output = out_buf.getvalue()
            errors = err_buf.getvalue()
            result = output if output else "OK"
            if errors:
                result += f"\nSTDERR: {errors}"
            return {"output": result}
        except Exception:
            return {"output": f"Error:\n{traceback.format_exc()}"}
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def _tool_get_model_info(self, args: dict[str, Any]) -> dict:
        """Get objects and dimensions from current document."""
        doc = App.ActiveDocument
        if not doc:
            return {"error": "No active document"}

        target = args.get("object_name", "")
        info = {"document": doc.Name, "objects": []}

        for obj in doc.Objects:
            if target and obj.Name != target:
                continue
            obj_info = {"name": obj.Name, "label": obj.Label, "type": obj.TypeId}
            if hasattr(obj, "Shape") and obj.Shape.Volume > 0:
                bb = obj.Shape.BoundBox
                obj_info["dimensions"] = {
                    "length": round(bb.XMax - bb.XMin, 3),
                    "width": round(bb.YMax - bb.YMin, 3),
                    "height": round(bb.ZMax - bb.ZMin, 3),
                    "volume": round(obj.Shape.Volume, 3),
                    "area": round(obj.Shape.Area, 3),
                }
                obj_info["edges"] = len(obj.Shape.Edges)
                obj_info["faces"] = len(obj.Shape.Faces)
            info["objects"].append(obj_info)

        return info

    def _tool_get_selection(self, args: dict[str, Any]) -> dict:
        """Get currently selected objects/faces/edges in FreeCAD GUI."""
        sel = Gui.Selection.getSelectionEx()
        if not sel:
            return {"selection": [], "count": 0}

        items = []
        for s in sel:
            obj = App.ActiveDocument.getObject(s.ObjectName)
            entry = {"object": s.ObjectName, "type": obj.TypeId if obj else "unknown"}

            if s.SubElementNames:
                subs = []
                for sub_name in s.SubElementNames:
                    sub_info = {"name": sub_name}
                    try:
                        sub_shape = obj.Shape.getElement(sub_name)
                        sub_info["shape_type"] = sub_shape.__class__.__name__
                        bb = sub_shape.BoundBox
                        sub_info["bounds"] = {
                            "x": [round(bb.XMin, 2), round(bb.XMax, 2)],
                            "y": [round(bb.YMin, 2), round(bb.YMax, 2)],
                            "z": [round(bb.ZMin, 2), round(bb.ZMax, 2)],
                        }
                        sub_info["center"] = [
                            round(sub_shape.CenterOfMass.x, 2),
                            round(sub_shape.CenterOfMass.y, 2),
                            round(sub_shape.CenterOfMass.z, 2),
                        ]
                        if hasattr(sub_shape, "Surface"):
                            surf = sub_shape.Surface
                            if hasattr(surf, "Axis"):
                                sub_info["normal"] = [
                                    round(surf.Axis.x, 3),
                                    round(surf.Axis.y, 3),
                                    round(surf.Axis.z, 3),
                                ]
                        if hasattr(sub_shape, "Length"):
                            sub_info["length"] = round(sub_shape.Length, 3)
                        if hasattr(sub_shape, "Area"):
                            sub_info["area"] = round(sub_shape.Area, 3)
                    except Exception as e:
                        sub_info["error"] = str(e)
                    subs.append(sub_info)
                entry["sub_elements"] = subs
            items.append(entry)

        return {"selection": items, "count": len(items)}

    def _tool_get_screenshot(self, args: dict[str, Any]) -> dict:
        """Capture screenshot of current FreeCAD 3D view."""
        import base64
        import os
        import tempfile

        width = args.get("width", 800)
        height = args.get("height", 600)

        view = Gui.ActiveDocument.ActiveView
        if not view:
            return {"error": "No active view"}

        fd, filepath = tempfile.mkstemp(suffix=".png")
        os.close(fd)

        try:
            view.saveImage(filepath, width, height, "White")
            with open(filepath, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode("utf-8")
            return {
                "image_base64": image_b64,
                "width": width,
                "height": height,
                "format": "png",
            }
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


# === Module-level API ===

_server = None


def start_server(host="localhost", port=9875):
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
    return _server is not None
