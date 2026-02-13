"""Skin cluster I/O operations for facial rigging.

This module provides functions for exporting and importing skin cluster
weights using Maya's OpenMaya API for efficient data transfer. It supports
both single-object and batch operations with pickle serialization.

The module uses OpenMaya 1.0 API for skin cluster manipulation which
provides significantly better performance than maya.cmds for large meshes.

Example:
    Export skin weights::

        from mayaLib.rigLib.face.io import skin_io
        skin_io.export_skin("/path/to/weights.data", [mesh])

    Import skin weights::

        skin_io.import_skin("/path/to/weights.data")
"""

import contextlib
import json
import logging
import os

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)

# Constants are imported at function level to avoid Maya imports at module load
# FILE_EXT = ".data"
# PACK_EXT = ".list"

# Python 2/3 compatibility for pickle
try:
    import cPickle as pickle_module  # noqa: N813 - Python 2/3 compatibility
except (ImportError, ModuleNotFoundError):
    import _pickle as pickle_module  # noqa: N812 - Python 2/3 compatibility

# Try to import basestring for Python 2/3 compatibility
with contextlib.suppress(NameError):
    # In Python 2, basestring exists
    basestring  # noqa: B018, F821 - checking if basestring exists

# Define basestring for Python 3 if not imported
try:
    basestring  # noqa: B018, F821 - checking if basestring exists
except NameError:
    basestring = str  # noqa: A001 - Python 2/3 compatibility


def _get_constants():
    """Get file extension constants from the constants module.

    Returns:
        tuple: (file_ext, pack_ext) file extension strings.
    """
    try:
        from mayaLib.rigLib.face.constants import FILE_EXT, PACK_EXT

        file_ext = FILE_EXT
        pack_ext = PACK_EXT
    except ImportError:
        # Fallback if constants module not available
        file_ext = ".data"
        pack_ext = ".list"
    return file_ext, pack_ext


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


def get_geometry_components(skin_cls):
    """Get the geometry components affected by a skin cluster.

    Uses OpenMaya API to efficiently retrieve the DAG path and
    component list for the deformer set members.

    Args:
        skin_cls: PyMEL skin cluster node.

    Returns:
        tuple: (dag_path, components) where dag_path is an MDagPath
            and components is an MObject containing the affected vertices.
    """
    import maya.OpenMaya as OpenMaya

    fn_set = OpenMaya.MFnSet(skin_cls.__apimfn__().deformerSet())
    members = OpenMaya.MSelectionList()
    fn_set.getMembers(members, False)
    dag_path = OpenMaya.MDagPath()
    components = OpenMaya.MObject()
    members.getDagPath(0, dag_path, components)
    return (dag_path, components)


def get_current_weights(skin_cls, dag_path, components):
    """Get the current skin weights from a skin cluster.

    Uses OpenMaya API to efficiently retrieve weight values.

    Args:
        skin_cls: PyMEL skin cluster node.
        dag_path: MDagPath to the skinned geometry.
        components: MObject containing the affected vertices.

    Returns:
        MDoubleArray: Array of weight values.
    """
    import maya.OpenMaya as OpenMaya

    weights = OpenMaya.MDoubleArray()
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    p_uint = util.asUintPtr()
    skin_cls.__apimfn__().getWeights(dag_path, components, weights, p_uint)
    return weights


def collect_influence_weights(skin_cls, dag_path, components, list_dic):
    """Collect influence weights from a skin cluster into a dictionary.

    Iterates through all influences and stores their weights indexed
    by influence name (without namespace).

    Args:
        skin_cls: PyMEL skin cluster node.
        dag_path: MDagPath to the skinned geometry.
        components: MObject containing the affected vertices.
        list_dic: Dictionary to store the collected weights.
            Will have 'weights' key populated with {influence_name: [weights]}.
    """
    import maya.OpenMaya as OpenMaya
    import pymel.all as pm

    weights = get_current_weights(skin_cls, dag_path, components)
    influence_paths = OpenMaya.MDagPathArray()
    num_influences = skin_cls.__apimfn__().influenceObjects(influence_paths)
    num_components_per_influence = int(weights.length() / num_influences)

    for ii in range(influence_paths.length()):
        influence_name = influence_paths[ii].partialPathName()
        influence_without_ns = pm.PyNode(influence_name).stripNamespace()
        inf_w = [weights[(jj * num_influences + ii)] for jj in range(num_components_per_influence)]
        list_dic["weights"][influence_without_ns] = inf_w


