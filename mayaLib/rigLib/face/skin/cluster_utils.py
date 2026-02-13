"""Skin cluster utility functions for facial rigging.

This module provides general-purpose utilities for working with Maya skin
clusters in facial rigs. It includes functions for querying skin cluster
properties, managing influences, and performing common skin cluster operations.

These utilities complement the copy.py module (for weight transfer) and
skin_io.py module (for file I/O) by providing general cluster manipulation
functions.

Example:
    Get the skin cluster from a mesh::

        from mayaLib.rigLib.face.skin import cluster_utils
        skin = cluster_utils.get_skin_cluster("face_geo")

    Find all skinned objects::

        skinned_objs = cluster_utils.get_all_skinned_objects()

    Add influences to skin cluster::

        cluster_utils.add_influences(skin_cluster, ["jaw_jnt", "lip_jnt"])
"""

import contextlib
import logging

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)

# Try to import basestring for Python 2/3 compatibility
with contextlib.suppress(NameError):
    # In Python 2, basestring exists
    basestring  # noqa: B018, F821 - checking if basestring exists

# Define basestring for Python 3 if not imported
try:
    basestring  # noqa: B018, F821 - checking if basestring exists
except NameError:
    basestring = str  # noqa: A001 - Python 2/3 compatibility


def get_skin_cluster(obj):
    """Get the skin cluster deformer from a mesh object.

    Searches the deformation history of the given object to find
    its associated skin cluster node.

    Args:
        obj: Maya mesh or transform node. Can be a string name or
            PyMEL node object.

    Returns:
        pymel.core.nodetypes.SkinCluster: The skin cluster node if found,
            None otherwise.

    Example:
        >>> skin = get_skin_cluster("body_geo")
        >>> if skin:
        ...     print(f"Found skin cluster: {skin.name()}")
    """
    import pymel.all as pm

    skin_cluster = None

    if isinstance(obj, basestring):
        obj = pm.PyNode(obj)

    try:
        shape = obj.getShape()
        if shape is None:
            return None

        if pm.nodeType(shape) in ("mesh", "nurbsSurface", "nurbsCurve"):
            for shape in obj.getShapes():
                try:
                    for skin_c in pm.listHistory(shape, type="skinCluster"):
                        try:
                            if skin_c.getGeometry()[0] == shape:
                                skin_cluster = skin_c
                        except Exception:
                            pass
                except Exception:
                    pass

    except Exception:
        pm.displayWarning(f"{obj.name()}: is not supported.")

    return skin_cluster


def find_related_skin_cluster(geo):
    """Find the related skinCluster for the given geometry using MEL.

    Uses Maya's built-in findRelatedSkinCluster MEL command for
    reliable skin cluster detection.

    Args:
        geo: The geometry name (string) or PyNode object.

    Returns:
        pymel.core.nodetypes.SkinCluster: The found skinCluster node,
            or None if no skinCluster is found.
    """
    import maya.mel as mel
    import pymel.all as pm

    if not isinstance(geo, basestring):
        geo = str(geo)

    skincluster = mel.eval(f"findRelatedSkinCluster {geo}")
    if skincluster == "" or len(pm.ls(skincluster, type="skinCluster")) == 0:
        skincluster = pm.ls(pm.listHistory(geo), type="skinCluster")
        if len(skincluster) == 0:
            return None
        return skincluster[0]

    return pm.ls(skincluster)[0]


def has_skin_cluster(obj):
    """Check if an object has a skin cluster.

    Args:
        obj: Maya mesh or transform node.

    Returns:
        bool: True if object has a skin cluster, False otherwise.
    """
    return get_skin_cluster(obj) is not None


def get_all_skinned_objects():
    """Get all objects in the scene that have skin clusters.

    Returns:
        list: List of PyNode transform objects that have skin clusters.
    """
    import pymel.all as pm

    object_list = []
    skin_cluster_list = pm.ls(type="skinCluster")

    for skin_cluster in skin_cluster_list:
        obj_shapes = pm.skinCluster(skin_cluster, q=True, geometry=True)
        if obj_shapes:
            for shape in obj_shapes:
                transform = pm.listRelatives(shape, parent=True)
                if transform:
                    object_list.append(transform[0])

    return object_list


