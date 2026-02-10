# FreeCAD Python Scripting Reference

Patterns for 3D modeling, printing, and AI-assisted design.

---

## Document Setup

```python
import FreeCAD as App
import Part

doc = App.newDocument("MyPart")
doc = App.ActiveDocument
```

---

## Primitives

```python
box = Part.makeBox(length, width, height)
cyl = Part.makeCylinder(radius, height)
sphere = Part.makeSphere(radius)
cone = Part.makeCone(r1, r2, height)
torus = Part.makeTorus(major_r, minor_r)
```

---

## Boolean Operations

```python
result = shape1.fuse(shape2)       # Union
result = base.cut(tool)             # Difference
result = shape1.common(shape2)      # Intersection
Part.show(result)
```

---

## Transforms

```python
shape.translate(App.Vector(x, y, z))
shape.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)  # degrees

moved = shape.copy()
moved.translate(App.Vector(10, 0, 0))
```

---

## PartDesign Workflow

```python
# Body → Sketch → Feature
body = doc.addObject("PartDesign::Body", "Body")
sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
body.addObject(sketch)

# Geometry
sketch.addGeometry(Part.LineSegment(App.Vector(0,0,0), App.Vector(80,0,0)))
sketch.addGeometry(Part.Circle(App.Vector(20, 20, 0), App.Vector(0,0,1), 5))

# Constraints
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 80))
sketch.addConstraint(Sketcher.Constraint("Radius", 4, 5))

# Pad (extrude)
pad = doc.addObject("PartDesign::Pad", "Pad")
pad.Profile = sketch
pad.Length = 10
body.addObject(pad)

# Pocket (cut)
pocket = doc.addObject("PartDesign::Pocket", "Pocket")
pocket.Profile = hole_sketch
pocket.Length = 15
body.addObject(pocket)

# Fillet / Chamfer
fillet = doc.addObject("PartDesign::Fillet", "Fillet")
fillet.Base = (pad, ["Edge1", "Edge2"])
fillet.Radius = 2
body.addObject(fillet)
```

---

## Dimensions (BoundBox)

```python
obj = doc.getObject("Body")
bb = obj.Shape.BoundBox
print(f"L: {bb.XMax - bb.XMin}, W: {bb.YMax - bb.YMin}, H: {bb.ZMax - bb.ZMin}")
print(f"Volume: {obj.Shape.Volume}, Area: {obj.Shape.Area}")
```

---

## Selection API (Interactive)

```python
import FreeCADGui as Gui

# Get what user selected
sel = Gui.Selection.getSelectionEx()
for s in sel:
    print(f"Object: {s.ObjectName}")
    for sub in s.SubElementNames:
        shape = s.Object.Shape.getElement(sub)
        print(f"  {sub}: center={shape.CenterOfMass}")
        if hasattr(shape, "Surface"):
            print(f"  Normal: {shape.Surface.Axis}")

# Select programmatically
Gui.Selection.addSelection(doc.getObject("Box"), "Face1")
Gui.Selection.clearSelection()
```

---

## 3D Text (Deboss/Emboss)

```python
# Use full font path (not font name)
font = "/System/Library/Fonts/Helvetica.ttc"  # macOS
# font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux

wires = Part.makeWireString("CaiD", font, 3.0, 0.0)
text_solids = []
for wire_group in wires:
    if wire_group:
        face = Part.Face(wire_group)
        text_solids.append(face.extrude(App.Vector(0, 0, 0.5)))

text = text_solids[0]
for t in text_solids[1:]:
    text = text.fuse(t)

# Deboss (cut into surface)
result = base.cut(text)

# Emboss (add to surface)
result = base.fuse(text)
```

---

## Export

```python
# STL (3D printing)
import Mesh
mesh = Mesh.Mesh(obj.Shape.tessellate(0.1))
mesh.write("/path/to/output.stl")

# STEP (CAD exchange)
Part.export([obj], "/path/to/output.step")
```

---

## 3D Printing Patterns

### Through Hole
```python
base = Part.makeBox(50, 50, 10)
hole = Part.makeCylinder(3, 15)
hole.translate(App.Vector(25, 25, -2))
result = base.cut(hole)
```

### Counterbore
```python
shaft = Part.makeCylinder(2, 15)
head = Part.makeCylinder(4, 5)
head.translate(App.Vector(0, 0, 5))
hole = shaft.fuse(head)
hole.translate(App.Vector(25, 25, -2))
result = base.cut(hole)
```

### Slot / Channel
```python
slot = Part.makeBox(30, 6, 15)
slot.translate(App.Vector(25, 17, -2))
result = base.cut(slot)
```

### Hole Array
```python
holes = []
for i in range(4):
    h = Part.makeCylinder(2, 15)
    h.translate(App.Vector(10 + i*15, 20, -2))
    holes.append(h)

combined = holes[0]
for h in holes[1:]:
    combined = combined.fuse(h)
result = base.cut(combined)
```

### Snap-Fit Clip (Cantilever)
```python
# Clip on case wall (flexible tab with hook)
clip_w, clip_h, clip_thick = 4.0, 3.0, 1.0
hook_overhang = 0.8

clip = Part.makeBox(clip_w, clip_thick, clip_h)
hook = Part.makeBox(clip_w, hook_overhang, clip_thick)
hook.translate(App.Vector(0, 0, clip_h - clip_thick))  # at top
result = clip.fuse(hook)

# Matching slot in lid
slot = Part.makeBox(clip_w + 0.5, clip_thick + 0.5, clip_thick + 0.3)
```

### Enclosure Tolerances
```python
# Standard clearances for 3D printing
tol = 0.5          # gap around PCB
wall = 2.0         # minimum wall thickness
lip_tol = 0.3      # lid lip clearance
post_r = 2.5       # mounting post radius
screw_r = 1.0      # M2 screw hole
standoff_h = 3.0   # PCB standoff height
```

---

## Recompute

```python
doc.recompute()
```

---

## Fit View

```python
import FreeCADGui as Gui
Gui.ActiveDocument.ActiveView.fitAll()
```
