"""Utilities for authoring, storing, and reusing control shapes."""

from __future__ import annotations

import functools
import json
from collections.abc import Iterable, Sequence
from pathlib import Path

import pymel.core as pm
from maya import OpenMaya

SHAPE_LIBRARY_PATH = ""
SHELF_NAME = ""
ICON_PATH = ""
CTL_SHAPE_CLIPBOARD: list[dict] = []

__all__ = [
    "create_shape_dir",
    "validate_path",
    "load_data",
    "save_data",
    "get_shape",
    "set_shape",
    "load_from_library",
    "save_to_library",
    "set_colour",
    "get_colour",
    "get_available_control_shapes",
    "get_available_colours",
    "assign_colour",
    "assign_control_shape",
    "assign_all_control_shapes",
    "save_all_control_shapes",
    "mirror_control_shapes",
    "copy_control_shape",
    "paste_control_shape",
    "flip_control_shape",
    "flip_control_shape_x",
    "flip_control_shape_y",
    "flip_control_shape_z",
    "sphereCtrlShape",
    "moveCtrlShape",
    "trapeziumCtrlShape",
    "chestCtrlShape",
    "hipCtrlShape",
    "headCtrlShape",
    "displayCtrlShape",
    "ikfkCtrlShape",
    "pinCtrlShape",
    "arrowCtrlShape",
    "cubeCtrlShape",
    "crossCtrlShape",
    "squareCtrlShape",
]


def _scene_directory() -> Path:
    """Return the directory containing the current Maya scene."""
    scene = Path(pm.sceneName())
    if not scene:
        raise RuntimeError("Save the Maya scene before using control-shape utilities.")
    return scene.parent


def _library_root() -> Path:
    """Resolve the root directory for storing control-shape files."""
    if SHAPE_LIBRARY_PATH:
        return Path(SHAPE_LIBRARY_PATH)
    return _scene_directory()


def create_shape_dir(root: Path | None = None) -> Path:
    """Ensure the control-shape subdirectory exists and return it."""
    root = root or _library_root()
    path = root / "ctrl_shapes"
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_path(path: Path) -> bool:
    """Confirm overwriting an existing file is acceptable."""
    if path.is_file():
        confirm = pm.confirmDialog(
            title="Overwrite file?",
            message=f"The file {path} already exists. Do you want to overwrite it?",
            button=["Yes", "No"],
            defaultButton="Yes",
            cancelButton="No",
            dismissString="No",
        )
        if confirm == "No":
            pm.warning(f"The file {path} was not saved.")
            return False
    return True


def load_data(path: Path) -> dict:
    """Load JSON data from disk."""
    if not path.is_file():
        raise FileNotFoundError(f"Control-shape file '{path}' does not exist.")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(path: Path, data: dict | list) -> bool:
    """Write JSON data to disk."""
    if not validate_path(path):
        return False
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, sort_keys=True, indent=4, separators=(",", ":"))
    return True


def _get_knots(curve_shape: pm.PyNode) -> list[float]:
    """Return knot values for a NURBS curve shape."""
    selection = OpenMaya.MSelectionList()
    selection.add(str(curve_shape))
    m_object = OpenMaya.MObject()
    selection.getDependNode(0, m_object)
    fn_curve = OpenMaya.MFnNurbsCurve(m_object)
    tmp_knots = OpenMaya.MDoubleArray()
    fn_curve.getKnots(tmp_knots)
    return [tmp_knots[i] for i in range(tmp_knots.length())]


def _validate_curve(curve) -> list[pm.PyNode]:
    """Return all curve shapes under the provided node."""
    node = pm.PyNode(curve)
    if node.nodeType() == "transform":
        shapes = node.getShapes(type="nurbsCurve")
    elif node.nodeType() == "nurbsCurve":
        shapes = node.getParent().getShapes(type="nurbsCurve")
    else:
        raise pm.MayaNodeError(f"{curve} is not a NURBS curve transform.")
    if not shapes:
        raise pm.MayaNodeError(f"{curve} does not contain a NURBS curve.")
    return shapes