def select_skinned_objects():
    """Select all objects in the scene that have skin clusters.

    Returns:
        list: List of PyNode transform objects that were selected.
    """
    import pymel.all as pm

    object_list = get_all_skinned_objects()
    if object_list:
        pm.select(object_list)
    else:
        pm.select(clear=True)

    return object_list


def get_influences(skin_cluster):
    """Get all influence objects from a skin cluster.

    Args:
        skin_cluster: The skin cluster node (PyNode or string name).

    Returns:
        list: List of PyNode influence objects (joints/transforms).
    """
    import pymel.all as pm

    if isinstance(skin_cluster, basestring):
        skin_cluster = pm.PyNode(skin_cluster)

    return pm.skinCluster(skin_cluster, query=True, influence=True) or []


def get_influence_count(skin_cluster):
    """Get the number of influences in a skin cluster.

    Args:
        skin_cluster: The skin cluster node.

    Returns:
        int: Number of influences.
    """
    return len(get_influences(skin_cluster))


def get_max_influences(skin_cluster):
    """Get the maximum influences per vertex setting.

    Args:
        skin_cluster: The skin cluster node.

    Returns:
        int: Maximum number of influences per vertex.
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    return cmds.getAttr(f"{skin_cluster}.maxInfluences")


def set_max_influences(skin_cluster, max_inf=4):
    """Set the maximum influences per vertex.

    Args:
        skin_cluster: The skin cluster node.
        max_inf: Maximum number of influences per vertex (default 4).
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    cmds.setAttr(f"{skin_cluster}.maxInfluences", max_inf)
    cmds.setAttr(f"{skin_cluster}.maintainMaxInfluences", 1)


def get_skinning_method(skin_cluster):
    """Get the skinning method (linear, dual quaternion, weight blended).

    Args:
        skin_cluster: The skin cluster node.

    Returns:
        int: Skinning method value (0=linear, 1=dual quat, 2=blended).
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    return cmds.getAttr(f"{skin_cluster}.skinningMethod")


def set_skinning_method(skin_cluster, method=0):
    """Set the skinning method.

    Args:
        skin_cluster: The skin cluster node.
        method: Skinning method (0=linear, 1=dual quaternion, 2=blended).
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    cmds.setAttr(f"{skin_cluster}.skinningMethod", method)


def get_normalize_weights(skin_cluster):
    """Get the normalize weights setting.

    Args:
        skin_cluster: The skin cluster node.

    Returns:
        int: Normalize weights value (0=none, 1=interactive, 2=post).
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    return cmds.getAttr(f"{skin_cluster}.normalizeWeights")


def set_normalize_weights(skin_cluster, normalize=1):
    """Set the normalize weights mode.

    Args:
        skin_cluster: The skin cluster node.
        normalize: Normalize mode (0=none, 1=interactive, 2=post).
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    cmds.setAttr(f"{skin_cluster}.normalizeWeights", normalize)


def add_influences(skin_cluster, joints, lock_weights=False, weight=0.0):
    """Add influences to an existing skin cluster.

    Args:
        skin_cluster: The skin cluster node.
        joints: Single joint or list of joints to add as influences.
        lock_weights: Whether to lock the weights of new influences.
        weight: Default weight for new influences.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if isinstance(skin_cluster, basestring):
        skin_cluster = pm.PyNode(skin_cluster)

    if isinstance(joints, basestring) or not isinstance(joints, (list, tuple)):
        joints = [joints]

    existing_influences = get_influences(skin_cluster)
    existing_names = [str(inf) for inf in existing_influences]

    for joint in joints:
        joint_name = str(joint)
        if joint_name not in existing_names:
            cmds.skinCluster(
                str(skin_cluster),
                edit=True,
                addInfluence=joint_name,
                lockWeights=lock_weights,
                weight=weight,
            )
            logger.info("Added influence: %s to %s", joint_name, skin_cluster)


def remove_influences(skin_cluster, joints):
    """Remove influences from a skin cluster.

    Args:
        skin_cluster: The skin cluster node.
        joints: Single joint or list of joints to remove.

    Note:
        Removes unused influences only. Active influences with
        weights assigned must have weights removed first.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if isinstance(skin_cluster, basestring):
        skin_cluster = pm.PyNode(skin_cluster)

    if isinstance(joints, basestring) or not isinstance(joints, (list, tuple)):
        joints = [joints]

    for joint in joints:
        try:
            cmds.skinCluster(
                str(skin_cluster),
                edit=True,
                removeInfluence=str(joint),
            )
            logger.info("Removed influence: %s from %s", joint, skin_cluster)
        except Exception as e:
            logger.warning("Could not remove influence %s: %s", joint, e)


