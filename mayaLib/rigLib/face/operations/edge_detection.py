"""Edge detection algorithms for facial rigging.

This module provides functions for detecting and manipulating edge loops
on facial geometry. Used for selecting specific edge loops on eyelids,
lips, tongue, and other facial features.

The algorithms analyze vertex positions to determine which edges belong
to the upper or lower parts of a loop, useful for facial rig construction.

Example:
    Select upper eyelid edges::

        from mayaLib.rigLib.face.operations import edge_detection
        import maya.cmds as cmds

        # Select an edge loop first
        upper_verts = edge_detection.find_edge_up_down(
            head_geo="head_geo",
            direction=edge_detection.Direction.UP
        )

    Enable edge loop selection mode::

        edge_detection.enable_edge_loop_mode()
"""

import logging
from enum import IntEnum

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)


class Direction(IntEnum):
    """Direction constants for edge selection.

    Attributes:
        UP: Select upper edges (direction=0).
        DOWN: Select lower edges (direction=1).
    """

    UP = 0
    DOWN = 1


def _get_vertex_positions(vertices, axis="x"):
    """Get positions of vertices along a specified axis.

    Args:
        vertices: List of vertex names.
        axis: Axis to extract positions from ('x', 'y', or 'z').

    Returns:
        list: Position values along the specified axis.
    """
    import maya.cmds as cmds

    axis_index = {"x": 0, "y": 1, "z": 2}.get(axis.lower(), 0)
    positions = []

    for vtx in vertices:
        pos = cmds.xform(vtx, q=True, t=True)
        positions.append(pos[axis_index])

    return positions


def _find_extremity_vertices(vertices, positions):
    """Find the first and last vertices based on sorted positions.

    Args:
        vertices: List of vertex names.
        positions: List of position values corresponding to vertices.

    Returns:
        tuple: (first_vertex, last_vertex) - the extremity vertices.
    """
    import maya.cmds as cmds

    sorted_positions = sorted(positions)
    first_vertex = None
    last_vertex = None

    for i, vtx in enumerate(vertices):
        if positions[i] == sorted_positions[0]:
            cmds.select(vtx, replace=True)
            first_vertex = cmds.ls(sl=True)[0]
        if positions[i] == sorted_positions[-1]:
            cmds.select(vtx, replace=True)
            last_vertex = cmds.ls(sl=True)[0]

    return first_vertex, last_vertex


def _find_adjacent_vertices(first_vertex, vertices):
    """Find vertices adjacent to the first vertex that are in the original list.

    Args:
        first_vertex: Starting vertex name.
        vertices: Original vertex list to filter against.

    Returns:
        list: Adjacent vertices that exist in the original vertex list.
    """
    import maya.cmds as cmds

    cmds.select(first_vertex, replace=True)
    cmds.GrowPolygonSelectionRegion()
    grown_selection = cmds.ls(fl=True, sl=True)
    cmds.select(clear=True)

    # Filter to only vertices in the original list
    adjacent = []
    for sel_vtx in grown_selection:
        if sel_vtx in vertices and sel_vtx != first_vertex:
            adjacent.append(sel_vtx)

    return adjacent


def _select_vertex_by_direction(vertices, direction, axis="y"):
    """Select a vertex from a list based on direction preference.

    For UP direction, selects the vertex with higher position.
    For DOWN direction, selects the vertex with lower position.

    Args:
        vertices: List of two vertices to choose from.
        direction: Direction enum (UP or DOWN).
        axis: Axis to compare positions on ('y' for vertical).

    Returns:
        str: The selected vertex name.
    """
    import maya.cmds as cmds

    if len(vertices) < 2:
        return vertices[0] if vertices else None

    axis_index = {"x": 0, "y": 1, "z": 2}.get(axis.lower(), 1)
    pos1 = cmds.xform(vertices[0], q=True, t=True)
    pos2 = cmds.xform(vertices[1], q=True, t=True)

    if direction == Direction.DOWN:
        # Select lower vertex
        if pos1[axis_index] < pos2[axis_index]:
            cmds.select(vertices[0], replace=True)
            return vertices[0]
        else:
            cmds.select(vertices[1], replace=True)
            return vertices[1]
    else:
        # Select upper vertex
        if pos1[axis_index] > pos2[axis_index]:
            cmds.select(vertices[0], replace=True)
            return vertices[0]
        else:
            cmds.select(vertices[1], replace=True)
            return vertices[1]


