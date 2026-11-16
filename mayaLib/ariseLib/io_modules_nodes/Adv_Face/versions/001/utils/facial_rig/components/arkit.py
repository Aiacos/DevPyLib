"""
ARKit BlendShape component for facial rig.

Handles Apple ARKit face tracking blendshape creation and connection.
This component creates blendshapes compatible with ARKit face tracking
from facial rig controls.

ARKit 52 Blendshapes:
- Eye: eyeBlinkLeft, eyeBlinkRight, eyeLookDownLeft, eyeLookDownRight,
       eyeLookInLeft, eyeLookInRight, eyeLookOutLeft, eyeLookOutRight,
       eyeLookUpLeft, eyeLookUpRight, eyeSquintLeft, eyeSquintRight,
       eyeWideLeft, eyeWideRight
- Jaw: jawForward, jawLeft, jawRight, jawOpen
- Mouth: mouthClose, mouthFunnel, mouthPucker, mouthLeft, mouthRight,
         mouthSmileLeft, mouthSmileRight, mouthFrownLeft, mouthFrownRight,
         mouthDimpleLeft, mouthDimpleRight, mouthStretchLeft, mouthStretchRight,
         mouthRollLower, mouthRollUpper, mouthShrugLower, mouthShrugUpper,
         mouthPressLeft, mouthPressRight, mouthLowerDownLeft, mouthLowerDownRight,
         mouthUpperUpLeft, mouthUpperUpRight
- Brow: browDownLeft, browDownRight, browInnerUp, browOuterUpLeft, browOuterUpRight
- Cheek: cheekPuff, cheekSquintLeft, cheekSquintRight
- Nose: noseSneerLeft, noseSneerRight
- Tongue: tongueOut
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side


@dataclass
class ARKitBlendShape:
    """Definition of an ARKit blendshape."""

    name: str
    display_name: str
    category: str
    driver_ctrl: str  # Controller that drives this shape
    driver_attr: str  # Attribute on controller
    driver_range: Tuple[float, float]  # (min, max) value range
    weight: float = 1.0  # Default blend weight


class ARKitComponent(FacialComponent):
    """
    ARKit BlendShape facial component.

    Creates Apple ARKit compatible blendshapes that can be:
    - Connected to face motion capture data
    - Used with Live Link Face app
    - Exported for game engines (Unreal, Unity)

    The component can operate in two modes:
    1. Create Mode: Creates blendshapes from facial rig deformation
    2. Connect Mode: Connects existing blendshapes to ARKit input

    Reference: https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation
    """

    # ARKit 52 blendshape definitions
    ARKIT_SHAPES: Dict[str, ARKitBlendShape] = {}

    # Category order for UI
    CATEGORIES = ["Eye", "Brow", "Jaw", "Mouth", "Cheek", "Nose", "Tongue"]

    def __init__(self, config: FacialRigConfig, side: Side = Side.CENTER):
        """
        Initialize ARKit component.

        Args:
            config: Facial rig configuration
            side: Side (usually CENTER for ARKit)
        """
        super().__init__(config, side)

        self._blendshape_node: str = ""
        self._arkit_shapes: Dict[str, str] = {}
        self._init_arkit_shapes()

    @classmethod
    def _init_arkit_shapes(cls):
        """Initialize all 52 ARKit blendshape definitions."""
        if cls.ARKIT_SHAPES:
            return

        # === EYE SHAPES ===
        eye_shapes = [
            ("eyeBlinkLeft", "Eye Blink Left", "ctrlEye_L", "blink", (0, 10)),
            ("eyeBlinkRight", "Eye Blink Right", "ctrlEye_R", "blink", (0, 10)),
            ("eyeLookDownLeft", "Eye Look Down Left", "FKEye_L", "rotateX", (0, 30)),
            ("eyeLookDownRight", "Eye Look Down Right", "FKEye_R", "rotateX", (0, 30)),
            ("eyeLookInLeft", "Eye Look In Left", "FKEye_L", "rotateY", (0, 30)),
            ("eyeLookInRight", "Eye Look In Right", "FKEye_R", "rotateY", (0, -30)),
            ("eyeLookOutLeft", "Eye Look Out Left", "FKEye_L", "rotateY", (0, -30)),
            ("eyeLookOutRight", "Eye Look Out Right", "FKEye_R", "rotateY", (0, 30)),
            ("eyeLookUpLeft", "Eye Look Up Left", "FKEye_L", "rotateX", (0, -30)),
            ("eyeLookUpRight", "Eye Look Up Right", "FKEye_R", "rotateX", (0, -30)),
            ("eyeSquintLeft", "Eye Squint Left", "ctrlEye_L", "squint", (0, 10)),
            ("eyeSquintRight", "Eye Squint Right", "ctrlEye_R", "squint", (0, 10)),
            ("eyeWideLeft", "Eye Wide Left", "ctrlEye_L", "wide", (0, 10)),
            ("eyeWideRight", "Eye Wide Right", "ctrlEye_R", "wide", (0, 10)),
        ]

        for name, display, ctrl, attr, range_val in eye_shapes:
            cls.ARKIT_SHAPES[name] = ARKitBlendShape(
                name=name,
                display_name=display,
                category="Eye",
                driver_ctrl=ctrl,
                driver_attr=attr,
                driver_range=range_val,
            )

        # === BROW SHAPES ===
        brow_shapes = [
            ("browDownLeft", "Brow Down Left", "ctrlBrow_L", "translateY", (0, -1)),
            ("browDownRight", "Brow Down Right", "ctrlBrow_R", "translateY", (0, -1)),
            ("browInnerUp", "Brow Inner Up", "ctrlBrowInner_M", "translateY", (0, 1)),
            ("browOuterUpLeft", "Brow Outer Up Left", "ctrlBrowOuter_L", "translateY", (0, 1)),
            ("browOuterUpRight", "Brow Outer Up Right", "ctrlBrowOuter_R", "translateY", (0, 1)),
        ]

        for name, display, ctrl, attr, range_val in brow_shapes:
            cls.ARKIT_SHAPES[name] = ARKitBlendShape(
                name=name,
                display_name=display,
                category="Brow",
                driver_ctrl=ctrl,
                driver_attr=attr,
                driver_range=range_val,
            )

        # === JAW SHAPES ===
        jaw_shapes = [
            ("jawForward", "Jaw Forward", "FKJaw_M", "translateZ", (0, 1)),
            ("jawLeft", "Jaw Left", "FKJaw_M", "translateX", (0, -1)),
            ("jawRight", "Jaw Right", "FKJaw_M", "translateX", (0, 1)),
            ("jawOpen", "Jaw Open", "FKJaw_M", "rotateX", (0, 30)),
        ]

        for name, display, ctrl, attr, range_val in jaw_shapes:
            cls.ARKIT_SHAPES[name] = ARKitBlendShape(
                name=name,
                display_name=display,
                category="Jaw",
                driver_ctrl=ctrl,
                driver_attr=attr,
                driver_range=range_val,
            )

        # === MOUTH SHAPES ===
        mouth_shapes = [
            ("mouthClose", "Mouth Close", "ctrlLips_M", "close", (0, 10)),
            ("mouthFunnel", "Mouth Funnel", "ctrlLips_M", "funnel", (0, 10)),
            ("mouthPucker", "Mouth Pucker", "ctrlLips_M", "pucker", (0, 10)),
            ("mouthLeft", "Mouth Left", "ctrlLips_M", "translateX", (0, -1)),
            ("mouthRight", "Mouth Right", "ctrlLips_M", "translateX", (0, 1)),
            ("mouthSmileLeft", "Mouth Smile Left", "cornerLip_L", "translateY", (0, 1)),
            ("mouthSmileRight", "Mouth Smile Right", "cornerLip_R", "translateY", (0, 1)),
            ("mouthFrownLeft", "Mouth Frown Left", "cornerLip_L", "translateY", (0, -1)),
            ("mouthFrownRight", "Mouth Frown Right", "cornerLip_R", "translateY", (0, -1)),
            ("mouthDimpleLeft", "Mouth Dimple Left", "cornerLip_L", "dimple", (0, 10)),
            ("mouthDimpleRight", "Mouth Dimple Right", "cornerLip_R", "dimple", (0, 10)),
            ("mouthStretchLeft", "Mouth Stretch Left", "cornerLip_L", "translateX", (0, 1)),
            ("mouthStretchRight", "Mouth Stretch Right", "cornerLip_R", "translateX", (0, -1)),
            ("mouthRollLower", "Mouth Roll Lower", "ctrlLips_M", "lowerRoll", (0, 10)),
            ("mouthRollUpper", "Mouth Roll Upper", "ctrlLips_M", "upperRoll", (0, 10)),
            ("mouthShrugLower", "Mouth Shrug Lower", "ctrlLips_M", "lowerShrug", (0, 10)),
            ("mouthShrugUpper", "Mouth Shrug Upper", "ctrlLips_M", "upperShrug", (0, 10)),
            ("mouthPressLeft", "Mouth Press Left", "cornerLip_L", "press", (0, 10)),
            ("mouthPressRight", "Mouth Press Right", "cornerLip_R", "press", (0, 10)),
            (
                "mouthLowerDownLeft",
                "Mouth Lower Down Left",
                "ctrlLowerLip_L",
                "translateY",
                (0, -1),
            ),
            (
                "mouthLowerDownRight",
                "Mouth Lower Down Right",
                "ctrlLowerLip_R",
                "translateY",
                (0, -1),
            ),
            ("mouthUpperUpLeft", "Mouth Upper Up Left", "ctrlUpperLip_L", "translateY", (0, 1)),
            ("mouthUpperUpRight", "Mouth Upper Up Right", "ctrlUpperLip_R", "translateY", (0, 1)),
        ]

        for name, display, ctrl, attr, range_val in mouth_shapes:
            cls.ARKIT_SHAPES[name] = ARKitBlendShape(
                name=name,
                display_name=display,
                category="Mouth",
                driver_ctrl=ctrl,
                driver_attr=attr,
                driver_range=range_val,
            )

        # === CHEEK SHAPES ===
        cheek_shapes = [
            ("cheekPuff", "Cheek Puff", "ctrlCheek_M", "puff", (0, 10)),
            ("cheekSquintLeft", "Cheek Squint Left", "ctrlCheek_L", "squint", (0, 10)),
            ("cheekSquintRight", "Cheek Squint Right", "ctrlCheek_R", "squint", (0, 10)),
        ]

        for name, display, ctrl, attr, range_val in cheek_shapes:
            cls.ARKIT_SHAPES[name] = ARKitBlendShape(
                name=name,
                display_name=display,
                category="Cheek",
                driver_ctrl=ctrl,
                driver_attr=attr,
                driver_range=range_val,
            )

        # === NOSE SHAPES ===
        nose_shapes = [
            ("noseSneerLeft", "Nose Sneer Left", "ctrlNose_L", "sneer", (0, 10)),
            ("noseSneerRight", "Nose Sneer Right", "ctrlNose_R", "sneer", (0, 10)),
        ]

        for name, display, ctrl, attr, range_val in nose_shapes:
            cls.ARKIT_SHAPES[name] = ARKitBlendShape(
                name=name,
                display_name=display,
                category="Nose",
                driver_ctrl=ctrl,
                driver_attr=attr,
                driver_range=range_val,
            )

        # === TONGUE SHAPES ===
        cls.ARKIT_SHAPES["tongueOut"] = ARKitBlendShape(
            name="tongueOut",
            display_name="Tongue Out",
            category="Tongue",
            driver_ctrl="FKTongue1_M",
            driver_attr="translateZ",
            driver_range=(0, 1),
        )

    @property
    def name(self) -> str:
        return "ARKit"

    def build(self) -> bool:
        """
        Build the ARKit blendshape component.

        Returns:
            True if build succeeded
        """
        if not self.pre_build():
            return False

        try:
            self._create_arkit_group()
            self._create_blendshape_node()
            self._create_arkit_targets()
            self._setup_arkit_connections()

            self.post_build()
            return True

        except Exception as e:
            cmds.warning(f"ARKit build failed: {e}")
            return False

    def _create_arkit_group(self):
        """Create ARKit setup group in hierarchy."""
        if not cmds.objExists("ARKitSetup"):
            cmds.createNode("transform", name="ARKitSetup")

            if cmds.objExists("FaceDeformationSystem"):
                cmds.parent("ARKitSetup", "FaceDeformationSystem")

    def _create_blendshape_node(self):
        """Create the main ARKit blendshape node."""
        geometry = self.config.geometry

        if not cmds.objExists(geometry):
            raise ValueError(f"Geometry '{geometry}' not found")

        # Check if blendshape already exists
        bs_name = "asFaceBS"
        if cmds.objExists(bs_name):
            self._blendshape_node = bs_name
            return

        # Create blendshape node
        self._blendshape_node = cmds.blendShape(geometry, name=bs_name, frontOfChain=True)[0]

        print(f"// Created blendshape node: {self._blendshape_node}")

    def _create_arkit_targets(self):
        """Create all 52 ARKit blendshape targets."""
        geometry = self.config.geometry

        for shape_name, shape_def in self.ARKIT_SHAPES.items():
            # Check if target already exists
            existing_targets = cmds.blendShape(self._blendshape_node, query=True, target=True) or []

            if shape_name in existing_targets:
                self._arkit_shapes[shape_name] = shape_name
                continue

            # Create target geometry (duplicate at pose)
            target_geo = self._create_shape_target(shape_name, shape_def)

            if target_geo:
                # Add as blendshape target
                target_index = len(existing_targets)
                cmds.blendShape(
                    self._blendshape_node,
                    edit=True,
                    target=(geometry, target_index, target_geo, 1.0),
                )

                # Rename the target
                cmds.aliasAttr(shape_name, f"{self._blendshape_node}.weight[{target_index}]")

                # Delete target geo after adding to blendshape
                cmds.delete(target_geo)

                self._arkit_shapes[shape_name] = shape_name

    def _create_shape_target(self, shape_name: str, shape_def: ARKitBlendShape) -> Optional[str]:
        """
        Create a blendshape target by posing controllers.

        Args:
            shape_name: ARKit shape name
            shape_def: Shape definition

        Returns:
            Name of created target geometry or None
        """
        ctrl = shape_def.driver_ctrl
        attr = shape_def.driver_attr
        range_min, range_max = shape_def.driver_range

        # Skip if controller doesn't exist
        if not cmds.objExists(ctrl):
            cmds.warning(f"Controller '{ctrl}' not found for {shape_name}")
            return None

        full_attr = f"{ctrl}.{attr}"

        # Check if attribute exists
        if not cmds.attributeQuery(attr, node=ctrl, exists=True):
            cmds.warning(f"Attribute '{attr}' not found on {ctrl}")
            return None

        # Store current value
        current_value = cmds.getAttr(full_attr)

        try:
            # Set to target pose
            cmds.setAttr(full_attr, range_max)

            # Duplicate geometry at this pose
            geometry = self.config.geometry
            target = cmds.duplicate(geometry, name=f"{shape_name}_target")[0]

            # Reset controller
            cmds.setAttr(full_attr, current_value)

            return target

        except Exception as e:
            cmds.warning(f"Failed to create target for {shape_name}: {e}")
            # Make sure we reset
            try:
                cmds.setAttr(full_attr, current_value)
            except RuntimeError:
                pass
            return None

    def _setup_arkit_connections(self):
        """Setup connections from ARKit input to blendshape weights."""
        # Create ARKit input node if it doesn't exist
        input_node = "ARKitInput"

        if not cmds.objExists(input_node):
            input_node = cmds.createNode("transform", name=input_node)
            cmds.parent(input_node, "ARKitSetup")

            # Add all 52 attributes
            for shape_name in self.ARKIT_SHAPES:
                cmds.addAttr(
                    input_node,
                    longName=shape_name,
                    attributeType="double",
                    minValue=0,
                    maxValue=1,
                    defaultValue=0,
                    keyable=True,
                )

        # Connect input attributes to blendshape weights
        for shape_name in self._arkit_shapes:
            src = f"{input_node}.{shape_name}"
            dst = f"{self._blendshape_node}.{shape_name}"

            if cmds.objExists(src) and cmds.objExists(dst):
                if not cmds.isConnected(src, dst):
                    cmds.connectAttr(src, dst, force=True)

        print("// ARKit connections setup complete")

    def connect_arkit(self, source_node: str):
        """
        Connect an external ARKit source to the blendshape.

        Args:
            source_node: Node with ARKit attributes (0-1 range)
        """
        if not cmds.objExists(source_node):
            cmds.warning(f"Source node '{source_node}' not found")
            return

        for shape_name in self._arkit_shapes:
            src = f"{source_node}.{shape_name}"
            dst = f"{self._blendshape_node}.{shape_name}"

            if cmds.objExists(src) and cmds.objExists(dst):
                if not cmds.isConnected(src, dst):
                    cmds.connectAttr(src, dst, force=True)

        print(f"// Connected ARKit from {source_node}")

    def disconnect_arkit(self):
        """Disconnect ARKit input from blendshape."""
        for shape_name in self._arkit_shapes:
            dst = f"{self._blendshape_node}.{shape_name}"

            if cmds.objExists(dst):
                connections = cmds.listConnections(dst, source=True, plugs=True)
                if connections:
                    for conn in connections:
                        cmds.disconnectAttr(conn, dst)

        print("// ARKit disconnected")

    def bake_arkit_to_controls(self, start_frame: int, end_frame: int):
        """
        Bake ARKit animation to facial rig controls.

        Args:
            start_frame: Start frame
            end_frame: End frame
        """
        # Get all controls that are driven by ARKit
        controls_to_bake = set()

        for shape_def in self.ARKIT_SHAPES.values():
            if cmds.objExists(shape_def.driver_ctrl):
                controls_to_bake.add(shape_def.driver_ctrl)

        if not controls_to_bake:
            cmds.warning("No controls found to bake")
            return

        # Bake simulation
        cmds.bakeResults(
            list(controls_to_bake),
            time=(start_frame, end_frame),
            simulation=True,
            sampleBy=1,
            oversamplingRate=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=True,
        )

        print(f"// Baked ARKit to {len(controls_to_bake)} controls")

    @classmethod
    def get_arkit_shape_names(cls) -> List[str]:
        """Get list of all 52 ARKit shape names."""
        cls._init_arkit_shapes()
        return list(cls.ARKIT_SHAPES.keys())

    @classmethod
    def get_shapes_by_category(cls, category: str) -> List[str]:
        """Get ARKit shape names for a specific category."""
        cls._init_arkit_shapes()
        return [name for name, shape in cls.ARKIT_SHAPES.items() if shape.category == category]


def create_arkit_blendshapes(config: FacialRigConfig) -> bool:
    """
    Convenience function to create ARKit blendshapes.

    Args:
        config: Facial rig configuration

    Returns:
        True if successful
    """
    component = ARKitComponent(config)
    return component.build()


def connect_arkit_source(source_node: str, config: FacialRigConfig):
    """
    Connect an ARKit source to existing blendshapes.

    Args:
        source_node: Node with ARKit attributes
        config: Facial rig configuration
    """
    component = ARKitComponent(config)
    component._blendshape_node = "asFaceBS"
    component._arkit_shapes = {name: name for name in ARKitComponent.get_arkit_shape_names()}
    component.connect_arkit(source_node)
