"""Skin copy and transfer operations for facial rigging.

This module provides functions for copying and transferring skin cluster
weights between meshes at runtime. It handles vertex-based weight copying,
blendshape connections, and deformation transfer workflows.

The functions support both component-based transfers (vertex-to-vertex) and
full mesh transfers with influence matching.

Example:
    Copy skin weights from source to target::

        from mayaLib.rigLib.face.skin import copy
        copy.skin_copy(source_mesh, target_mesh)

    Transfer weights between vertex selections::

        copy.source_define()  # Select source vertices
        copy.destination_define()  # Select target vertices
        copy.copy_skin_global()  # Transfer based on proximity
"""

import contextlib
import logging

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)

# Global storage for vertex selections used in copy operations
_source_vertex_list = []
_destination_vertex_list = []

# Storage for facial influence joints used in set-based transfers
_facial_influence_joints = []

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


def skin_copy(source_mesh=None, target_mesh=None, *args):
    """Copy skin weights from source mesh to target meshes.

    Creates a new skin cluster on each target mesh using the influences
    from the source mesh, then copies the weights using Maya's copySkinWeights
    command with one-to-one influence association.

    Args:
        source_mesh: Source mesh with skin cluster. If None, uses
            first selected object.
        target_mesh: Target mesh or list of target meshes. If None,
            uses remaining selected objects.
        *args: Additional arguments (ignored, for Maya callback compatibility).

    Returns:
        None. Displays warnings if source mesh has no skin cluster.

    Example:
        >>> skin_copy("body_source_geo", "body_target_geo")
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if not source_mesh or not target_mesh:
        if len(cmds.ls(sl=1)) >= 2:
            source_mesh = pm.ls(sl=1)[0]
            target_meshes = pm.ls(sl=1)[1:]
        else:
            pm.displayWarning(
                "Please select target mesh/meshes and source mesh with skinCluster."
            )
            return
    else:
        target_meshes = [target_mesh]
        if isinstance(source_mesh, basestring):
            source_mesh = pm.PyNode(source_mesh)

    for target in target_meshes:
        if isinstance(target, basestring):
            target = pm.PyNode(target)

        ss = get_skin_cluster(source_mesh)
        if ss:
            source_influences = pm.skinCluster(source_mesh, query=True, influence=True)
            skin_cluster = pm.skinCluster(
                source_influences,
                target,
                tsb=True,
                nw=1,
                n=target.name() + "_SkinCluster",
            )
            pm.copySkinWeights(
                ss=ss.stripNamespace(),
                ds=skin_cluster.name(),
                noMirror=True,
                ia="oneToOne",
                sm=True,
                nr=True,
            )
        else:
            pm.displayError(
                f"Source Mesh: {source_mesh.name()} doesn't have skinCluster"
            )


def source_define():
    """Define source vertices for component-based weight transfer.

    Converts the current selection to vertices and stores them as the
    source for subsequent copy_skin_global() operations.

    Note:
        Uses a global list that persists until copy_skin_global() is called.
    """
    import maya.cmds as cmds
    import maya.mel as mel

    global _source_vertex_list

    base = cmds.ls(sl=1)
    mel.eval("PolySelectConvert 3;")
    _source_destination_sel("source")
    logger.info("Source vertices defined: %d vertices", len(_source_vertex_list))
    cmds.select(base)


def destination_define():
    """Define destination vertices for component-based weight transfer.

    Converts the current selection to vertices and stores them as the
    destination for subsequent copy_skin_global() operations.

    Note:
        Uses a global list that persists until copy_skin_global() is called.
    """
    import maya.cmds as cmds
    import maya.mel as mel

    global _destination_vertex_list

    base = cmds.ls(sl=1)
    mel.eval("PolySelectConvert 3;")
    _source_destination_sel("destination")
    logger.info("Destination vertices defined: %d vertices", len(_destination_vertex_list))
    cmds.select(base)


def _source_destination_sel(sd_type):
    """Store vertices as source or destination selection.

    Internal function that populates global vertex lists based on selection.

    Args:
        sd_type: Either "source" or "destination" to indicate which
            global list to populate.
    """
    import maya.mel as mel
    import pymel.all as pm

    global _destination_vertex_list
    global _source_vertex_list

    selection_list = pm.ls(sl=1, flatten=1)
    if selection_list and pm.nodeType(selection_list[0]) == "mesh":
        mel.eval("PolySelectConvert 3;")
        selection_list = pm.ls(sl=1, flatten=1)

    if sd_type == "destination":
        _destination_vertex_list = list(selection_list)
    elif sd_type == "source":
        _source_vertex_list = list(selection_list)


def copy_skin_global(progress_callback=None):
    """Copy skin weights from source to destination vertices.

    Uses the previously defined source and destination vertex lists
    (set via source_define() and destination_define()) to transfer
    skin weights by proximity matching.

    After transfer, clears the source and destination lists.

    Args:
        progress_callback: Optional callback function(value) for
            progress reporting (0-100 range).

    Returns:
        None
    """
    import maya.cmds as cmds

    global _source_vertex_list
    global _destination_vertex_list

    base = cmds.ls(sl=1)
    copy_skin_main(progress_callback)
    _source_vertex_list = []
    _destination_vertex_list = []
    cmds.select(base)


def copy_skin_main(progress_callback=None):
    """Transfer skin weights vertex-by-vertex using closest distance.

    For each destination vertex, finds the closest source vertex and
    copies its skin weights using Maya's artAttrSkinWeight tool.

    Args:
        progress_callback: Optional callback function(value) for
            progress reporting (0-100 range).

    Note:
        This is a brute-force O(n*m) algorithm. For large vertex counts,
        consider using Maya's native copySkinWeights with surface association.
    """
    import maya.mel as mel
    import pymel.all as pm

    source_ver = _source_vertex_list
    destination_ver = _destination_vertex_list
    progress_value = 0.0

    if len(destination_ver) > 0:
        for x_dis in destination_ver:
            x_dis_pos = x_dis.getPosition()
            min_length = 20000
            closest_src = None

            for x_src in source_ver:
                new_length = (x_dis_pos - x_src.getPosition()).length()
                if new_length < min_length:
                    min_length = new_length
                    closest_src = x_src

            if closest_src:
                pm.select(closest_src)
                mel.eval("artAttrSkinWeightCopy")
                pm.select(x_dis)
                mel.eval("artAttrSkinWeightPaste")

                progress_value += 10.0 / len(destination_ver)
                if progress_callback:
                    progress_callback(progress_value * 10)


def hammer_skin_weights():
    """Hammer skin weights on selected vertices.

    Calls Maya's weightHammerVerts mel command to smooth skin
    weights on the selected vertices based on their neighbors.
    """
    import pymel.all as pm

    pm.mel.weightHammerVerts()


def copy_pivot(source, target):
    """Copy the rotate pivot from target to source transform.

    Args:
        source: Transform to receive the pivot (string or PyNode).
        target: Transform to copy the pivot from (string or PyNode).
    """
    import maya.cmds as cmds

    pivot_translate = cmds.xform(target, q=True, ws=True, rotatePivot=True)
    cmds.xform(source, ws=True, pivots=pivot_translate)


def connect_blendshape():
    """Connect two objects with parent constraint and scale connection.

    Expects two objects selected. The first object constrains the
    second with a parent constraint (maintain offset) and connects
    scale attributes directly.

    For curve objects, also copies the pivot position.
    """
    import pymel.all as pm

    objects = pm.ls(sl=1)
    if len(objects) < 2:
        pm.displayWarning("Please select two objects")
        return

    object_type = pm.objectType(objects[0])
    if object_type != "joint":
        object_shape_type = pm.objectType(objects[0].getShape())
        if object_shape_type == "nurbsCurve":
            copy_pivot(str(objects[1]), str(objects[0]))

    pm.parentConstraint(objects[0], objects[1], n=objects[0] + "_Facial_pc", mo=1)
    pm.connectAttr(objects[0] + ".scale", objects[1] + ".scale")


def connect_blendshape_node():
    """Connect source mesh to target mesh using a blendShape deformer.

    Creates a front-of-chain blendShape with the source driving the target.
    Automatically sets the blendShape weight to 1.

    Expects exactly two objects selected: [source, target].
    """
    import pymel.all as pm

    objects = pm.ls(sl=1)
    if len(objects) != 2:
        pm.displayWarning("Please select source and target mesh to connect with BlendShape")
        return

    namespace = pm.selected()[0].namespace()
    obj_no_namespace = objects[0].replace(namespace, "")
    pm.blendShape(objects[0], objects[1], frontOfChain=1, tc=0, n=objects[0] + "_faceRig_bs")
    pm.setAttr(objects[0] + "_faceRig_bs." + obj_no_namespace, 1)
    logger.info("BlendShape created: %s_faceRig_bs", objects[0])


def connect_wrap_deformer():
    """Connect source mesh to target mesh using a wrap deformer.

    Creates a wrap deformer with exclusive binding for tight deformation.

    Expects exactly two objects selected: [driver, driven].
    """
    import maya.cmds as cmds
    import pymel.all as pm

    objects = pm.ls(sl=1)
    if len(objects) != 2:
        pm.displayWarning("Please select driver and driven mesh for wrap deformer")
        return

    cmds.optionVar(
        fv=("exclusiveBind", 1),
        iv=[("autoWeightThreshold", 0), ("maxDistance", 0.01)],
    )
    pm.select(objects[1], objects[0], r=1)
    cmds.CreateWrap(n=objects[0] + "_wrap", frontOfChain=1)
    logger.info("Wrap deformer created for %s", objects[0])


def connect_eye_target_space(name_prefix="", use_prefix=True):
    """Add space switching to the eye target control.

    Creates parent space options for the eye target control using
    condition nodes and parent constraint weights.

    Args:
        name_prefix: Optional name prefix for the rig elements.
        use_prefix: Whether to use the name prefix (default True).

    Note:
        Expects the eye_Target_ctrl and eye_Target_ctrl_grp to exist.
        Selected objects will be added as space options.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if not use_prefix:
        parents_dict = [[name_prefix + "_face_Ctrl_root", "local"]]
        aim_ctrl = pm.PyNode(name_prefix + "_eye_Target_ctrl")
        cns_grp = name_prefix + "_eye_Target_ctrl_grp"
    else:
        parents_dict = [["face_Ctrl_root", "local"]]
        aim_ctrl = pm.PyNode("eye_Target_ctrl")
        cns_grp = "eye_Target_ctrl_grp"

    objects = cmds.ls(sl=1)
    for obj in objects:
        parents_dict.append([obj, obj])

    # Add space attribute
    space_names = ":".join([item[1] for item in parents_dict])
    aim_ctrl.addAttr("space", at="enum", en=space_names, k=1)

    # Create parent constraint
    constraint_targets = [item[0] for item in parents_dict] + [cns_grp]
    par_constraint = pm.parentConstraint(*constraint_targets, mo=1)

    # Wire up condition nodes for each space
    for i, (ctrl, _space_name) in enumerate(parents_dict):
        cnd = pm.createNode("condition")
        cnd.secondTerm.set(i)
        aim_ctrl.space >> cnd.firstTerm
        cnd.colorIfTrueR.set(1)
        cnd.colorIfFalseR.set(0)
        cnd.outColorR >> par_constraint.attr(ctrl + "W" + str(i))


