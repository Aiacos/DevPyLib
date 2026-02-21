"""HumanIK rigging framework for Maya.

Provides a comprehensive HumanIK integration system including constants,
skeleton mapping, control definitions, MEL interface, and rig templates.
This module was extracted from the monolithic human_ik.py for better
maintainability and single responsibility adherence.

This module provides backward compatibility by re-exporting all symbols
that were previously available from the monolithic human_ik.py file.

Public API:
    Submodules:
        - constants: HumanIK joint and control naming constants
        - rig_templates: Predefined rig templates (Arise, Rokoko, Advanced Skeleton)
        - mel_interface: MEL command interface for HumanIK operations
        - pose_utils: Utilities for managing character poses
        - skeleton_mapper: Skeleton to HumanIK mapping utilities
        - control_mapper: Control to HumanIK mapping utilities

    Classes:
        - HumanIK: Unified facade for HumanIK character setup

    Functions:
        - is_available: Check if HumanIK module is available

    Constants (backward compatibility):
        Joint defaults, control defaults, mapping dictionaries, and rig templates
        are re-exported for backward compatibility with the monolithic API.

Example:
    >>> import mayaLib.rigLib.utils.human_ik as hik
    >>> # Create HumanIK character using Arise template
    >>> character = hik.HumanIK("MyCharacter", rig_template="arise")
    >>> # Access constants
    >>> joint_map = hik.HUMAN_IK_JOINT_MAP
    >>> # Use submodules directly
    >>> hik.skeleton_mapper.SkeletonMapper("character")
"""

# Public exports - comprehensive list for IDE support and documentation
__all__ = [
    # Main class
    "HumanIK",
    # Utility function
    "is_available",
    # Submodules
    "constants",
    "rig_templates",
    "mel_interface",
    "pose_utils",
    "skeleton_mapper",
    "control_mapper",
    # Joint name constants (backward compatibility)
    "REFERENCE_JOINT_DEFAULT",
    "HIP_JOINT_DEFAULT",
    "SPINE_JOINT_LIST_DEFAULT",
    "NECK_JOINT_LIST_DEFAULT",
    "HEAD_JOINT_DEFAULT",
    "LEFT_ARM_JOINT_LIST_DEFAULT",
    "LEFT_LEG_JOINT_LIST_DEFAULT",
    "RIGHT_ARM_JOINT_LIST_DEFAULT",
    "RIGHT_LEG_JOINT_LIST_DEFAULT",
    "LEFT_HAND_THUMB_JOINT_LIST_DEFAULT",
    "LEFT_HAND_INDEX_JOINT_LIST_DEFAULT",
    "LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT",
    "LEFT_HAND_RING_JOINT_LIST_DEFAULT",
    "LEFT_HAND_PINKY_JOINT_LIST_DEFAULT",
    "RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT",
    "RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT",
    "RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT",
    "RIGHT_HAND_RING_JOINT_LIST_DEFAULT",
    "RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT",
    # Control name constants (backward compatibility)
    "HIP_CTRL_DEFAULT",
    "SPINE_CTRL_LIST_DEFAULT",
    "CHEST_CTRL_DEFAULT",
    "NECK_CTRL_DEFAULT",
    "HEAD_CTRL_DEFAULT",
    "LEFT_CLAVICLE_CTRL_DEFAULT",
    "LEFT_SHOULDER_CTRL_DEFAULT",
    "LEFT_ELBOW_CTRL_DEFAULT",
    "LEFT_HAND_FK_CTRL_DEFAULT",
    "LEFT_HAND_IK_CTRL_DEFAULT",
    "RIGHT_CLAVICLE_CTRL_DEFAULT",
    "RIGHT_SHOULDER_CTRL_DEFAULT",
    "RIGHT_ELBOW_CTRL_DEFAULT",
    "RIGHT_HAND_FK_CTRL_DEFAULT",
    "RIGHT_HAND_IK_CTRL_DEFAULT",
    "LEFT_HIP_CTRL_DEFAULT",
    "LEFT_KNEE_CTRL_DEFAULT",
    "LEFT_ANKLE_FK_CTRL_DEFAULT",
    "LEFT_ANKLE_IK_CTRL_DEFAULT",
    "RIGHT_HIP_CTRL_DEFAULT",
    "RIGHT_KNEE_CTRL_DEFAULT",
    "RIGHT_ANKLE_FK_CTRL_DEFAULT",
    "RIGHT_ANKLE_IK_CTRL_DEFAULT",
    "LEFT_HAND_THUMB_CTRL_LIST_DEFAULT",
    "LEFT_HAND_INDEX_CTRL_LIST_DEFAULT",
    "LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT",
    "LEFT_HAND_RING_CTRL_LIST_DEFAULT",
    "LEFT_HAND_PINKY_CTRL_LIST_DEFAULT",
    "RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT",
    "RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT",
    "RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT",
    "RIGHT_HAND_RING_CTRL_LIST_DEFAULT",
    "RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT",
    # Mapping dictionaries and templates (backward compatibility)
    "HUMAN_IK_JOINT_MAP",
    "HUMAN_IK_CTRL_MAP",
    "ARISE_HIK_DATA",
    "ROKOKO_HIK_DATA",
    "ADVANCED_SKELETON_DATA",
]

