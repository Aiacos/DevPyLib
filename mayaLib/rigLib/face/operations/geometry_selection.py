"""Geometry selection handlers for facial rigging.

This module provides functions for handling geometry selections in Maya,
including vertex/edge conversion, selection filtering, namespace handling,
and storing selections for facial rig construction.

The operations handle:
- Converting between selection types (vertices, edges, faces)
- Filtering out joints from vertex selections
- Namespace removal from selected objects
- Growing/shrinking polygon selections
- Inverting selections
- Storing and validating selections

Example:
    Get vertices from current selection excluding joints::

        from mayaLib.rigLib.face.operations import geometry_selection
        import maya.cmds as cmds

        # Select some components
        cmds.select("head_geo.vtx[100:200]")
        verts = geometry_selection.get_vertices_excluding_joints()

    Get geometry from selection with namespace removal::

        geo = geometry_selection.get_geometry_with_namespace_removal()
        print(f"Selected: {geo}")
"""

import logging
from enum import IntEnum
from typing import Optional, Union

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)


class SelectionType(IntEnum):
    """Selection component type constants.

    Attributes:
        VERTEX: Vertex selection mode (0).
        EDGE: Edge selection mode (1).
        FACE: Face selection mode (2).
    """

    VERTEX = 0
    EDGE = 1
    FACE = 2


def get_current_selection(flatten: bool = True) -> list:
    """Get the current Maya selection.

    Args:
        flatten: If True, expand component ranges to individual items.

    Returns:
        list: List of selected objects or components.

    Example:
        >>> selection = get_current_selection()
        >>> print(f"Selected {len(selection)} items")
    """
    import maya.cmds as cmds

    return cmds.ls(fl=flatten, sl=True) or []


def convert_selection_to_vertices() -> list:
    """Convert current selection to vertices.

    Converts any component selection (edges, faces) to the
    constituent vertices.

    Returns:
        list: List of vertex names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.e[0:3]")
        >>> verts = convert_selection_to_vertices()
        >>> print(f"Converted to {len(verts)} vertices")
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToVertices()
    return cmds.ls(fl=True, sl=True) or []


def convert_selection_to_contained_edges() -> list:
    """Convert current selection to contained edges.

    Returns only edges that are fully contained within the
    current vertex selection (both vertices selected).

    Returns:
        list: List of edge names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.vtx[0:4]")
        >>> edges = convert_selection_to_contained_edges()
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToContainedEdges()
    return cmds.ls(fl=True, sl=True) or []


def convert_selection_to_edges() -> list:
    """Convert current selection to all connected edges.

    Returns all edges connected to any selected vertex,
    not just fully contained edges.

    Returns:
        list: List of edge names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.vtx[0]")
        >>> edges = convert_selection_to_edges()
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToEdges()
    return cmds.ls(fl=True, sl=True) or []


def convert_selection_to_faces() -> list:
    """Convert current selection to faces.

    Converts vertex or edge selection to faces.

    Returns:
        list: List of face names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.vtx[0:4]")
        >>> faces = convert_selection_to_faces()
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToFaces()
    return cmds.ls(fl=True, sl=True) or []


def convert_selection_to_contained_faces() -> list:
    """Convert current selection to contained faces.

    Returns only faces that are fully contained within the
    current selection (all vertices of the face selected).

    Returns:
        list: List of face names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.vtx[0:8]")
        >>> faces = convert_selection_to_contained_faces()
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToContainedFaces()
    return cmds.ls(fl=True, sl=True) or []


def get_vertices_excluding_joints() -> list:
    """Get vertices from current selection, excluding any joints.

    Converts selection to vertices and filters out any selected
    joint objects. Useful when selecting regions that may include
    joint markers.

    Returns:
        list: List of vertex names (joints excluded).

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("head_geo.vtx[*]", "head_jnt", r=True)
        >>> verts = get_vertices_excluding_joints()
        >>> # Returns only head_geo vertices, no joints
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToVertices()
    exclude_jnt = cmds.ls(type="joint", sl=True) or []
    if exclude_jnt:
        cmds.select(exclude_jnt, deselect=True)
    return cmds.ls(fl=True, sl=True) or []


