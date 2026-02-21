"""Unit tests for HumanIK refactoring.

Tests the modular HumanIK components to verify:
1. All constants are accessible
2. HumanIK class instantiates correctly
3. All methods exist and have correct signatures
4. Lazy loading works properly
5. Backward compatibility is maintained
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestConstantsModule:
    """Test suite for human_ik.constants module."""

    def test_constants_module_imports(self):
        """Test that constants module can be imported directly."""
        # Import the actual constants module file
        import mayaLib.rigLib.utils.human_ik.constants as constants_module

        # Verify the module was loaded and has expected attributes
        assert constants_module is not None
        assert hasattr(constants_module, "HUMAN_IK_JOINT_MAP")
        assert hasattr(constants_module, "HUMAN_IK_CTRL_MAP")

    def test_joint_name_constants_exist(self):
        """Test that all joint name constants are defined."""
        from mayaLib.rigLib.utils.human_ik.constants import (
            REFERENCE_JOINT_DEFAULT,
            HIP_JOINT_DEFAULT,
            HEAD_JOINT_DEFAULT,
            SPINE_JOINT_LIST_DEFAULT,
            NECK_JOINT_LIST_DEFAULT,
            LEFT_ARM_JOINT_LIST_DEFAULT,
            LEFT_LEG_JOINT_LIST_DEFAULT,
            RIGHT_ARM_JOINT_LIST_DEFAULT,
            RIGHT_LEG_JOINT_LIST_DEFAULT,
        )

        # Verify they are strings or lists
        assert isinstance(REFERENCE_JOINT_DEFAULT, str)
        assert isinstance(HIP_JOINT_DEFAULT, str)
        assert isinstance(HEAD_JOINT_DEFAULT, str)
        assert isinstance(SPINE_JOINT_LIST_DEFAULT, list)
        assert isinstance(NECK_JOINT_LIST_DEFAULT, list)
        assert isinstance(LEFT_ARM_JOINT_LIST_DEFAULT, list)
        assert isinstance(LEFT_LEG_JOINT_LIST_DEFAULT, list)
        assert isinstance(RIGHT_ARM_JOINT_LIST_DEFAULT, list)
        assert isinstance(RIGHT_LEG_JOINT_LIST_DEFAULT, list)

    def test_control_name_constants_exist(self):
        """Test that all control name constants are defined."""
        from mayaLib.rigLib.utils.human_ik.constants import (
            HIP_CTRL_DEFAULT,
            CHEST_CTRL_DEFAULT,
            NECK_CTRL_DEFAULT,
            HEAD_CTRL_DEFAULT,
            SPINE_CTRL_LIST_DEFAULT,
            LEFT_CLAVICLE_CTRL_DEFAULT,
            LEFT_SHOULDER_CTRL_DEFAULT,
            LEFT_ELBOW_CTRL_DEFAULT,
            LEFT_HAND_FK_CTRL_DEFAULT,
            LEFT_HAND_IK_CTRL_DEFAULT,
        )

        # Verify they are strings or lists
        assert isinstance(HIP_CTRL_DEFAULT, str)
        assert isinstance(CHEST_CTRL_DEFAULT, str)
        assert isinstance(NECK_CTRL_DEFAULT, str)
        assert isinstance(HEAD_CTRL_DEFAULT, str)
        assert isinstance(SPINE_CTRL_LIST_DEFAULT, list)
        assert isinstance(LEFT_CLAVICLE_CTRL_DEFAULT, str)
        assert isinstance(LEFT_SHOULDER_CTRL_DEFAULT, str)
        assert isinstance(LEFT_ELBOW_CTRL_DEFAULT, str)
        assert isinstance(LEFT_HAND_FK_CTRL_DEFAULT, str)
        assert isinstance(LEFT_HAND_IK_CTRL_DEFAULT, str)

    def test_human_ik_joint_map_exists(self):
        """Test that HUMAN_IK_JOINT_MAP constant exists and is a dict."""
        from mayaLib.rigLib.utils.human_ik.constants import HUMAN_IK_JOINT_MAP

        assert isinstance(HUMAN_IK_JOINT_MAP, dict)
        assert len(HUMAN_IK_JOINT_MAP) > 0

    def test_human_ik_ctrl_map_exists(self):
        """Test that HUMAN_IK_CTRL_MAP constant exists and is a dict."""
        from mayaLib.rigLib.utils.human_ik.constants import HUMAN_IK_CTRL_MAP

        assert isinstance(HUMAN_IK_CTRL_MAP, dict)
        assert len(HUMAN_IK_CTRL_MAP) > 0

    def test_finger_joint_constants_exist(self):
        """Test that finger joint constants are defined."""
        from mayaLib.rigLib.utils.human_ik.constants import (
            LEFT_HAND_THUMB_JOINT_LIST_DEFAULT,
            LEFT_HAND_INDEX_JOINT_LIST_DEFAULT,
            LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT,
            LEFT_HAND_RING_JOINT_LIST_DEFAULT,
            LEFT_HAND_PINKY_JOINT_LIST_DEFAULT,
            RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT,
            RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT,
        )

        # Verify they are all lists
        assert isinstance(LEFT_HAND_THUMB_JOINT_LIST_DEFAULT, list)
        assert isinstance(LEFT_HAND_INDEX_JOINT_LIST_DEFAULT, list)
        assert isinstance(LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT, list)
        assert isinstance(LEFT_HAND_RING_JOINT_LIST_DEFAULT, list)
        assert isinstance(LEFT_HAND_PINKY_JOINT_LIST_DEFAULT, list)
        assert isinstance(RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT, list)
        assert isinstance(RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT, list)


@pytest.mark.unit
class TestRigTemplates:
    """Test suite for human_ik.rig_templates module."""

    def test_rig_templates_module_imports(self):
        """Test that rig_templates module can be imported directly."""
        # Import the actual rig_templates module file
        import mayaLib.rigLib.utils.human_ik.rig_templates as rig_templates_module

        # Verify the module was loaded and has expected attributes
        assert rig_templates_module is not None
        assert hasattr(rig_templates_module, "ARISE_HIK_DATA")
        assert hasattr(rig_templates_module, "ROKOKO_HIK_DATA")

    def test_arise_hik_data_exists(self):
        """Test that ARISE_HIK_DATA template exists and has correct structure."""
        from mayaLib.rigLib.utils.human_ik.rig_templates import ARISE_HIK_DATA

        assert isinstance(ARISE_HIK_DATA, dict)
        assert "joints" in ARISE_HIK_DATA
        assert "ctrls" in ARISE_HIK_DATA
        assert isinstance(ARISE_HIK_DATA["joints"], dict)
        assert isinstance(ARISE_HIK_DATA["ctrls"], dict)

    def test_rokoko_hik_data_exists(self):
        """Test that ROKOKO_HIK_DATA template exists and has correct structure."""
        from mayaLib.rigLib.utils.human_ik.rig_templates import ROKOKO_HIK_DATA

        assert isinstance(ROKOKO_HIK_DATA, dict)
        assert "joints" in ROKOKO_HIK_DATA
        assert isinstance(ROKOKO_HIK_DATA["joints"], dict)

    def test_advanced_skeleton_data_exists(self):
        """Test that ADVANCED_SKELETON_DATA template exists and has correct structure."""
        from mayaLib.rigLib.utils.human_ik.rig_templates import ADVANCED_SKELETON_DATA

        assert isinstance(ADVANCED_SKELETON_DATA, dict)
        assert "joints" in ADVANCED_SKELETON_DATA
        assert isinstance(ADVANCED_SKELETON_DATA["joints"], dict)

    def test_all_templates_available(self):
        """Test that all three rig templates are available."""
        from mayaLib.rigLib.utils.human_ik.rig_templates import (
            ARISE_HIK_DATA,
            ROKOKO_HIK_DATA,
            ADVANCED_SKELETON_DATA,
        )

        templates = [ARISE_HIK_DATA, ROKOKO_HIK_DATA, ADVANCED_SKELETON_DATA]
        for template in templates:
            assert isinstance(template, dict)
            assert len(template) > 0


@pytest.mark.unit
class TestMelInterface:
    """Test suite for human_ik.mel_interface.MelInterface class."""

    def test_mel_interface_imports(self):
        """Test that MelInterface class can be imported."""
        from mayaLib.rigLib.utils.human_ik.mel_interface import MelInterface

        assert MelInterface is not None

    def test_mel_interface_instantiates(self):
        """Test that MelInterface can be instantiated."""
        from mayaLib.rigLib.utils.human_ik.mel_interface import MelInterface

        mel_interface = MelInterface("test_character")
        assert mel_interface is not None
        assert mel_interface.character_name == "test_character"

    def test_mel_interface_has_required_methods(self):
        """Test that MelInterface has all required methods."""
        from mayaLib.rigLib.utils.human_ik.mel_interface import MelInterface

        mel_interface = MelInterface("test_character")

        # Verify all 6 MEL command wrapper methods exist
        assert hasattr(mel_interface, "open_character_controls_tool")
        assert hasattr(mel_interface, "create_character")
        assert hasattr(mel_interface, "set_character_object")
        assert hasattr(mel_interface, "load_custom_rig_ui_configuration")
        assert hasattr(mel_interface, "create_custom_rig")
        assert hasattr(mel_interface, "assign_custom_rig_effector")

        # Verify they are callable
        assert callable(mel_interface.open_character_controls_tool)
        assert callable(mel_interface.create_character)
        assert callable(mel_interface.set_character_object)


@pytest.mark.unit
class TestPoseUtils:
    """Test suite for human_ik.pose_utils.PoseUtils class."""

    def test_pose_utils_imports(self):
        """Test that PoseUtils class can be imported."""
        from mayaLib.rigLib.utils.human_ik.pose_utils import PoseUtils

        assert PoseUtils is not None

    def test_pose_utils_instantiates(self):
        """Test that PoseUtils can be instantiated."""
        from mayaLib.rigLib.utils.human_ik.pose_utils import PoseUtils

        pose_utils = PoseUtils()
        assert pose_utils is not None

    def test_pose_utils_has_required_methods(self):
        """Test that PoseUtils has all required methods."""
        from mayaLib.rigLib.utils.human_ik.pose_utils import PoseUtils

        pose_utils = PoseUtils()

        # Verify all 3 T-pose methods exist
        assert hasattr(pose_utils, "arise_t_pose")
        assert hasattr(pose_utils, "arms_parallel_to_grid")
        assert hasattr(pose_utils, "go_to_t_pose")

        # Verify they are callable
        assert callable(pose_utils.arise_t_pose)
        assert callable(pose_utils.arms_parallel_to_grid)
        assert callable(pose_utils.go_to_t_pose)


@pytest.mark.unit
class TestSkeletonMapper:
    """Test suite for human_ik.skeleton_mapper.SkeletonMapper class."""

    def test_skeleton_mapper_imports(self):
        """Test that SkeletonMapper class can be imported."""
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper

        assert SkeletonMapper is not None

    def test_skeleton_mapper_instantiates(self):
        """Test that SkeletonMapper can be instantiated."""
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper

        skeleton_mapper = SkeletonMapper("test_character")
        assert skeleton_mapper is not None
        assert skeleton_mapper.character_name == "test_character"

    def test_skeleton_mapper_has_core_methods(self):
        """Test that SkeletonMapper has core skeleton mapping methods."""
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper

        skeleton_mapper = SkeletonMapper("test_character")

        # Core methods
        assert hasattr(skeleton_mapper, "set_character_object")
        assert hasattr(skeleton_mapper, "define_skeleton")
        assert hasattr(skeleton_mapper, "add_reference")
        assert hasattr(skeleton_mapper, "add_hip")
        assert hasattr(skeleton_mapper, "add_spine")
        assert hasattr(skeleton_mapper, "add_neck")
        assert hasattr(skeleton_mapper, "add_head")

    def test_skeleton_mapper_has_limb_methods(self):
        """Test that SkeletonMapper has limb mapping methods."""
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper

        skeleton_mapper = SkeletonMapper("test_character")

        # Limb methods
        assert hasattr(skeleton_mapper, "add_left_arm")
        assert hasattr(skeleton_mapper, "add_right_arm")
        assert hasattr(skeleton_mapper, "add_left_leg")
        assert hasattr(skeleton_mapper, "add_right_leg")

        # Individual joint methods
        assert hasattr(skeleton_mapper, "add_left_shoulder")
        assert hasattr(skeleton_mapper, "add_left_arm_joint")
        assert hasattr(skeleton_mapper, "add_left_fore_arm")
        assert hasattr(skeleton_mapper, "add_left_hand_joint")

    def test_skeleton_mapper_has_finger_methods(self):
        """Test that SkeletonMapper has finger mapping methods."""
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper

        skeleton_mapper = SkeletonMapper("test_character")

        # Finger methods
        assert hasattr(skeleton_mapper, "add_left_hand_thumb")
        assert hasattr(skeleton_mapper, "add_left_hand_index")
        assert hasattr(skeleton_mapper, "add_left_hand_middle")
        assert hasattr(skeleton_mapper, "add_left_hand_ring")
        assert hasattr(skeleton_mapper, "add_left_hand_pinky")
        assert hasattr(skeleton_mapper, "add_right_hand_thumb")
        assert hasattr(skeleton_mapper, "add_right_hand_index")


@pytest.mark.unit
class TestControlMapper:
    """Test suite for human_ik.control_mapper.ControlMapper class."""

    def test_control_mapper_imports(self):
        """Test that ControlMapper class can be imported."""
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        assert ControlMapper is not None

    def test_control_mapper_instantiates(self):
        """Test that ControlMapper can be instantiated."""
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        control_mapper = ControlMapper("test_character")
        assert control_mapper is not None
        assert control_mapper.character_name == "test_character"

    def test_control_mapper_has_core_methods(self):
        """Test that ControlMapper has core control mapping methods."""
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        control_mapper = ControlMapper("test_character")

        # Core methods
        assert hasattr(control_mapper, "add_ctrl")
        assert hasattr(control_mapper, "load_custom_rig_template")
        assert hasattr(control_mapper, "create_custom_rig_mapping")
        assert hasattr(control_mapper, "define_custom_ctrls")

    def test_control_mapper_has_body_control_methods(self):
        """Test that ControlMapper has body control mapping methods."""
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        control_mapper = ControlMapper("test_character")

        # Body control methods
        assert hasattr(control_mapper, "add_hip_ctrl")
        assert hasattr(control_mapper, "add_spine_ctrl")
        assert hasattr(control_mapper, "add_chest_ctrl")
        assert hasattr(control_mapper, "add_neck_ctrl")
        assert hasattr(control_mapper, "add_head_ctrl")

    def test_control_mapper_has_limb_control_methods(self):
        """Test that ControlMapper has limb control mapping methods."""
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        control_mapper = ControlMapper("test_character")

        # Limb control methods
        assert hasattr(control_mapper, "add_left_clavicle_ctrl")
        assert hasattr(control_mapper, "add_left_shoulder_ctrl")
        assert hasattr(control_mapper, "add_left_elbow_ctrl")
        assert hasattr(control_mapper, "add_left_hand_ctrl")
        assert hasattr(control_mapper, "add_left_hip_ctrl")
        assert hasattr(control_mapper, "add_left_knee_ctrl")
        assert hasattr(control_mapper, "add_left_ankle_ctrl")

    def test_control_mapper_has_finger_control_methods(self):
        """Test that ControlMapper has finger control mapping methods."""
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        control_mapper = ControlMapper("test_character")

        # Finger control methods
        assert hasattr(control_mapper, "add_left_hand_thumb_ctrl")
        assert hasattr(control_mapper, "add_left_hand_index_ctrl")
        assert hasattr(control_mapper, "add_left_hand_middle_ctrl")
        assert hasattr(control_mapper, "add_left_hand_ring_ctrl")
        assert hasattr(control_mapper, "add_left_hand_pinky_ctrl")
        assert hasattr(control_mapper, "add_right_hand_thumb_ctrl")


@pytest.mark.unit
class TestHumanIKFacade:
    """Test suite for the unified HumanIK facade class."""

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_imports(self, mock_control, mock_skeleton, mock_pose, mock_mel):
        """Test that HumanIK facade class can be imported."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        assert HumanIK is not None

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_instantiates_with_arise_template(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK facade instantiates with arise template."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        # Mock the component instances
        mock_mel_instance = MagicMock()
        mock_pose_instance = MagicMock()
        mock_skeleton_instance = MagicMock()
        mock_control_instance = MagicMock()

        mock_mel.return_value = mock_mel_instance
        mock_pose.return_value = mock_pose_instance
        mock_skeleton.return_value = mock_skeleton_instance
        mock_control.return_value = mock_control_instance

        # Instantiate HumanIK
        hik = HumanIK("test_character", rig_template="arise", auto_t_pose=False)

        assert hik is not None
        assert hik.character_name == "test_character"
        assert hik.rig_data is not None
        assert "joints" in hik.rig_data

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_instantiates_with_rokoko_template(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK facade instantiates with rokoko template."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        # Mock the component instances
        mock_mel_instance = MagicMock()
        mock_pose_instance = MagicMock()
        mock_skeleton_instance = MagicMock()
        mock_control_instance = MagicMock()

        mock_mel.return_value = mock_mel_instance
        mock_pose.return_value = mock_pose_instance
        mock_skeleton.return_value = mock_skeleton_instance
        mock_control.return_value = mock_control_instance

        # Instantiate HumanIK
        hik = HumanIK("test_character", rig_template="rokoko", auto_t_pose=False)

        assert hik is not None
        assert hik.character_name == "test_character"

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_raises_error_for_invalid_template(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK raises ValueError for invalid template."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        with pytest.raises(ValueError, match="Unknown rig template"):
            HumanIK("test_character", rig_template="invalid_template", auto_t_pose=False)

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_calls_t_pose_when_auto_t_pose_true(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK calls go_to_t_pose when auto_t_pose is True."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        # Mock the component instances
        mock_mel_instance = MagicMock()
        mock_pose_instance = MagicMock()
        mock_skeleton_instance = MagicMock()
        mock_control_instance = MagicMock()

        mock_mel.return_value = mock_mel_instance
        mock_pose.return_value = mock_pose_instance
        mock_skeleton.return_value = mock_skeleton_instance
        mock_control.return_value = mock_control_instance

        # Instantiate HumanIK with auto_t_pose=True
        HumanIK("test_character", rig_template="arise", auto_t_pose=True)

        # Verify go_to_t_pose was called
        mock_pose_instance.go_to_t_pose.assert_called_once()

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_delegates_to_skeleton_mapper(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK delegates skeleton methods to SkeletonMapper."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        # Mock the component instances
        mock_mel_instance = MagicMock()
        mock_pose_instance = MagicMock()
        mock_skeleton_instance = MagicMock()
        mock_control_instance = MagicMock()

        mock_mel.return_value = mock_mel_instance
        mock_pose.return_value = mock_pose_instance
        mock_skeleton.return_value = mock_skeleton_instance
        mock_control.return_value = mock_control_instance

        # Add a test method to skeleton mapper
        mock_skeleton_instance.add_hip = MagicMock()

        hik = HumanIK("test_character", rig_template="arise", auto_t_pose=False)

        # Access method via facade
        assert hasattr(hik, "add_hip")
        assert hik.add_hip == mock_skeleton_instance.add_hip

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_delegates_to_control_mapper(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK delegates control methods to ControlMapper."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        # Mock the component instances with spec to avoid hasattr issues
        mock_mel_instance = MagicMock(spec=["open_character_controls_tool", "create_character"])
        mock_pose_instance = MagicMock(spec=["go_to_t_pose"])
        # SkeletonMapper should NOT have add_hip_ctrl
        mock_skeleton_instance = MagicMock(spec=["define_skeleton", "add_hip", "add_spine"])
        mock_control_instance = MagicMock(spec=["define_custom_ctrls", "add_hip_ctrl"])

        mock_mel.return_value = mock_mel_instance
        mock_pose.return_value = mock_pose_instance
        mock_skeleton.return_value = mock_skeleton_instance
        mock_control.return_value = mock_control_instance

        # Add a test method to control mapper
        mock_control_instance.add_hip_ctrl = MagicMock()

        hik = HumanIK("test_character", rig_template="arise", auto_t_pose=False)

        # Access method via facade - should delegate to control mapper
        assert hasattr(hik, "add_hip_ctrl")
        # Call the method to verify delegation
        _ = hik.add_hip_ctrl
        # Verify it came from control mapper (not skeleton mapper)
        assert hik.add_hip_ctrl == mock_control_instance.add_hip_ctrl

    @patch("mayaLib.rigLib.utils.human_ik.mel_interface.MelInterface")
    @patch("mayaLib.rigLib.utils.human_ik.pose_utils.PoseUtils")
    @patch("mayaLib.rigLib.utils.human_ik.skeleton_mapper.SkeletonMapper")
    @patch("mayaLib.rigLib.utils.human_ik.control_mapper.ControlMapper")
    def test_human_ik_raises_attribute_error_for_nonexistent_method(
        self, mock_control, mock_skeleton, mock_pose, mock_mel
    ):
        """Test that HumanIK raises AttributeError for non-existent attributes."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        # Create mock instances with limited spec to prevent hasattr from succeeding
        # Include only the methods needed for initialization
        mock_mel_instance = MagicMock(spec=["open_character_controls_tool", "create_character"])
        mock_pose_instance = MagicMock(spec=["go_to_t_pose"])
        mock_skeleton_instance = MagicMock(spec=["define_skeleton"])
        mock_control_instance = MagicMock(spec=["define_custom_ctrls"])

        mock_mel.return_value = mock_mel_instance
        mock_pose.return_value = mock_pose_instance
        mock_skeleton.return_value = mock_skeleton_instance
        mock_control.return_value = mock_control_instance

        hik = HumanIK("test_character", rig_template="arise", auto_t_pose=False)

        # Attempt to access non-existent attribute - should raise AttributeError
        # because none of the mocked components have 'nonexistent_method' in their spec
        with pytest.raises(AttributeError, match="'HumanIK' object has no attribute"):
            _ = hik.nonexistent_method


@pytest.mark.unit
class TestLazyLoading:
    """Test suite for lazy loading functionality."""

    def test_is_available_function_exists(self):
        """Test that is_available() function exists."""
        from mayaLib.rigLib.utils.human_ik import is_available

        assert callable(is_available)

    def test_is_available_returns_true(self):
        """Test that is_available() returns True after initialization."""
        from mayaLib.rigLib.utils.human_ik import is_available

        result = is_available()
        assert result is True

    def test_submodule_lazy_loading_via_getattr(self):
        """Test that submodules are lazily loaded via __getattr__."""
        import mayaLib.rigLib.utils.human_ik as hik

        # Access constants submodule via lazy loading
        constants = hik.constants
        assert constants is not None

        # Access other submodules
        rig_templates = hik.rig_templates
        assert rig_templates is not None

        mel_interface = hik.mel_interface
        assert mel_interface is not None

        pose_utils = hik.pose_utils
        assert pose_utils is not None

        skeleton_mapper = hik.skeleton_mapper
        assert skeleton_mapper is not None

        control_mapper = hik.control_mapper
        assert control_mapper is not None

    def test_module_dir_includes_submodules(self):
        """Test that __dir__() includes all submodules."""
        import mayaLib.rigLib.utils.human_ik as hik

        dir_output = dir(hik)

        # Verify all expected submodules are in dir output
        expected_modules = [
            "constants",
            "rig_templates",
            "mel_interface",
            "pose_utils",
            "skeleton_mapper",
            "control_mapper",
            "HumanIK",
            "is_available",
        ]

        for module_name in expected_modules:
            assert module_name in dir_output

    def test_invalid_submodule_raises_attribute_error(self):
        """Test that accessing invalid submodule raises AttributeError."""
        import mayaLib.rigLib.utils.human_ik as hik

        with pytest.raises(AttributeError, match="has no attribute"):
            _ = hik.nonexistent_module


@pytest.mark.unit
class TestBackwardCompatibility:
    """Test suite for backward compatibility verification."""

    def test_import_human_ik_from_main_module(self):
        """Test importing HumanIK from main human_ik module."""
        from mayaLib.rigLib.utils.human_ik import HumanIK

        assert HumanIK is not None

    def test_import_constants_from_submodule(self):
        """Test importing constants from human_ik.constants submodule."""
        from mayaLib.rigLib.utils.human_ik.constants import (
            HUMAN_IK_JOINT_MAP,
            HUMAN_IK_CTRL_MAP,
        )

        assert HUMAN_IK_JOINT_MAP is not None
        assert HUMAN_IK_CTRL_MAP is not None

    def test_import_templates_from_submodule(self):
        """Test importing templates from human_ik.rig_templates submodule."""
        from mayaLib.rigLib.utils.human_ik.rig_templates import (
            ARISE_HIK_DATA,
            ROKOKO_HIK_DATA,
            ADVANCED_SKELETON_DATA,
        )

        assert ARISE_HIK_DATA is not None
        assert ROKOKO_HIK_DATA is not None
        assert ADVANCED_SKELETON_DATA is not None

    def test_import_all_component_classes(self):
        """Test importing all component classes from submodules."""
        from mayaLib.rigLib.utils.human_ik.mel_interface import MelInterface
        from mayaLib.rigLib.utils.human_ik.pose_utils import PoseUtils
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper

        assert MelInterface is not None
        assert PoseUtils is not None
        assert SkeletonMapper is not None
        assert ControlMapper is not None

    def test_lazy_loaded_modules_are_accessible(self):
        """Test that lazy-loaded modules are accessible via parent module."""
        import mayaLib.rigLib.utils.human_ik as hik

        # Access submodules via lazy loading
        assert hik.constants is not None
        assert hik.rig_templates is not None
        assert hik.mel_interface is not None
        assert hik.pose_utils is not None
        assert hik.skeleton_mapper is not None
        assert hik.control_mapper is not None

    def test_constants_accessible_from_main_module(self):
        """Test that key constants are accessible via lazy loading."""
        import mayaLib.rigLib.utils.human_ik as hik

        # Access constants via lazy-loaded constants module
        assert hasattr(hik.constants, "HUMAN_IK_JOINT_MAP")
        assert hasattr(hik.constants, "HUMAN_IK_CTRL_MAP")
        assert hasattr(hik.constants, "REFERENCE_JOINT_DEFAULT")