def fix_edge_loop_direction(direction):
    """Fix edge loop selection direction by selecting appropriate vertex.

    When multiple vertices are selected, this function selects the one
    that matches the desired direction (up or down) based on Y position.

    Args:
        direction: Direction enum or int (0=UP, 1=DOWN).

    Returns:
        str: The selected vertex name, or None if selection invalid.
    """
    import maya.cmds as cmds

    up_down_sel = cmds.ls(fl=True, sl=True)
    if len(up_down_sel) != 2:
        return up_down_sel[0] if up_down_sel else None

    return _select_vertex_by_direction(up_down_sel, direction)


def find_edge_up_down(head_geo, direction, enable_loop_mode=True):
    """Find upper or lower edge loop vertices from current selection.

    This algorithm takes an edge loop selection and separates it into
    upper and lower halves, returning the vertices for the requested
    direction. Used for eyelid and lip edge detection.

    The algorithm:
    1. Converts edges to vertices
    2. Finds extremity vertices (leftmost/rightmost on X axis)
    3. Walks along the loop selecting vertices based on Y position
    4. Returns ordered vertex list for the requested direction

    Args:
        head_geo: Name of the head geometry mesh.
        direction: Direction enum or int (0=UP, 1=DOWN).
        enable_loop_mode: Whether to enable edge loop selection mode after.

    Returns:
        list: Ordered list of vertex names forming the requested half-loop.

    Raises:
        RuntimeError: If no edges are selected or geometry is invalid.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("head_geo.e[100:120]")  # Select eye edge loop
        >>> upper_verts = find_edge_up_down("head_geo", Direction.UP)
        >>> print(f"Found {len(upper_verts)} upper vertices")
    """
    import maya.cmds as cmds
    import pymel.all as pm

    # Get current edge selection
    edge_sel = cmds.ls(fl=True, sl=True)
    if not edge_sel:
        raise RuntimeError("No edges selected")

    # Convert to vertices
    cmds.ConvertSelectionToVertices()
    vertex_list = cmds.ls(fl=True, sl=True)
    if not vertex_list:
        raise RuntimeError("Could not convert selection to vertices")

    # Get X positions to find extremities
    pos_x = _get_vertex_positions(vertex_list, axis="x")
    first_vtx, end_vtx = _find_extremity_vertices(vertex_list, pos_x)

    # Find adjacent vertices to first vertex
    cmds.select(first_vtx, replace=True)
    cmds.GrowPolygonSelectionRegion()
    cmds.select(first_vtx, end_vtx, deselect=True)
    grown_sel = cmds.ls(fl=True, sl=True)
    cmds.select(clear=True)

    # Filter grown selection to vertices in our loop
    for vtx in vertex_list:
        for sel_vtx in grown_sel:
            if sel_vtx == vtx:
                cmds.select(sel_vtx, toggle=True)

    up_down_sel = cmds.ls(fl=True, sl=True)
    if len(up_down_sel) >= 2:
        _select_vertex_by_direction(up_down_sel, direction)

    # Build vertex path from first to end
    down_vertex = [first_vtx]
    second = cmds.ls(fl=True, sl=True)
    if second:
        down_vertex.append(second[0])

    # Walk along the edge loop
    for k in range(2, len(vertex_list)):
        cmds.GrowPolygonSelectionRegion()
        # Deselect previous two vertices
        if len(down_vertex) >= 2:
            cmds.select(down_vertex[k - 2], down_vertex[k - 1], deselect=True)
        new_sel = cmds.ls(fl=True, sl=True)
        cmds.select(clear=True)

        # Find next vertex in our loop
        for vtx in vertex_list:
            for sel_vtx in new_sel:
                if sel_vtx == vtx:
                    cmds.select(sel_vtx, add=True)

        # Fix direction if multiple candidates
        fix_edge_loop_direction(direction)
        second = cmds.ls(fl=True, sl=True)

        if second:
            # Check if we reached the end
            pos1 = cmds.xform(second[0], q=True, t=True)
            pos2 = cmds.xform(end_vtx, q=True, t=True)
            if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
                break
            down_vertex.append(second[0])

    down_vertex.append(end_vtx)

    # Restore edge selection and enable loop mode
    cmds.select(edge_sel, replace=True)
    cmds.ConvertSelectionToContainedEdges()

    if enable_loop_mode:
        enable_edge_loop_mode()

    # Set component selection mode
    import contextlib
    with contextlib.suppress(Exception):
        pm.catch(lambda: pm.mel.doMenuComponentSelection(head_geo, "edge"))

    return down_vertex


