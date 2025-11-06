import importlib.util as importlib_util
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
    if "hou" in sys.modules:
        return "Houdini"

    # If none of the above, return None
    return None


def detect_host_app() -> str | None:
    """Detects which host application we are currently inside.

    Returns:
        str | None: The name of the host application or None if not detected.
    """
    if importlib_util.find_spec("maya.cmds") is not None:
        return "Maya"
    if importlib_util.find_spec("hou") is not None:
        return "Houdini"
    return None


if __name__ == "__main__":
    host = detect_host_app()
    print("Host application:", host)
    if host == "Houdini":
        pass