def collect_blend_weights(skin_cls, dag_path, components, list_dic):
    """Collect dual quaternion blend weights from a skin cluster.

    Args:
        skin_cls: PyMEL skin cluster node.
        dag_path: MDagPath to the skinned geometry.
        components: MObject containing the affected vertices.
        list_dic: Dictionary to store the collected blend weights.
            Will have 'blendWeights' key populated with list of values.
    """
    import maya.OpenMaya as OpenMaya

    weights = OpenMaya.MDoubleArray()
    skin_cls.__apimfn__().getBlendWeights(dag_path, components, weights)
    list_dic["blendWeights"] = [weights[i] for i in range(weights.length())]


def collect_skin_data(skin_cls, list_dic):
    """Collect all skin cluster data into a dictionary.

    Gathers influence weights, blend weights, skinning method,
    and normalization settings.

    Args:
        skin_cls: PyMEL skin cluster node.
        list_dic: Dictionary to store the collected data.
    """
    import maya.cmds as cmds

    dag_path, components = get_geometry_components(skin_cls)
    collect_influence_weights(skin_cls, dag_path, components, list_dic)
    collect_blend_weights(skin_cls, dag_path, components, list_dic)

    for attr in ["skinningMethod", "normalizeWeights"]:
        list_dic[attr] = cmds.getAttr(f"{skin_cls}.{attr}")

    list_dic["skinClsName"] = skin_cls.name()


def set_influence_weights(skin_cls, dag_path, components, list_dic):
    """Apply influence weights to a skin cluster from dictionary data.

    Maps imported influence names to scene influences and sets
    the weight values using OpenMaya API.

    Args:
        skin_cls: PyMEL skin cluster node.
        dag_path: MDagPath to the skinned geometry.
        components: MObject containing the affected vertices.
        list_dic: Dictionary containing 'weights' data with
            {influence_name: [weight_values]} format.
    """
    import maya.OpenMaya as OpenMaya
    import pymel.all as pm

    unused_imports = []
    weights = get_current_weights(skin_cls, dag_path, components)
    influence_paths = OpenMaya.MDagPathArray()
    num_influences = skin_cls.__apimfn__().influenceObjects(influence_paths)
    num_components_per_influence = int(weights.length() / num_influences)

    for imported_influence, imported_weights in list_dic["weights"].items():
        for ii in range(influence_paths.length()):
            influence_name = influence_paths[ii].partialPathName()
            ns_stripped = pm.PyNode(influence_name).stripNamespace()
            influence_without_ns = ns_stripped
            if influence_without_ns == imported_influence:
                for jj in range(num_components_per_influence):
                    weights.set(imported_weights[jj], jj * num_influences + ii)
                break
        else:
            unused_imports.append(imported_influence)

    if unused_imports:
        logger.warning("Unused influences in import data: %s", unused_imports)

    influence_indices = OpenMaya.MIntArray(num_influences)
    for ii in range(num_influences):
        influence_indices.set(ii, ii)

    skin_cls.__apimfn__().setWeights(dag_path, components, influence_indices, weights, False)


def set_blend_weights(skin_cls, dag_path, components, list_dic):
    """Apply dual quaternion blend weights to a skin cluster.

    Args:
        skin_cls: PyMEL skin cluster node.
        dag_path: MDagPath to the skinned geometry.
        components: MObject containing the affected vertices.
        list_dic: Dictionary containing 'blendWeights' data.
    """
    import maya.OpenMaya as OpenMaya

    blend_weights = OpenMaya.MDoubleArray(len(list_dic["blendWeights"]))
    for i, w in enumerate(list_dic["blendWeights"]):
        blend_weights.set(w, i)

    skin_cls.__apimfn__().setBlendWeights(dag_path, components, blend_weights)


def apply_skin_data(skin_cls, list_dic):
    """Apply all skin data from a dictionary to a skin cluster.

    Sets influence weights, blend weights, skinning method,
    and normalization settings.

    Args:
        skin_cls: PyMEL skin cluster node.
        list_dic: Dictionary containing the complete skin data.
    """
    import maya.cmds as cmds

    dag_path, components = get_geometry_components(skin_cls)
    set_influence_weights(skin_cls, dag_path, components, list_dic)
    set_blend_weights(skin_cls, dag_path, components, list_dic)

    for attr in ["skinningMethod", "normalizeWeights"]:
        cmds.setAttr(f"{skin_cls}.{attr}", list_dic[attr])