def find_edge_up_down_tongue(direction, enable_loop_mode=True):
    """Find upper or lower tongue edge loop vertices from current selection.

    Similar to find_edge_up_down but optimized for tongue geometry where
    the loop orientation is along the Z axis (front-to-back) rather than
    the X axis (side-to-side).

    Args:
        direction: Direction enum or int (0=UP, 1=DOWN).
        enable_loop_mode: Whether to enable edge loop selection mode after.

    Returns:
        list: Ordered list of vertex names forming the requested half-loop.

    Raises:
        RuntimeError: If no edges are selected.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("tongue_geo.e[50:70]")  # Select tongue edge loop
        >>> upper_verts = find_edge_up_down_tongue(Direction.UP)
    """
    import maya.cmds as cmds

    # Get current edge selection
    edge_sel = cmds.ls(fl=True, sl=True)
    if not edge_sel:
        raise RuntimeError("No edges selected")

    # Convert to vertices
    cmds.ConvertSelectionToVertices()
    vertex_list = cmds.ls(fl=True, sl=True)
    if not vertex_list:
        raise RuntimeError("Could not convert selection to vertices")

    # Get Z positions for tongue (front-back axis)
    pos_z = _get_vertex_positions(vertex_list, axis="z")
    first_vtx, end_vtx = _find_extremity_vertices(vertex_list, pos_z)

    # Find adjacent vertices to first vertex
    cmds.select(first_vtx, replace=True)
    cmds.GrowPolygonSelectionRegion()
    cmds.select(first_vtx, end_vtx, deselect=True)
    grown_sel = cmds.ls(fl=True, sl=True)
    cmds.select(clear=True)

    # Filter grown selection to vertices in our loop
    for vtx in vertex_list:
        for sel_vtx in grown_sel:
            if sel_vtx == vtx:
                cmds.select(sel_vtx, toggle=True)

    up_down_sel = cmds.ls(fl=True, sl=True)
    if len(up_down_sel) >= 2:
        _select_vertex_by_direction(up_down_sel, direction)

    # Build vertex path from first to end
    down_vertex = [first_vtx]
    second = cmds.ls(fl=True, sl=True)
    if second:
        down_vertex.append(second[0])

    # Walk along the edge loop
    for k in range(2, len(vertex_list)):
        cmds.GrowPolygonSelectionRegion()
        # Deselect previous two vertices
        if len(down_vertex) >= 2:
            cmds.select(down_vertex[k - 2], down_vertex[k - 1], deselect=True)
        new_sel = cmds.ls(fl=True, sl=True)

        # Find next vertex in our loop
        for vtx in vertex_list:
            for sel_vtx in new_sel:
                if sel_vtx == vtx:
                    cmds.select(sel_vtx, replace=True)

        second = cmds.ls(fl=True, sl=True)

        if second:
            # Check if we reached the end
            pos1 = cmds.xform(second[0], q=True, t=True)
            pos2 = cmds.xform(end_vtx, q=True, t=True)
            if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
                break
            down_vertex.append(second[0])

    down_vertex.append(end_vtx)

    # Restore edge selection and enable loop mode
    cmds.select(edge_sel, replace=True)
    cmds.ConvertSelectionToContainedEdges()

    if enable_loop_mode:
        enable_edge_loop_mode()

    return down_vertex


def enable_edge_loop_mode():
    """Enable edge loop selection constraint mode in Maya.

    This turns on the edge loop selection constraint which makes
    clicking on edges select the entire loop automatically.

    Example:
        >>> enable_edge_loop_mode()
        >>> # Now clicking on an edge will select the whole loop
    """
    import pymel.all as pm

    try:
        pm.mel.dR_selConstraintEdgeLoop()
        logger.debug("Edge loop selection mode enabled")
    except Exception as e:
        logger.warning(f"Could not enable edge loop mode: {e}")