def lock_influence_weights(skin_cluster, joints, lock=True):
    """Lock or unlock influence weights.

    Args:
        skin_cluster: The skin cluster node.
        joints: Single joint or list of joints.
        lock: True to lock, False to unlock.
    """
    import maya.cmds as cmds

    if isinstance(joints, basestring) or not isinstance(joints, (list, tuple)):
        joints = [joints]

    skin_name = str(skin_cluster)

    for joint in joints:
        with contextlib.suppress(Exception):
            cmds.skinCluster(
                skin_name,
                edit=True,
                influence=str(joint),
                lockWeights=lock,
            )


def get_weighted_influences(skin_cluster, threshold=0.001):
    """Get influences that have weights above threshold.

    Args:
        skin_cluster: The skin cluster node.
        threshold: Minimum weight to consider (default 0.001).

    Returns:
        list: List of influence names that have weights above threshold.
    """
    import maya.cmds as cmds

    if not isinstance(skin_cluster, basestring):
        skin_cluster = str(skin_cluster)

    influences = get_influences(skin_cluster)
    weighted = []

    for inf in influences:
        # Check if this influence has any weights above threshold
        try:
            # Get the weight list attribute
            weights = cmds.skinPercent(skin_cluster, str(inf), query=True, value=True)
            if weights and any(w > threshold for w in weights):
                weighted.append(inf)
        except Exception:
            # If we can't query weights, assume it's weighted
            weighted.append(inf)

    return weighted


def prune_weights(skin_cluster, threshold=0.01):
    """Prune skin weights below threshold.

    Sets all weights below the threshold to zero and normalizes.

    Args:
        skin_cluster: The skin cluster node.
        threshold: Minimum weight to keep (default 0.01).
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if isinstance(skin_cluster, basestring):
        skin_cluster = pm.PyNode(skin_cluster)

    geometry = pm.skinCluster(skin_cluster, query=True, geometry=True)
    if geometry:
        cmds.skinPercent(str(skin_cluster), str(geometry[0]), pruneWeights=threshold)


def smooth_weights(vertices, iterations=1):
    """Smooth skin weights on selected vertices.

    Uses Maya's paint weights smooth brush to smooth weights.

    Args:
        vertices: List of vertices to smooth.
        iterations: Number of smoothing iterations.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    pm.select(vertices)
    for _ in range(iterations):
        cmds.WeightHammerVerts()


def unbind_skin(obj, history=True):
    """Unbind skin from an object.

    Args:
        obj: The skinned object.
        history: Whether to keep deformation history (default True).

    Returns:
        bool: True if unbind was successful.
    """
    import pymel.all as pm

    if isinstance(obj, basestring):
        obj = pm.PyNode(obj)

    skin_cluster = get_skin_cluster(obj)
    if skin_cluster:
        pm.skinCluster(skin_cluster, edit=True, unbind=True)
        if not history:
            pm.delete(obj, constructionHistory=True)
        logger.info("Unbound skin from: %s", obj)
        return True

    return False


def bind_skin(obj, joints, max_influences=4, normalize_weights=1, skinning_method=0):
    """Bind skin to an object.

    Creates a new skin cluster binding the object to the specified joints.

    Args:
        obj: The object to bind.
        joints: List of joints to use as influences.
        max_influences: Maximum influences per vertex (default 4).
        normalize_weights: Normalize weights mode (default 1=interactive).
        skinning_method: Skinning method (default 0=linear).

    Returns:
        pymel.core.nodetypes.SkinCluster: The created skin cluster, or None.
    """
    import pymel.all as pm

    if isinstance(obj, basestring):
        obj = pm.PyNode(obj)

    if isinstance(joints, basestring):
        joints = [pm.PyNode(joints)]
    elif not all(hasattr(j, "__class__") for j in joints):
        joints = [pm.PyNode(j) if isinstance(j, basestring) else j for j in joints]

    try:
        skin_cluster = pm.skinCluster(
            joints,
            obj,
            toSelectedBones=True,
            maximumInfluences=max_influences,
            normalizeWeights=normalize_weights,
            skinMethod=skinning_method,
        )
        logger.info("Created skin cluster for: %s", obj)
        return skin_cluster
    except Exception as e:
        logger.error("Failed to bind skin to %s: %s", obj, e)
        return None


