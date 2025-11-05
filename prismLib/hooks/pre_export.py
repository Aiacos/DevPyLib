# This script will be executed before the execution of an export state in the Prism State Manager.
# You can use this file to define project specific actions, like cleaning up your scene or preparing objects for export.

# Example:
# print "Prism is going to export objects now."

# If the main function exists in this script, it will be called.
# The "kwargs" argument is a dictionary with usefull information about Prism and the current export.

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
    print(core.projectName)
    print(filepath)
    print(version_up)
    print(comment)
    print(publish)
    print(details)

    if detect_host_app() == "Maya":
        import maya.cmds as cmds

        cmds.currentUnit(linear="m")