# Lazy loading state
_human_ik_initialized = False
_human_ik_available = False

# Module references (initialized on first access via __getattr__)
# Note: These are intentionally NOT pre-declared to allow __getattr__ to work


def _initialize_human_ik():
    """Initialize human_ik modules (lazy loading).

    This function is called on first access to human_ik functionality.
    It imports all human_ik submodules and populates backward compatibility exports.

    Returns:
        bool: True if human_ik module was successfully initialized.
    """
    global _human_ik_initialized, _human_ik_available

    if _human_ik_initialized:
        return _human_ik_available

    _human_ik_initialized = True

    try:
        # Import constants and rig_templates first (no Maya dependencies)
        from . import constants as _constants
        from . import rig_templates as _rig_templates

        # Assign to module-level variables
        globals()["constants"] = _constants
        globals()["rig_templates"] = _rig_templates

        # Populate backward compatibility exports from constants using globals()
        globals()["REFERENCE_JOINT_DEFAULT"] = _constants.REFERENCE_JOINT_DEFAULT
        globals()["HIP_JOINT_DEFAULT"] = _constants.HIP_JOINT_DEFAULT
        globals()["SPINE_JOINT_LIST_DEFAULT"] = _constants.SPINE_JOINT_LIST_DEFAULT
        globals()["NECK_JOINT_LIST_DEFAULT"] = _constants.NECK_JOINT_LIST_DEFAULT
        globals()["HEAD_JOINT_DEFAULT"] = _constants.HEAD_JOINT_DEFAULT
        globals()["LEFT_ARM_JOINT_LIST_DEFAULT"] = _constants.LEFT_ARM_JOINT_LIST_DEFAULT
        globals()["LEFT_LEG_JOINT_LIST_DEFAULT"] = _constants.LEFT_LEG_JOINT_LIST_DEFAULT
        globals()["RIGHT_ARM_JOINT_LIST_DEFAULT"] = _constants.RIGHT_ARM_JOINT_LIST_DEFAULT
        globals()["RIGHT_LEG_JOINT_LIST_DEFAULT"] = _constants.RIGHT_LEG_JOINT_LIST_DEFAULT
        globals()["LEFT_HAND_THUMB_JOINT_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_THUMB_JOINT_LIST_DEFAULT
        )
        globals()["LEFT_HAND_INDEX_JOINT_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_INDEX_JOINT_LIST_DEFAULT
        )
        globals()["LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT
        )
        globals()["LEFT_HAND_RING_JOINT_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_RING_JOINT_LIST_DEFAULT
        )
        globals()["LEFT_HAND_PINKY_JOINT_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_PINKY_JOINT_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_RING_JOINT_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_RING_JOINT_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT
        )
        globals()["HIP_CTRL_DEFAULT"] = _constants.HIP_CTRL_DEFAULT
        globals()["SPINE_CTRL_LIST_DEFAULT"] = _constants.SPINE_CTRL_LIST_DEFAULT
        globals()["CHEST_CTRL_DEFAULT"] = _constants.CHEST_CTRL_DEFAULT
        globals()["NECK_CTRL_DEFAULT"] = _constants.NECK_CTRL_DEFAULT
        globals()["HEAD_CTRL_DEFAULT"] = _constants.HEAD_CTRL_DEFAULT
        globals()["LEFT_CLAVICLE_CTRL_DEFAULT"] = _constants.LEFT_CLAVICLE_CTRL_DEFAULT
        globals()["LEFT_SHOULDER_CTRL_DEFAULT"] = _constants.LEFT_SHOULDER_CTRL_DEFAULT
        globals()["LEFT_ELBOW_CTRL_DEFAULT"] = _constants.LEFT_ELBOW_CTRL_DEFAULT
        globals()["LEFT_HAND_FK_CTRL_DEFAULT"] = _constants.LEFT_HAND_FK_CTRL_DEFAULT
        globals()["LEFT_HAND_IK_CTRL_DEFAULT"] = _constants.LEFT_HAND_IK_CTRL_DEFAULT
        globals()["RIGHT_CLAVICLE_CTRL_DEFAULT"] = _constants.RIGHT_CLAVICLE_CTRL_DEFAULT
        globals()["RIGHT_SHOULDER_CTRL_DEFAULT"] = _constants.RIGHT_SHOULDER_CTRL_DEFAULT
        globals()["RIGHT_ELBOW_CTRL_DEFAULT"] = _constants.RIGHT_ELBOW_CTRL_DEFAULT
        globals()["RIGHT_HAND_FK_CTRL_DEFAULT"] = _constants.RIGHT_HAND_FK_CTRL_DEFAULT
        globals()["RIGHT_HAND_IK_CTRL_DEFAULT"] = _constants.RIGHT_HAND_IK_CTRL_DEFAULT
        globals()["LEFT_HIP_CTRL_DEFAULT"] = _constants.LEFT_HIP_CTRL_DEFAULT
        globals()["LEFT_KNEE_CTRL_DEFAULT"] = _constants.LEFT_KNEE_CTRL_DEFAULT
        globals()["LEFT_ANKLE_FK_CTRL_DEFAULT"] = _constants.LEFT_ANKLE_FK_CTRL_DEFAULT
        globals()["LEFT_ANKLE_IK_CTRL_DEFAULT"] = _constants.LEFT_ANKLE_IK_CTRL_DEFAULT
        globals()["RIGHT_HIP_CTRL_DEFAULT"] = _constants.RIGHT_HIP_CTRL_DEFAULT
        globals()["RIGHT_KNEE_CTRL_DEFAULT"] = _constants.RIGHT_KNEE_CTRL_DEFAULT
        globals()["RIGHT_ANKLE_FK_CTRL_DEFAULT"] = _constants.RIGHT_ANKLE_FK_CTRL_DEFAULT
        globals()["RIGHT_ANKLE_IK_CTRL_DEFAULT"] = _constants.RIGHT_ANKLE_IK_CTRL_DEFAULT
        globals()["LEFT_HAND_THUMB_CTRL_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_THUMB_CTRL_LIST_DEFAULT
        )
        globals()["LEFT_HAND_INDEX_CTRL_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_INDEX_CTRL_LIST_DEFAULT
        )
        globals()["LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT
        )
        globals()["LEFT_HAND_RING_CTRL_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_RING_CTRL_LIST_DEFAULT
        )
        globals()["LEFT_HAND_PINKY_CTRL_LIST_DEFAULT"] = (
            _constants.LEFT_HAND_PINKY_CTRL_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_RING_CTRL_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_RING_CTRL_LIST_DEFAULT
        )
        globals()["RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT"] = (
            _constants.RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT
        )
        globals()["HUMAN_IK_JOINT_MAP"] = _constants.HUMAN_IK_JOINT_MAP
        globals()["HUMAN_IK_CTRL_MAP"] = _constants.HUMAN_IK_CTRL_MAP

        # Populate backward compatibility exports from rig templates
        globals()["ARISE_HIK_DATA"] = _rig_templates.ARISE_HIK_DATA
        globals()["ROKOKO_HIK_DATA"] = _rig_templates.ROKOKO_HIK_DATA
        globals()["ADVANCED_SKELETON_DATA"] = _rig_templates.ADVANCED_SKELETON_DATA

        # Try to import Maya-dependent modules (optional)
        try:
            from . import control_mapper as _control_mapper
            from . import mel_interface as _mel_interface
            from . import pose_utils as _pose_utils
            from . import skeleton_mapper as _skeleton_mapper

            globals()["mel_interface"] = _mel_interface
            globals()["pose_utils"] = _pose_utils
            globals()["skeleton_mapper"] = _skeleton_mapper
            globals()["control_mapper"] = _control_mapper
            _human_ik_available = True
        except ImportError as e:
            # Maya modules not available, but constants are still usable
            print(f"Warning: Maya-dependent human_ik modules unavailable - {e}")
            _human_ik_available = False

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

        # Get module references from globals (set by _initialize_human_ik)
        _mel_interface = globals()["mel_interface"]
        _pose_utils = globals()["pose_utils"]
        _skeleton_mapper = globals()["skeleton_mapper"]
        _control_mapper = globals()["control_mapper"]
        _rig_templates = globals()["rig_templates"]

        # Create component instances
        self._mel_interface = _mel_interface.MelInterface()
        self._pose_utils = _pose_utils.PoseUtils()
        self._skeleton_mapper = _skeleton_mapper.SkeletonMapper(character_name)
        self._control_mapper = _control_mapper.ControlMapper(character_name)

        # Get rig template data
        rig_definition = {
            "arise": _rig_templates.ARISE_HIK_DATA,
            "rokoko": _rig_templates.ROKOKO_HIK_DATA,
            "advanced_skeleton": _rig_templates.ADVANCED_SKELETON_DATA,
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
    """Lazy loading of human_ik submodules and constants.

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

    # List of backward compatibility constants
    _constants = [
        # Joint names
        "REFERENCE_JOINT_DEFAULT",
        "HIP_JOINT_DEFAULT",
        "SPINE_JOINT_LIST_DEFAULT",
        "NECK_JOINT_LIST_DEFAULT",
        "HEAD_JOINT_DEFAULT",
        "LEFT_ARM_JOINT_LIST_DEFAULT",
        "LEFT_LEG_JOINT_LIST_DEFAULT",
        "RIGHT_ARM_JOINT_LIST_DEFAULT",
        "RIGHT_LEG_JOINT_LIST_DEFAULT",
        "LEFT_HAND_THUMB_JOINT_LIST_DEFAULT",
        "LEFT_HAND_INDEX_JOINT_LIST_DEFAULT",
        "LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT",
        "LEFT_HAND_RING_JOINT_LIST_DEFAULT",
        "LEFT_HAND_PINKY_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_RING_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT",
        # Control names
        "HIP_CTRL_DEFAULT",
        "SPINE_CTRL_LIST_DEFAULT",
        "CHEST_CTRL_DEFAULT",
        "NECK_CTRL_DEFAULT",
        "HEAD_CTRL_DEFAULT",
        "LEFT_CLAVICLE_CTRL_DEFAULT",
        "LEFT_SHOULDER_CTRL_DEFAULT",
        "LEFT_ELBOW_CTRL_DEFAULT",
        "LEFT_HAND_FK_CTRL_DEFAULT",
        "LEFT_HAND_IK_CTRL_DEFAULT",
        "RIGHT_CLAVICLE_CTRL_DEFAULT",
        "RIGHT_SHOULDER_CTRL_DEFAULT",
        "RIGHT_ELBOW_CTRL_DEFAULT",
        "RIGHT_HAND_FK_CTRL_DEFAULT",
        "RIGHT_HAND_IK_CTRL_DEFAULT",
        "LEFT_HIP_CTRL_DEFAULT",
        "LEFT_KNEE_CTRL_DEFAULT",
        "LEFT_ANKLE_FK_CTRL_DEFAULT",
        "LEFT_ANKLE_IK_CTRL_DEFAULT",
        "RIGHT_HIP_CTRL_DEFAULT",
        "RIGHT_KNEE_CTRL_DEFAULT",
        "RIGHT_ANKLE_FK_CTRL_DEFAULT",
        "RIGHT_ANKLE_IK_CTRL_DEFAULT",
        "LEFT_HAND_THUMB_CTRL_LIST_DEFAULT",
        "LEFT_HAND_INDEX_CTRL_LIST_DEFAULT",
        "LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT",
        "LEFT_HAND_RING_CTRL_LIST_DEFAULT",
        "LEFT_HAND_PINKY_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_RING_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT",
        # Maps and templates
        "HUMAN_IK_JOINT_MAP",
        "HUMAN_IK_CTRL_MAP",
        "ARISE_HIK_DATA",
        "ROKOKO_HIK_DATA",
        "ADVANCED_SKELETON_DATA",
    ]

    # Handle submodule access
    if name in _submodules:
        if _initialize_human_ik():
            return globals()[name]
        else:
            raise AttributeError(
                f"human_ik submodule '{name}' could not be loaded - initialization failed"
            )

    # Handle constant access (backward compatibility)
    if name in _constants:
        if _initialize_human_ik():
            return globals()[name]
        else:
            raise AttributeError(
                f"human_ik constant '{name}' could not be loaded - initialization failed"
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

    _constants = [
        # Joint names
        "REFERENCE_JOINT_DEFAULT",
        "HIP_JOINT_DEFAULT",
        "SPINE_JOINT_LIST_DEFAULT",
        "NECK_JOINT_LIST_DEFAULT",
        "HEAD_JOINT_DEFAULT",
        "LEFT_ARM_JOINT_LIST_DEFAULT",
        "LEFT_LEG_JOINT_LIST_DEFAULT",
        "RIGHT_ARM_JOINT_LIST_DEFAULT",
        "RIGHT_LEG_JOINT_LIST_DEFAULT",
        "LEFT_HAND_THUMB_JOINT_LIST_DEFAULT",
        "LEFT_HAND_INDEX_JOINT_LIST_DEFAULT",
        "LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT",
        "LEFT_HAND_RING_JOINT_LIST_DEFAULT",
        "LEFT_HAND_PINKY_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_RING_JOINT_LIST_DEFAULT",
        "RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT",
        # Control names
        "HIP_CTRL_DEFAULT",
        "SPINE_CTRL_LIST_DEFAULT",
        "CHEST_CTRL_DEFAULT",
        "NECK_CTRL_DEFAULT",
        "HEAD_CTRL_DEFAULT",
        "LEFT_CLAVICLE_CTRL_DEFAULT",
        "LEFT_SHOULDER_CTRL_DEFAULT",
        "LEFT_ELBOW_CTRL_DEFAULT",
        "LEFT_HAND_FK_CTRL_DEFAULT",
        "LEFT_HAND_IK_CTRL_DEFAULT",
        "RIGHT_CLAVICLE_CTRL_DEFAULT",
        "RIGHT_SHOULDER_CTRL_DEFAULT",
        "RIGHT_ELBOW_CTRL_DEFAULT",
        "RIGHT_HAND_FK_CTRL_DEFAULT",
        "RIGHT_HAND_IK_CTRL_DEFAULT",
        "LEFT_HIP_CTRL_DEFAULT",
        "LEFT_KNEE_CTRL_DEFAULT",
        "LEFT_ANKLE_FK_CTRL_DEFAULT",
        "LEFT_ANKLE_IK_CTRL_DEFAULT",
        "RIGHT_HIP_CTRL_DEFAULT",
        "RIGHT_KNEE_CTRL_DEFAULT",
        "RIGHT_ANKLE_FK_CTRL_DEFAULT",
        "RIGHT_ANKLE_IK_CTRL_DEFAULT",
        "LEFT_HAND_THUMB_CTRL_LIST_DEFAULT",
        "LEFT_HAND_INDEX_CTRL_LIST_DEFAULT",
        "LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT",
        "LEFT_HAND_RING_CTRL_LIST_DEFAULT",
        "LEFT_HAND_PINKY_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_RING_CTRL_LIST_DEFAULT",
        "RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT",
        # Maps and templates
        "HUMAN_IK_JOINT_MAP",
        "HUMAN_IK_CTRL_MAP",
        "ARISE_HIK_DATA",
        "ROKOKO_HIK_DATA",
        "ADVANCED_SKELETON_DATA",
    ]

    return sorted(
        list(globals().keys()) + _submodules + _constants + ["is_available", "HumanIK"]
    )
