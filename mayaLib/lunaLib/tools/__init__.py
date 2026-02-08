"""Luna tool launchers for mayaLib.

This module provides launcher functions for Luna's GUI tools
such as the visual rig builder and configuration editor.
"""

__all__ = ["builder", "configer", "anim_tools"]


def __getattr__(name):
    """Lazy load submodules on first access.

    Args:
        name: The attribute name being accessed.

    Returns:
        The requested module or function.

    Raises:
        AttributeError: If the attribute is not found.
    """
    if name in __all__:
        import importlib

        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module

    # Support direct access to commonly used function exports
    function_map = {
        "launch_builder": "builder",
        "launch_configer": "configer",
        "launch_anim_baker": "anim_tools",
        "launch_keyframe_transfer": "anim_tools",
        "launch_space_tool": "anim_tools",
    }

    if name in function_map:
        import importlib

        module_name = function_map[name]
        module = importlib.import_module(f".{module_name}", __name__)
        globals()[module_name] = module
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return the list of available attributes for introspection.

    Returns:
        List of attribute names.
    """
    return __all__ + [
        "launch_builder",
        "launch_configer",
        "launch_anim_baker",
        "launch_keyframe_transfer",
        "launch_space_tool",
    ]
