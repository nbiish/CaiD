# OpenSCAD Scripting Reference

Comprehensive scripting patterns for 3D printing. Use code instead of tools.

---

## Core Primitives

```scad
// 3D Shapes
cube([width, depth, height]);
cube(size, center=true);
cylinder(h=height, r=radius, $fn=32);
cylinder(h=height, r1=bottom, r2=top);  // Cone
sphere(r=radius, $fn=32);

// 2D Shapes
circle(r=radius, $fn=32);
square([width, height], center=true);
polygon(points=[[0,0], [10,0], [5,10]]);
```

---

## Transforms

```scad
translate([x, y, z]) object();
rotate([rx, ry, rz]) object();
scale([sx, sy, sz]) object();
mirror([1, 0, 0]) object();   // Mirror on X
```

---

## Boolean Operations

```scad
// Union: combine parts
union() { cube(10); sphere(7); }

// Difference: cut holes
difference() {
    cube(20);
    cylinder(h=25, r=5, $fn=32);
}

// Intersection: keep overlap only
intersection() { cube(10); sphere(8); }
```

---

## Modules (Reusable Parts)

```scad
module mounting_hole(d=3, h=10) {
    cylinder(h=h, r=d/2, $fn=32);
}

module bracket(w=80, d=40, h=10) {
    difference() {
        cube([w, d, h]);
        translate([10, d/2, 0]) mounting_hole();
        translate([w-10, d/2, 0]) mounting_hole();
    }
}

bracket();  // Use the module
bracket(w=100, h=15);  // Override parameters
```

---

## 3D Printing Patterns

### Through Hole
```scad
difference() {
    cube([20, 20, 10]);
    translate([10, 10, -1])
        cylinder(h=12, r=2.5, $fn=32);
}
```

### Blind Hole
```scad
difference() {
    cube([20, 20, 10]);
    translate([10, 10, 5])  // Start 5mm from top
        cylinder(h=6, r=2, $fn=32);
}
```

### Chamfered Hole
```scad
difference() {
    cube([20, 20, 10]);
    translate([10, 10, -1]) {
        cylinder(h=12, r=2.5, $fn=32);
        cylinder(h=2, r1=4, r2=2.5, $fn=32);  // Chamfer
    }
}
```

### Slot/Channel
```scad
difference() {
    cube([50, 20, 10]);
    translate([10, 5, 5])
        cube([30, 10, 10]);  // Slot cutout
}
```

### Rounded Slot
```scad
module rounded_slot(l=30, w=6, h=10) {
    hull() {
        translate([0, 0, 0]) cylinder(h=h, r=w/2, $fn=32);
        translate([l, 0, 0]) cylinder(h=h, r=w/2, $fn=32);
    }
}
```

### Counterbore
```scad
difference() {
    cube([20, 20, 10]);
    translate([10, 10, -1]) {
        cylinder(h=12, r=1.6, $fn=32);      // Screw shaft
        translate([0, 0, 6])
            cylinder(h=5, r=3.5, $fn=32);   // Head recess
    }
}
```

---

## BOSL2 Library (Advanced)

```scad
include <BOSL2/std.scad>
include <BOSL2/screws.scad>

// Teardrop hole for better printing
teardrop(r=3, h=10);

// Screw hole with tolerance
screw_hole("M3", length=10, $slop=0.1);

// Threaded insert
threaded_rod(d=8, pitch=1.25, length=20);

// Rounded box
cuboid([50, 30, 10], rounding=3);

// Attachments
cuboid([50, 30, 10])
    attach(TOP) cylinder(h=5, r=3);
```

---

## SolidPython2 (Python)

```python
from solid2 import cube, cylinder, difference, scad_render
from solid2 import translate, rotate, union

# Bracket with holes
base = cube([80, 40, 10])
hole = cylinder(h=15, r=3)
holes = union()(
    translate([20, 20, 0])(hole),
    translate([60, 20, 0])(hole)
)
bracket = difference()(base, holes)

# Output SCAD code
print(scad_render(bracket))

# With BOSL2
from solid2.extensions.bosl2 import cuboid, screw_hole
box = cuboid([50, 30, 10], rounding=2)
```

---

## FreeCAD Integration

FreeCAD OpenSCAD workbench imports `.scad` and `.csg` files:

1. **File → Import** `.scad` file
2. OpenSCAD converts to CSG internally
3. FreeCAD imports as solid geometry

Export: **File → Export → CSG**

---

## Workflow

```bash
# Generate SCAD from Python
python my_part.py > part.scad

# Render to STL
openscad -o part.stl part.scad

# Or import to FreeCAD for editing
```
