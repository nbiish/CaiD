"""SolidPython2 code builder for OpenSCAD generation.

This module provides functions to generate OpenSCAD code using SolidPython2,
enabling programmatic CAD design through Python.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

try:
    from solid2 import cube, cylinder, sphere, cone, union, difference, intersection
    from solid2 import translate, rotate, scale, mirror, hull, minkowski
    from solid2 import linear_extrude, rotate_extrude, polygon, circle, square
    from solid2 import scad_render

    SOLIDPYTHON_AVAILABLE = True
except ImportError:
    SOLIDPYTHON_AVAILABLE = False


def check_openscad_installed() -> tuple[bool, str]:
    """Check if OpenSCAD CLI is available."""
    try:
        result = subprocess.run(
            ["openscad", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return True, result.stdout.strip() or result.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "OpenSCAD not found in PATH"


def render_scad_to_stl(
    scad_code: str,
    output_path: str | None = None,
) -> tuple[bool, str]:
    """Render OpenSCAD code to STL file.

    Args:
        scad_code: OpenSCAD source code
        output_path: Optional output STL path. If None, uses temp file.

    Returns:
        Tuple of (success, output_path_or_error)
    """
    installed, msg = check_openscad_installed()
    if not installed:
        return False, msg

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".scad", delete=False
    ) as scad_file:
        scad_file.write(scad_code)
        scad_path = scad_file.name

    if output_path is None:
        output_path = tempfile.mktemp(suffix=".stl")

    try:
        result = subprocess.run(
            ["openscad", "-o", output_path, scad_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            return False, result.stderr

        return True, output_path
    except subprocess.TimeoutExpired:
        return False, "OpenSCAD render timeout (>120s)"
    finally:
        os.unlink(scad_path)


def render_scad_to_png(
    scad_code: str,
    output_path: str | None = None,
    width: int = 800,
    height: int = 600,
) -> tuple[bool, str]:
    """Render OpenSCAD code to PNG preview.

    Args:
        scad_code: OpenSCAD source code
        output_path: Optional output PNG path
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Tuple of (success, output_path_or_error)
    """
    installed, msg = check_openscad_installed()
    if not installed:
        return False, msg

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".scad", delete=False
    ) as scad_file:
        scad_file.write(scad_code)
        scad_path = scad_file.name

    if output_path is None:
        output_path = tempfile.mktemp(suffix=".png")

    try:
        result = subprocess.run(
            [
                "openscad",
                "--imgsize", f"{width},{height}",
                "-o", output_path,
                scad_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return False, result.stderr

        return True, output_path
    except subprocess.TimeoutExpired:
        return False, "OpenSCAD preview timeout (>60s)"
    finally:
        os.unlink(scad_path)


# SolidPython2 helper functions
def create_cube(size: float | list[float], center: bool = False) -> str:
    """Generate OpenSCAD code for a cube/box."""
    if not SOLIDPYTHON_AVAILABLE:
        if isinstance(size, list):
            return f"cube([{size[0]}, {size[1]}, {size[2]}], center={str(center).lower()});"
        return f"cube({size}, center={str(center).lower()});"

    obj = cube(size, center=center)
    return scad_render(obj)


def create_cylinder(
    height: float,
    radius: float | None = None,
    radius1: float | None = None,
    radius2: float | None = None,
    center: bool = False,
    segments: int = 32,
) -> str:
    """Generate OpenSCAD code for a cylinder or cone."""
    if not SOLIDPYTHON_AVAILABLE:
        if radius is not None:
            return f"cylinder(h={height}, r={radius}, center={str(center).lower()}, $fn={segments});"
        return f"cylinder(h={height}, r1={radius1}, r2={radius2}, center={str(center).lower()}, $fn={segments});"

    if radius is not None:
        obj = cylinder(h=height, r=radius, center=center, segments=segments)
    else:
        obj = cylinder(h=height, r1=radius1, r2=radius2, center=center, segments=segments)
    return scad_render(obj)


def create_sphere(radius: float, segments: int = 32) -> str:
    """Generate OpenSCAD code for a sphere."""
    if not SOLIDPYTHON_AVAILABLE:
        return f"sphere(r={radius}, $fn={segments});"

    obj = sphere(r=radius, segments=segments)
    return scad_render(obj)


def apply_transform(
    scad_code: str,
    transform_type: str,
    values: list[float],
) -> str:
    """Apply a transformation to existing SCAD code.

    Args:
        scad_code: Existing OpenSCAD code
        transform_type: One of 'translate', 'rotate', 'scale', 'mirror'
        values: [x, y, z] values for the transformation

    Returns:
        Transformed OpenSCAD code
    """
    if transform_type == "translate":
        return f"translate([{values[0]}, {values[1]}, {values[2]}]) {{\n{scad_code}\n}}"
    elif transform_type == "rotate":
        return f"rotate([{values[0]}, {values[1]}, {values[2]}]) {{\n{scad_code}\n}}"
    elif transform_type == "scale":
        return f"scale([{values[0]}, {values[1]}, {values[2]}]) {{\n{scad_code}\n}}"
    elif transform_type == "mirror":
        return f"mirror([{values[0]}, {values[1]}, {values[2]}]) {{\n{scad_code}\n}}"
    else:
        raise ValueError(f"Unknown transform type: {transform_type}")


def boolean_operation(
    operation: str,
    *scad_codes: str,
) -> str:
    """Combine multiple SCAD objects with a boolean operation.

    Args:
        operation: One of 'union', 'difference', 'intersection'
        *scad_codes: Variable number of SCAD code strings

    Returns:
        Combined OpenSCAD code
    """
    if operation not in ("union", "difference", "intersection"):
        raise ValueError(f"Unknown operation: {operation}")

    inner = "\n".join(f"  {code}" for code in scad_codes)
    return f"{operation}() {{\n{inner}\n}}"


def create_module(
    name: str,
    scad_code: str,
    parameters: dict[str, Any] | None = None,
) -> str:
    """Create a reusable OpenSCAD module.

    Args:
        name: Module name
        scad_code: Module body
        parameters: Optional dict of parameter_name: default_value

    Returns:
        Module definition string
    """
    if parameters:
        param_str = ", ".join(f"{k}={v}" for k, v in parameters.items())
        return f"module {name}({param_str}) {{\n{scad_code}\n}}"
    return f"module {name}() {{\n{scad_code}\n}}"


def validate_scad(scad_code: str) -> tuple[bool, str]:
    """Validate OpenSCAD code syntax.

    Args:
        scad_code: OpenSCAD source code to validate

    Returns:
        Tuple of (is_valid, error_message_or_success)
    """
    installed, msg = check_openscad_installed()
    if not installed:
        return False, msg

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".scad", delete=False
    ) as scad_file:
        scad_file.write(scad_code)
        scad_path = scad_file.name

    try:
        # Use --export=off to validate without rendering
        result = subprocess.run(
            ["openscad", "--export-format=off", "-o", "/dev/null", scad_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return False, result.stderr

        return True, "Valid OpenSCAD code"
    except subprocess.TimeoutExpired:
        return False, "Validation timeout"
    finally:
        os.unlink(scad_path)
