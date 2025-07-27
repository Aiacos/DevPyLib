# This script will be executed after the execution of an export state in the Prism State Manager.
# You can use this file to define project specific actions, like manipulating the outputfiles.

# Example:
# print "Prism has exported objects."


# If the main function exists in this script, it will be called.


def detect_host_app() -> str:
    """Detects which host application we are currently inside.

    Returns:
        str: The name of the host application or None if not detected.
    """
    # Try to detect Maya
    try:
        import maya.cmds as cmds

        return "Maya"
    except ImportError:
        # Maya is not available
        pass

    # Try to detect Houdini
    try:
        import hou

        return "Houdini"
    except ImportError:
        # Houdini is not available
        pass

    return None


def main(core, filepath, versionUp, comment, publish, details):
    print(core.projectName)
    print(filepath)
    print(versionUp)
    print(comment)
    print(publish)
    print(details)

    if detect_host_app() == "Maya":
        import maya.cmds as cmds

        cmds.currentUnit(linear="m")
