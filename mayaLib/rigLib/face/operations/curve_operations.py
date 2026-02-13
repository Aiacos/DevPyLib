"""Curve projection operations for facial rigging.

This module provides functions for projecting curves onto geometry,
rebuilding curves with specific parameters, and managing curve-based
rigs for facial animation. Used for brow, jaw, cheek, and other
facial curve systems.

The operations handle:
- Projecting curves onto polygon surfaces using polyProjectCurve
- Selecting optimal projected curves from multiple results
- Rebuilding curves with facial rig-specific parameters
- Reversing curve direction based on CV positions
- Reconnecting curves to pointOnCurveInfo nodes
- Setting curve display colors and visibility

Example:
    Project a curve onto head geometry::

        from mayaLib.rigLib.face.operations import curve_operations
        import maya.cmds as cmds

        # Project brow curve onto head
        result = curve_operations.project_curve_onto_mesh(
            curve="l_browsCurve",
            mesh="head_geo",
            name_prefix="brow",
            curve_samples=50
        )

    Rebuild curve for facial rig::

        curve_operations.rebuild_facial_curve(
            curve="l_browsCurve",
            spans=4,
            degree=3
        )
"""

import logging
from enum import IntEnum
from typing import Optional

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)


class CurveDirection(IntEnum):
    """Curve direction constants for CV ordering.

    Attributes:
        LEFT_TO_RIGHT: CVs ordered from left (-X) to right (+X).
        RIGHT_TO_LEFT: CVs ordered from right (+X) to left (-X).
        TOP_TO_BOTTOM: CVs ordered from top (+Y) to bottom (-Y).
        BOTTOM_TO_TOP: CVs ordered from bottom (-Y) to top (+Y).
    """

    LEFT_TO_RIGHT = 0
    RIGHT_TO_LEFT = 1
    TOP_TO_BOTTOM = 2
    BOTTOM_TO_TOP = 3


def get_curve_cv_position(curve, cv_index, world_space=True):
    """Get the position of a specific CV on a curve.

    Args:
        curve: Curve name or transform.
        cv_index: Index of the CV to query.
        world_space: If True, return world space position.

    Returns:
        tuple: (x, y, z) position of the CV.

    Example:
        >>> pos = get_curve_cv_position("l_browsCurve", 0)
        >>> print(f"Start position: {pos}")
    """
    import maya.cmds as cmds

    cv_path = f"{curve}.cv[{cv_index}]"
    pos = cmds.xform(cv_path, q=True, ws=world_space, t=True)
    return tuple(pos) if pos else (0, 0, 0)


def get_curve_cv_count(curve):
    """Get the number of CVs on a curve.

    Args:
        curve: Curve name or transform.

    Returns:
        int: Number of CVs on the curve.

    Example:
        >>> count = get_curve_cv_count("l_browsCurve")
        >>> print(f"Curve has {count} CVs")
    """
    import maya.cmds as cmds

    cmds.select(f"{curve}.cv[*]", replace=True)
    cvs = cmds.ls(fl=True, sl=True)
    cmds.select(clear=True)
    return len(cvs) if cvs else 0


def calculate_curve_parameter_distances(curve):
    """Calculate parameter distances along a curve for each CV.

    Creates a list of accumulated distances along the curve,
    useful for setting pointOnCurveInfo parameters.

    Args:
        curve: Curve name or transform.

    Returns:
        list: List of accumulated distance values, starting with 0.0.

    Example:
        >>> distances = calculate_curve_parameter_distances("l_browsCurve")
        >>> print(f"Total length parameters: {distances[-1]}")
    """
    import maya.cmds as cmds

    cmds.select(f"{curve}.cv[*]", replace=True)
    cv_list = cmds.ls(fl=True, sl=True)
    cmds.select(clear=True)

    if not cv_list:
        return [0.0]

    distances = [0.0]

    for i in range(1, len(cv_list)):
        prev_pos = get_curve_cv_position(curve, i - 1)
        curr_pos = get_curve_cv_position(curve, i)

        # Create temporary curve to measure distance
        temp_curve = cmds.curve(
            p=[prev_pos, curr_pos],
            k=[0, 1],
            d=1,
        )
        segment_length = cmds.arclen(temp_curve)
        distances.append(distances[i - 1] + segment_length)
        cmds.delete(temp_curve)

    return distances


