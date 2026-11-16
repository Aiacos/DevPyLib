"""
Hierarchy management for facial rig structure.
"""

from typing import List, Optional

import maya.cmds as cmds


class HierarchyManager:
    """
    Manages the creation and organization of the facial rig hierarchy.

    Creates the standard group structure:
    - FaceGroup
      - FaceFitSkeleton
      - FaceMotionSystem
        - OnFacecontrols
        - CtrlBoxes
        - ...
      - FaceDeformationSystem
        - LidSetup
        - LipSetup
        - ...
    """

    # Standard group names
    FACE_GROUP = "FaceGroup"
    FIT_SKELETON = "FaceFitSkeleton"
    MOTION_SYSTEM = "FaceMotionSystem"
    DEFORMATION_SYSTEM = "FaceDeformationSystem"
    ON_FACE_CONTROLS = "OnFacecontrols"
    BUILD_IN_PROGRESS = "FaceBuildInProgress"
    FACE_JOINT = "FaceJoint_M"
    CTRL_BOX = "ctrlBox"

    def __init__(self):
        """Initialize the hierarchy manager."""
        self._created_groups: List[str] = []

    def create_base_hierarchy(self, parent: Optional[str] = None) -> dict:
        """
        Create the base facial rig hierarchy.

        Args:
            parent: Optional parent transform (e.g., "|Group")

        Returns:
            Dictionary mapping group names to their full paths
        """
        hierarchy = {}

        # Create FaceGroup
        if not cmds.objExists(self.FACE_GROUP):
            cmds.createNode("transform", name=self.FACE_GROUP)
            if parent and cmds.objExists(parent):
                cmds.parent(self.FACE_GROUP, parent)
        hierarchy[self.FACE_GROUP] = self.FACE_GROUP

        # Create FaceFitSkeleton under FaceGroup
        if not cmds.objExists(self.FIT_SKELETON):
            cmds.createNode("transform", name=self.FIT_SKELETON, parent=self.FACE_GROUP)
        hierarchy[self.FIT_SKELETON] = self.FIT_SKELETON

        return hierarchy

    def create_motion_system(self) -> str:
        """
        Create the FaceMotionSystem hierarchy.

        Returns:
            Name of the created motion system group
        """
        if not cmds.objExists(self.MOTION_SYSTEM):
            cmds.createNode("transform", name=self.MOTION_SYSTEM, parent=self.FACE_GROUP)

        # Create OnFacecontrols
        if not cmds.objExists(self.ON_FACE_CONTROLS):
            cmds.createNode("transform", name=self.ON_FACE_CONTROLS, parent=self.MOTION_SYSTEM)

        return self.MOTION_SYSTEM

    def create_deformation_system(self) -> str:
        """
        Create the FaceDeformationSystem hierarchy.

        Returns:
            Name of the created deformation system group
        """
        if not cmds.objExists(self.DEFORMATION_SYSTEM):
            cmds.createNode("transform", name=self.DEFORMATION_SYSTEM, parent=self.FACE_GROUP)

        return self.DEFORMATION_SYSTEM

    def create_face_joint(self, head_joint: str) -> str:
        """
        Create the main face joint.

        Args:
            head_joint: Parent head joint name

        Returns:
            Name of the created face joint
        """
        if cmds.objExists(self.FACE_JOINT):
            return self.FACE_JOINT

        # Select parent joint
        cmds.select(head_joint)

        # Create face joint
        cmds.joint(name=self.FACE_JOINT)
        cmds.setAttr(f"{self.FACE_JOINT}.segmentScaleCompensate", 0)
        cmds.setAttr(f"{self.FACE_JOINT}.drawStyle", 2)

        return self.FACE_JOINT

    def create_component_group(
        self, name: str, parent: str, inherits_transform: bool = True
    ) -> str:
        """
        Create a component-specific group.

        Args:
            name: Group name
            parent: Parent transform
            inherits_transform: Whether to inherit parent transforms

        Returns:
            Name of the created group
        """
        if cmds.objExists(name):
            return name

        cmds.createNode("transform", name=name, parent=parent)

        if not inherits_transform:
            cmds.setAttr(f"{name}.inheritsTransform", 0)

        self._created_groups.append(name)
        return name

    def create_ctrl_box(self, name: str, side: str) -> str:
        """
        Create a control box container.

        Args:
            name: Base name (e.g., "Eye", "Brow")
            side: Side suffix ("_R", "_L", "_M")

        Returns:
            Name of the created control box
        """
        ctrl_box_name = f"ctrlBox{name}{side}"

        if cmds.objExists(ctrl_box_name):
            return ctrl_box_name

        # Create the control box transform
        cmds.createNode("transform", name=ctrl_box_name)

        return ctrl_box_name

    def create_build_progress_group(self) -> str:
        """
        Create temporary build progress group.

        Used to hold temporary objects during the build process.

        Returns:
            Name of the build progress group
        """
        if not cmds.objExists(self.BUILD_IN_PROGRESS):
            cmds.createNode("transform", name=self.BUILD_IN_PROGRESS, parent=self.FACE_GROUP)
            cmds.setAttr(f"{self.BUILD_IN_PROGRESS}.visibility", 0)

        return self.BUILD_IN_PROGRESS

    def cleanup_build_progress(self):
        """Remove the build progress group and its contents."""
        if cmds.objExists(self.BUILD_IN_PROGRESS):
            cmds.delete(self.BUILD_IN_PROGRESS)

    def lock_transform_attrs(
        self,
        node: str,
        translate: bool = True,
        rotate: bool = True,
        scale: bool = True,
        visibility: bool = False,
    ):
        """
        Lock transform attributes on a node.

        Args:
            node: Node name
            translate: Lock translate attributes
            rotate: Lock rotate attributes
            scale: Lock scale attributes
            visibility: Lock visibility attribute
        """
        attrs = []
        if translate:
            attrs.extend(["tx", "ty", "tz"])
        if rotate:
            attrs.extend(["rx", "ry", "rz"])
        if scale:
            attrs.extend(["sx", "sy", "sz"])
        if visibility:
            attrs.append("v")

        for attr in attrs:
            if cmds.attributeQuery(attr, node=node, exists=True):
                cmds.setAttr(f"{node}.{attr}", lock=True)

    def add_to_set(self, node: str, set_name: str):
        """
        Add a node to an object set.

        Args:
            node: Node to add
            set_name: Name of the set
        """
        if not cmds.objExists(set_name):
            cmds.sets(name=set_name, empty=True)

        cmds.sets(node, add=set_name)

    def create_sets(self) -> dict:
        """
        Create standard facial rig sets.

        Returns:
            Dictionary of created set names
        """
        sets = {
            "all": "FaceAllSet",
            "controls": "FaceControlSet",
            "areas": "FaceAreas",
            "building": "FaceBuildingSets",
        }

        for set_name in sets.values():
            if not cmds.objExists(set_name):
                cmds.sets(name=set_name, empty=True)

        return sets
