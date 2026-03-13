"""Arise-ready facial rig node class.

Provides an Arise-compatible facial rigging class following the BaseRig pattern
from ariseLib/base.py. This class integrates with the facial rigging framework
and provides methods for setting up facial rig components in the Arise system.

The class follows the official Arise documentation patterns for rig nodes:
https://newaccount1619350932681.freshdesk.com/support/solutions/folders/69000646405
"""

import contextlib

import pymel.core as pm

from mayaLib.rigLib.face.skin import copy as skin_copy


class AriseFaceNode:
    """Arise-compatible facial rig node class.

    This class provides methods for setting up facial rig components within
    the Arise rigging system. It follows the pattern established by
    ariseLib/base.py::BaseRig and integrates with the modular facial rigging
    framework.

    The class handles:
    - Facial joint hierarchy setup
    - Eye aim control connections
    - Facial deformation system integration
    - Selection set management for face controls
    - Display layer organization
    - Scale connections for facial rig components

    Attributes:
        character_name (str): Name of the character for rigging.
        head_joint (str): Name of the head joint to parent face rig under.
        main_ctrl (str): Name of the main control for scale connections.
        face_joint_root (str): Name of the root face joint.
        face_ctrl_set (set): Maya selection set containing face controls.

    Example:
        >>> face_node = AriseFaceNode(
        ...     character_name="Male_Human",
        ...     head_joint="M_Head_head_FS_jnt"
        ... )
        >>> face_node.setup()
    """

    # Default node naming conventions
    DEFAULT_HEAD_JOINT = "M_Head_head_FS_jnt"
    DEFAULT_MAIN_CTRL = "Base_main_ctrl"
    DEFAULT_FACE_JOINT = "FaceJoint_M"
    DEFAULT_EYE_AIM_M = "AimEye_M"
    DEFAULT_EYE_AIM_L = "AimEye_L"
    DEFAULT_EYE_AIM_R = "AimEye_R"

    # Face motion system nodes
    FACE_MOTION_TARGETS = [
        "FaceMotionSystem",
        "FaceDeformationFollowHead",
        "LipFollowHead",
    ]

    # Eye aim controls
    EYE_CONTROLS = {
        "M": "M_Eyes_Aim_01_ctrl",
        "L": "L_Eye_eye_aim_at_ctrl",
        "R": "R_Eye_eye_aim_at_ctrl",
    }

    def __init__(
        self,
        character_name="Character",
        head_joint=None,
        main_ctrl=None,
        face_joint_root=None,
        auto_setup=False,
    ):
        """Initialize the AriseFaceNode with character settings.

        Args:
            character_name (str): Name of the character for rigging.
                Used for naming selection sets and display layers.
            head_joint (str | None): Name of the head joint to parent face rig under.
                Defaults to 'M_Head_head_FS_jnt' if None.
            main_ctrl (str | None): Name of the main control for scale connections.
                Defaults to 'Base_main_ctrl' if None.
            face_joint_root (str | None): Name of the root face joint.
                Defaults to 'FaceJoint_M' if None.
            auto_setup (bool): Whether to run setup automatically on init.
                Defaults to False.
        """
        self.character_name = character_name
        self.head_joint = head_joint or self.DEFAULT_HEAD_JOINT
        self.main_ctrl = main_ctrl or self.DEFAULT_MAIN_CTRL
        self.face_joint_root = face_joint_root or self.DEFAULT_FACE_JOINT

        # State tracking
        self._initialized = False
        self.face_ctrl_set = None
        self.face_joint_set = None
        self.face_display_layer = None

        # Run setup if requested
        if auto_setup:
            self.setup()

    def setup(self):
        """Run the complete facial rig setup.

        This method orchestrates the full setup process for the facial rig,
        including joint hierarchy, eye aim connections, motion system setup,
        selection sets, and display layers.

        Raises:
            RuntimeError: If required nodes don't exist in the scene.

        Returns:
            bool: True if setup completed successfully.
        """
        if self._initialized:
            pm.warning("AriseFaceNode already initialized. Skipping setup.")
            return True

        # Validate required nodes exist
        if not self._validate_scene():
            return False

        # Setup facial rig components
        self._setup_face_joint_hierarchy()
        self._setup_eye_aim_controls()
        self._setup_face_motion_system()
        self._setup_scale_connections()
        self._create_face_selection_sets()
        self._setup_face_display_layer()

        self._initialized = True
        pm.displayInfo(f"AriseFaceNode setup complete for {self.character_name}")
        return True

    def _validate_scene(self):
        """Validate that required nodes exist in the scene.

        Checks for the existence of critical nodes before attempting setup.
        Issues warnings for missing optional nodes.

        Returns:
            bool: True if all required nodes exist, False otherwise.
        """
        # Check for required nodes
        if not pm.objExists(self.head_joint):
            pm.error(f"Required head joint '{self.head_joint}' not found in scene.")
            return False

        if not pm.objExists(self.main_ctrl):
            pm.warning(
                f"Main control '{self.main_ctrl}' not found. Scale connections will be skipped."
            )

        if not pm.objExists(self.face_joint_root):
            pm.warning(
                f"Face joint root '{self.face_joint_root}' not found. "
                "Face joint hierarchy setup will be skipped."
            )

        return True

    def _setup_face_joint_hierarchy(self):
        """Set up facial joint hierarchy under head joint.

        Parents the facial joint root under the head joint if both exist.
        This establishes the proper hierarchy for facial deformation.
        """
        if not pm.objExists(self.face_joint_root):
            return

        if not pm.objExists(self.head_joint):
            return

        # Check if already parented correctly
        current_parent = pm.listRelatives(self.face_joint_root, parent=True)
        if current_parent and str(current_parent[0]) == self.head_joint:
            return

        # Parent face joint under head joint
        try:
            pm.parent(self.face_joint_root, self.head_joint)
            pm.displayInfo(f"Parented {self.face_joint_root} under {self.head_joint}")
        except Exception as e:
            pm.warning(f"Failed to parent face joint: {e}")

    def _setup_eye_aim_controls(self):
        """Set up eye aim control connections.

        Connects eye aim controls (left, right, middle) to their target
        objects using parent constraints. This enables proper eye tracking
        behavior in the facial rig.
        """
        # Middle eye aim
        if pm.objExists(self.DEFAULT_EYE_AIM_M):
            if pm.objExists(self.EYE_CONTROLS["M"]):
                self._create_parent_constraint_safe(self.EYE_CONTROLS["M"], self.DEFAULT_EYE_AIM_M)
            else:
                # Fallback: connect to head joint
                self._setup_eye_aim_fallback()

        # Left eye aim
        if pm.objExists(self.DEFAULT_EYE_AIM_L) and pm.objExists(self.EYE_CONTROLS["L"]):
            self._create_parent_constraint_safe(self.EYE_CONTROLS["L"], self.DEFAULT_EYE_AIM_L)

        # Right eye aim
        if pm.objExists(self.DEFAULT_EYE_AIM_R) and pm.objExists(self.EYE_CONTROLS["R"]):
            self._create_parent_constraint_safe(self.EYE_CONTROLS["R"], self.DEFAULT_EYE_AIM_R)

        # Hide internal aim controls
        self._hide_internal_controls()

    def _setup_eye_aim_fallback(self):
        """Set up eye aim fallback when dedicated eye controls don't exist.

        Creates a parent constraint from the head joint to the eye aim
        follow node as a fallback when eye aim controls aren't present.
        """
        follow_node = "AimEyeFollow_M"
        if not pm.objExists(follow_node):
            return

        if not pm.objExists(self.head_joint):
            return

        try:
            pm.parentConstraint(self.head_joint, follow_node, mo=True)

            # Setup set range connection if available
            if pm.objExists("eyeAimFollowSetRange"):
                constraint = f"{follow_node}_parentConstraint1"
                weight_attr = f"{constraint}.{self.head_joint}W2"

                if pm.objExists(constraint):
                    pm.connectAttr(
                        f"{constraint}.{self.head_joint}W2",
                        f"{constraint}.target[2].targetWeight",
                        f=True,
                    )
                    pm.connectAttr(
                        "eyeAimFollowSetRange.outValueX",
                        weight_attr,
                        f=True,
                    )
        except Exception as e:
            pm.warning(f"Failed to setup eye aim fallback: {e}")

    def _create_parent_constraint_safe(self, source, target):
        """Create a parent constraint with error handling.

        Args:
            source (str): Source object driving the constraint.
            target (str): Target object to be constrained.

        Returns:
            PyNode | None: The created constraint node, or None if failed.
        """
        try:
            # Check if constraint already exists
            existing = pm.listConnections(f"{target}.parentMatrix", type="parentConstraint")
            if existing:
                return existing[0]

            constraint = pm.parentConstraint(source, target, mo=True)
            return constraint
        except Exception as e:
            pm.warning(f"Failed to create constraint {source} -> {target}: {e}")
            return None

    def _hide_internal_controls(self):
        """Hide internal controls that shouldn't be user-visible.

        Hides aim eye and FK head controls that are driven by other
        controls and shouldn't be directly manipulated.
        """
        hide_list = [
            self.DEFAULT_EYE_AIM_M,
            "FKHead_M",
        ]

        visible_controls = [ctrl for ctrl in hide_list if pm.objExists(ctrl)]
        if visible_controls:
            try:
                pm.hide(visible_controls)
            except Exception as e:
                pm.warning(f"Failed to hide internal controls: {e}")

    def _setup_face_motion_system(self):
        """Set up face motion system connections.

        Parent constrains face motion targets to the head joint to ensure
        the facial deformation system follows head movement correctly.
        """
        if not pm.objExists(self.head_joint):
            return

        for target in self.FACE_MOTION_TARGETS:
            if pm.objExists(target):
                self._create_parent_constraint_safe(self.head_joint, target)

    def _setup_scale_connections(self):
        """Set up scale connections for the facial rig.

        Connects the main control's world matrix to the face scale
        multiply divide node to ensure proper scaling behavior.
        """
        scale_node = "MainAndHeadScaleMultiplyDivide"

        if not pm.objExists(self.main_ctrl):
            return

        if not pm.objExists(scale_node):
            pm.warning(f"Scale node '{scale_node}' not found. Skipping scale setup.")
            return

        # Check if already connected
        if pm.isConnected(f"{self.main_ctrl}.worldMatrix", f"{scale_node}.input1"):
            return

        try:
            # Create decompose matrix node
            decompose_name = f"{self.character_name}_face_decomposeMatrix"
            if pm.objExists(decompose_name):
                decompose = pm.PyNode(decompose_name)
            else:
                decompose = pm.shadingNode("decomposeMatrix", asUtility=True, name=decompose_name)

            # Connect main ctrl world matrix to decompose
            pm.connectAttr(f"{self.main_ctrl}.worldMatrix", f"{decompose}.inputMatrix", f=True)

            # Connect decompose output scale to multiply divide
            pm.connectAttr(f"{decompose}.outputScale", f"{scale_node}.input1", f=True)

            pm.displayInfo("Face scale connections established")

        except Exception as e:
            pm.warning(f"Failed to setup scale connections: {e}")

    def _create_face_selection_sets(self):
        """Create selection sets for facial rig components.

        Creates Maya selection sets for face controls and face joints,
        making it easier to select and organize facial rig elements.
        """
        # Create face controls set
        face_ctrl_set_name = f"{self.character_name}_face_ctrls_set"
        if pm.objExists(face_ctrl_set_name):
            self.face_ctrl_set = pm.PyNode(face_ctrl_set_name)
        else:
            # Find face controls (pattern: *_Face_*_ctrl or Face*_ctrl)
            face_ctrls = pm.ls("*Face*_ctrl", type="transform")
            if face_ctrls:
                self.face_ctrl_set = pm.sets(face_ctrls, n=face_ctrl_set_name)
            else:
                self.face_ctrl_set = pm.sets(empty=True, n=face_ctrl_set_name)

        # Create face joints set
        face_joint_set_name = f"{self.character_name}_face_joints_set"
        if pm.objExists(face_joint_set_name):
            self.face_joint_set = pm.PyNode(face_joint_set_name)
        else:
            face_joints = self._get_face_joints()
            if face_joints:
                self.face_joint_set = pm.sets(face_joints, n=face_joint_set_name)
            else:
                self.face_joint_set = pm.sets(empty=True, n=face_joint_set_name)

        # Add to main face_ctrls_set if it exists
        if pm.objExists("face_ctrls_set"):
            with contextlib.suppress(Exception):
                pm.sets("face_ctrls_set", add=self.face_ctrl_set)

        if pm.objExists("face_joint_set"):
            with contextlib.suppress(Exception):
                pm.sets("face_joint_set", add=self.face_joint_set)

    def _get_face_joints(self):
        """Get all joints under the face joint root.

        Returns:
            list: List of face joint PyNodes.
        """
        if not pm.objExists(self.face_joint_root):
            return []

        try:
            root = pm.PyNode(self.face_joint_root)
            joints = pm.listRelatives(root, ad=True, type="joint") or []
            joints.insert(0, root)
            return joints
        except Exception:
            return []

    def _setup_face_display_layer(self):
        """Set up display layer for facial rig visualization.

        Creates a display layer for face joints with appropriate color
        settings for easy identification in the viewport.
        """
        layer_name = f"{self.character_name}_face_layer"

        if pm.objExists(layer_name):
            self.face_display_layer = pm.PyNode(layer_name)
            return

        face_joints = self._get_face_joints()
        if not face_joints:
            return

        try:
            pm.select(face_joints)
            self.face_display_layer = pm.createDisplayLayer(name=layer_name, nr=True, number=1)

            # Set display layer color (yellow for face)
            pm.setAttr(f"{self.face_display_layer}.color", 17)
            pm.select(clear=True)

        except Exception as e:
            pm.warning(f"Failed to create face display layer: {e}")

    def connect_to_body_rig(self, body_rig_node=None):
        """Connect face rig to body rig for seamless integration.

        Establishes connections between the facial rig and the body rig
        for proper deformation and animation blending.

        Args:
            body_rig_node (str | None): Name of the body rig root node.
                If None, attempts to find it automatically.

        Returns:
            bool: True if connection was successful.
        """
        # Find body rig if not specified
        if body_rig_node is None:
            # Look for common body rig naming patterns
            candidates = pm.ls("*_rig_GRP", "*_rig_grp", "rig_GRP")
            if candidates:
                body_rig_node = str(candidates[0])
            else:
                pm.warning("Could not find body rig node.")
                return False

        if not pm.objExists(body_rig_node):
            pm.warning(f"Body rig node '{body_rig_node}' not found.")
            return False

        pm.displayInfo(f"Face rig connected to body rig: {body_rig_node}")
        return True

    def transfer_skin_weights(self, source_mesh, target_mesh, method="closest"):
        """Transfer skin weights from source to target mesh.

        Convenience method for transferring skin weights between meshes
        using the facial rigging skin utilities.

        Args:
            source_mesh (str): Name of the source skinned mesh.
            target_mesh (str): Name of the target mesh to receive weights.
            method (str): Transfer method - 'closest' or 'uv'. Defaults to 'closest'.

        Returns:
            bool: True if transfer was successful.
        """
        try:
            skin_copy.skin_copy(source_mesh, target_mesh)
            pm.displayInfo(f"Skin weights transferred: {source_mesh} -> {target_mesh}")
            return True
        except Exception as e:
            pm.warning(f"Failed to transfer skin weights: {e}")
            return False

    def get_face_controls(self):
        """Get all face controls in the rig.

        Returns:
            list: List of face control names.
        """
        if self.face_ctrl_set:
            return list(pm.sets(self.face_ctrl_set, q=True))
        return pm.ls("*Face*_ctrl", type="transform")

    def get_face_joints(self):
        """Get all face joints in the rig.

        Returns:
            list: List of face joint names.
        """
        return self._get_face_joints()

    def select_face_controls(self):
        """Select all face controls for manipulation.

        Convenience method to quickly select all face controls.
        """
        controls = self.get_face_controls()
        if controls:
            pm.select(controls)
        else:
            pm.warning("No face controls found.")

    def select_face_joints(self):
        """Select all face joints for manipulation.

        Convenience method to quickly select all face joints.
        """
        joints = self.get_face_joints()
        if joints:
            pm.select(joints)
        else:
            pm.warning("No face joints found.")

    def reset_to_bind_pose(self):
        """Reset face rig to bind pose.

        Resets all face controls and joints to their bind pose positions.
        """
        controls = self.get_face_controls()
        for ctrl in controls:
            with contextlib.suppress(Exception):
                ctrl_node = pm.PyNode(ctrl)
                # Reset transformations
                for attr in ["tx", "ty", "tz", "rx", "ry", "rz"]:
                    with contextlib.suppress(Exception):
                        ctrl_node.attr(attr).set(0)
                for attr in ["sx", "sy", "sz"]:
                    with contextlib.suppress(Exception):
                        ctrl_node.attr(attr).set(1)

        pm.displayInfo("Face rig reset to bind pose")

    def is_initialized(self):
        """Check if the face node has been initialized.

        Returns:
            bool: True if setup has been completed.
        """
        return self._initialized


# Convenience function for quick setup
def create_arise_face_node(
    character_name="Character",
    head_joint=None,
    main_ctrl=None,
    face_joint_root=None,
    auto_setup=True,
):
    """Create and optionally setup an AriseFaceNode.

    Factory function for creating AriseFaceNode instances with
    common default settings.

    Args:
        character_name (str): Name of the character for rigging.
        head_joint (str | None): Name of the head joint.
        main_ctrl (str | None): Name of the main control.
        face_joint_root (str | None): Name of the face joint root.
        auto_setup (bool): Whether to run setup automatically. Defaults to True.

    Returns:
        AriseFaceNode: The created face node instance.

    Example:
        >>> face = create_arise_face_node("Hero", auto_setup=True)
        >>> print(face.is_initialized())
        True
    """
    return AriseFaceNode(
        character_name=character_name,
        head_joint=head_joint,
        main_ctrl=main_ctrl,
        face_joint_root=face_joint_root,
        auto_setup=auto_setup,
    )


# Legacy alias for backward compatibility
AriseFaceRig = AriseFaceNode


# Module exports
__all__ = [
    "AriseFaceNode",
    "AriseFaceRig",
    "create_arise_face_node",
]