def get_shape(curve) -> list[dict]:
    """Capture curve information into a serialisable structure."""
    shapes = _validate_curve(curve)
    curve_data = []
    for shape in shapes:
        shape_dict = {
            "points": [
                list(point[0]) for point in pm.getAttr(f"{shape}.controlPoints", multiIndices=True)
            ],
            "knots": _get_knots(shape),
            "form": pm.getAttr(f"{shape}.form"),
            "degree": pm.getAttr(f"{shape}.degree"),
            "colour": pm.getAttr(f"{shape}.overrideColor"),
        }
        curve_data.append(shape_dict)
    return curve_data


def set_shape(curve, shape_data: Sequence[dict]) -> None:
    """Apply stored curve data to the supplied transform."""
    shapes = _validate_curve(curve)
    original_colour = pm.getAttr(f"{shapes[0]}.overrideColor")
    pm.delete(shapes)

    for index, shape_dict in enumerate(shape_data, start=1):
        tmp_curve = pm.curve(
            p=shape_dict["points"],
            k=shape_dict["knots"],
            d=shape_dict["degree"],
            per=bool(shape_dict["form"]),
        )
        new_shape = tmp_curve.getShape()
        pm.parent(new_shape, curve, r=True, s=True)
        pm.delete(tmp_curve)
        new_shape.rename(f"{curve}Shape{index:02d}")
        pm.setAttr(f"{new_shape}.overrideEnabled", True)
        colour = shape_dict.get("colour", original_colour)
        set_colour(new_shape, colour)


def load_from_library(shape_name: str) -> list[dict]:
    """Retrieve shape data from the cache directory."""
    library_dir = create_shape_dir()
    return load_data(library_dir / f"{shape_name}.json")


def save_to_library(curve, shape_name: str) -> bool:
    """Persist the supplied curve definition to a JSON file."""
    shape_data = get_shape(curve)
    for shape in shape_data:
        shape.pop("colour", None)
    library_dir = create_shape_dir()
    target_file = library_dir / f"{shape_name.replace(' ', '')}.json"
    return save_data(target_file, shape_data)


def set_colour(curve, colour_index: int) -> None:
    """Assign override colour to the transform or shape."""
    node = pm.PyNode(curve)
    shapes = node.getShapes() if node.nodeType() == "transform" else [node]
    for shape in shapes:
        pm.setAttr(f"{shape}.overrideColor", colour_index)


def get_colour(curve) -> int:
    """Return the override colour for the given curve."""
    node = pm.PyNode(curve)
    if node.nodeType() == "transform":
        node = node.getShapes()[0]
    return pm.getAttr(f"{node}.overrideColor")


def get_available_control_shapes() -> list[tuple[str, callable]]:
    """List saved control shapes to populate UI menus."""
    shapes_dir = create_shape_dir()
    return [
        (path.stem, functools.partial(assign_control_shape, path.stem))
        for path in shapes_dir.glob("*.json")
    ]


def get_available_colours() -> list[tuple[str, callable, str]]:
    """Return colour menu entries for UI construction."""
    return [
        (f"index{i:02d}", functools.partial(assign_colour, i), f"shapeColour{i:02d}.png")
        for i in range(32)
    ]


def assign_colour(colour_index: int, *_):
    """Apply an override colour to the current selection."""
    for node in pm.ls(sl=True, fl=True):
        set_colour(node, colour_index)


def assign_control_shape(shape_name: str, *_):
    """Assign a stored control shape to all selected nodes."""
    shape_data = load_from_library(shape_name)
    selected = pm.ls(sl=True, fl=True)
    for node in selected:
        set_shape(node, shape_data)
    pm.select(selected)


def assign_all_control_shapes(nodes: Iterable[str]) -> None:
    """Assign matching shapes to every node in the iterable."""
    for node in nodes:
        set_shape(node, load_from_library(node))


def save_all_control_shapes(nodes: Iterable[str]) -> None:
    """Save control shapes for every node in the iterable."""
    for node in nodes:
        save_to_library(node, node)