def get_curve_length(curve):
    """Get the arc length of a curve.

    Args:
        curve: Curve name or transform.

    Returns:
        float: Arc length of the curve.

    Example:
        >>> length = get_curve_length("l_browsCurve")
        >>> print(f"Curve length: {length}")
    """
    import maya.cmds as cmds

    return cmds.arclen(curve)


def project_curve_onto_mesh(
    curve,
    mesh,
    name_prefix="projected",
    auto_direction=True,
    curve_samples=50,
    points_on_edges=False,
):
    """Project a curve onto a polygon mesh surface.

    Uses Maya's polyProjectCurve command to project the curve onto
    the mesh from the front view direction.

    Args:
        curve: Source curve to project.
        mesh: Target polygon mesh.
        name_prefix: Name prefix for the projected curve.
        auto_direction: Use automatic projection direction.
        curve_samples: Number of samples for curve projection.
        points_on_edges: Whether to snap points to mesh edges.

    Returns:
        str: Name of the projected curve transform, or None if failed.

    Example:
        >>> projected = project_curve_onto_mesh(
        ...     "l_browsCurve", "head_geo", "brow"
        ... )
        >>> print(f"Created: {projected}")
    """
    import maya.cmds as cmds
    import pymel.all as pm

    try:
        cmds.select(curve, replace=True)
        cmds.select(mesh, toggle=True)

        # Set front view for projection
        pm.mel.lookThroughModelPanel("front", "modelPanel4")

        cmds.polyProjectCurve(
            curve,
            mesh,
            ch=True,
            automatic=1 if auto_direction else 0,
            pointsOnEdges=1 if points_on_edges else 0,
            curveSamples=curve_samples,
            n=name_prefix,
        )

        # Restore perspective view
        pm.mel.lookThroughModelPanel("persp", "modelPanel4")

        # Get the projected curve shape
        pattern = f"{name_prefix}Shape_*"
        cmds.select(pattern, replace=True)
        cmds.select(f"{name_prefix}Shape_Shape*", deselect=True)
        projected_curves = cmds.ls(sl=True)

        if projected_curves:
            return projected_curves[0]

        return None

    except Exception as e:
        logger.error(f"Failed to project curve: {e}")
        return None


def select_frontmost_projected_curve(projected_pattern, shape_pattern_exclude=None):
    """Select the frontmost curve from multiple projected curves.

    When polyProjectCurve creates multiple curve results (front and back),
    this function selects the one closest to the front (highest Z value).

    Args:
        projected_pattern: Pattern to match projected curves (e.g., "browShape_*").
        shape_pattern_exclude: Pattern to exclude shape nodes (e.g., "browShape_Shape*").

    Returns:
        str: Name of the frontmost curve, or None if none found.

    Example:
        >>> front_curve = select_frontmost_projected_curve(
        ...     "browShape_*", "browShape_Shape*"
        ... )
    """
    import maya.cmds as cmds

    cmds.select(projected_pattern, replace=True)
    if shape_pattern_exclude:
        cmds.select(shape_pattern_exclude, deselect=True)

    curves = cmds.ls(sl=True)
    if not curves:
        return None

    # Calculate center Z position for each curve
    z_positions = []
    for crv in curves:
        cmds.select(crv, replace=True)
        cmds.CenterPivot()
        center = cmds.xform(crv, q=True, ws=True, piv=True)
        z_positions.append(float(center[2]))

    # Find curve with highest Z (frontmost)
    sorted_z = sorted(z_positions)
    front_z = sorted_z[-1]  # Last element is highest

    for i, crv in enumerate(curves):
        center = cmds.xform(crv, q=True, ws=True, piv=True)
        if center[2] == front_z:
            cmds.select(crv, replace=True)
            return crv

    return curves[0] if curves else None


