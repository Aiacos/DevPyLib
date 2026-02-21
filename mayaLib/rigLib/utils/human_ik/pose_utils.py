"""Pose utility helpers for HumanIK T-pose setup and alignment."""

from __future__ import annotations

import importlib
import platform
import sys
from pathlib import Path

import pymel.core as pm

from mayaLib.rigLib.utils import joint as joint_utils
from mayaLib.rigLib.utils.human_ik.constants import (
    LEFT_CLAVICLE_CTRL_DEFAULT,
    LEFT_ELBOW_CTRL_DEFAULT,
    LEFT_HAND_FK_CTRL_DEFAULT,
    LEFT_SHOULDER_CTRL_DEFAULT,
    RIGHT_CLAVICLE_CTRL_DEFAULT,
    RIGHT_ELBOW_CTRL_DEFAULT,
    RIGHT_HAND_FK_CTRL_DEFAULT,
    RIGHT_SHOULDER_CTRL_DEFAULT,
)

__all__ = ["PoseUtils"]


class PoseUtils:
    """Utilities for setting up T-pose and character alignment for HumanIK rigs."""

    @staticmethod
    def arise_t_pose() -> None:
        """Set the character to a T pose using the Arise plug-in utilities.

        This method automatically detects the Maya plug-ins directory based on the
        current platform and loads the Arise utilities to apply a zero pose to all
        controls, effectively setting up a T-pose.

        Note:
            If the Arise utilities are not available, a warning is issued and the
            operation is skipped without raising an error.
        """
        # Get Maya plug-ins directory based on platform
        system = platform.system()
        if system == "Windows":
            maya_base = Path.home() / "Documents" / "maya"
        elif system == "Darwin":  # macOS
            maya_base = Path.home() / "Library" / "Preferences" / "Autodesk" / "maya"
        else:  # Linux
            maya_base = Path.home() / "maya"

        base_plugin_path = maya_base / "Plug-ins" / "arise_main"
        version_folder = f"py_{sys.version_info.major}_{sys.version_info.minor}"
        plugin_path = str(base_plugin_path / version_folder)

        if plugin_path not in sys.path:
            sys.path.append(plugin_path)

        try:
            arise_utils = importlib.import_module("arise.utils.ctrls_utils")
        except ImportError:
            pm.warning(
                "Arise zero pose utilities not available; skipping T pose alignment."
            )
            return

        arise_utils.apply_zero_pose_all(silent=True)

    @staticmethod
    def arms_parallel_to_grid(
        left_arm_transforms: list[str] | None = None,
        right_arm_transforms: list[str] | None = None,
    ) -> None:
        """Align arms parallel to the grid by adjusting their transforms.

        This method takes lists of transform names for the left and right arms
        and aligns them so they are parallel to the ground plane. If no transforms
        are provided, default Arise rig control names are used.

        Args:
            left_arm_transforms: Optional sequence of transforms for the left arm.
                Defaults to Arise rig left arm controls.
            right_arm_transforms: Optional sequence of transforms for the right arm.
                Defaults to Arise rig right arm controls.
        """
        left_arm_transforms = left_arm_transforms or [
            LEFT_CLAVICLE_CTRL_DEFAULT,
            LEFT_SHOULDER_CTRL_DEFAULT,
            LEFT_ELBOW_CTRL_DEFAULT,
            LEFT_HAND_FK_CTRL_DEFAULT,
        ]
        right_arm_transforms = right_arm_transforms or [
            RIGHT_CLAVICLE_CTRL_DEFAULT,
            RIGHT_SHOULDER_CTRL_DEFAULT,
            RIGHT_ELBOW_CTRL_DEFAULT,
            RIGHT_HAND_FK_CTRL_DEFAULT,
        ]
        joint_utils.set_arm_parallel_to_grid(left_arm_transforms)
        joint_utils.set_arm_parallel_to_grid(right_arm_transforms)

    @staticmethod
    def go_to_t_pose(template: str) -> None:
        """Set the character to the T pose.

        Depending on the template provided, this function sets the character
        to the T pose using either the Arise plugin utilities or by aligning
        the arms parallel to the grid.

        Args:
            template: The name of the template used to determine the method
                for setting the T pose. Use 'arise' to invoke Arise plugin
                utilities, or any other value to use the grid alignment method.
        """
        if template == "arise":
            # Use Arise plugin utilities to set T pose
            PoseUtils.arise_t_pose()
        else:
            # Set arms parallel to the grid
            PoseUtils.arms_parallel_to_grid()
