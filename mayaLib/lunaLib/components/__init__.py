"""Luna component wrappers for mayaLib.

This module provides snake_case wrapper functions around Luna rig components,
making them compatible with mayaLib's FunctionUI auto-generation system.
"""

__all__ = [
    "character",
    "fk_chain",
    "ik_chain",
    "fkik_chain",
    "spine",
    "biped_leg",
    "hand",
    "eye",
]


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
        "create_character": "character",
        "create_fk_chain": "fk_chain",
        "create_ik_chain": "ik_chain",
        "create_fkik_chain": "fkik_chain",
        "create_fkik_spine": "spine",
        "create_ribbon_spine": "spine",
        "create_biped_leg": "biped_leg",
        "create_hand": "hand",
        "create_eye": "eye",
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
        "create_character",
        "create_fk_chain",
        "create_ik_chain",
        "create_fkik_chain",
        "create_fkik_spine",
        "create_ribbon_spine",
        "create_biped_leg",
        "create_hand",
        "create_eye",
    ]