def grow_polygon_selection(iterations: int = 1) -> list:
    """Grow the current polygon selection by specified iterations.

    Expands the selection to include adjacent components.

    Args:
        iterations: Number of times to grow the selection.

    Returns:
        list: The expanded selection.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.vtx[0]")
        >>> expanded = grow_polygon_selection(2)
        >>> print(f"Selection grew to {len(expanded)} vertices")
    """
    import maya.cmds as cmds

    for _ in range(iterations):
        cmds.GrowPolygonSelectionRegion()
    return cmds.ls(fl=True, sl=True) or []


def shrink_polygon_selection(iterations: int = 1) -> list:
    """Shrink the current polygon selection by specified iterations.

    Contracts the selection by removing boundary components.

    Args:
        iterations: Number of times to shrink the selection.

    Returns:
        list: The contracted selection.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.f[*]")
        >>> shrunk = shrink_polygon_selection(1)
    """
    import maya.cmds as cmds

    for _ in range(iterations):
        cmds.ShrinkPolygonSelectionRegion()
    return cmds.ls(fl=True, sl=True) or []


def invert_selection() -> list:
    """Invert the current selection within the same object.

    Selects all components of the same type that are not
    currently selected.

    Returns:
        list: The inverted selection.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.vtx[0:3]")
        >>> inverted = invert_selection()
        >>> # Now all OTHER vertices are selected
    """
    import pymel.all as pm

    pm.mel.invertSelection()
    import maya.cmds as cmds

    return cmds.ls(fl=True, sl=True) or []


def remove_namespace_from_object(obj_name: str) -> str:
    """Remove namespace from a Maya object and return cleaned name.

    If the object has a namespace, removes it by merging with parent
    namespace and returns the cleaned name.

    Args:
        obj_name: Object name potentially with namespace.

    Returns:
        str: Object name without namespace.

    Example:
        >>> clean_name = remove_namespace_from_object("character:head_geo")
        >>> print(clean_name)  # "head_geo"
    """
    import maya.cmds as cmds

    chk_namespace = len(obj_name.split(":"))
    if chk_namespace > 1:
        namespace = obj_name.split(":")[0]
        try:
            cmds.namespace(removeNamespace=":" + namespace, mergeNamespaceWithParent=True)
        except Exception as e:
            logger.warning(f"Could not remove namespace '{namespace}': {e}")

    # Re-query to get updated name
    try:
        cmds.select(obj_name.split(":")[-1], replace=True)
        return cmds.ls(sl=True)[0]
    except Exception:
        return obj_name.split(":")[-1]


def get_geometry_with_namespace_removal() -> Optional[str]:
    """Get selected geometry object with namespace removed.

    Selects the first object in the current selection, removes any
    namespace, and returns the cleaned name.

    Returns:
        str: Geometry name without namespace, or None if no selection.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("character:head_geo")
        >>> geo = get_geometry_with_namespace_removal()
        >>> print(geo)  # "head_geo"
    """
    import maya.cmds as cmds

    selection = cmds.ls(sl=True)
    if not selection:
        logger.warning("No geometry selected")
        return None

    geo_name = selection[0]
    return remove_namespace_from_object(geo_name)


def select_all_vertices(mesh: str) -> list:
    """Select all vertices of a mesh.

    Args:
        mesh: Name of the mesh to select vertices from.

    Returns:
        list: All vertex names from the mesh.

    Example:
        >>> verts = select_all_vertices("head_geo")
        >>> print(f"Mesh has {len(verts)} vertices")
    """
    import maya.cmds as cmds

    cmds.select(f"{mesh}.vtx[*]", replace=True)
    return cmds.ls(fl=True, sl=True) or []


