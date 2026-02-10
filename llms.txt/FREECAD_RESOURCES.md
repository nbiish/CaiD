# FreeCAD Python Scripting Reference

Comprehensive scripting patterns for 3D modeling and printing.

---

## Document Setup

```python
import FreeCAD as App
import Part

# Create/access document
doc = App.newDocument("MyPart")
doc = App.ActiveDocument
```

---

## Part Module (Direct Geometry)

### Primitives

```python
# Box
box = Part.makeBox(length, width, height)
box = Part.makeBox(80, 40, 10)

# Cylinder
cyl = Part.makeCylinder(radius, height)
cyl = Part.makeCylinder(5, 20)

# Sphere
sphere = Part.makeSphere(radius)

# Cone
cone = Part.makeCone(r1, r2, height)

# Torus
torus = Part.makeTorus(major_r, minor_r)
```

### Boolean Operations

```python
# Union (combine)
result = shape1.fuse(shape2)

# Difference (cut hole)
result = base.cut(tool)

# Intersection (common volume)
result = shape1.common(shape2)

# Show result
Part.show(result)
```

### Transform

```python
# Move
shape.translate(App.Vector(x, y, z))

# Rotate (degrees)
shape.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle)

# Copy and transform
moved = shape.copy()
moved.translate(App.Vector(10, 0, 0))
```

---

## PartDesign (Feature-Based)

### Workflow: Body → Sketch → Feature

```python
import FreeCAD as App
import Part
import Sketcher
import PartDesign

doc = App.newDocument("Bracket")

# Create Body
body = doc.addObject("PartDesign::Body", "Body")

# Create Sketch on XY plane
sketch = doc.addObject("Sketcher::SketchObject", "Sketch")
sketch.MapMode = "FlatFace"
sketch.Support = [(doc.getObject("XY_Plane"), "")]

# Or attach to body's origin
body.addObject(sketch)
```

### Sketcher Geometry

```python
# Rectangle
sketch.addGeometry(Part.LineSegment(App.Vector(0,0,0), App.Vector(80,0,0)))
sketch.addGeometry(Part.LineSegment(App.Vector(80,0,0), App.Vector(80,40,0)))
sketch.addGeometry(Part.LineSegment(App.Vector(80,40,0), App.Vector(0,40,0)))
sketch.addGeometry(Part.LineSegment(App.Vector(0,40,0), App.Vector(0,0,0)))

# Circle
sketch.addGeometry(Part.Circle(App.Vector(20, 20, 0), App.Vector(0, 0, 1), 5))

# Arc
sketch.addGeometry(Part.ArcOfCircle(
    Part.Circle(App.Vector(0,0,0), App.Vector(0,0,1), 10),
    0, 1.57  # start/end radians
))
```

### Constraints

```python
# Fix point
sketch.addConstraint(Sketcher.Constraint("Fixed", 0, 1))

# Horizontal/Vertical
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("Vertical", 1))

# Distance
sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 80))
sketch.addConstraint(Sketcher.Constraint("DistanceY", 1, 1, 40))

# Radius
sketch.addConstraint(Sketcher.Constraint("Radius", 4, 5))  # geom 4, radius 5

# Coincident
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
```

### Features

```python
# Pad (extrude)
pad = doc.addObject("PartDesign::Pad", "Pad")
pad.Profile = sketch
pad.Length = 10
body.addObject(pad)

# Pocket (cut)
pocket = doc.addObject("PartDesign::Pocket", "Pocket")
pocket.Profile = hole_sketch
pocket.Length = 15  # or "Through All"
body.addObject(pocket)

# Hole (wizard)
hole = doc.addObject("PartDesign::Hole", "Hole")
hole.Profile = center_sketch
hole.Diameter = 6
hole.Depth = 10
hole.Threaded = True
body.addObject(hole)

# Fillet
fillet = doc.addObject("PartDesign::Fillet", "Fillet")
fillet.Base = (pad, ["Edge1", "Edge2"])
fillet.Radius = 2
body.addObject(fillet)

# Chamfer
chamfer = doc.addObject("PartDesign::Chamfer", "Chamfer")
chamfer.Base = (pad, ["Edge3"])
chamfer.Size = 1
body.addObject(chamfer)
```

---

## Get Dimensions (BoundBox)

```python
# Get bounding box of any object
obj = doc.getObject("Body")
shape = obj.Shape
bb = shape.BoundBox

# Dimensions
length = bb.XMax - bb.XMin
width = bb.YMax - bb.YMin
height = bb.ZMax - bb.ZMin

print(f"L: {length}, W: {width}, H: {height}")
print(f"Volume: {shape.Volume}")
print(f"Area: {shape.Area}")
```

---

## List Objects

```python
# All objects
for obj in doc.Objects:
    print(f"{obj.Name}: {obj.TypeId}")

# Object properties
obj = doc.getObject("Pad")
print(obj.Length)
print(obj.Profile)
```

---

## Export

```python
# Export to STL
import Mesh
obj = doc.getObject("Body")
mesh = doc.addObject("Mesh::Feature", "Mesh")
mesh.Mesh = Mesh.Mesh(obj.Shape.tessellate(0.1))
Mesh.export([mesh], "/path/to/output.stl")

# Or simpler
import MeshPart
MeshPart.export([obj], "/path/to/output.stl")

# Export to STEP
import ImportGui
ImportGui.export([obj], "/path/to/output.step")
```

---

## 3D Printing Patterns

### Through Hole

```python
base = Part.makeBox(50, 50, 10)
hole = Part.makeCylinder(3, 15)
hole.translate(App.Vector(25, 25, -2))
result = base.cut(hole)
Part.show(result)
```

### Counterbore

```python
base = Part.makeBox(50, 50, 10)
shaft = Part.makeCylinder(2, 15)
head = Part.makeCylinder(4, 5)
head.translate(App.Vector(0, 0, 5))
hole = shaft.fuse(head)
hole.translate(App.Vector(25, 25, -2))
result = base.cut(hole)
```

### Slot/Channel

```python
base = Part.makeBox(80, 40, 10)
slot = Part.makeBox(30, 6, 15)
slot.translate(App.Vector(25, 17, -2))
result = base.cut(slot)
```

### Rounded Slot

```python
# Slot with rounded ends using hull of cylinders
c1 = Part.makeCylinder(3, 10)
c2 = Part.makeCylinder(3, 10)
c2.translate(App.Vector(20, 0, 0))
slot = c1.fuse(c2).makeShell().makeSolid()
```

### Pattern (Linear Array)

```python
holes = []
for i in range(4):
    h = Part.makeCylinder(2, 15)
    h.translate(App.Vector(10 + i*15, 20, -2))
    holes.append(h)

all_holes = holes[0]
for h in holes[1:]:
    all_holes = all_holes.fuse(h)

result = base.cut(all_holes)
```

---

## Recompute

```python
doc.recompute()
```