def export_skin(file_path=None, objs=None, *args):
    """Export skin cluster weights for one or more objects.

    Serializes skin cluster data including influence weights,
    blend weights, and cluster settings to a pickle file.

    Args:
        file_path: Output file path. If None, opens a file dialog.
        objs: List of mesh objects to export. If None, uses selection.
        *args: Additional arguments (ignored, for Maya callback compatibility).

    Returns:
        bool: True if export was successful, False otherwise.

    Example:
        >>> export_skin("/path/to/weights.data", [pm.PyNode("body_geo")])
        True
    """
    import pymel.all as pm

    file_ext, _ = _get_constants()

    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning("Please Select One or more objects")
            return False

    pack_dic = {"objs": [], "objDDic": [], "bypassObj": []}

    if not file_path:
        start_dir = pm.workspace(q=True, rootDirectory=True)
        file_path = pm.fileDialog2(
            dialogStyle=2,
            fileMode=0,
            startingDirectory=start_dir,
            fileFilter=f"data data (*{file_ext})",
        )
        if file_path:
            file_path = file_path[0]

    if not file_path:
        return False

    if not file_path.endswith(file_ext):
        file_path += file_ext

    for obj in objs:
        skin_cls = get_skin_cluster(obj)
        if not skin_cls:
            pm.displayWarning(f"{obj.name()}: Skipped because don't have Skin Cluster")
        else:
            list_dic = {
                "weights": {},
                "blendWeights": [],
                "skinClsName": "",
                "objName": "",
                "nameSpace": "",
            }
            list_dic["objName"] = obj.name()
            list_dic["nameSpace"] = obj.namespace()
            collect_skin_data(skin_cls, list_dic)
            pack_dic["objs"].append(obj.name())
            pack_dic["objDDic"].append(list_dic)
            pm.displayInfo(
                f"{skin_cls.name()} ({len(list_dic['weights'].keys())} influences, "
                f"{len(list_dic['blendWeights'])} points) {obj.name()}"
            )

    if pack_dic["objs"]:
        with open(file_path, "wb") as fh:
            pickle_module.dump(pack_dic, fh, pickle_module.HIGHEST_PROTOCOL)
        logger.info("Skin data exported to: %s", file_path)
        return True

    return False


def export_skin_pack(pack_path=None, objs=None, *args):
    """Export skin weights for multiple objects as a batch pack.

    Creates a pack file (.list) containing references to individual
    skin data files for each object.

    Args:
        pack_path: Output pack file path. If None, opens a file dialog.
        objs: List of mesh objects to export. If None, uses selection.
        *args: Additional arguments (ignored, for Maya callback compatibility).

    Returns:
        bool: True if export was successful, False otherwise.
    """
    import pymel.all as pm

    file_ext, pack_ext = _get_constants()

    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning("Please Select Some Objects")
            return False

    pack_dic = {"objectsList": [], "rootPath": []}

    if not pack_path:
        start_dir = pm.workspace(q=True, rootDirectory=True)
        pack_path = pm.fileDialog2(
            dialogStyle=2,
            fileMode=0,
            startingDirectory=start_dir,
            fileFilter=f"data list (*{pack_ext})",
        )

    if not pack_path:
        return False

    if not isinstance(pack_path, basestring):
        pack_path = pack_path[0]

    if not pack_path.endswith(pack_ext):
        pack_path += pack_ext

    pack_dic["Path"], pack_name = os.path.split(pack_path)
    _ = pack_name  # Unused but needed from os.path.split

    for obj in objs:
        file_name = obj.stripNamespace() + file_ext
        file_out_path = os.path.join(pack_dic["Path"], file_name)
        if export_skin(file_out_path, [obj]):
            pack_dic["objectsList"].append(file_name)
            pm.displayInfo(file_out_path)
        else:
            pm.displayWarning(f"{obj.name()}: Skipped because don't have Skin Cluster")

    if pack_dic["objectsList"]:
        data_string = json.dumps(pack_dic, indent=4, sort_keys=True)
        with open(pack_path, "w", encoding="utf-8") as f:
            f.write(data_string + "\n")
        pm.displayInfo(f"Skin Data exported: {pack_path}")
        return True
    else:
        pm.displayWarning(
            "Any of the selected objects have Skin Cluster. Skin Pack export aborted."
        )
        return False