def rebuild_facial_curve(
    curve,
    spans=4,
    degree=3,
    keep_range=0,
    keep_control_points=False,
    keep_end_points=True,
    keep_tangents=False,
    tolerance=0.01,
    replace_original=True,
):
    """Rebuild a curve with facial rig-specific parameters.

    Rebuilds the curve to have a specific number of spans and degree,
    commonly used to standardize curves for facial rigging.

    Args:
        curve: Curve to rebuild.
        spans: Number of spans in the rebuilt curve.
        degree: Degree of the rebuilt curve (1=linear, 3=cubic).
        keep_range: Keep parameter range (0=0-1, 1=original, 2=spans).
        keep_control_points: Keep the original control point positions.
        keep_end_points: Keep the original end points.
        keep_tangents: Keep the original end tangents.
        tolerance: Rebuild tolerance.
        replace_original: Replace the original curve.

    Returns:
        str: Name of the rebuilt curve.

    Example:
        >>> rebuilt = rebuild_facial_curve(
        ...     "l_browsCurve", spans=4, degree=3
        ... )
    """
    import maya.cmds as cmds

    cmds.rebuildCurve(
        curve,
        rt=0,  # Rebuild type: uniform
        ch=1,  # Construction history
        end=1,  # End conditions
        d=degree,
        kr=keep_range,
        s=spans,
        kcp=1 if keep_control_points else 0,
        tol=tolerance,
        kt=1 if keep_tangents else 0,
        rpo=1 if replace_original else 0,
        kep=1 if keep_end_points else 0,
    )

    return curve


def ensure_curve_direction(curve, direction, cv_check_indices=(0, -1)):
    """Ensure curve CVs are ordered in the specified direction.

    Checks the positions of specified CVs and reverses the curve
    if it doesn't match the desired direction.

    Args:
        curve: Curve to check and potentially reverse.
        direction: Desired CurveDirection enum value.
        cv_check_indices: Tuple of (start_cv, end_cv) indices to compare.
            Use -1 for last CV.

    Returns:
        bool: True if curve was reversed, False if already correct.

    Example:
        >>> was_reversed = ensure_curve_direction(
        ...     "l_browsCurve", CurveDirection.LEFT_TO_RIGHT
        ... )
        >>> if was_reversed:
        ...     print("Curve was reversed")
    """
    import maya.cmds as cmds

    start_idx, end_idx = cv_check_indices

    # Handle negative index for last CV
    if end_idx < 0:
        cv_count = get_curve_cv_count(curve)
        end_idx = cv_count + end_idx

    start_pos = get_curve_cv_position(curve, start_idx)
    end_pos = get_curve_cv_position(curve, end_idx)

    needs_reverse = False

    if direction == CurveDirection.LEFT_TO_RIGHT:
        # Start X should be less than end X
        needs_reverse = start_pos[0] > end_pos[0]
    elif direction == CurveDirection.RIGHT_TO_LEFT:
        # Start X should be greater than end X
        needs_reverse = start_pos[0] < end_pos[0]
    elif direction == CurveDirection.TOP_TO_BOTTOM:
        # Start Y should be greater than end Y
        needs_reverse = start_pos[1] < end_pos[1]
    elif direction == CurveDirection.BOTTOM_TO_TOP:
        # Start Y should be less than end Y
        needs_reverse = start_pos[1] > end_pos[1]

    if needs_reverse:
        cmds.reverseCurve(curve, ch=True, rpo=True)
        logger.debug(f"Reversed curve {curve} to match direction {direction.name}")
        return True

    return False


def reverse_curve(curve, construction_history=True, replace_original=True):
    """Reverse the direction of a curve.

    Args:
        curve: Curve to reverse.
        construction_history: Keep construction history.
        replace_original: Replace the original curve.

    Returns:
        str: Name of the reversed curve.

    Example:
        >>> reversed_crv = reverse_curve("l_browsCurve")
    """
    import maya.cmds as cmds

    cmds.reverseCurve(
        curve,
        ch=construction_history,
        rpo=replace_original,
    )

    return curve


def set_curve_display_color(curve, color_index=17):
    """Set the display color override for a curve.

    Args:
        curve: Curve to set color for.
        color_index: Maya color index (0-31).
            Common values: 6=blue, 13=red, 14=green, 16=white, 17=yellow.

    Example:
        >>> set_curve_display_color("l_browsCurve", 17)  # Yellow
    """
    import maya.cmds as cmds

    cmds.setAttr(f"{curve}.overrideEnabled", 1)
    cmds.setAttr(f"{curve}.overrideColor", color_index)


