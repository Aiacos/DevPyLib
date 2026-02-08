"""Luna function wrappers for mayaLib.

This module provides snake_case wrapper functions around Luna utility functions,
making them compatible with mayaLib's FunctionUI auto-generation system.
"""

__all__ = ["joint_utils", "name_utils", "rig_utils"]


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
        # joint_utils functions
        "duplicate_chain": "joint_utils",
        "joint_chain": "joint_utils",
        "get_pole_vector": "joint_utils",
        "create_chain": "joint_utils",
        "mirror_chain": "joint_utils",
        "joints_along_curve": "joint_utils",
        # name_utils functions
        "generate_name": "name_utils",
        "deconstruct_name": "name_utils",
        "rename_node": "name_utils",
        # rig_utils functions
        "list_controls": "rig_utils",
        "get_character": "rig_utils",
        "list_characters": "rig_utils",
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
        "duplicate_chain",
        "joint_chain",
        "get_pole_vector",
        "create_chain",
        "mirror_chain",
        "joints_along_curve",
        "generate_name",
        "deconstruct_name",
        "rename_node",
        "list_controls",
        "get_character",
        "list_characters",
    ]