def rebind_skin(obj, joints=None, preserve_weights=True):
    """Rebind skin, optionally preserving weights.

    Unbinds and rebinds the skin cluster, optionally preserving
    the original weights.

    Args:
        obj: The skinned object.
        joints: New joints list (uses original if None).
        preserve_weights: Whether to preserve weights (default True).

    Returns:
        pymel.core.nodetypes.SkinCluster: The new skin cluster, or None.
    """
    import pymel.all as pm

    if isinstance(obj, basestring):
        obj = pm.PyNode(obj)

    old_skin = get_skin_cluster(obj)
    if not old_skin:
        logger.warning("No existing skin cluster on %s", obj)
        return None

    # Get original settings
    old_joints = joints or get_influences(old_skin)
    max_inf = get_max_influences(old_skin)
    norm_weights = get_normalize_weights(old_skin)
    skin_method = get_skinning_method(old_skin)

    # Store weights if preserving
    weight_data = None
    if preserve_weights:
        try:
            import tempfile

            # Import the io module to export weights
            from mayaLib.rigLib.face.io import skin_io

            temp_file = tempfile.mktemp(suffix=".data")
            skin_io.export_skin(temp_file, [obj])
            weight_data = temp_file
        except Exception:
            logger.warning("Could not preserve weights")

    # Unbind
    unbind_skin(obj, history=False)

    # Rebind
    new_skin = bind_skin(obj, old_joints, max_inf, norm_weights, skin_method)

    # Restore weights
    if preserve_weights and weight_data and new_skin:
        try:
            from mayaLib.rigLib.face.io import skin_io

            skin_io.import_skin(weight_data)
            import os

            os.remove(weight_data)
        except Exception:
            logger.warning("Could not restore weights")

    return new_skin