def create_point_on_curve_info(curve, name, parameter=0.0):
    """Create a pointOnCurveInfo node connected to a curve.

    Args:
        curve: Source curve to attach to.
        name: Name for the pointOnCurveInfo node.
        parameter: Parameter position on curve (0.0 to curve length).

    Returns:
        str: Name of the created pointOnCurveInfo node.

    Example:
        >>> poc = create_point_on_curve_info(
        ...     "l_browsCurve", "l_brows_pcInfo_0", 0.5
        ... )
    """
    import maya.cmds as cmds

    poc_node = cmds.shadingNode("pointOnCurveInfo", asUtility=True, n=name)

    # Get shape node
    shapes = cmds.listRelatives(curve, shapes=True)
    shape = shapes[0] if shapes else f"{curve}Shape"

    cmds.connectAttr(f"{shape}.worldSpace[0]", f"{poc_node}.inputCurve")
    cmds.setAttr(f"{poc_node}.parameter", parameter)

    return poc_node


def reconnect_curve_to_poc_nodes(curve, poc_prefix, count, world_space_index=0):
    """Reconnect a curve to multiple pointOnCurveInfo nodes.

    Used after curve projection to reconnect the new curve to
    existing pointOnCurveInfo nodes.

    Args:
        curve: New curve to connect.
        poc_prefix: Prefix of pointOnCurveInfo nodes (e.g., "l_brows_pcInfo_").
        count: Number of pointOnCurveInfo nodes to reconnect.
        world_space_index: World space output index to use.

    Example:
        >>> reconnect_curve_to_poc_nodes(
        ...     "l_browsCurve", "l_brows_pcInfo_", 5
        ... )
    """
    import maya.cmds as cmds

    # Get curve shape
    cmds.select(curve, replace=True)
    cmds.pickWalk(d="down")
    shape_nodes = cmds.ls(sl=True)

    if not shape_nodes:
        logger.warning(f"No shape node found for curve {curve}")
        return

    shape = shape_nodes[0]

    for i in range(count):
        poc_node = f"{poc_prefix}{i}"

        # Try to find existing connection to disconnect
        try:
            existing_connections = cmds.listConnections(
                f"{poc_node}.inputCurve", source=True, plugs=True
            )
            if existing_connections:
                cmds.disconnectAttr(existing_connections[0], f"{poc_node}.inputCurve")
        except Exception:
            pass

        # Connect new curve
        try:
            cmds.connectAttr(
                f"{shape}.worldSpace[{world_space_index}]",
                f"{poc_node}.inputCurve",
            )
        except Exception as e:
            logger.warning(f"Failed to connect {shape} to {poc_node}: {e}")


def create_mirrored_curve_instance(curve, axis="x"):
    """Create a mirrored instance of a curve.

    Args:
        curve: Source curve to mirror.
        axis: Axis to mirror across ('x', 'y', or 'z').

    Returns:
        str: Name of the mirrored curve instance.

    Example:
        >>> mirrored = create_mirrored_curve_instance("l_browsCurve")
        >>> # Creates instance scaled -1 on X axis
    """
    import maya.cmds as cmds
    import pymel.all as pm

    cmds.select(curve, replace=True)
    instance = cmds.instance()[0]

    scale_values = {"x": (-1, 1, 1), "y": (1, -1, 1), "z": (1, 1, -1)}
    scale = scale_values.get(axis.lower(), (-1, 1, 1))

    pm.mel.scale(scale[0], scale[1], scale[2], r=True)

    return instance


def create_locator_on_curve(curve, name, parameter=0.0, create_joint=True):
    """Create a locator (and optionally joint) driven by curve position.

    Args:
        curve: Source curve.
        name: Base name for created nodes.
        parameter: Parameter position on curve.
        create_joint: Whether to create a child joint.

    Returns:
        dict: Dictionary with keys 'locator', 'joint', 'poc_node'.

    Example:
        >>> result = create_locator_on_curve(
        ...     "l_browsCurve", "l_brows_0", 0.5, create_joint=True
        ... )
        >>> print(result['locator'], result['joint'])
    """
    import maya.cmds as cmds

    cmds.select(clear=True)

    # Create empty group as locator
    loc = cmds.CreateEmptyGroup()
    loc = cmds.rename(loc, f"{name}_loc")

    joint = None
    if create_joint:
        joint = cmds.joint(n=f"{name}_jnt_skin")

    # Create pointOnCurveInfo
    poc_name = f"{name}_pcInfo"
    poc_node = create_point_on_curve_info(curve, poc_name, parameter)

    # Connect position
    cmds.connectAttr(f"{poc_node}.position", f"{loc}.translate", force=True)

    cmds.select(clear=True)

    return {
        "locator": loc,
        "joint": joint,
        "poc_node": poc_node,
    }


