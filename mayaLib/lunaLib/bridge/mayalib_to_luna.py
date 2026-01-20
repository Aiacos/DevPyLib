"""MayaLib to Luna bridge utilities.

Provides a bridge registry that allows Luna components to access
mayaLib utilities without direct dependencies.
"""


class MayaLibBridge:
    """Registry for exposing mayaLib utilities to Luna.

    This class acts as a bridge allowing Luna components to access
    mayaLib functionality through a registered interface, avoiding
    tight coupling between the two libraries.

    Example:
        >>> # Register a mayaLib utility
        >>> MayaLibBridge.register("control_utils", mayaLib.rigLib.utils.control)
        >>> # Access from Luna
        >>> control_mod = MayaLibBridge.get("control_utils")

    """

    _registry = {}

    @classmethod
    def register(cls, name, module_or_func):
        """Register a mayaLib module or function.

        Args:
            name: Registry key name.
            module_or_func: The module or function to register.

        """
        cls._registry[name] = module_or_func

    @classmethod
    def get(cls, name, default=None):
        """Get a registered module or function.

        Args:
            name: Registry key name.
            default: Value to return if not found. Defaults to None.

        Returns:
            The registered module/function or default value.

        """
        return cls._registry.get(name, default)

    @classmethod
    def list_registered(cls):
        """List all registered module/function names.

        Returns:
            list: List of registered key names.

        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name):
        """Check if a name is registered.

        Args:
            name: Registry key name to check.

        Returns:
            bool: True if registered, False otherwise.

        """
        return name in cls._registry

    @classmethod
    def unregister(cls, name):
        """Remove a registered module or function.

        Args:
            name: Registry key name to remove.

        Returns:
            bool: True if removed, False if not found.

        """
        if name in cls._registry:
            del cls._registry[name]
            return True
        return False


def register_mayalib_utilities():
    """Register common mayaLib utilities with the bridge.

    Call this function during mayaLib initialization to make
    mayaLib utilities available to Luna components.

    Returns:
        None: Registers utilities with MayaLibBridge.

    """
    try:
        # Import mayaLib modules
        from mayaLib.rigLib.utils import control
        from mayaLib.rigLib.utils import joint
        from mayaLib.rigLib.utils import deform
        from mayaLib.rigLib.utils import skin
        from mayaLib.pipelineLib.utility import naming_utils

        # Register with bridge
        MayaLibBridge.register("control", control)
        MayaLibBridge.register("joint", joint)
        MayaLibBridge.register("deform", deform)
        MayaLibBridge.register("skin", skin)
        MayaLibBridge.register("naming", naming_utils)

        print("MayaLib utilities registered with Luna bridge")

    except ImportError as e:
        print(f"Warning: Could not register all mayaLib utilities - {e}")


def get_mayalib_control():
    """Get mayaLib control utilities.

    Convenience function to access mayaLib control module through bridge.

    Returns:
        module: The mayaLib control module, or None if not available.

    """
    return MayaLibBridge.get("control")


def get_mayalib_joint():
    """Get mayaLib joint utilities.

    Convenience function to access mayaLib joint module through bridge.

    Returns:
        module: The mayaLib joint module, or None if not available.

    """
    return MayaLibBridge.get("joint")


def get_mayalib_deform():
    """Get mayaLib deform utilities.

    Convenience function to access mayaLib deform module through bridge.

    Returns:
        module: The mayaLib deform module, or None if not available.

    """
    return MayaLibBridge.get("deform")


def get_mayalib_skin():
    """Get mayaLib skin utilities.

    Convenience function to access mayaLib skin module through bridge.

    Returns:
        module: The mayaLib skin module, or None if not available.

    """
    return MayaLibBridge.get("skin")