def get_foreground_face_selection(
    head_geo: str,
    exclude_vertices: Optional[list] = None,
) -> list:
    """Get foreground (front-facing) vertex selection for facial rig.

    Inverts the current selection to get vertices NOT in the selection,
    typically used to separate forehead/face from back of head.

    Args:
        head_geo: Name of the head geometry mesh.
        exclude_vertices: Optional list of vertices to exclude.

    Returns:
        list: Foreground vertex selection.

    Example:
        >>> # Select back of head vertices first
        >>> cmds.select("head_geo.vtx[500:600]")
        >>> front_verts = get_foreground_face_selection("head_geo")
    """
    import maya.cmds as cmds

    # Get current selection as the exclusion area
    cmds.ConvertSelectionToVertices()
    exclude_jnt = cmds.ls(type="joint", sl=True) or []
    if exclude_jnt:
        cmds.select(exclude_jnt, deselect=True)

    exclude_selection = cmds.ls(fl=True, sl=True) or []

    if exclude_vertices:
        exclude_selection.extend(exclude_vertices)

    # Select all vertices then deselect the exclusion area
    cmds.select(f"{head_geo}.vtx[*]", replace=True)
    if exclude_selection:
        cmds.select(exclude_selection, deselect=True)

    return cmds.ls(fl=True, sl=True) or []


def validate_vertex_selection(
    vertices: list,
    minimum_count: int = 1,
    maximum_count: Optional[int] = None,
) -> bool:
    """Validate a vertex selection meets requirements.

    Args:
        vertices: List of vertex names to validate.
        minimum_count: Minimum number of vertices required.
        maximum_count: Maximum number of vertices allowed (None for unlimited).

    Returns:
        bool: True if selection is valid, False otherwise.

    Example:
        >>> verts = ["pCube1.vtx[0]", "pCube1.vtx[1]"]
        >>> is_valid = validate_vertex_selection(verts, minimum_count=2)
        >>> print(is_valid)  # True
    """
    if not vertices:
        logger.warning("Empty vertex selection")
        return False

    count = len(vertices)

    if count < minimum_count:
        logger.warning(f"Selection has {count} vertices, minimum required is {minimum_count}")
        return False

    if maximum_count is not None and count > maximum_count:
        logger.warning(f"Selection has {count} vertices, maximum allowed is {maximum_count}")
        return False

    return True


def get_vertex_positions(vertices: list, world_space: bool = True) -> list:
    """Get world or local positions for a list of vertices.

    Args:
        vertices: List of vertex names.
        world_space: If True, return world space positions.

    Returns:
        list: List of (x, y, z) tuples for each vertex.

    Example:
        >>> positions = get_vertex_positions(["pCube1.vtx[0]", "pCube1.vtx[1]"])
        >>> for pos in positions:
        ...     print(f"Position: {pos}")
    """
    import maya.cmds as cmds

    positions = []
    for vtx in vertices:
        pos = cmds.xform(vtx, q=True, ws=world_space, t=True)
        if pos:
            positions.append(tuple(pos))

    return positions


def get_selection_center(selection: Optional[list] = None) -> tuple:
    """Calculate the center point of a selection.

    Args:
        selection: List of components to find center of.
            If None, uses current selection.

    Returns:
        tuple: (x, y, z) center position.

    Example:
        >>> center = get_selection_center()
        >>> print(f"Selection center: {center}")
    """
    import maya.cmds as cmds

    if selection is None:
        selection = cmds.ls(sl=True, fl=True)

    if not selection:
        return (0.0, 0.0, 0.0)

    # Convert to vertices if not already
    cmds.select(selection, replace=True)
    cmds.ConvertSelectionToVertices()
    vertices = cmds.ls(sl=True, fl=True)

    if not vertices:
        return (0.0, 0.0, 0.0)

    # Calculate average position
    total_x, total_y, total_z = 0.0, 0.0, 0.0
    for vtx in vertices:
        pos = cmds.xform(vtx, q=True, ws=True, t=True)
        total_x += pos[0]
        total_y += pos[1]
        total_z += pos[2]

    count = len(vertices)
    return (total_x / count, total_y / count, total_z / count)