def reset_bind_pose(joints=None):
    """Reset bind pose for joints.

    Args:
        joints: List of joints to reset. If None, uses all joints
            in the scene connected to skin clusters.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if joints is None:
        # Get all joints connected to skin clusters
        joints = []
        for skin in pm.ls(type="skinCluster"):
            joints.extend(get_influences(skin))
        joints = list(set(joints))

    if joints:
        pm.select(joints)
        cmds.dagPose(reset=True, n="bindPose", bindPose=True)


def disable_inherits_transform(objects=None):
    """Disable inheritsTransform on skinned objects.

    Useful when transferring skin weights between objects.

    Args:
        objects: List of objects. If None, uses all skinned objects.
    """
    if objects is None:
        objects = get_all_skinned_objects()

    for obj in objects:
        with contextlib.suppress(Exception):
            obj.inheritsTransform.set(0)


def get_vertex_weights(skin_cluster, vertex_index):
    """Get the skin weights for a specific vertex.

    Args:
        skin_cluster: The skin cluster node.
        vertex_index: The vertex index to query.

    Returns:
        dict: Dictionary mapping influence names to weight values.
    """
    import maya.cmds as cmds

    skin_name = str(skin_cluster)
    geometry = cmds.skinCluster(skin_name, query=True, geometry=True)

    if not geometry:
        return {}

    vertex = f"{geometry[0]}.vtx[{vertex_index}]"
    influences = get_influences(skin_cluster)

    weights = {}
    for inf in influences:
        weight = cmds.skinPercent(skin_name, vertex, transform=str(inf), query=True)
        if weight > 0:
            weights[str(inf)] = weight

    return weights


def set_vertex_weights(skin_cluster, vertex_index, weights):
    """Set skin weights for a specific vertex.

    Args:
        skin_cluster: The skin cluster node.
        vertex_index: The vertex index to modify.
        weights: Dictionary mapping influence names to weight values.
    """
    import maya.cmds as cmds

    skin_name = str(skin_cluster)
    geometry = cmds.skinCluster(skin_name, query=True, geometry=True)

    if not geometry:
        return

    vertex = f"{geometry[0]}.vtx[{vertex_index}]"

    # Build transform-value pairs
    transform_value = []
    for inf, weight in weights.items():
        transform_value.extend([inf, weight])

    if transform_value:
        cmds.skinPercent(skin_name, vertex, transformValue=transform_value)


# Legacy function aliases for backward compatibility
# These maintain the original camelCase naming from facial3.py
getSkinCluster = get_skin_cluster  # noqa: N816 - backward compat
findRelatedSkinCluster = find_related_skin_cluster  # noqa: N816 - backward compat
hasSkinCluster = has_skin_cluster  # noqa: N816 - backward compat
getAllSkinnedObjects = get_all_skinned_objects  # noqa: N816 - backward compat
selectSkinnedObjects = select_skinned_objects  # noqa: N816 - backward compat
getInfluences = get_influences  # noqa: N816 - backward compat
getInfluenceCount = get_influence_count  # noqa: N816 - backward compat
getMaxInfluences = get_max_influences  # noqa: N816 - backward compat
setMaxInfluences = set_max_influences  # noqa: N816 - backward compat
getSkinningMethod = get_skinning_method  # noqa: N816 - backward compat
setSkinningMethod = set_skinning_method  # noqa: N816 - backward compat
getNormalizeWeights = get_normalize_weights  # noqa: N816 - backward compat
setNormalizeWeights = set_normalize_weights  # noqa: N816 - backward compat
addInfluences = add_influences  # noqa: N816 - backward compat
removeInfluences = remove_influences  # noqa: N816 - backward compat
lockInfluenceWeights = lock_influence_weights  # noqa: N816 - backward compat
getWeightedInfluences = get_weighted_influences  # noqa: N816 - backward compat
pruneWeights = prune_weights  # noqa: N816 - backward compat
smoothWeights = smooth_weights  # noqa: N816 - backward compat
unbindSkin = unbind_skin  # noqa: N816 - backward compat
bindSkin = bind_skin  # noqa: N816 - backward compat
rebindSkin = rebind_skin  # noqa: N816 - backward compat
resetBindPose = reset_bind_pose  # noqa: N816 - backward compat
disableInheritsTransform = disable_inherits_transform  # noqa: N816 - backward compat
getVertexWeights = get_vertex_weights  # noqa: N816 - backward compat
setVertexWeights = set_vertex_weights  # noqa: N816 - backward compat

# Module-level exports
__all__ = [
    # Primary API (snake_case)
    "get_skin_cluster",
    "find_related_skin_cluster",
    "has_skin_cluster",
    "get_all_skinned_objects",
    "select_skinned_objects",
    "get_influences",
    "get_influence_count",
    "get_max_influences",
    "set_max_influences",
    "get_skinning_method",
    "set_skinning_method",
    "get_normalize_weights",
    "set_normalize_weights",
    "add_influences",
    "remove_influences",
    "lock_influence_weights",
    "get_weighted_influences",
    "prune_weights",
    "smooth_weights",
    "unbind_skin",
    "bind_skin",
    "rebind_skin",
    "reset_bind_pose",
    "disable_inherits_transform",
    "get_vertex_weights",
    "set_vertex_weights",
    # Legacy API (camelCase) for backward compatibility
    "getSkinCluster",
    "findRelatedSkinCluster",
    "hasSkinCluster",
    "getAllSkinnedObjects",
    "selectSkinnedObjects",
    "getInfluences",
    "getInfluenceCount",
    "getMaxInfluences",
    "setMaxInfluences",
    "getSkinningMethod",
    "setSkinningMethod",
    "getNormalizeWeights",
    "setNormalizeWeights",
    "addInfluences",
    "removeInfluences",
    "lockInfluenceWeights",
    "getWeightedInfluences",
    "pruneWeights",
    "smoothWeights",
    "unbindSkin",
    "bindSkin",
    "rebindSkin",
    "resetBindPose",
    "disableInheritsTransform",
    "getVertexWeights",
    "setVertexWeights",
]
