"""HumanIK rigging framework for Maya.

Provides a comprehensive HumanIK integration system including constants,
skeleton mapping, control definitions, MEL interface, and rig templates.
This module was extracted from the monolithic human_ik.py for better
maintainability and single responsibility adherence.
"""

# Lazy loading state
_human_ik_initialized = False
_human_ik_available = False

# Module references (initialized on first access)
constants = None
rig_templates = None
mel_interface = None
pose_utils = None
skeleton_mapper = None
control_mapper = None


def _initialize_human_ik():
    """Initialize human_ik modules (lazy loading).

    This function is called on first access to human_ik functionality.
    It imports all human_ik submodules.

    Returns:
        bool: True if human_ik module was successfully initialized.
    """
    global _human_ik_initialized, _human_ik_available
    global constants, rig_templates, mel_interface, pose_utils
    global skeleton_mapper, control_mapper

    if _human_ik_initialized:
        return _human_ik_available

    _human_ik_initialized = True

    try:
        # Import all submodules
        from . import constants as _constants
        from . import control_mapper as _control_mapper
        from . import mel_interface as _mel_interface
        from . import pose_utils as _pose_utils
        from . import rig_templates as _rig_templates
        from . import skeleton_mapper as _skeleton_mapper

        # Assign to module-level variables
        constants = _constants
        rig_templates = _rig_templates
        mel_interface = _mel_interface
        pose_utils = _pose_utils
        skeleton_mapper = _skeleton_mapper
        control_mapper = _control_mapper

        _human_ik_available = True
        return True

    except ImportError as e:
        print(f"Warning: human_ik submodule import failed - {e}")
        return False
    except Exception as e:
        print(f"Warning: human_ik initialization error - {e}")
        return False


class HumanIK:
    """Unified HumanIK facade for managing HumanIK mapping.

    This class composes the modular HumanIK components (skeleton mapper,
    control mapper, MEL interface, and pose utilities) into a unified
    interface that matches the original monolithic API.
    """

    def __init__(
        self,
        character_name,
        rig_template="arise",
        auto_t_pose=True,
        custom_ctrl_definition=True,
        use_ik=True,
        use_hybrid=True,
        skip_reference_joint=True,
    ):
        """Initialize the HumanIK facade.

        Args:
            character_name: The name of the character to be created.
            rig_template: The template of the rig data to be used. Available
                templates are 'arise', 'rokoko', and 'advanced_skeleton'.
                Defaults to 'arise'.
            auto_t_pose: Whether to go to T pose after initialization.
                Defaults to True.
            custom_ctrl_definition: Whether to define custom controls.
                Defaults to True.
            use_ik: Whether to use IK. Defaults to True.
            use_hybrid: Whether to use hybrid IK. Defaults to True.
            skip_reference_joint: Whether to skip the reference joint.
                Defaults to True.
        """
        # Initialize submodules if not already done
        if not _initialize_human_ik():
            raise RuntimeError("Failed to initialize HumanIK submodules")

        self.character_name = str(character_name)

        # Create component instances
        self._mel_interface = mel_interface.MelInterface()
        self._pose_utils = pose_utils.PoseUtils()
        self._skeleton_mapper = skeleton_mapper.SkeletonMapper(character_name)
        self._control_mapper = control_mapper.ControlMapper(character_name)

        # Get rig template data
        rig_definition = {
            "arise": rig_templates.ARISE_HIK_DATA,
            "rokoko": rig_templates.ROKOKO_HIK_DATA,
            "advanced_skeleton": rig_templates.ADVANCED_SKELETON_DATA,
        }
        self.rig_data = rig_definition.get(rig_template)
        if self.rig_data is None:
            raise ValueError(
                f"Unknown rig template: {rig_template}. "
                f"Available: {list(rig_definition.keys())}"
            )

        # Set T Pose
        if auto_t_pose:
            self._pose_utils.go_to_t_pose(rig_template)

        # Init HumanIK Window
        self._mel_interface.open_character_controls_tool()

        # Create Character
        self._mel_interface.create_character(self.character_name)

        # Define skeleton
        self._skeleton_mapper.define_skeleton(self.rig_data, skip_reference_joint)

        # Define custom controls
        if custom_ctrl_definition:
            self._control_mapper.define_custom_ctrls(self.rig_data, use_ik, use_hybrid)

    def __getattr__(self, name):
        """Delegate attribute access to component classes.

        This allows the facade to expose all methods from the component
        classes as if they were part of the HumanIK class itself.

        Args:
            name: The name of the attribute being accessed.

        Returns:
            The requested attribute from one of the component classes.

        Raises:
            AttributeError: If the attribute doesn't exist in any component.
        """
        # Try to get from skeleton mapper
        if hasattr(self._skeleton_mapper, name):
            return getattr(self._skeleton_mapper, name)

        # Try to get from control mapper
        if hasattr(self._control_mapper, name):
            return getattr(self._control_mapper, name)

        # Try to get from pose utils
        if hasattr(self._pose_utils, name):
            return getattr(self._pose_utils, name)

        # Try to get from MEL interface
        if hasattr(self._mel_interface, name):
            return getattr(self._mel_interface, name)

        raise AttributeError(f"'HumanIK' object has no attribute '{name}'")


def is_available():
    """Check if human_ik module is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if human_ik module is available and initialized.
    """
    return _initialize_human_ik()


def __getattr__(name):
    """Lazy loading of human_ik submodules.

    This function is called when an attribute is accessed that doesn't exist
    in the module's __dict__. It triggers initialization of human_ik module and
    returns the requested attribute.

    Args:
        name: The name of the attribute being accessed.

    Returns:
        The requested attribute from the initialized human_ik module.

    Raises:
        AttributeError: If the attribute doesn't exist after initialization.
    """
    # List of available submodules
    _submodules = [
        "constants",
        "rig_templates",
        "mel_interface",
        "pose_utils",
        "skeleton_mapper",
        "control_mapper",
    ]

    if name in _submodules:
        if _initialize_human_ik():
            return globals()[name]
        else:
            raise AttributeError(
                f"human_ik submodule '{name}' could not be loaded - initialization failed"
            )

    raise AttributeError(
        f"module 'mayaLib.rigLib.utils.human_ik' has no attribute '{name}'"
    )


def __dir__():
    """Return list of available attributes for introspection.

    Returns:
        list: Sorted list of available module attributes.
    """
    _submodules = [
        "constants",
        "rig_templates",
        "mel_interface",
        "pose_utils",
        "skeleton_mapper",
        "control_mapper",
    ]
    return sorted(list(globals().keys()) + _submodules + ["is_available", "HumanIK"])
