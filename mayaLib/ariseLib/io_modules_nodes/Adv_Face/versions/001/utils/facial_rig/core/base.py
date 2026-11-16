"""
Base class for facial rig components.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

import maya.cmds as cmds

from .config import FacialRigConfig
from .hierarchy import HierarchyManager
from .naming import NamingConvention, Side


class FacialComponent(ABC):
    """
    Abstract base class for facial rig components.

    All facial components (EyeLid, Lip, EyeBrow, etc.) inherit from this class.
    Provides common functionality for building rig elements.
    """

    def __init__(self, config: FacialRigConfig, side: Side = Side.RIGHT):
        """
        Initialize the facial component.

        Args:
            config: Facial rig configuration
            side: Side to build (RIGHT, LEFT, or CENTER)
        """
        self.config = config
        self.side = side
        self.naming = NamingConvention
        self.hierarchy = HierarchyManager()

        # Component state
        self._built = False
        self._joints: List[str] = []
        self._controllers: List[str] = []
        self._nodes: List[str] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the component name (e.g., 'EyeLid', 'Lip')."""
        pass

    @abstractmethod
    def build(self) -> bool:
        """
        Build the component.

        Returns:
            True if build succeeded, False otherwise
        """
        pass

    def pre_build(self) -> bool:
        """
        Pre-build validation and setup.

        Override in subclasses for component-specific validation.

        Returns:
            True if pre-build checks pass
        """
        if not self.config.is_valid():
            errors = self.config.validate()
            for error in errors:
                cmds.warning(f"Config error: {error}")
            return False

        return True

    def post_build(self):
        """
        Post-build cleanup and finalization.

        Override in subclasses for component-specific cleanup.
        """
        self._built = True

    def create_controller(
        self, name: str, side: Side, ctrl_type: int = 2, radius: float = 0.2
    ) -> str:
        """
        Create a facial controller.

        Args:
            name: Controller base name
            side: Side enum
            ctrl_type: Controller type (1=red/small, 2=green/medium, 3=blue/small, 4=region, 5=custom)
            radius: Controller radius

        Returns:
            Name of the created controller
        """
        # Determine radius and color based on type
        color = 14  # Default green

        if ctrl_type == 1:
            radius = 0.15
            color = 13  # Red
        elif ctrl_type in (2, 12):
            radius = 0.3
            color = 14  # Green
        elif ctrl_type in (3, 13):
            radius = 0.15
            color = 6  # Blue
        elif ctrl_type == 4:
            color = 14  # Region
        elif ctrl_type == 5:
            color = 28  # Custom

        # Scale radius by face scale
        if self.config.face_scale > 0:
            radius *= self.config.face_scale / 15.0

        # Create circle controller
        ctrl_name = self.naming.controller(name, side)
        ctrl = cmds.circle(
            name=ctrl_name,
            center=(0, 0, 0),
            normal=(0, 0, 1),
            radius=radius,
            degree=3,
            sections=8,
            constructionHistory=False,
        )[0]

        # Set display color
        shape = cmds.listRelatives(ctrl, shapes=True)[0]
        cmds.setAttr(f"{shape}.overrideEnabled", 1)
        cmds.setAttr(f"{shape}.overrideColor", color)

        # Create offset and SDK groups
        offset_name = self.naming.offset(name, side)
        sdk_name = self.naming.sdk(name, side)

        offset = cmds.createNode("transform", name=offset_name)
        sdk = cmds.createNode("transform", name=sdk_name, parent=offset)
        cmds.parent(ctrl, sdk)

        # Create joint for region type
        if ctrl_type == 4:
            cmds.select(clear=True)
            joint_name = self.naming.joint(name, side)
            cmds.joint(name=joint_name)

        self._controllers.append(ctrl)
        return ctrl

    def create_joint(
        self,
        name: str,
        side: Side,
        position: tuple = (0, 0, 0),
        parent: Optional[str] = None,
        index: Optional[int] = None,
    ) -> str:
        """
        Create a joint for the component.

        Args:
            name: Joint base name
            side: Side enum
            position: World space position
            parent: Optional parent joint
            index: Optional index for numbered joints

        Returns:
            Name of the created joint
        """
        if parent:
            cmds.select(parent)
        else:
            cmds.select(clear=True)

        joint_name = self.naming.joint(name, side, index)
        joint = cmds.joint(name=joint_name, position=position)

        cmds.setAttr(f"{joint}.segmentScaleCompensate", 0)
        cmds.setAttr(f"{joint}.radius", 0.1)

        self._joints.append(joint)
        return joint

    def add_to_skin_cluster(self, joint: str, skin_cluster: str, weight: float = 0.0):
        """
        Add a joint to the skin cluster.

        Args:
            joint: Joint to add
            skin_cluster: Target skin cluster
            weight: Default weight value
        """
        cmds.skinCluster(
            skin_cluster,
            edit=True,
            addInfluence=joint,
            weight=weight,
            lockWeights=False,
            dropoffRate=4,
        )

    def create_curve_from_positions(
        self, name: str, positions: List[tuple], degree: int = 3
    ) -> str:
        """
        Create a curve from a list of positions.

        Args:
            name: Curve name
            positions: List of (x, y, z) positions
            degree: Curve degree

        Returns:
            Name of the created curve
        """
        # Build curve command
        point_args = []
        for pos in positions:
            point_args.extend(["-p", pos[0], pos[1], pos[2]])

        curve = cmds.curve(name=name, degree=degree, point=positions)
        self._nodes.append(curve)
        return curve

    def get_fit_selection(self, fit_object: str) -> str:
        """
        Get the vertex selection from a FaceFit object.

        Parita' asGetFaceFitSelection: il build NON legge l'attributo
        selection salvato (storico della selezione originale) ma
        ricampiona le posizioni correnti di curve/locator/AreaMesh in
        vertici della Face, perche' l'utente puo' ritoccare i fit dopo
        la selezione.

        Args:
            fit_object: FaceFit object name (curva, gruppo di curve,
                locator o AreaMesh)

        Returns:
            Selection string (vertici della Face, formato MEL)
        """
        from .fitting import get_face_fit_selection

        if not cmds.objExists(fit_object):
            return ""
        return get_face_fit_selection(fit_object, self.config.geometry or "")

    def get_fit_position(self, region_name: str) -> Optional[tuple]:
        """
        Get position from fit data for this component's side.

        Args:
            region_name: Name of the fit region (e.g., "eye_ball", "cheek")

        Returns:
            Position tuple (x, y, z) or None
        """
        if not self.config.fit_data:
            return None

        is_left = self.side == Side.LEFT
        return self.config.fit_data.get_position(region_name, left_side=is_left)

    def get_fit_curve(self, curve_type: str, upper: bool = True) -> Optional[str]:
        """
        Get fit curve name for eyelid or lip curves.

        Args:
            curve_type: Type of curve ("eyelid_outer", "lip_main", etc.)
            upper: Whether to get upper curve (True) or lower (False)

        Returns:
            Curve name or None
        """
        if not self.config.fit_data:
            return None

        prefix = "upper_" if upper else "lower_"
        attr_name = f"{prefix}{curve_type}_curve"
        return getattr(self.config.fit_data, attr_name, None)

    def get_fit_vertices(self, region_name: str) -> List[str]:
        """
        Get stored vertices for a fit region.

        Args:
            region_name: Name of the region

        Returns:
            List of vertex names
        """
        if not self.config.fit_data:
            # Try from scene
            selection = self.get_fit_selection(f"FaceFit{region_name}")
            return selection.split() if selection else []

        selection = self.config.fit_data.get_selection(region_name)
        return selection.split() if selection else []

    def align_to(
        self,
        source: str,
        target: str,
        translate: bool = True,
        rotate: bool = True,
        scale: bool = False,
    ):
        """
        Align source transform to target transform.

        Args:
            source: Source transform to move
            target: Target transform to match
            translate: Match translation
            rotate: Match rotation
            scale: Match scale
        """
        if translate:
            pos = cmds.xform(target, query=True, worldSpace=True, translation=True)
            cmds.xform(source, worldSpace=True, translation=pos)

        if rotate:
            rot = cmds.xform(target, query=True, worldSpace=True, rotation=True)
            cmds.xform(source, worldSpace=True, rotation=rot)

        if scale:
            scl = cmds.xform(target, query=True, worldSpace=True, scale=True)
            cmds.xform(source, worldSpace=True, scale=scl)

    def connect_attr(self, source: str, destination: str, force: bool = True):
        """
        Connect attributes with error handling.

        Args:
            source: Source attribute
            destination: Destination attribute
            force: Force connection even if already connected
        """
        try:
            cmds.connectAttr(source, destination, force=force)
        except RuntimeError as e:
            cmds.warning(f"Failed to connect {source} -> {destination}: {e}")

    def create_sdk_setup(
        self, driver_attr: str, driven_attr: str, driver_value: float, driven_value: float
    ):
        """
        Create a set driven key setup.

        Args:
            driver_attr: Driver attribute (e.g., "ctrl.ty")
            driven_attr: Driven attribute (e.g., "joint.tx")
            driver_value: Driver value at pose
            driven_value: Driven value at pose
        """
        # Store current values
        current_driver = cmds.getAttr(driver_attr)
        current_driven = cmds.getAttr(driven_attr)

        # Set default pose (0, 0)
        cmds.setAttr(driver_attr, 0)
        cmds.setAttr(driven_attr, 0)
        cmds.setDrivenKeyframe(driven_attr, currentDriver=driver_attr)

        # Set target pose
        cmds.setAttr(driver_attr, driver_value)
        cmds.setAttr(driven_attr, driven_value)
        cmds.setDrivenKeyframe(driven_attr, currentDriver=driver_attr)

        # Restore values
        cmds.setAttr(driver_attr, current_driver)
        cmds.setAttr(driven_attr, current_driven)

    def cleanup(self):
        """Clean up temporary nodes created during build."""
        # Delete temporary nodes
        for node in self._nodes:
            if cmds.objExists(node) and "temp" in node.lower():
                cmds.delete(node)

    @property
    def is_built(self) -> bool:
        """Check if component has been built."""
        return self._built

    @property
    def joints(self) -> List[str]:
        """Return list of created joints."""
        return self._joints.copy()

    @property
    def controllers(self) -> List[str]:
        """Return list of created controllers."""
        return self._controllers.copy()