def delete_projected_curve_group(name_pattern):
    """Delete a projected curve and its group node.

    Args:
        name_pattern: Name or pattern of curve/group to delete.

    Example:
        >>> delete_projected_curve_group("browShape")
    """
    import maya.cmds as cmds
    import pymel.all as pm

    cmds.select(name_pattern, replace=True)
    pm.mel.doDelete()


def parent_curve_to_group(curve, group):
    """Parent a curve under a group node.

    Args:
        curve: Curve to parent.
        group: Target parent group.

    Example:
        >>> parent_curve_to_group("l_browsCurve", "all_facial_grp")
    """
    import maya.cmds as cmds

    cmds.select(curve, replace=True)
    cmds.select(group, add=True)
    cmds.parent()


def rename_curve_after_projection(curve, new_name):
    """Rename a curve after projection.

    Args:
        curve: Current curve name (can be a list).
        new_name: New name for the curve.

    Returns:
        str: The new curve name.

    Example:
        >>> renamed = rename_curve_after_projection("browShape_1", "l_browsCurve")
    """
    import maya.cmds as cmds

    if isinstance(curve, list):
        curve = curve[0]

    return cmds.rename(curve, new_name)


def project_brow_curve(head_geo, curve_name="l_browsCurve", poc_count=5):
    """Project brow curve onto head geometry with standard parameters.

    Complete workflow for projecting a brow curve and reconnecting
    to pointOnCurveInfo nodes.

    Args:
        head_geo: Head geometry mesh name.
        curve_name: Name of the brow curve.
        poc_count: Number of pointOnCurveInfo nodes to reconnect.

    Returns:
        str: Name of the final projected curve.

    Example:
        >>> result = project_brow_curve("head_geo", "l_browsCurve", 5)
    """
    import maya.cmds as cmds
    import pymel.all as pm

    # Project curve
    project_curve_onto_mesh(curve_name, head_geo, "brow", curve_samples=50)

    # Select frontmost result
    front_curve = select_frontmost_projected_curve("browShape_*", "browShape_Shape*")

    if not front_curve:
        logger.error("Failed to find projected brow curve")
        return None

    # Unparent and clean up
    cmds.parent(front_curve, world=True)
    delete_projected_curve_group("browShape")

    # Rebuild with standard brow parameters
    rebuild_facial_curve(front_curve, spans=1, degree=3, keep_range=0)

    # Ensure left-to-right direction
    ensure_curve_direction(front_curve, CurveDirection.LEFT_TO_RIGHT, (0, 3))

    # Reconnect to pointOnCurveInfo nodes
    reconnect_curve_to_poc_nodes(front_curve, "l_brows_pcInfo_", poc_count)

    # Set display color (yellow)
    set_curve_display_color(front_curve, 17)

    # Clean up original and rename
    cmds.select(curve_name, replace=True)
    pm.mel.doDelete()
    final_name = rename_curve_after_projection(front_curve, curve_name)

    return final_name


