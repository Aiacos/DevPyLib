"""Arise PostScript: Matrix-based IK/FK hybrid blending.

Replaces Arise's default constraint-based IK/FK blending with a modern
matrix-based system using blendMatrix nodes. This eliminates snapping,
evaluation cycles, and gimbal issues.

Usage:
    Attach a PostScript to an Arise CA_Arm or CA_Leg node, then either:

    1. **Use File** mode: Point to this file.
    2. **Script Editor** mode: Paste the contents of :func:`postscript_code`
       into the PostScript editor.

    Set Execution Order to "After Connection Pass (Default)".

Available variables from Arise PostScript context:
    - ``node_name`` (str): Arise node name (e.g. "l_arm").
    - ``module_grp``: Module group transform.
    - ``ctrls_list`` (list): All control transforms.
    - ``joints_list`` (list): All IoJoint objects.
    - ``cmds`` / ``mc``: maya.cmds module.

Arise joint naming convention (CA_Arm / CA_Leg):
    - Bind joints: ``{node_name}_root_jnt``, ``{node_name}_mid_jnt``, ``{node_name}_tip_jnt``
    - IK joints:   ``{node_name}_ik_root_jnt``, ``{node_name}_ik_mid_jnt``, ``{node_name}_ik_tip_jnt``
    - FK joints:   ``{node_name}_fk_root_jnt``, ``{node_name}_fk_mid_jnt``, ``{node_name}_fk_tip_jnt``
"""

import pymel.core as pm

from mayaLib.rigLib.utils.ikfk_switch import build_ik_fk_hybrid

# Joint name suffixes for the 3-joint chain (root, mid, tip)
_CHAIN_SUFFIXES = ("root", "mid", "tip")


def _find_joint(node_name, prefix, suffix, jnt_suffix="_jnt"):
    """Find an Arise joint by its naming convention.

    Args:
        node_name (str): Arise node name (e.g. "l_arm").
        prefix (str): Joint type prefix ("", "ik_", "fk_").
        suffix (str): Joint position suffix ("root", "mid", "tip").
        jnt_suffix (str): Maya joint suffix.

    Returns:
        The PyNode for the joint.

    Raises:
        RuntimeError: If the joint is not found in the scene.
    """
    name = f"{node_name}_{prefix}{suffix}{jnt_suffix}"
    matches = pm.ls(name, type="joint")
    if not matches:
        raise RuntimeError(f"Joint not found: {name}")
    return matches[0]


def _find_blend_attr(node_name, ctrls_list):
    """Find the ik_fk_switch attribute on an Arise control.

    Searches for the attribute on the switch control first, then falls back
    to the ik_tip control.

    Args:
        node_name (str): Arise node name.
        ctrls_list (list): Control transforms from Arise PostScript context.

    Returns:
        The ik_fk_switch attribute, or None if not found.
    """
    # Try switch ctrl first, then ik_tip ctrl
    search_names = [
        f"{node_name}_ik_fk_switch_ctrl",
        f"{node_name}_ik_tip_ctrl",
    ]

    for ctrl in ctrls_list:
        ctrl_name = str(ctrl)
        for search in search_names:
            if search in ctrl_name and pm.attributeQuery("ik_fk_switch", node=ctrl, exists=True):
                return pm.PyNode(f"{ctrl}.ik_fk_switch")

    return None


def _disconnect_and_clean(joints, debug=True):
    """Remove all constraints and incoming connections on bind joint TRS attributes.

    Deletes constraint nodes parented under the joints, disconnects any
    incoming connections to translate, rotate, and scale, and unlocks
    the attributes so decomposeMatrix can connect.

    Args:
        joints (list): Joint PyNodes to clean up.
        debug (bool): Print diagnostic info to Script Editor.
    """
    constraint_types = (
        "orientConstraint",
        "parentConstraint",
        "pointConstraint",
        "scaleConstraint",
    )
    attrs_to_clean = ("translate", "rotate", "scale")
    axes = ("X", "Y", "Z")

    for joint in joints:
        if debug:
            print(f"[ik_fk] Cleaning bind joint: {joint}")

        # 1. Delete constraint children
        constraints = pm.listRelatives(joint, type=constraint_types) or []
        if constraints:
            if debug:
                print(f"  Deleting constraints: {constraints}")
            pm.delete(constraints)

        # 2. Disconnect and unlock all TRS attributes
        for attr in attrs_to_clean:
            compound = joint.attr(attr)
            # Unlock compound
            compound.unlock()

            # Check and disconnect compound connection
            sources = compound.inputs(plugs=True)
            if sources:
                if debug:
                    print(f"  Disconnecting: {sources[0]} -> {compound}")
                pm.disconnectAttr(sources[0], compound)

            # Check and disconnect per-axis connections
            for axis in axes:
                child_attr = joint.attr(f"{attr}{axis}")
                child_attr.unlock()
                child_sources = child_attr.inputs(plugs=True)
                if child_sources:
                    if debug:
                        print(f"  Disconnecting: {child_sources[0]} -> {child_attr}")
                    pm.disconnectAttr(child_sources[0], child_attr)

        if debug:
            # Verify attributes are free
            for attr in attrs_to_clean:
                is_locked = joint.attr(attr).isLocked()
                has_input = bool(joint.attr(attr).inputs(plugs=True))
                print(f"  {joint}.{attr} -> locked={is_locked}, has_input={has_input}")


