"""FK tentacle rig utilities for the Arise rig system."""

import pymel.core as pm


def fk_tentacle(ctrl_list):
    """Build an FK parent chain between tentacle controls.

    Reparents each control's offset group under the next control toward the
    root, so rotating a parent control propagates to every descendant. The
    root control (index ``0`` in the original list) becomes the chain root
    and is left untouched.

    The list is traversed from tip to root by reversing it in place; each
    control's parent transform (the offset group above the control shape)
    is then parented under the next control in the reversed list.

    Args:
        ctrl_list: Ordered list of PyMEL controls from root (index ``0``) to
            tip (last index). The list is reversed in place as a side
            effect — pass a copy (``list(ctrls)``) if the original order
            must be preserved.

    Example:
        >>> ctrls = pm.ls("M_Spine_C_Spring_tentacle_?_ctrl")
        >>> fk_tentacle(ctrls)
    """
    ctrl_list.reverse()

    for ctrl in ctrl_list:
        ctrl_parent = ctrl.getParent()
        index = ctrl_list.index(ctrl)

        if index < len(ctrl_list) - 1:
            pm.parent(ctrl_parent, ctrl_list[index + 1])
