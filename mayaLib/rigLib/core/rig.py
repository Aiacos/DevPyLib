"""High-level rig assembly routines for DevPyLib."""

from __future__ import annotations

from collections.abc import Sequence

import pymel.core as pm

from mayaLib.rigLib.base import ik_chain, limb, neck, spine
from mayaLib.rigLib.base.module import Base
from mayaLib.rigLib.utils import (
    ctrl_shape,
    ikfk_switch,
    joint,
    proxy_geo,
    skin,
    stretchy_ik_chain,
    util,
)

__all__ = ["BaseRig", "HumanoidRig"]


class BaseRig:  # pylint: disable=too-many-instance-attributes
    """Bootstrap common rig-building flows used by specialised rigs."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,too-many-positional-arguments
        self,
        character_name: str = "new",
        model_file_path: str = "",
        build_scene_file_path: str = "",
        root_joint: str = "spineJA_jnt",
        head_joint: str = "headJA_jnt",
        load_skin_cluster: bool = True,
        do_proxy_geo: bool = True,
        go_to_t_pose: bool = True,
    ) -> None:
        """Initialize base rig setup with model and build scene.

        Sets up the foundational rig hierarchy, imports model and build files,
        loads skin weights, and optionally generates proxy geometry for fast display.

        Args:
            character_name: Name prefix for rig hierarchy nodes. Defaults to 'new'.
            model_file_path: Path to model file to import. Defaults to '' (skip import).
            build_scene_file_path: Path to build scene with joints/guides. Defaults to '' (skip).
            root_joint: Root joint of skeleton hierarchy. Defaults to 'spineJA_jnt'.
            head_joint: Head joint for head/neck setup. Defaults to 'headJA_jnt'.
            load_skin_cluster: Load saved skin weights if available. Defaults to True.
            do_proxy_geo: Generate per-joint proxy geometry for fast display. Defaults to True.
            go_to_t_pose: Load T-pose before rigging. Defaults to True.

        Attributes:
            proxy_geo_list: List of generated proxy geometry meshes
            skin_model: Main skinned model mesh

        Example:
            >>> rig = Rig(character_name='hero', model_file_path='hero_model.ma')
        """
        start_time = pm.timerX()
        print("-- START --")

        if build_scene_file_path:
            pm.newFile(force=True)

        if model_file_path:
            pm.importFile(model_file_path)

        if build_scene_file_path:
            pm.importFile(build_scene_file_path)

        if go_to_t_pose:
            joint.load_t_pose(root_joint)

        self.proxy_geo_list = pm.ls("*_PRX")
        proxy_geo_instance = None
        if do_proxy_geo and not self.proxy_geo_list and pm.ls("mainProxy_GEO"):
            main_proxy_geo = pm.ls("mainProxy_GEO")[0]
            proxy_geo_instance = proxy_geo.ProxyGeo(main_proxy_geo)
            self.proxy_geo_list = proxy_geo_instance.get_proxy_geo_list()

        self.prepare()

        self.scene_radius = 1
        model_group = pm.ls(f"{character_name}_model_GRP")
        if model_group:
            radius = util.get_planar_radius_bbox(model_group[0])["planarY"]
            self.scene_radius = radius

        self.base_module = Base(
            character_name=character_name,
            scale=self.scene_radius,
            main_ctrl_attach_obj=head_joint,
        )
        self.rig()

        if model_group:
            pm.parent(model_group, self.base_module.medium_slow_group)
            if self.proxy_geo_list:
                pm.parent(self.proxy_geo_list, self.base_module.fast_model_group)
                if (
                    do_proxy_geo
                    and pm.ls("mainProxy_GEO")
                    and proxy_geo_instance
                    and pm.objExists(proxy_geo_instance.get_fast_geo_group())
                ):
                    pm.delete(proxy_geo_instance.get_fast_geo_group(), pm.ls("mainProxy_GEO"))

        if pm.objExists("skeletonModel_GRP"):
            pm.parent("skeletonModel_GRP", self.base_module.rig_model_group)

        if pm.objExists(root_joint):
            pm.parent(root_joint, self.base_module.joints_group)

        if load_skin_cluster:
            joint.load_projection_pose(root_joint)
            geo_list = [geo.name() for geo in pm.ls("*_GEO")]
            skin.load_skin_weights(character_name, geo_list)

        self.upgrade()

        if pm.objExists("controlShapes_GRP"):
            control_shape_nodes = pm.ls("*_shape_CTRL*")
            ctrl_nodes = [
                node for node in pm.ls("*_CTRL", "*_CTRL?") if node not in control_shape_nodes
            ]
            for ctrl_node in ctrl_nodes:
                for shape_node in control_shape_nodes:
                    ctrl_name = str(ctrl_node.name())
                    shape_name = str(shape_node.name())
                    if shape_name.replace("_shape_CTRL", "_CTRL") == ctrl_name:
                        print(f"Transfering Shape: {shape_name} <-----> {ctrl_name}")
                        ctrl_shape.copyShape(shape_node, ctrl_node)
            pm.delete("controlShapes_GRP")

        self.finalize()

        total = pm.timerX(startTime=start_time)
        print("-- END --")
        print(("Total time: ", total))

    def prepare(self) -> None:  # pragma: no cover - intended override hook
        """Hook for subclasses to prepare prerequisites before rigging."""
        print("-- PREPARE --")

    def rig(self) -> None:  # pragma: no cover - intended override hook
        """Hook invoked to build the specific rig implementation."""
        print("-- RIG --")

    def upgrade(self) -> None:  # pragma: no cover - intended override hook
        """Hook invoked after rig creation for additional setup."""
        print("-- UPGRADE --")

    def finalize(self) -> None:  # pragma: no cover - intended override hook
        """Hook invoked after rig building to perform clean-up."""
        print("-- FINALIZE --")

    def make_spine(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prefix: str,
        root_joint: str,
        spine_joints: Sequence[str],
        scene_scale: float,
    ) -> spine.Spine:
        """Create a spine rig module."""
        return spine.Spine(
            spine_joints,
            root_joint,
            prefix=prefix,
            rig_scale=scene_scale,
            base_rig=self.base_module,
        )

    def make_neck(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prefix: str,
        head_joint: str,
        neck_joints: Sequence[str],
        scene_scale: float,
        spine_rig: spine.Spine | None = None,
        spine_joints: Sequence[str] | None = None,
    ) -> neck.Neck:
        """Create a neck rig module and parent it to the spine when available."""
        neck_rig = neck.Neck(
            neck_joints,
            head_joint,
            prefix=prefix,
            rig_scale=scene_scale,
            base_rig=self.base_module,
        )

        if spine_rig and spine_joints:
            pm.parentConstraint(
                spine_joints[-1],
                neck_rig.getModuleDict()["baseAttachGrp"],
                mo=1,
            )
            pm.parentConstraint(
                spine_rig.getModuleDict()["bodyCtrl"].C,
                neck_rig.getModuleDict()["bodyAttachGrp"],
                mo=1,
            )

        return neck_rig

    def make_tail(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        pelvis_joint: pm.PyNode,
        tail_joints: Sequence[str],
        do_dynamic_tail: bool,
        scene_scale: float,
    ) -> ik_chain.IKChain:
        """Create a tail rig as an IK chain attached to the pelvis joint."""
        tail_rig = ik_chain.IKChain(
            chain_joints=tail_joints,
            prefix="tail",
            rig_scale=scene_scale,
            do_dynamic=do_dynamic_tail,
            smallest_scale_percent=0.4,
            fk_parenting=False,
            base_rig=self.base_module,
        )

        pm.parentConstraint(
            pelvis_joint,
            tail_rig.getModuleDict()["baseAttachGrp"],
            mo=1,
        )

        return tail_rig

    def make_limb(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        spine_rig: spine.Spine,
        clavicle_joint: str,
        scapula_joint: str,
        limb_joints: Sequence[str],
        top_finger_joints: Sequence[str],
        spine_driver_joint: str = "",
        use_metacarpal_joint: bool = False,
    ) -> limb.Limb:
        """Create an arm or leg rig and attach it to the provided spine module."""
        limb_rig = limb.Limb(
            limb_joints=limb_joints,
            top_finger_joints=top_finger_joints,
            clavicle_joint=clavicle_joint,
            scapula_joint=scapula_joint,
            base_rig=self.base_module,
            use_metacarpal_joint=use_metacarpal_joint,
        )

        if spine_driver_joint:
            pm.parentConstraint(
                spine_driver_joint,
                limb_rig.get_module_dict()["base_attach_grp"],
                mo=1,
            )
        pm.parentConstraint(
            spine_rig.getModuleDict()["bodyCtrl"].C,
            limb_rig.get_module_dict()["body_attach_grp"],
            mo=1,
        )

        return limb_rig


class HumanoidRig(BaseRig):  # pylint: disable=too-many-instance-attributes
    """Concrete rig builder targeting humanoid character templates."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-positional-arguments
        self,
        character_name: str = "new",
        model_file_path: str = "",
        build_scene_file_path: str = "",
        scene_scale: float = 1.0,
        root_joint: str = "rootJA_JNT",
        head_joint: str = "headJA_JNT",
        load_skin_cluster: bool = True,
        do_proxy_geo: bool = True,
        do_spine: bool = True,
        do_neck: bool = True,
        do_tail: bool = False,
        do_dynamic_tail: bool = False,
        do_stretchy: bool = False,
        do_flexyplane: bool = False,
        go_to_t_pose: bool = True,
    ) -> None:
        """Initialize humanoid character rig with full body setup.

        Creates a complete humanoid rig including spine, neck, limbs, hands, feet,
        with optional features like stretchy IK, dynamic tails, and Flexiplanes.

        Args:
            character_name: Name prefix for rig hierarchy. Defaults to 'new'.
            model_file_path: Path to model file to import. Defaults to '' (skip).
            build_scene_file_path: Path to build scene with skeleton. Defaults to '' (skip).
            scene_scale: Global scale multiplier for rig. Defaults to 1.0.
            root_joint: Root joint of skeleton. Defaults to 'rootJA_JNT'.
            head_joint: Head joint for head setup. Defaults to 'headJA_JNT'.
            load_skin_cluster: Load saved skin weights. Defaults to True.
            do_proxy_geo: Generate proxy geometry for fast display. Defaults to True.
            do_spine: Build spine rig module. Defaults to True.
            do_neck: Build neck rig module. Defaults to True.
            do_tail: Build tail rig module. Defaults to False.
            do_dynamic_tail: Use dynamic curve for tail. Defaults to False.
            do_stretchy: Add stretchy IK to limbs. Defaults to False.
            do_flexyplane: Add Flexiplane volume preservation. Defaults to False.
            go_to_t_pose: Load T-pose before rigging. Defaults to True.

        Example:
            >>> rig = HumanoidRig(
            ...     character_name='hero',
            ...     model_file_path='hero.ma',
            ...     do_stretchy=True
            ... )
        """
        self.root_joint = root_joint
        self.head_joint = head_joint
        self.do_spine = do_spine
        self.do_neck = do_neck
        self.do_tail = do_tail
        self.do_dynamic_tail = do_dynamic_tail
        self.do_stretchy = do_stretchy
        self.do_flexyplane = do_flexyplane
        self.go_to_t_pose = go_to_t_pose
        self.scene_scale = scene_scale

        super().__init__(
            character_name=character_name,
            model_file_path=model_file_path,
            build_scene_file_path=build_scene_file_path,
            root_joint=root_joint,
            head_joint=head_joint,
            load_skin_cluster=load_skin_cluster,
            do_proxy_geo=do_proxy_geo,
            go_to_t_pose=go_to_t_pose,
        )

    def rig(self) -> None:  # pylint: disable=too-many-locals
        """Build the humanoid rig by instantiating spine, limbs, and accessories."""
        print("-- RIG HUMANOID --")

        if self.go_to_t_pose:
            joint.load_t_pose(self.root_joint)

        spine_joints = []
        if self.do_spine:
            spine_joints = pm.ls("spineJ?_JNT")
            self.spine_rig = self.make_spine(
                prefix="spine",
                root_joint=self.root_joint,
                spine_joints=spine_joints,
                scene_scale=self.scene_scale,
            )

        if self.do_neck:
            neck_joints = pm.ls("neckJ?_JNT")
            self.neck_rig = self.make_neck(
                prefix="neck",
                head_joint=self.head_joint,
                neck_joints=neck_joints,
                scene_scale=self.scene_scale,
                spine_rig=getattr(self, "spine_rig", None),
                spine_joints=spine_joints,
            )

        if self.do_tail:
            tail_joints = pm.ls("tail*_JNT")
            pelvis_joint = pm.ls(self.root_joint)[0]
            self.tail_rig = self.make_tail(
                pelvis_joint,
                tail_joints,
                self.do_dynamic_tail,
                self.scene_scale,
            )
        else:
            pelvis_joint = None

        if getattr(self, "spine_rig", None) and spine_joints:
            spine_module = self.spine_rig.getModuleDict()
            spine_driver = spine_joints[-1]
        else:
            spine_module = None
            spine_driver = ""

        if getattr(self, "neck_rig", None) and spine_module:
            pm.parentConstraint(
                spine_driver,
                self.neck_rig.getModuleDict()["baseAttachGrp"],
                mo=1,
            )
            pm.parentConstraint(
                spine_module["bodyCtrl"].C,
                self.neck_rig.getModuleDict()["bodyAttachGrp"],
                mo=1,
            )

        if getattr(self, "tail_rig", None) and spine_module and pelvis_joint:
            pm.parentConstraint(
                pelvis_joint,
                self.tail_rig.getModuleDict()["baseAttachGrp"],
                mo=1,
            )

        if getattr(self, "spine_rig", None):
            hip_joint = spine_joints[0] if spine_joints else ""
            self.l_arm_rig = self.make_limb(
                self.spine_rig,
                pm.ls("l_clavicleJA_JNT")[0],
                "",
                pm.ls("l_armJ?_JNT", "l_handJA_JNT"),
                pm.ls(
                    "l_fngThumbJA_JNT",
                    "l_fngIndexJA_JNT",
                    "l_fngMiddleJA_JNT",
                    "l_fngRingJA_JNT",
                    "l_fngPinkyJA_JNT",
                ),
                spine_driver,
            )
            self.r_arm_rig = self.make_limb(
                self.spine_rig,
                pm.ls("r_clavicleJA_JNT")[0],
                "",
                pm.ls("r_armJ?_JNT", "r_handJA_JNT"),
                pm.ls(
                    "r_fngThumbJA_JNT",
                    "r_fngIndexJA_JNT",
                    "r_fngMiddleJA_JNT",
                    "r_fngRingJA_JNT",
                    "r_fngPinkyJA_JNT",
                ),
                spine_driver,
            )
            self.l_leg_rig = self.make_limb(
                self.spine_rig,
                "",
                "",
                pm.ls("l_legJ?_JNT", "l_footJA_JNT"),
                pm.ls(
                    "l_toeThumbJA_JNT",
                    "l_toeIndexJA_JNT",
                    "l_toeMiddleJA_JNT",
                    "l_toeRingJA_JNT",
                    "l_toePinkyJA_JNT",
                ),
                hip_joint,
            )
            self.r_leg_rig = self.make_limb(
                self.spine_rig,
                "",
                "",
                pm.ls("r_legJ?_JNT", "r_footJA_JNT"),
                pm.ls(
                    "r_toeThumbJA_JNT",
                    "r_toeIndexJA_JNT",
                    "r_toeMiddleJA_JNT",
                    "r_toeRingJA_JNT",
                    "r_toePinkyJA_JNT",
                ),
                hip_joint,
            )

        if self.do_stretchy:
            stretchy_ik_chain.StretchyIKChain(
                self.l_arm_rig.get_main_limb_ik(),
                self.l_arm_rig.get_main_ik_control().get_control(),
                do_flexyplane=self.do_flexyplane,
            )
            stretchy_ik_chain.StretchyIKChain(
                self.r_arm_rig.get_main_limb_ik(),
                self.r_arm_rig.get_main_ik_control().get_control(),
                do_flexyplane=self.do_flexyplane,
            )
            stretchy_ik_chain.StretchyIKChain(
                self.l_leg_rig.get_main_limb_ik(),
                self.l_leg_rig.get_main_ik_control().get_control(),
                do_flexyplane=self.do_flexyplane,
            )
            stretchy_ik_chain.StretchyIKChain(
                self.r_leg_rig.get_main_limb_ik(),
                self.r_leg_rig.get_main_ik_control().get_control(),
                do_flexyplane=self.do_flexyplane,
            )

        ikfk_switch.installIKFK(
            [
                self.l_arm_rig.get_main_limb_ik(),
                self.r_arm_rig.get_main_limb_ik(),
                self.l_leg_rig.get_main_limb_ik(),
                self.r_leg_rig.get_main_limb_ik(),
            ]
        )


if __name__ == "__main__":
    pass
