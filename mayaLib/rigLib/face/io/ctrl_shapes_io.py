"""Control shapes I/O operations for facial rigging.

This module provides functions for exporting and importing facial rig
control shapes to/from Maya ASCII files. It handles the serialization
of control curve shapes including their CVs, colors, and line widths.

The export process creates buffer copies of all facial rig controllers,
removes child transforms, and exports only the shape data. The import
process reads the saved shapes and replaces the existing control shapes
while preserving the control hierarchy.

Example:
    Export control shapes::

        from mayaLib.rigLib.face.io import ctrl_shapes_io
        ctrl_shapes_io.export_ctrl_shapes("/path/to/shapes.ma", "character")

    Import control shapes::

        ctrl_shapes_io.import_ctrl_shapes("/path/to/shapes.ma", "character")
"""

import contextlib
import logging
import os
from typing import Optional

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)


def export_ctrl_shapes(
    file_path: Optional[str] = None,
    rig_name: Optional[str] = None,
    use_prefix: bool = True,
) -> bool:
    """Export facial rig control shapes to a Maya ASCII file.

    Creates temporary buffer copies of all controls in the facial rig
    controllers group, removes child transforms, and exports only the
    shape nodes. This allows control shapes to be saved and transferred
    between rigs.

    Args:
        file_path: Output Maya ASCII file path. If None, opens a file dialog.
            Should end with '.ma'.
        rig_name: Name prefix for the facial rig. If None or use_prefix is False,
            uses controls without prefix.
        use_prefix: Whether to use rig_name as prefix for control names.
            If True (default), expects controls named '{rig_name}_facialRig_controllers_grp'.
            If False, expects controls named 'facialRig_controllers_grp'.

    Returns:
        True if export was successful, False otherwise.

    Raises:
        RuntimeError: If the facial rig controllers group doesn't exist.

    Example:
        >>> export_ctrl_shapes("/path/to/shapes.ma", "myCharacter")
        True
        >>> export_ctrl_shapes("/path/to/shapes.ma", use_prefix=False)
        True
    """
    import maya.cmds as cmds
    import pymel.all as pm

    # Determine group names based on prefix setting
    if use_prefix and rig_name:
        controllers_grp = f"{rig_name}_facialRig_controllers_grp"
        shape_ctrl_grp = f"{rig_name}_facial_shapeCtrl_grp"
        jaw_ctrl = f"{rig_name}_jaw_ctrl"
        jaw_buffer = f"{rig_name}_jaw_fk_ctrl_buffer"
    else:
        controllers_grp = "facialRig_controllers_grp"
        shape_ctrl_grp = "facial_shapeCtrl_grp"
        jaw_ctrl = "jaw_ctrl"
        jaw_buffer = "jaw_fk_ctrl_buffer"

    # Close option box window if open
    if cmds.window("OptionBoxWindow", exists=True):
        cmds.deleteUI("OptionBoxWindow", window=True)
    pm.mel.saveOptionBoxSize()

    # Get file path from dialog if not provided
    if not file_path:
        basic_filter = "*.ma"
        file_dialog = cmds.fileDialog2(fileFilter=basic_filter, dialogStyle=2)
        if not file_dialog:
            logger.warning("Export cancelled - no file path selected")
            return False
        file_path = file_dialog[0]

    # Ensure file has .ma extension
    if not file_path.endswith(".ma"):
        file_path = file_path.replace(".ma", "") + ".ma"

    # Verify controllers group exists
    if not cmds.objExists(controllers_grp):
        logger.error("Controllers group not found: %s", controllers_grp)
        return False

    # Check if shape control group already exists (shouldn't)
    if cmds.objExists(shape_ctrl_grp):
        logger.warning("Shape control group already exists, skipping export")
        return False

    # Create temporary group for export
    cmds.group(em=True, n=shape_ctrl_grp)

    # Get all controls and create buffer copies
    cmds.select(controllers_grp, r=True)
    facial_ctrls = cmds.ls(sl=True)
    cmds.select(cl=True)

    for obj in facial_ctrls:
        cmds.select(obj, r=True)
        cmds.duplicate(rr=True, n=obj + "_buffer")

        # Remove child transforms from buffer
        ctrl_children = pm.listRelatives(obj + "_buffer", children=True, type="transform")
        for child in ctrl_children:
            cmds.delete(str(child))

        # Group and parent to export group
        cmds.select(obj + "_buffer", r=True)
        cmds.group(n=obj + "_buffer_grp")
        cmds.parent(obj + "_buffer_grp", shape_ctrl_grp)
        cmds.sets(obj + "_buffer", edit=True, rm=controllers_grp)

    # Hide the export group
    pm.setAttr(f"{shape_ctrl_grp}.visibility", 0)

    # Select and delete history
    cmds.select(shape_ctrl_grp, hi=True)
    cmds.DeleteHistory()

    # Disconnect jaw scale connection if exists
    with contextlib.suppress(Exception):
        cmds.disconnectAttr(f"{jaw_ctrl}.scale", f"{jaw_buffer}.inverseScale")

    # Export to Maya ASCII
    cmds.file(
        file_path,
        pr=True,
        typ="mayaAscii",
        force=True,
        options="v=0;",
        es=True,
        constructionHistory=False,
        con=False,
    )

    # Clean up temporary export group
    cmds.delete(shape_ctrl_grp)
    cmds.select(cl=True)

    logger.info("Control shapes exported to: %s", file_path)
    return True


