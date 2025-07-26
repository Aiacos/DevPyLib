import sys


def detect_host_app_v2():
    """Detects which host application we are currently inside.

    Checks the names of the modules that are currently loaded and returns the name
    of the host application. If none of the known host applications are detected,
    returns None.

    Returns:
        str: The name of the host application or None if not detected.
    """
    # Check if Maya is loaded
    if "maya.cmds" in sys.modules or "maya" in sys.modules:
        return "Maya"
    # Check if Houdini is loaded
    elif "hou" in sys.modules:
        return "Houdini"

    # If none of the above, return None
    return None


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


if __name__ == "__main__":
    host = detect_host_app()
    print("Host application:", host)
    if host == "Houdini":
        pass
