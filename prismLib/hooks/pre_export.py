"""Prism Pipeline pre-export hook script.

This script is executed before the execution of an export state in the Prism State Manager.
Use this file to define project-specific actions, like cleaning up your scene or preparing
objects for export.

Example:
    print("Prism is going to export objects now.")

Note:
    If the main function exists in this script, it will be called automatically.
    The kwargs argument is a dictionary with useful information about Prism and the current export.
"""

import importlib.util as importlib_util


def detect_host_app() -> str:
    """Detects which host application we are currently inside.

    Returns:
        str: The name of the host application or None if not detected.
    """
    if importlib_util.find_spec("maya.cmds") is not None:
        return "Maya"
    if importlib_util.find_spec("hou") is not None:
        return "Houdini"
    return None


def main(core, filepath, version_up, comment, publish, details):
    """Execute pre-export actions before Prism State Manager export.

    Args:
        core: Prism core object with project configuration.
        filepath: Path where the export will be saved.
        version_up: Whether to increment version number.
        comment: Export comment string.
        publish: Whether this is a publish operation.
        details: Additional export details dictionary.
    """
    print(core.projectName)
    print(filepath)
    print(version_up)
    print(comment)
    print(publish)
    print(details)

    if detect_host_app() == "Maya":
        import maya.cmds as cmds

        cmds.currentUnit(linear="m")