def project_jaw_curve(head_geo, curve_name="l_jawCurve", poc_count=8):
    """Project jaw curve onto head geometry with standard parameters.

    Complete workflow for projecting a jaw curve and reconnecting
    to pointOnCurveInfo nodes.

    Args:
        head_geo: Head geometry mesh name.
        curve_name: Name of the jaw curve.
        poc_count: Number of pointOnCurveInfo nodes to reconnect.

    Returns:
        str: Name of the final projected curve.

    Example:
        >>> result = project_jaw_curve("head_geo", "l_jawCurve", 8)
    """
    import maya.cmds as cmds
    import pymel.all as pm

    # Project curve
    project_curve_onto_mesh(curve_name, head_geo, "jaw", curve_samples=50)

    # Select frontmost result
    front_curve = select_frontmost_projected_curve("jawShape_*", "jawShape_Shape*")

    if not front_curve:
        logger.error("Failed to find projected jaw curve")
        return None

    # Unparent and clean up
    cmds.parent(front_curve, world=True)
    delete_projected_curve_group("jawShape")

    # Rebuild with standard jaw parameters
    rebuild_facial_curve(front_curve, spans=7, degree=3, keep_range=2)

    # Ensure top-to-bottom direction
    ensure_curve_direction(front_curve, CurveDirection.TOP_TO_BOTTOM, (0, 9))

    # Reconnect to pointOnCurveInfo nodes
    reconnect_curve_to_poc_nodes(front_curve, "l_jaw_pcInfo_", poc_count)

    # Set display color (yellow)
    set_curve_display_color(front_curve, 17)

    # Clean up original and rename
    cmds.select(curve_name, replace=True)
    pm.mel.doDelete()
    final_name = rename_curve_after_projection(front_curve, curve_name)

    return final_name


def project_cheek_curve(head_geo, curve_name="l_cheekCurve", poc_count=5):
    """Project cheek curve onto head geometry with standard parameters.

    Complete workflow for projecting a cheek curve and reconnecting
    to pointOnCurveInfo nodes.

    Args:
        head_geo: Head geometry mesh name.
        curve_name: Name of the cheek curve.
        poc_count: Number of pointOnCurveInfo nodes to reconnect.

    Returns:
        str: Name of the final projected curve.

    Example:
        >>> result = project_cheek_curve("head_geo", "l_cheekCurve", 5)
    """
    import maya.cmds as cmds
    import pymel.all as pm

    # Project curve
    project_curve_onto_mesh(curve_name, head_geo, "cheek", curve_samples=50)

    # Select frontmost result
    front_curve = select_frontmost_projected_curve("cheekShape_*", "cheekShape_Shape*")

    if not front_curve:
        logger.error("Failed to find projected cheek curve")
        return None

    # Unparent and clean up
    cmds.parent(front_curve, world=True)
    delete_projected_curve_group("cheekShape")

    # Rebuild with standard cheek parameters (linear, 4 spans)
    rebuild_facial_curve(front_curve, spans=4, degree=1, keep_range=2)

    # Ensure left-to-right direction
    ensure_curve_direction(front_curve, CurveDirection.LEFT_TO_RIGHT, (0, 4))

    # Reconnect to pointOnCurveInfo nodes
    reconnect_curve_to_poc_nodes(front_curve, "l_cheek_pcInfo_", poc_count, world_space_index=1)

    # Set display color (yellow)
    set_curve_display_color(front_curve, 17)

    # Clean up original and rename
    cmds.select(curve_name, replace=True)
    pm.mel.doDelete()
    final_name = rename_curve_after_projection(front_curve, curve_name)

    return final_name


def project_all_facial_curves(head_geo):
    """Project all standard facial curves onto head geometry.

    Convenience function to project brow, jaw, and cheek curves
    in sequence.

    Args:
        head_geo: Head geometry mesh name.

    Returns:
        dict: Dictionary with keys 'brow', 'jaw', 'cheek' containing curve names.

    Example:
        >>> curves = project_all_facial_curves("head_geo")
        >>> print(curves)
        {'brow': 'l_browsCurve', 'jaw': 'l_jawCurve', 'cheek': 'l_cheekCurve'}
    """
    import maya.cmds as cmds

    cmds.undoInfo(openChunk=True)

    try:
        result = {
            "brow": project_brow_curve(head_geo),
            "jaw": project_jaw_curve(head_geo),
            "cheek": project_cheek_curve(head_geo),
        }
        return result
    finally:
        cmds.undoInfo(closeChunk=True)


# Legacy function name aliases for backward compatibility
projectCrv = project_all_facial_curves  # noqa: N816
rebuildFacialCurve = rebuild_facial_curve  # noqa: N816
getCurveCVPosition = get_curve_cv_position  # noqa: N816
getCurveCVCount = get_curve_cv_count  # noqa: N816
getCurveLength = get_curve_length  # noqa: N816
reverseCurve = reverse_curve  # noqa: N816
setCurveDisplayColor = set_curve_display_color  # noqa: N816