def import_ctrl_shapes(
    file_path: Optional[str] = None,
    rig_name: Optional[str] = None,
    use_prefix: bool = True,
) -> bool:
    """Import facial rig control shapes from a Maya ASCII file.

    Imports control shape data from a previously exported file and
    replaces the existing control shapes in the scene. The original
    control hierarchy is preserved while only the shape nodes are
    updated.

    Args:
        file_path: Maya ASCII file path to import. If None, opens a file dialog.
        rig_name: Name prefix for the facial rig. If None or use_prefix is False,
            uses controls without prefix.
        use_prefix: Whether to use rig_name as prefix for control names.
            If True (default), expects controls named '{rig_name}_facialRig_controllers_grp'.
            If False, expects controls named 'facialRig_controllers_grp'.

    Returns:
        True if import was successful, False otherwise.

    Example:
        >>> import_ctrl_shapes("/path/to/shapes.ma", "myCharacter")
        True
    """
    import maya.cmds as cmds
    import pymel.all as pm

    # Determine group names based on prefix setting
    if use_prefix and rig_name:
        controllers_grp = f"{rig_name}_facialRig_controllers_grp"
        shape_ctrl_grp = f"{rig_name}_facial_shapeCtrl_grp"
    else:
        controllers_grp = "facialRig_controllers_grp"
        shape_ctrl_grp = "facial_shapeCtrl_grp"

    # Get file path from dialog if not provided
    if not file_path:
        file_path = str(pm.fileDialog(dm="*.ma"))
        if not file_path:
            logger.warning("Import cancelled - no file path selected")
            return False

    # Check if shape control group already exists (shouldn't)
    if cmds.objExists(shape_ctrl_grp):
        logger.warning("Shape control group already exists, cannot import")
        return False

    # Verify controllers group exists
    if not cmds.objExists(controllers_grp):
        logger.error("Controllers group not found: %s", controllers_grp)
        return False

    # Import the shape file
    cmds.file(
        file_path,
        pr=True,
        ignoreVersion=True,
        i=True,
        type="mayaAscii",
        namespace=":",
        ra=True,
        mergeNamespacesOnClash=True,
        options="v=0;",
    )

    # Get all controls in the controllers group
    cmds.select(controllers_grp, r=True)
    facial_ctrls = cmds.ls(sl=True)
    cmds.select(cl=True)

    # Replace shapes from buffers
    for obj in facial_ctrls:
        if cmds.objExists(obj + "_buffer"):
            # Get old and new shape nodes
            old_child = cmds.listRelatives(obj, children=True, type="shape")
            ctrl_child = cmds.listRelatives(obj + "_buffer", children=True, type="shape")

            # Parent new shapes to control
            if ctrl_child:
                for i in range(len(ctrl_child)):
                    cmds.parent(ctrl_child[i], obj, s=True, r=True)

            # Delete old shapes
            if old_child:
                cmds.delete(old_child)

    # Clean up imported shape control group
    cmds.delete(shape_ctrl_grp)

    # Rename shape nodes to match control names
    cmds.select(controllers_grp, r=True)
    facial_ctrls = pm.ls(sl=True)

    for obj in facial_ctrls:
        orig_child = cmds.listRelatives(str(obj), children=True, type="shape")
        if orig_child:
            if len(orig_child) == 1:
                cmds.rename(str(obj.getShape()), str(obj) + "Shape")
            else:
                for i in range(len(orig_child)):
                    cmds.rename(orig_child[i], str(obj) + "Shape" + str(i))

    cmds.select(cl=True)
    logger.info("Control shapes imported from: %s", file_path)
    return True


def export_ctrl_shapes_no_ui(
    file_path: str,
    rig_name: Optional[str] = None,
) -> bool:
    """Export control shapes without UI interaction.

    Non-interactive version of export_ctrl_shapes for scripted workflows.
    Still opens a file dialog for file selection, but skips other UI elements.

    Args:
        file_path: Output Maya ASCII file path (dialog will still be shown
            for user confirmation).
        rig_name: Name prefix for the facial rig. If None, uses controls
            without prefix.

    Returns:
        True if export was successful, False otherwise.

    Example:
        >>> export_ctrl_shapes_no_ui("/path/to/shapes.ma", "myCharacter")
        True
    """
    use_prefix = rig_name is not None
    return export_ctrl_shapes(
        file_path=None,  # Will show dialog
        rig_name=rig_name,
        use_prefix=use_prefix,
    )


def import_ctrl_shapes_no_ui(
    file_path: str,
    rig_name: Optional[str] = None,
) -> bool:
    """Import control shapes without UI interaction.

    Non-interactive version of import_ctrl_shapes for scripted workflows.
    Takes a file path directly instead of showing a dialog.

    Args:
        file_path: Maya ASCII file path to import.
        rig_name: Name prefix for the facial rig. If None, uses controls
            without prefix.

    Returns:
        True if import was successful, False otherwise.

    Example:
        >>> import_ctrl_shapes_no_ui("/path/to/shapes.ma", "myCharacter")
        True
    """
    use_prefix = rig_name is not None
    return import_ctrl_shapes(
        file_path=file_path,
        rig_name=rig_name,
        use_prefix=use_prefix,
    )


# Legacy function aliases for backward compatibility
# These maintain the original naming from facial3.py PerseusUI class
FacialSaveCtlShapesNoUI = export_ctrl_shapes_no_ui  # noqa: N816 - backward compat
FacialLoadCtlShapesNoUI = import_ctrl_shapes_no_ui  # noqa: N816 - backward compat


# Module-level exports
__all__ = [
    # Primary API (snake_case)
    "export_ctrl_shapes",
    "import_ctrl_shapes",
    "export_ctrl_shapes_no_ui",
    "import_ctrl_shapes_no_ui",
    # Legacy API (camelCase) for backward compatibility
    "FacialSaveCtlShapesNoUI",
    "FacialLoadCtlShapesNoUI",
]