def store_edge_selection() -> list:
    """Store the current edge selection.

    Returns the current edge selection as a flattened list
    for later recall.

    Returns:
        list: List of edge names in current selection.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.e[0:5]")
        >>> stored_edges = store_edge_selection()
        >>> # Later...
        >>> cmds.select(stored_edges)
    """
    import maya.cmds as cmds

    return cmds.ls(fl=True, sl=True) or []


def store_vertex_selection() -> list:
    """Store the current vertex selection.

    Converts selection to vertices and returns as a flattened list.

    Returns:
        list: List of vertex names.

    Example:
        >>> import maya.cmds as cmds
        >>> cmds.select("pCube1.e[0:5]")
        >>> stored_verts = store_vertex_selection()
        >>> # Stored as vertices, not edges
    """
    import maya.cmds as cmds

    cmds.ConvertSelectionToVertices()
    return cmds.ls(fl=True, sl=True) or []


def restore_selection(selection: list) -> None:
    """Restore a previously stored selection.

    Args:
        selection: List of objects/components to select.

    Example:
        >>> stored = store_edge_selection()
        >>> # Do other operations...
        >>> restore_selection(stored)
    """
    import maya.cmds as cmds

    if selection:
        cmds.select(selection, replace=True)
    else:
        cmds.select(clear=True)


def clear_selection() -> None:
    """Clear the current Maya selection.

    Example:
        >>> clear_selection()
        >>> # Selection is now empty
    """
    import maya.cmds as cmds

    cmds.select(clear=True)


def update_selection_mode_icons() -> None:
    """Update Maya selection mode icons in the toolbar.

    Forces Maya to refresh the selection mode icons to reflect
    the current mode.

    Example:
        >>> update_selection_mode_icons()
    """
    import pymel.all as pm

    try:
        pm.mel.updateSelectionModeIcons()
    except Exception as e:
        logger.debug(f"Could not update selection mode icons: {e}")


def set_component_selection_mode(mesh: str, component_type: str = "edge") -> None:
    """Set Maya to component selection mode for a specific mesh.

    Args:
        mesh: Mesh to enable component selection on.
        component_type: Type of component ('vertex', 'edge', 'face').

    Example:
        >>> set_component_selection_mode("head_geo", "edge")
        >>> # Now clicking on head_geo selects edges
    """
    import contextlib

    import pymel.all as pm

    with contextlib.suppress(Exception):
        pm.catch(lambda: pm.mel.doMenuComponentSelection(mesh, component_type))


def get_mesh_from_component(component: str) -> str:
    """Extract mesh name from a component name.

    Args:
        component: Component name (e.g., "pCube1.vtx[0]").

    Returns:
        str: Mesh name (e.g., "pCube1").

    Example:
        >>> mesh = get_mesh_from_component("head_geo.vtx[100]")
        >>> print(mesh)  # "head_geo"
    """
    if "." in component:
        return component.split(".")[0]
    return component


def get_component_indices(components: list) -> list:
    """Extract numeric indices from component names.

    Args:
        components: List of component names.

    Returns:
        list: List of integer indices.

    Example:
        >>> indices = get_component_indices(["pCube1.vtx[0]", "pCube1.vtx[5]"])
        >>> print(indices)  # [0, 5]
    """
    import re

    indices = []
    for comp in components:
        match = re.search(r"\[(\d+)\]", comp)
        if match:
            indices.append(int(match.group(1)))

    return indices


# Legacy function name aliases for backward compatibility
ConvertSelectionToVertices = convert_selection_to_vertices  # noqa: N816
ConvertSelectionToContainedEdges = convert_selection_to_contained_edges  # noqa: N816
GrowPolygonSelectionRegion = grow_polygon_selection  # noqa: N816
getVerticesExcludingJoints = get_vertices_excluding_joints  # noqa: N816
getGeometryWithNamespaceRemoval = get_geometry_with_namespace_removal  # noqa: N816
removeNamespaceFromObject = remove_namespace_from_object  # noqa: N816
storeEdgeSelection = store_edge_selection  # noqa: N816
storeVertexSelection = store_vertex_selection  # noqa: N816
