"""Utility functions for facial rigging system.

This module contains general utility functions used throughout the facial
rigging framework, including Maya window access and data encoding utilities.
"""

import sys

# Qt imports with PySide6/PySide2 fallback
try:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
except (ImportError, ModuleNotFoundError):
    from PySide2 import QtWidgets
    from shiboken2 import wrapInstance

# Python 2/3 compatibility
long = int


def maya_main_window():
    """Return the Maya main window widget as a Python object.

    Gets the Maya main window from OpenMayaUI and wraps it as a Qt widget
    that can be used as a parent for custom Qt dialogs.

    Returns:
        QtWidgets.QWidget: The Maya main window as a Qt widget.

    Raises:
        RuntimeError: If Maya is not running or the main window
            cannot be retrieved.

    Example:
        >>> parent = maya_main_window()
        >>> dialog = QtWidgets.QDialog(parent)
        >>> dialog.show()
    """
    # Import Maya modules here to allow syntax checking without Maya
    try:
        import maya.OpenMayaUI as OMUI  # noqa: N817 - Maya convention
    except ImportError as err:
        raise RuntimeError("Maya is not available in this environment") from err

    main_window_ptr = OMUI.MQtUtil.mainWindow()
    python_version = sys.version_info.major

    try:
        if python_version == 2:
            return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
        else:
            return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    except Exception:
        # Fallback to Qt.py compatibility layer
        from Qt import QtCompat

        return QtCompat.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


def get_license_string():
    """Generate obfuscated license string for UI.

    Creates an encoded license information string using character
    extraction from predefined code strings. This is used for
    displaying license information in the UI.

    Returns:
        str: Encoded license information string.

    Note:
        This function uses obfuscation for license display purposes.
        The encoding is based on extracting characters from template
        code strings at specific indices.
    """
    pr_check_test_1 = "pm.mel.moveJointsMode(0)"
    pr_check_test_2 = "cmds.aimConstraint(weight=1, upVector=(2, 1, 0),f=1)"
    pr_check_test_3 = "cmds.aimConstreint(weight=1, upVector=(0, 1, 0),h=0),r=0)"
    pr_check_test_4 = "name_LIPs_All_Jnt"
    pr_check_test_5 = "setStyleSheet"
    pr_check_test_6 = "QtWidgets.QPushButton"
    pr_check_test_7 = "self.edgeColor"
    pr_check_test_8 = "background-color"
    pr_check_test_9 = "self.LEyeLidMainBoxButton"
    pr_check_test_10 = "self.REyeLidMainBoxButton"

    word_a = (
        pr_check_test_4[7]
        + pr_check_test_1[4]
        + pr_check_test_3[53]
        + pr_check_test_4[8]
        + pr_check_test_4[3]
        + pr_check_test_2[29]
        + pr_check_test_1[16]
    )
    word_b = (
        pr_check_test_10[5]
        + pr_check_test_1[13]
        + pr_check_test_6[5]
        + pr_check_test_7[7]
        + pr_check_test_6[3]
        + pr_check_test_10[15]
        + pr_check_test_6[5]
    )
    word_c = str(3)
    word_d = pr_check_test_3[8] + pr_check_test_3[9] + pr_check_test_1[0] + pr_check_test_5[5]
    word_e = (
        pr_check_test_8[5]
        + pr_check_test_6[3]
        + pr_check_test_8[4]
        + pr_check_test_5[9]
        + pr_check_test_5[2]
    )
    word_f = str(2017)
    word_g = (
        pr_check_test_6[2]
        + pr_check_test_7[13]
        + word_e[1]
        + pr_check_test_6[1]
        + pr_check_test_6[1]
        + pr_check_test_1[4]
        + pr_check_test_4[0]
    )
    word_h = pr_check_test_8[0] + pr_check_test_5[5]
    word_i = (
        pr_check_test_9[12]
        + pr_check_test_3[9]
        + pr_check_test_3[48]
        + pr_check_test_8[1]
        + pr_check_test_3[1]
        + pr_check_test_2[1]
        + pr_check_test_8[1]
        + pr_check_test_6[4]
    )
    word_j = (
        pr_check_test_4[14]
        + pr_check_test_4[1]
        + pr_check_test_7[3]
        + pr_check_test_8[1]
        + pr_check_test_8[5]
        + pr_check_test_9[10]
        + pr_check_test_8[1]
        + pr_check_test_4[0]
    )
    word_k = pr_check_test_2[19] + pr_check_test_3[19] + pr_check_test_2[19] + pr_check_test_7[4]
    word_l = (
        pr_check_test_1[0]
        + pr_check_test_1[4]
        + pr_check_test_3[53]
        + pr_check_test_4[8]
        + pr_check_test_4[3]
        + pr_check_test_2[29]
        + pr_check_test_1[16]
    )
    word_m = (
        pr_check_test_3[53]
        + pr_check_test_1[13]
        + pr_check_test_6[5]
        + pr_check_test_7[7]
        + pr_check_test_6[3]
        + pr_check_test_10[15]
        + pr_check_test_6[5]
    )
    word_n = pr_check_test_9[4] + pr_check_test_3[0] + pr_check_test_3[9] + pr_check_test_2[7]
    word_space = pr_check_test_2[28]

    result = (
        word_space
        + word_a
        + word_space
        + word_b
        + word_space
        + word_c
        + word_space
        + word_d
        + word_e
        + word_space
        + word_f
        + word_space
        + word_g
        + word_space
        + word_h
        + word_space
        + word_i
        + word_space
        + word_j
        + word_space
        + word_space
        + word_k
        + word_l
        + word_m
        + word_n
        + word_space
    )
    return result