def mirror_control_shapes(node, axis: str = "x", sides: tuple[str, str] = ("_L", "_R")) -> None:
    """Mirror a control shape from one side to the other."""
    node = pm.PyNode(node)
    node_name = node.name()
    matched_side = next((side for side in sides if side in node_name), None)
    if not matched_side:
        pm.warning(f"No side suffix found in '{node_name}'.")
        return

    other_side = sides[1] if matched_side == sides[0] else sides[0]
    for shape in node.getShapes(type="nurbsCurve"):
        for cv in shape.cv[:]:
            position = pm.xform(cv, q=True, ws=True, t=True)
            counterpart_name = str(cv).replace(matched_side, other_side)
            counterpart = pm.ls(counterpart_name)
            if not counterpart:
                continue
            multiplier = [-1, 1, 1] if axis == "x" else [1, 1, -1]
            mirrored = [
                position[0] * multiplier[0],
                position[1] * multiplier[1],
                position[2] * multiplier[2],
            ]
            pm.xform(counterpart[0], ws=True, t=mirrored)


def copy_control_shape(*_):
    """Copy the first selected control shape into the clipboard."""
    selection = pm.ls(sl=True, fl=True)
    if not selection:
        pm.warning("Select a control to copy its shape.")
        return
    CTL_SHAPE_CLIPBOARD.clear()
    CTL_SHAPE_CLIPBOARD.extend(get_shape(selection[0]))
    for shape in CTL_SHAPE_CLIPBOARD:
        shape.pop("colour", None)


def paste_control_shape(*_):
    """Paste the clipboard control shape onto the selection."""
    if not CTL_SHAPE_CLIPBOARD:
        pm.warning("Clipboard is empty; copy a control shape first.")
        return
    selection = pm.ls(sl=True, fl=True)
    for node in selection:
        set_shape(node, CTL_SHAPE_CLIPBOARD)
    pm.select(selection)


def _flip_control_shape(node, scale):
    """Internal helper to apply a scale to control CVs."""
    shape_data = get_shape(node)
    for shape in shape_data:
        shape["points"] = [
            [point[0] * scale[0], point[1] * scale[1], point[2] * scale[2]]
            for point in shape["points"]
        ]
    set_shape(node, shape_data)


def flip_control_shape(*_):
    """Flip selected control shapes across all axes."""
    selection = pm.ls(sl=True, fl=True)
    for node in selection:
        _flip_control_shape(node, [-1, -1, -1])
    pm.select(selection)


def flip_control_shape_x(*_):
    """Flip selected control shapes across the X axis."""
    selection = pm.ls(sl=True, fl=True)
    for node in selection:
        _flip_control_shape(node, [-1, 1, 1])
    pm.select(selection)


def flip_control_shape_y(*_):
    """Flip selected control shapes across the Y axis."""
    selection = pm.ls(sl=True, fl=True)
    for node in selection:
        _flip_control_shape(node, [1, -1, 1])
    pm.select(selection)


def flip_control_shape_z(*_):
    """Flip selected control shapes across the Z axis."""
    selection = pm.ls(sl=True, fl=True)
    for node in selection:
        _flip_control_shape(node, [1, 1, -1])
    pm.select(selection)