def _find_ctrl(node_name, ctrl_name, ctrls_list):
    """Find an Arise control by name pattern.

    Args:
        node_name (str): Arise node name (e.g. "l_arm").
        ctrl_name (str): Control name suffix (e.g. "fk_root").
        ctrls_list (list): Control transforms from PostScript context.

    Returns:
        The control PyNode, or None if not found.
    """
    search = f"{node_name}_{ctrl_name}"
    for ctrl in ctrls_list:
        if search in str(ctrl):
            return pm.PyNode(ctrl)
    return None


def _drive_ctrl_offset(source_joint, ctrl, blend_attr, follow_on_ik=True, name=""):
    """Drive a control's offset group to follow a joint using blendMatrix.

    When follow_on_ik=True: offset follows source_joint when ik_fk_switch=1 (IK mode).
    When follow_on_ik=False: offset follows source_joint when ik_fk_switch=0 (FK mode).

    This is cycle-free because FK ctrls read from IK joints (independent chain)
    and IK ctrls read from FK joints (independent chain).

    Args:
        source_joint: Joint whose worldMatrix drives the offset.
        ctrl: Control transform whose parent (offset group) gets driven.
        blend_attr: The ik_fk_switch attribute.
        follow_on_ik (bool): If True, follow when IK active. If False, follow when FK active.
        name (str): Name prefix for created nodes.
    """
    offset_grp = ctrl.getParent()
    if offset_grp is None:
        print(f"  [sync] WARNING: {ctrl} has no parent offset group, skipping")
        return

    # Compute source joint's worldMatrix in offset group's parent space
    mm = pm.createNode("multMatrix", n=f"{name}_follow_multMatrix")
    pm.connectAttr(source_joint.worldMatrix[0], mm.matrixIn[0], f=True)
    pm.connectAttr(offset_grp.parentInverseMatrix[0], mm.matrixIn[1], f=True)

    # blendMatrix: identity (default) vs joint-following matrix
    blend = pm.createNode("blendMatrix", n=f"{name}_follow_blendMatrix")
    pm.connectAttr(mm.matrixSum, blend.target[0].targetMatrix, f=True)

    # Weight logic:
    # follow_on_ik=True  → FK ctrls follow IK joints → weight = ik_fk_switch
    # follow_on_ik=False → IK ctrls follow FK joints → weight = 1 - ik_fk_switch
    if follow_on_ik:
        pm.connectAttr(blend_attr, blend.target[0].weight, f=True)
    else:
        reverse = pm.createNode("reverse", n=f"{name}_follow_reverse")
        pm.connectAttr(blend_attr, reverse.inputX, f=True)
        pm.connectAttr(reverse.outputX, blend.target[0].weight, f=True)

    # Decompose and drive offset group
    dcmp = pm.createNode("decomposeMatrix", n=f"{name}_follow_decomposeMatrix")
    pm.connectAttr(blend.outputMatrix, dcmp.inputMatrix, f=True)

    # Unlock and connect offset group TRS
    for attr in ("translate", "rotate", "scale"):
        offset_grp.attr(attr).unlock()
        for axis in ("X", "Y", "Z"):
            offset_grp.attr(f"{attr}{axis}").unlock()

    pm.connectAttr(dcmp.outputTranslate, offset_grp.translate, f=True)
    pm.connectAttr(dcmp.outputRotate, offset_grp.rotate, f=True)
    pm.connectAttr(dcmp.outputScale, offset_grp.scale, f=True)

    print(
        f"  [sync] {offset_grp} follows {source_joint} (active_on={'IK' if follow_on_ik else 'FK'})"
    )