def save_facial_skin_set():
    """Save the current selection as a facial skin transfer source set.

    Creates a vertex set called "setA_Perseus" and stores the skin
    cluster influences for later transfer operations.

    Note:
        Deletes any existing setA_Perseus set before creating new one.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    global _facial_influence_joints

    first_obj = pm.selected()[0]
    orig = str(pm.selected()[0])
    _facial_influence_joints = pm.skinCluster(orig, q=True, influence=True)

    # Clean up existing set
    if pm.objExists("setA_Perseus"):
        pm.select("setA_Perseus", r=1, ne=1)
        pm.mel.doDelete()

    # Create new set from selection
    pm.select(first_obj, r=1)
    cmds.ConvertSelectionToVertices()
    cmds.sets(name="setA_Perseus")
    pm.select(first_obj, r=1)


def transfer_facial_skin_set():
    """Transfer skin weights from saved source set to current selection.

    Uses the influences stored by save_facial_skin_set() to create
    a skin cluster on the target object, then copies weights using
    closestPoint surface association and label influence matching.

    Note:
        Cleans up both setA_Perseus and setB_Perseus after transfer.
    """
    import maya.cmds as cmds
    import pymel.all as pm

    global _facial_influence_joints

    second_obj = pm.selected()

    # Clean up existing target set
    if pm.objExists("setB_Perseus"):
        pm.select("setB_Perseus", r=1, ne=1)
        pm.mel.doDelete()

    # Create target set
    pm.select(second_obj, r=1)
    cmds.ConvertSelectionToVertices()
    cmds.sets(name="setB_Perseus")

    # Create skin cluster on target
    vtx = pm.selected()[0]
    transforms = pm.listTransforms(vtx.node())
    pm.select(_facial_influence_joints, transforms, r=1)
    pm.mel.skinClusterInfluence(1, "-ug -dr 4 -ps 0 -ns 10 -lw true -wt 0")

    # Transfer weights
    pm.select("setA_Perseus", "setB_Perseus", r=1)
    pm.copySkinWeights(
        surfaceAssociation="closestPoint",
        influenceAssociation="label",
        noMirror=1,
    )

    # Clean up sets
    if pm.objExists("setA_Perseus"):
        pm.select("setA_Perseus", r=1, ne=1)
        pm.mel.doDelete()
    if pm.objExists("setB_Perseus"):
        pm.select("setB_Perseus", r=1, ne=1)
        pm.mel.doDelete()

    pm.select(second_obj, r=1)


def detach_skin_joint_connection():
    """Detach ghost joint connections from skin joints.

    For each joint in the hierarchy of the selected object,
    copies attributes from the joint to its _ghost counterpart.

    Note:
        Expects joints to have corresponding _ghost transform nodes.
    """
    import maya.cmds as cmds

    current_sel = cmds.ls(sl=1)
    cmds.select(hi=1)
    cmds.select(current_sel, d=1)
    skin_jnt_list = cmds.ls(sl=1, type="joint")

    if len(skin_jnt_list) > 0:
        for obj in skin_jnt_list:
            try:
                cmds.copyAttr(obj, obj + "_ghost", inConnections=True, values=True)
            except Exception:
                logger.warning("No ghost group for %s", obj)

    cmds.select(current_sel, r=1)


def attach_skin_joint_connection():
    """Attach ghost joint connections to skin joints.

    For each joint in the hierarchy of the selected object,
    copies attributes from its _ghost counterpart to the joint.

    Note:
        Expects joints to have corresponding _ghost transform nodes.
    """
    import maya.cmds as cmds

    current_sel = cmds.ls(sl=1)
    cmds.select(hi=1)
    cmds.select(current_sel, d=1)
    skin_jnt_list = cmds.ls(sl=1, type="joint")

    if len(skin_jnt_list) > 0:
        for obj in skin_jnt_list:
            try:
                cmds.copyAttr(obj + "_ghost", obj, inConnections=True, values=True)
            except Exception:
                logger.warning("No ghost group for %s", obj)

    cmds.select(current_sel, r=1)


def get_source_vertices():
    """Get the current source vertex list.

    Returns:
        list: Copy of the source vertex list.
    """
    return list(_source_vertex_list)


def get_destination_vertices():
    """Get the current destination vertex list.

    Returns:
        list: Copy of the destination vertex list.
    """
    return list(_destination_vertex_list)


def clear_vertex_selections():
    """Clear both source and destination vertex lists."""
    global _source_vertex_list
    global _destination_vertex_list

    _source_vertex_list = []
    _destination_vertex_list = []


# Legacy function aliases for backward compatibility
# These maintain the original camelCase naming from facial3.py
skinCopy = skin_copy  # noqa: N816 - backward compat
source_define = source_define  # Already snake_case
destination_define = destination_define  # Already snake_case
SourceDestinationSel = _source_destination_sel  # noqa: N816 - backward compat
copySkinGlobal = copy_skin_global  # noqa: N816 - backward compat
copySkinMain = copy_skin_main  # noqa: N816 - backward compat
hammerSkinGlobal = hammer_skin_weights  # noqa: N816 - backward compat
copyPivotF = copy_pivot  # noqa: N816 - backward compat
connectBlendShape = connect_blendshape  # noqa: N816 - backward compat
connectBlendShapeB = connect_blendshape_node  # noqa: N816 - backward compat
connectBlendShapeC = connect_wrap_deformer  # noqa: N816 - backward compat
connectBlendShapeD = connect_eye_target_space  # noqa: N816 - backward compat
SaveFacialSkinSet = save_facial_skin_set  # noqa: N816 - backward compat
TransferFacialSkinSet = transfer_facial_skin_set  # noqa: N816 - backward compat
detachSkinJntConnection = detach_skin_joint_connection  # noqa: N816 - backward compat
attachSkinJntConnection = attach_skin_joint_connection  # noqa: N816 - backward compat
getSkinCluster = get_skin_cluster  # noqa: N816 - backward compat

# Module-level exports
__all__ = [
    # Primary API (snake_case)
    "get_skin_cluster",
    "skin_copy",
    "source_define",
    "destination_define",
    "copy_skin_global",
    "copy_skin_main",
    "hammer_skin_weights",
    "copy_pivot",
    "connect_blendshape",
    "connect_blendshape_node",
    "connect_wrap_deformer",
    "connect_eye_target_space",
    "save_facial_skin_set",
    "transfer_facial_skin_set",
    "detach_skin_joint_connection",
    "attach_skin_joint_connection",
    "get_source_vertices",
    "get_destination_vertices",
    "clear_vertex_selections",
    # Legacy API (camelCase) for backward compatibility
    "skinCopy",
    "SourceDestinationSel",
    "copySkinGlobal",
    "copySkinMain",
    "hammerSkinGlobal",
    "copyPivotF",
    "connectBlendShape",
    "connectBlendShapeB",
    "connectBlendShapeC",
    "connectBlendShapeD",
    "SaveFacialSkinSet",
    "TransferFacialSkinSet",
    "detachSkinJntConnection",
    "attachSkinJntConnection",
    "getSkinCluster",
]