def import_skin(file_path=None, *args):
    """Import skin cluster weights from a data file.

    Loads skin data and applies it to matching objects in the scene.
    Creates skin clusters if they don't exist.

    Args:
        file_path: Path to the skin data file. If None, opens a file dialog.
        *args: Additional arguments (ignored, for Maya callback compatibility).

    Returns:
        bool: True if import was successful, False otherwise.
    """
    import pymel.all as pm

    file_ext, _ = _get_constants()

    if not file_path:
        start_dir = pm.workspace(q=True, rootDirectory=True)
        file_path = pm.fileDialog2(
            dialogStyle=2,
            fileMode=1,
            startingDirectory=start_dir,
            fileFilter=f"data data (*{file_ext})",
        )

    if not file_path:
        return False

    if not isinstance(file_path, basestring):
        file_path = file_path[0]

    with open(file_path, "rb") as fh:
        list_pack = pickle_module.load(fh)

    for obj_data in list_pack["objDDic"]:
        obj_name = obj_data["objName"]
        try:
            skin_cluster = None
            obj_node = pm.PyNode(obj_name)

            # Verify vertex count matches
            try:
                mesh_vertices = pm.polyEvaluate(obj_node, vertex=True)
                imported_vertices = len(obj_data["blendWeights"])
                if mesh_vertices != imported_vertices:
                    pm.displayWarning(
                        f"Vertex counts do not match. {mesh_vertices} != {imported_vertices}"
                    )
                    continue
            except Exception:
                pass

            # Get or create skin cluster
            skin_cluster = get_skin_cluster(obj_node)
            if not skin_cluster:
                try:
                    joints = list(obj_data["weights"].keys())
                    skin_cluster = pm.skinCluster(
                        joints, obj_node, tsb=True, nw=2, n=obj_data["skinClsName"]
                    )
                except Exception:
                    not_found = list(obj_data["weights"].keys())
                    scene_joints = {pm.PyNode(x).name() for x in pm.ls(type="joint")}
                    for j in list(not_found):
                        if j in scene_joints:
                            not_found.remove(j)

                    pm.displayWarning(
                        f"Object: {obj_name} Skipped. Can't find deformer for joints: {not_found}"
                    )
                    continue

            if skin_cluster:
                apply_skin_data(skin_cluster, obj_data)
                logger.info("%s skin data loaded.", obj_name)
                print(f"{obj_name} skin data loaded.")

        except Exception:
            pm.displayWarning(f"Object: {obj_name} Skipped. Cannot be found in the scene")

    return True


def import_skin_pack(file_path=None, *args):
    """Import all skin weights from a batch pack file.

    Reads a pack file (.list) and imports each referenced skin data file.

    Args:
        file_path: Path to the pack file. If None, opens a file dialog.
        *args: Additional arguments (ignored, for Maya callback compatibility).

    Returns:
        bool: True if import was successful, False otherwise.
    """
    import maya.cmds as cmds

    _, pack_ext = _get_constants()

    if not file_path:
        start_dir = cmds.workspace(q=True, rootDirectory=True)
        file_path = cmds.fileDialog2(
            dialogStyle=2,
            fileMode=1,
            startingDirectory=start_dir,
            fileFilter=f"data list (*{pack_ext})",
        )

    if not file_path:
        return False

    if not isinstance(file_path, basestring):
        file_path = file_path[0]

    with open(file_path, encoding="utf-8") as f:
        pack_dic = json.load(f)

    pack_dir = os.path.split(file_path)[0]
    for p_file in pack_dic["objectsList"]:
        data_file_path = os.path.join(pack_dir, p_file)
        import_skin(data_file_path, True)

    return True


def export_selection():
    """Export skin weights for the current selection.

    Convenience function that checks for a selection and calls export_skin_pack.
    """
    import pymel.all as pm

    new_sel = pm.selected()
    if len(new_sel) == 0:
        pm.displayWarning("Please Select Some Objects")
    else:
        export_skin_pack()


# Legacy function aliases for backward compatibility
# These maintain the original camelCase naming from facial3.py
getSkinCluster = get_skin_cluster  # noqa: N816 - backward compat
getGeometryComponents = get_geometry_components  # noqa: N816 - backward compat
getCurrentWeights = get_current_weights  # noqa: N816 - backward compat
collectInfluenceWeights = collect_influence_weights  # noqa: N816 - backward compat
collectBlendWeights = collect_blend_weights  # noqa: N816 - backward compat
collectlist = collect_skin_data  # noqa: N816 - backward compat
setInfluenceWeights = set_influence_weights  # noqa: N816 - backward compat
setBlendWeights = set_blend_weights  # noqa: N816 - backward compat
setlist = apply_skin_data  # noqa: N816 - backward compat
exportSkin = export_skin  # noqa: N816 - backward compat
prSkinExp = export_skin_pack  # noqa: N816 - backward compat
prImpSkin = import_skin  # noqa: N816 - backward compat
prImpSkinAll = import_skin_pack  # noqa: N816 - backward compat
prExportSkin = export_selection  # noqa: N816 - backward compat


# Module-level exports
__all__ = [
    # Primary API (snake_case)
    "get_skin_cluster",
    "get_geometry_components",
    "get_current_weights",
    "collect_influence_weights",
    "collect_blend_weights",
    "collect_skin_data",
    "set_influence_weights",
    "set_blend_weights",
    "apply_skin_data",
    "export_skin",
    "export_skin_pack",
    "import_skin",
    "import_skin_pack",
    "export_selection",
    # Legacy API (camelCase) for backward compatibility
    "getSkinCluster",
    "getGeometryComponents",
    "getCurrentWeights",
    "collectInfluenceWeights",
    "collectBlendWeights",
    "collectlist",
    "setInfluenceWeights",
    "setBlendWeights",
    "setlist",
    "exportSkin",
    "prSkinExp",
    "prImpSkin",
    "prImpSkinAll",
    "prExportSkin",
]
