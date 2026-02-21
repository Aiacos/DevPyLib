"""Rigging utilities for character setup and deformation in Maya.

This package provides a comprehensive collection of utility modules for
character rigging including control creation, IK/FK switching, joint utilities,
deformation tools, skin weighting, and specialized systems for dynamics,
spaces, and custom rig components.
"""

from typing import Any

__all__ = [
    "attributes",
    "cloth_muscle_setup",
    "color_control",
    "common",
    "control",
    "ctrl_shape",
    "deform",
    "dynamic",
    "flexiplane",
    "follow_ctrl",
    "foot_roll",
    "human_ik",
    "ikfk_switch",
    "joint",
    "line_of_action",
    "matrix_utils",
    "meta_human",
    "name",
    "parameter_resolution",
    "pole_vector",
    "proxy_geo",
    "pxr_control",
    "scapula",
    "skin",
    "smart_foot_roll",
    "spaces",
    "stretchy_ik_chain",
    "transform",
    "unreal_engine_skeleton_converter",
    "util",
]


def __getattr__(name: str) -> Any:
    """Lazy load rigging utility modules.

    Args:
        name: Module name to load.

    Returns:
        The requested module.

    Raises:
        AttributeError: If module not found.
    """
    if name in __all__:
        from importlib import import_module

        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
