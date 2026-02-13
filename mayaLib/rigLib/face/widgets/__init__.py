"""Qt widget components for facial rigging UI.

Provides Qt-based widget classes for the facial rigging interface including
geometry selection widgets, settings panels, skin operation widgets,
and the main Perseus UI.
"""

from typing import Any

__all__ = [
    "head_geo_widget",
    "perseus_ui",
    "settings_widget",
    "skin_widget",
]


def __getattr__(name: str) -> Any:
    """Lazy load facial widget modules.

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