def sphereCtrlShape(name: str = "sphere_CTRL", scale: float = 1.0):
    """Create a sphere-shaped control from three orthogonal circles.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    # Create three circles in X, Y, Z planes
    circle_x = pm.circle(
        name=f"{name}_tempX", normal=[1, 0, 0], radius=scale, sections=8, constructionHistory=False
    )[0]
    circle_y = pm.circle(
        name=f"{name}_tempY", normal=[0, 1, 0], radius=scale, sections=8, constructionHistory=False
    )[0]
    circle_z = pm.circle(
        name=f"{name}_tempZ", normal=[0, 0, 1], radius=scale, sections=8, constructionHistory=False
    )[0]

    # Parent shapes to first circle
    shapes_y = circle_y.getShapes()
    shapes_z = circle_z.getShapes()
    pm.parent(shapes_y + shapes_z, circle_x, r=True, s=True)
    pm.delete([circle_y, circle_z])

    # Rename
    circle_x.rename(name)
    return circle_x


def moveCtrlShape(name: str = "move_CTRL", scale: float = 1.0):
    """Create a four-way arrow control for translation.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Right arrow
        [0.5 * s, 0, 0],
        [0.75 * s, 0, 0],
        [0.75 * s, 0, 0.25 * s],
        [1.0 * s, 0, 0],
        [0.75 * s, 0, -0.25 * s],
        [0.75 * s, 0, 0],
        [0.5 * s, 0, 0],
        # Top arrow
        [0, 0, 0.5 * s],
        [0, 0, 0.75 * s],
        [0.25 * s, 0, 0.75 * s],
        [0, 0, 1.0 * s],
        [-0.25 * s, 0, 0.75 * s],
        [0, 0, 0.75 * s],
        [0, 0, 0.5 * s],
        # Left arrow
        [-0.5 * s, 0, 0],
        [-0.75 * s, 0, 0],
        [-0.75 * s, 0, 0.25 * s],
        [-1.0 * s, 0, 0],
        [-0.75 * s, 0, -0.25 * s],
        [-0.75 * s, 0, 0],
        [-0.5 * s, 0, 0],
        # Bottom arrow
        [0, 0, -0.5 * s],
        [0, 0, -0.75 * s],
        [0.25 * s, 0, -0.75 * s],
        [0, 0, -1.0 * s],
        [-0.25 * s, 0, -0.75 * s],
        [0, 0, -0.75 * s],
        [0, 0, -0.5 * s],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def trapeziumCtrlShape(name: str = "trapezium_CTRL", scale: float = 1.0):
    """Create a trapezoid-shaped control suitable for spine/torso.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        [-1.0 * s, 1.0 * s, 0],
        [1.0 * s, 1.0 * s, 0],
        [1.5 * s, -1.0 * s, 0],
        [-1.5 * s, -1.0 * s, 0],
        [-1.0 * s, 1.0 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def chestCtrlShape(name: str = "chest_CTRL", scale: float = 1.0):
    """Create a chest-shaped control for upper torso.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Outer rectangle
        [-1.5 * s, 1.0 * s, 0],
        [1.5 * s, 1.0 * s, 0],
        [1.5 * s, -1.0 * s, 0],
        [-1.5 * s, -1.0 * s, 0],
        [-1.5 * s, 1.0 * s, 0],
        # Connection to inner
        [-1.0 * s, 0.5 * s, 0],
        # Inner rectangle
        [-1.0 * s, 0.5 * s, 0],
        [1.0 * s, 0.5 * s, 0],
        [1.0 * s, -0.5 * s, 0],
        [-1.0 * s, -0.5 * s, 0],
        [-1.0 * s, 0.5 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def hipCtrlShape(name: str = "hip_CTRL", scale: float = 1.0):
    """Create a hip-shaped control for lower torso.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Inverted trapezoid for hips
        [-1.5 * s, 1.0 * s, 0],
        [1.5 * s, 1.0 * s, 0],
        [1.0 * s, -1.0 * s, 0],
        [-1.0 * s, -1.0 * s, 0],
        [-1.5 * s, 1.0 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def headCtrlShape(name: str = "head_CTRL", scale: float = 1.0):
    """Create a head-shaped control.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    # Create a circle with a vertical line (like a lollipop)
    points = [
        # Circle around head (8 points)
        [0, 1.0 * s, 1.0 * s],
        [0.707 * s, 1.0 * s, 0.707 * s],
        [1.0 * s, 1.0 * s, 0],
        [0.707 * s, 1.0 * s, -0.707 * s],
        [0, 1.0 * s, -1.0 * s],
        [-0.707 * s, 1.0 * s, -0.707 * s],
        [-1.0 * s, 1.0 * s, 0],
        [-0.707 * s, 1.0 * s, 0.707 * s],
        [0, 1.0 * s, 1.0 * s],
        # Neck line
        [0, 1.0 * s, 0],
        [0, 0, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def displayCtrlShape(name: str = "display_CTRL", scale: float = 1.0):
    """Create a simple square frame control for display/visibility toggles.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        [-1.0 * s, 1.0 * s, 0],
        [1.0 * s, 1.0 * s, 0],
        [1.0 * s, -1.0 * s, 0],
        [-1.0 * s, -1.0 * s, 0],
        [-1.0 * s, 1.0 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def ikfkCtrlShape(name: str = "ikfk_CTRL", scale: float = 1.0):
    """Create an IK/FK switch control shape.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    # Create a double-ended arrow for switching
    points = [
        # Left arrow
        [-1.0 * s, 0.5 * s, 0],
        [-1.5 * s, 0, 0],
        [-1.0 * s, -0.5 * s, 0],
        [-1.0 * s, -0.25 * s, 0],
        # Center bar
        [-1.0 * s, -0.25 * s, 0],
        [1.0 * s, -0.25 * s, 0],
        # Right arrow
        [1.0 * s, -0.5 * s, 0],
        [1.5 * s, 0, 0],
        [1.0 * s, 0.5 * s, 0],
        [1.0 * s, 0.25 * s, 0],
        # Back to start
        [-1.0 * s, 0.25 * s, 0],
        [-1.0 * s, 0.5 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def pinCtrlShape(name: str = "pin_CTRL", scale: float = 1.0):
    """Create a pin/thumbtack-shaped control.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Pin head (circle)
        [0, 1.0 * s, 0.5 * s],
        [0.354 * s, 1.0 * s, 0.354 * s],
        [0.5 * s, 1.0 * s, 0],
        [0.354 * s, 1.0 * s, -0.354 * s],
        [0, 1.0 * s, -0.5 * s],
        [-0.354 * s, 1.0 * s, -0.354 * s],
        [-0.5 * s, 1.0 * s, 0],
        [-0.354 * s, 1.0 * s, 0.354 * s],
        [0, 1.0 * s, 0.5 * s],
        # Pin shaft
        [0, 1.0 * s, 0],
        [0, -1.0 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def arrowCtrlShape(name: str = "arrow_CTRL", scale: float = 1.0):
    """Create a single arrow control pointing forward.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Arrow shaft
        [0, 0, -1.0 * s],
        [0, 0, 0.5 * s],
        # Arrow head
        [-0.5 * s, 0, 0.5 * s],
        [0, 0, 1.0 * s],
        [0.5 * s, 0, 0.5 * s],
        [0, 0, 0.5 * s],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def cubeCtrlShape(name: str = "cube_CTRL", scale: float = 1.0):
    """Create a cube wireframe control.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Bottom face
        [-1.0 * s, -1.0 * s, -1.0 * s],
        [1.0 * s, -1.0 * s, -1.0 * s],
        [1.0 * s, -1.0 * s, 1.0 * s],
        [-1.0 * s, -1.0 * s, 1.0 * s],
        [-1.0 * s, -1.0 * s, -1.0 * s],
        # Up to top face
        [-1.0 * s, 1.0 * s, -1.0 * s],
        [1.0 * s, 1.0 * s, -1.0 * s],
        [1.0 * s, 1.0 * s, 1.0 * s],
        [-1.0 * s, 1.0 * s, 1.0 * s],
        [-1.0 * s, 1.0 * s, -1.0 * s],
        # Connect edges
        [-1.0 * s, -1.0 * s, -1.0 * s],
        [-1.0 * s, -1.0 * s, 1.0 * s],
        [-1.0 * s, 1.0 * s, 1.0 * s],
        [1.0 * s, 1.0 * s, 1.0 * s],
        [1.0 * s, -1.0 * s, 1.0 * s],
        [1.0 * s, -1.0 * s, -1.0 * s],
        [1.0 * s, 1.0 * s, -1.0 * s],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def crossCtrlShape(name: str = "cross_CTRL", scale: float = 1.0):
    """Create a cross/plus-shaped control.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        # Vertical arm
        [0, 1.0 * s, 0],
        [0, 0.25 * s, 0],
        # Right arm
        [1.0 * s, 0, 0],
        [0.25 * s, 0, 0],
        # Bottom arm
        [0, -1.0 * s, 0],
        [-0.25 * s, 0, 0],
        # Left arm
        [-1.0 * s, 0, 0],
        [0, 0.25 * s, 0],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


def squareCtrlShape(name: str = "square_CTRL", scale: float = 1.0):
    """Create a simple square control.

    Args:
        name: Name for the control curve.
        scale: Uniform scale factor for the control.

    Returns:
        The created curve transform node.
    """
    s = scale
    points = [
        [-1.0 * s, 0, -1.0 * s],
        [1.0 * s, 0, -1.0 * s],
        [1.0 * s, 0, 1.0 * s],
        [-1.0 * s, 0, 1.0 * s],
        [-1.0 * s, 0, -1.0 * s],
    ]

    curve = pm.curve(name=name, d=1, p=points)
    return curve


if __name__ == "__main__":
    controls = pm.ls("ctl_*_N", "ctl_*_L", "ctl_*_R", type="transform")
    assign_all_control_shapes(controls)