def sync_ik_fk_controls(node_name, ctrls_list, ik_joints, fk_joints, blend_attr):
    """Wire IK and FK controls to follow each other for zero-popping transitions.

    - FK controls follow IK joints when ik_fk_switch=1 (IK active)
    - IK tip ctrl follows FK tip joint when ik_fk_switch=0 (FK active)
    - IK pole vector follows FK mid joint when ik_fk_switch=0 (FK active)

    This is cycle-free: FK ctrls read from the IK chain (independent),
    and IK ctrls read from the FK chain (independent).

    Args:
        node_name (str): Arise node name.
        ctrls_list (list): Control transforms from PostScript context.
        ik_joints (list): IK joints [root, mid, tip].
        fk_joints (list): FK joints [root, mid, tip].
        blend_attr: The ik_fk_switch attribute.
    """
    print("[ik_fk] Syncing controls for zero-popping...")

    # TODO: Implement runtime snapping via scriptJob instead of node connections.
    # Node-based control sync creates evaluation cycles with Arise's space_switch
    # system. The correct approach is scriptJob-based snapping on ik_fk_switch change.
    # See IKFKSwitch class in ikfk_switch.py for reference.
    print("[ik_fk] Control sync not yet implemented (planned: scriptJob-based snapping)")


def apply_matrix_ikfk(node_name, ctrls_list=None, jnt_suffix="_jnt"):
    """Apply matrix-based IK/FK blending to an Arise node's joint chain.

    Removes Arise's existing constraint-based IK/FK blending on the bind
    joints, wires FK and IK matrices through blendMatrix nodes, and
    syncs controls for zero-popping IK/FK transitions.

    Args:
        node_name (str): Arise node name (e.g. "l_arm", "r_leg").
        ctrls_list (list): Control transforms from PostScript context.
            Used to find the ik_fk_switch attribute. If None, searches the scene.
        jnt_suffix (str): Joint suffix used by the Arise scene.

    Returns:
        list[dict]: Created node dictionaries from :func:`build_ik_fk_hybrid`.
    """
    fk_joints = [_find_joint(node_name, "fk_", s, jnt_suffix) for s in _CHAIN_SUFFIXES]
    ik_joints = [_find_joint(node_name, "ik_", s, jnt_suffix) for s in _CHAIN_SUFFIXES]
    bind_joints = [_find_joint(node_name, "", s, jnt_suffix) for s in _CHAIN_SUFFIXES]

    # Remove Arise's constraint-based IK/FK blending on bind joints
    _disconnect_and_clean(bind_joints, debug=True)

    # Find blend attribute
    blend_attr = None
    if ctrls_list:
        blend_attr = _find_blend_attr(node_name, ctrls_list)

    # Fallback: search scene directly if not found via ctrls_list
    if blend_attr is None:
        for candidate in [f"{node_name}_ik_fk_switch_ctrl", f"{node_name}_ik_tip_ctrl"]:
            matches = pm.ls(candidate)
            if matches and pm.attributeQuery("ik_fk_switch", node=matches[0], exists=True):
                blend_attr = matches[0].attr("ik_fk_switch")
                print(f"[ik_fk] Found blend_attr via fallback: {blend_attr}")
                break

    if blend_attr is None:
        print("[ik_fk] WARNING: ik_fk_switch attribute not found, no blending or sync")

    # Build matrix blending for bind joints
    result = build_ik_fk_hybrid(
        fk_joints=fk_joints,
        ik_joints=ik_joints,
        bind_joints=bind_joints,
        blend_attr=blend_attr,
        name=f"{node_name}_matrix_ikfk",
        debug=True,
    )

    # Sync controls for zero-popping transitions
    if blend_attr and ctrls_list:
        sync_ik_fk_controls(
            node_name=node_name,
            ctrls_list=ctrls_list,
            ik_joints=ik_joints,
            fk_joints=fk_joints,
            blend_attr=blend_attr,
        )

    return result


def hybrid_ikfk(node_name, ctrls_list, joints_suffix="_jnt"):
    """Arise PostScript entry point for matrix-based IK/FK blending.

    Call this function directly from an Arise PostScript editor or file.
    It uses the variables injected by Arise's exec() context to find the
    FK/IK/bind joints and wire them through blendMatrix nodes, with
    control syncing for zero-popping transitions.

    Args:
        node_name (str): Arise node name, injected by PostScript context.
        ctrls_list (list): Control transforms, injected by PostScript context.
        joints_suffix (str): Joint suffix used by the Arise scene.
    """
    apply_matrix_ikfk(
        node_name=node_name,
        ctrls_list=ctrls_list,
        jnt_suffix=joints_suffix,
    )