def disable_edge_loop_mode():
    """Disable edge loop selection constraint mode in Maya.

    This turns off the edge loop selection constraint, returning
    to normal edge selection behavior.

    Example:
        >>> disable_edge_loop_mode()
        >>> # Now clicking on edges selects individual edges
    """
    import pymel.all as pm

    try:
        pm.mel.dR_selConstraintOff()
        logger.debug("Edge loop selection mode disabled")
    except Exception as e:
        logger.warning(f"Could not disable edge loop mode: {e}")


def toggle_edge_loop_mode(current_state):
    """Toggle edge loop selection mode on or off.

    Args:
        current_state: Current state of edge loop mode (True if on).

    Returns:
        bool: New state after toggle.

    Example:
        >>> state = False
        >>> state = toggle_edge_loop_mode(state)  # Turns on
        >>> state = toggle_edge_loop_mode(state)  # Turns off
    """
    if not current_state:
        enable_edge_loop_mode()
        return True
    else:
        disable_edge_loop_mode()
        return False


def convert_to_edge_loop():
    """Convert current selection to a complete edge loop.

    Takes the current edge selection and expands it to include
    the complete edge loop(s).

    Returns:
        list: The expanded edge selection as edge names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.e[0]")
        >>> edges = convert_to_edge_loop()
        >>> print(f"Loop contains {len(edges)} edges")
    """
    import maya.cmds as cmds

    cmds.polySelectSp(loop=True)
    return cmds.ls(sl=True, fl=True)


def convert_to_edge_ring():
    """Convert current selection to a complete edge ring.

    Takes the current edge selection and expands it to include
    the complete edge ring(s).

    Returns:
        list: The expanded edge selection as edge names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.e[0]")
        >>> edges = convert_to_edge_ring()
        >>> print(f"Ring contains {len(edges)} edges")
    """
    import maya.cmds as cmds

    cmds.polySelectSp(ring=True)
    return cmds.ls(sl=True, fl=True)


def get_edge_vertices(edge):
    """Get the two vertices that form an edge.

    Args:
        edge: Edge name or component (e.g., "pCube1.e[0]").

    Returns:
        list: Two vertex names that form the edge.

    Example:
        >>> verts = get_edge_vertices("pCube1.e[0]")
        >>> print(verts)  # ['pCube1.vtx[0]', 'pCube1.vtx[1]']
    """
    import maya.cmds as cmds

    cmds.select(edge, replace=True)
    cmds.ConvertSelectionToVertices()
    return cmds.ls(sl=True, fl=True)


def edges_to_vertices(edges):
    """Convert a list of edges to their constituent vertices.

    Args:
        edges: List of edge names.

    Returns:
        list: Unique vertex names from all edges.

    Example:
        >>> verts = edges_to_vertices(["pCube1.e[0]", "pCube1.e[1]"])
    """
    import maya.cmds as cmds

    cmds.select(edges, replace=True)
    cmds.ConvertSelectionToVertices()
    return cmds.ls(sl=True, fl=True)


def vertices_to_edges(vertices, contained=True):
    """Convert a list of vertices to edges.

    Args:
        vertices: List of vertex names.
        contained: If True, only return edges fully contained by vertices.
            If False, return all edges connected to any vertex.

    Returns:
        list: Edge names.

    Example:
        >>> edges = vertices_to_edges(["pCube1.vtx[0]", "pCube1.vtx[1]"])
    """
    import maya.cmds as cmds

    cmds.select(vertices, replace=True)
    if contained:
        cmds.ConvertSelectionToContainedEdges()
    else:
        cmds.ConvertSelectionToEdges()
    return cmds.ls(sl=True, fl=True)


# Legacy function name aliases for backward compatibility
findEdgeUpDown = find_edge_up_down  # noqa: N816
findEdgeUpDownTongue = find_edge_up_down_tongue  # noqa: N816
wfFixEdgeLoopA = fix_edge_loop_direction  # noqa: N816
EdgeLoopOn_fn = enable_edge_loop_mode  # noqa: N816
EdgeLoopOff_fn = disable_edge_loop_mode  # noqa: N816