def get_short_license_string():
    """Generate alternate obfuscated license string for UI.

    Creates a shorter encoded license information string using character
    extraction from predefined code strings. This is a compact version
    of the license display.

    Returns:
        str: Encoded short license information string.

    Note:
        This function uses obfuscation for license display purposes.
        The encoding is based on extracting characters from template
        code strings at specific indices.
    """
    pr_check_test_1 = "pm.mel.moveJointsMode(0)"
    pr_check_test_2 = "cmds.aimConstraint(weight=1, upVector=(2, 1, 0),f=1)"
    pr_check_test_3 = "cmds.aimConstreint(weight=1, upVector=(0, 1, 0),h=0),r=0)"
    pr_check_test_4 = "name_LIPs_All_Jnt"
    pr_check_test_9 = "self.LEyeLidMainBoxButton"
    pr_check_test_10 = "self.REyeLidMainBoxButton"

    word_a = (
        pr_check_test_4[7]
        + pr_check_test_1[4]
        + pr_check_test_3[53]
        + pr_check_test_4[8]
        + pr_check_test_4[3]
        + pr_check_test_2[29]
        + pr_check_test_1[16]
    )
    word_b = (
        pr_check_test_10[5]
        + pr_check_test_1[13]
        + "QtWidgets.QPushButton"[5]
        + "self.edgeColor"[7]
        + "QtWidgets.QPushButton"[3]
        + pr_check_test_10[15]
        + "QtWidgets.QPushButton"[5]
    )
    word_c = str(3)
    word_o = pr_check_test_10[12] + pr_check_test_10[13] + pr_check_test_9[7] + pr_check_test_4[1]
    word_space = pr_check_test_2[28]

    result = (
        word_space
        + word_a
        + word_space
        + word_b
        + word_space
        + word_c
        + word_space
        + word_o
        + word_space
    )
    return result


# Legacy function names for backward compatibility
# These aliases maintain compatibility with existing code that uses
# the original function names from facial3.py


def findMainName():  # noqa: N802 - Legacy name for backward compatibility
    """Generate obfuscated license string for UI.

    Deprecated:
        Use get_license_string() instead.

    Returns:
        str: Encoded license information string.
    """
    return get_license_string()


def findMainNameB():  # noqa: N802 - Legacy name for backward compatibility
    """Generate alternate obfuscated license string for UI.

    Deprecated:
        Use get_short_license_string() instead.

    Returns:
        str: Encoded short license information string.
    """
    return get_short_license_string()


# Module-level exports
__all__ = [
    "maya_main_window",
    "get_license_string",
    "get_short_license_string",
    "findMainName",
    "findMainNameB",
]
