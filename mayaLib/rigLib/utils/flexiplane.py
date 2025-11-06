"""Flexiplane rig builder utilities."""

from __future__ import annotations

from collections.abc import Iterable
from string import ascii_letters

import pymel.core as pm

from mayaLib.pipelineLib.utility import name_check
from mayaLib.rigLib.utils import util
from mayaLib.shaderLib.base import shader_base

__all__ = ['Flexiplane']


def _ensure_list(nodes: Iterable) -> list:
    """Convert a Maya selection to a concrete list."""
    return list(nodes or [])


class Flexiplane:  # pylint: disable=too-many-instance-attributes
    """Create and manage flexiplane deformation rigs."""

    DEFAULT_SETTINGS = {
        'prefix': 'M_',
        'num': 0,
    }

    def __init__(self, prefix: str = '') -> None:
        """Initialize Flexiplane surface deformer.

        Creates a flexible plane surface deformer useful for cloth, wings, fins,
        or other flat deformable surfaces driven by joint hierarchies.

        Args:
            prefix: Naming prefix for created nodes. Defaults to ''.

        Example:
            >>> flexi = Flexiplane(prefix='wing')
        """
        self.flexiplane_pattern = 'flexiPlane*'
        self.surface_suffix = 'NURBS'
        self.highlight_colour = 17

        Flexiplane.DEFAULT_SETTINGS['prefix'] = prefix
        Flexiplane.DEFAULT_SETTINGS['num'] += 1

        self.fp_grp = None
        self.fp_gm_ctrl = None
        self.ctrl_a = None
        self.ctrl_b = None
        self.ctrl_mid = None

        self._build_flexiplane(prefix)

    # ---------------------------------------------------------------------
    # Utility creation helpers
    def safe_delete(self) -> tuple[list, list]:
        """Delete the selected flexiplane controls and supporting nodes."""
        selection = pm.selected()
        flex_controls = [ctl for ctl in selection if '_flexiPlane_ctrl_global' in ctl.nodeName()]
        curve_names = [ctl.replace('ctrl_global', 'curveInfo') for ctl in flex_controls]

        for curve in curve_names:
            pm.delete(curve)
        for ctl in flex_controls:
            pm.delete(ctl.getParent())

        return flex_controls, curve_names

    @staticmethod
    def create_plane(name: str, width: float = 10, length_ratio: float = 0.2):
        """Create the base NURBS plane for the flexiplane surface."""
        return pm.nurbsPlane(
            name=name,
            width=width,
            lengthRatio=length_ratio,
            patchesU=width / 2,
            degree=3,
            axis=[0, 1, 0],
            constructionHistory=False,
        )

    @staticmethod
    def create_lambert(geo, color=(0.5, 0.5, 0.5), transparency=(0.0, 0.0, 0.0)) -> None:
        """Apply a lambert material to the supplied geometry."""
        shader = shader_base.build_lambert(
            shaderType='lambert',
            shaderName='flexiPlane_lambert_material',
            color=color,
            transparency=transparency,
        )
        shader_base.assign_shader(geo, shader)

    @staticmethod
    def create_surface_shader(geo, color=(0.5, 0.5, 0.5)) -> None:
        """Apply a simple surface shader to the supplied geometry."""
        shader = shader_base.build_surfaceshader(
            shaderType='surfaceShader',
            shaderName='flexiPlane_surface_material',
            color=color,
        )
        shader_base.assign_shader(geo, shader)

    @staticmethod
    def ctrl_square(name: str | None = None, pos=None):
        """Create a square control curve positioned at ``pos``."""
        if not name:
            name = 'flexiPlane_ctrl'
        if pos is None:
            pos = [0, 0, 0]
        ctrl = pm.curve(
            d=1,
            p=[(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1)],
            k=[0, 1, 2, 3, 4],
            n=name,
        )
        ctrl.overrideEnabled.set(1)
        ctrl.overrideColor.set(17)
        pm.move(pos, rpr=True)
        pm.scale(0.5, 0.5, 0.5, r=True)
        pm.makeIdentity(t=1, r=1, s=1, a=True)
        ctrl.rotateOrder.set('xzy')
        return ctrl

    @staticmethod
    def create_follicle(onurbs, name, u_pos=0.0, v_pos=0.0):
        """Create a follicle on the supplied NURBS surface."""
        if onurbs.type() == 'transform':
            onurbs = onurbs.getShape()
        elif onurbs.type() != 'nurbsSurface':
            pm.warning('Input must be a NURBS surface.')
            return None

        follicle_shape = pm.createNode('follicle', name=f'{name}Shape')
        onurbs.local.connect(follicle_shape.inputSurface)
        onurbs.worldMatrix[0].connect(follicle_shape.inputWorldMatrix)
        follicle_shape.outRotate.connect(follicle_shape.getParent().rotate)
        follicle_shape.outTranslate.connect(follicle_shape.getParent().translate)
        follicle_shape.parameterU.set(u_pos)
        follicle_shape.parameterV.set(v_pos)
        follicle_shape.getParent().t.lock()
        follicle_shape.getParent().r.lock()
        return follicle_shape

    @staticmethod
    def make_cluster(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        target,
        name=None,
        origin=0,
        pos_x=0,
        pos_y=0,
        pos_z=0,
    ):
        """Create a cluster for the given target CVs."""
        cluster = pm.cluster(target, rel=1, en=1.0, n=name)
        if origin != 0:
            cluster[1].originX.set(origin)
            pm.move(pos_x, pos_y, pos_z, cluster[1].scalePivot, cluster[1].rotatePivot)
        return cluster

    def cluster_curve(self, curve, name):
        """Add clusters to the three CV curve used by the flexiplane wire."""
        cluster_a = self.make_cluster(
            target=curve.cv[0:1],
            name=f'{name}_a_CL',
            origin=-6,
            pos_x=-5,
            pos_z=-5,
        )
        cluster_b = self.make_cluster(
            target=curve.cv[1:2],
            name=f'{name}_b_CL',
            origin=6,
            pos_x=5,
            pos_z=-5,
        )
        cluster_mid = self.make_cluster(target=curve.cv[1], name=f'{name}_mid_CL')
        pm.percent(cluster_a[0], curve.cv[1], v=0.5)
        pm.percent(cluster_b[0], curve.cv[1], v=0.5)
        return cluster_a, cluster_b, cluster_mid

    def flexiplane_mid_ctrl(self, name: str | None = None):
        """Create the mid control sphere used for bend control."""
        if not name:
            name = '_mid_ctrl'
        mid_ctrl = pm.polySphere(
            n=name,
            r=0.3,
            sx=8,
            sy=8,
            ax=(0.0, 1.0, 0.0),
            ch=False,
        )[0]
        self.create_surface_shader(mid_ctrl, color=(1.0, 1.0, 0.0))
        return mid_ctrl

    def global_ctrl(self, name: str = 'ctrl'):
        """Create the global move control for the flexiplane."""
        global_ctrl = pm.circle(
            c=[0, 0, -2],
            sw=360,
            r=0.3,
            nr=[0, 1, 0],
            ch=0,
            n=f'{name}_global_CTRL',
        )[0]
        shape_a = global_ctrl.getShape()
        shape_a.overrideEnabled.set(1)
        shape_a.overrideColor.set(17)
        pm.addAttr(ln='_', at='enum', en='volume:')
        global_ctrl._.set(e=True, cb=True)
        pm.addAttr(ln='enable', sn='en', at='bool', k=True)

        secondary_ctrl = pm.circle(
            c=[0, 0, 2],
            sw=360,
            r=0.3,
            nr=[0, 1, 0],
            ch=0,
            n=f'{name}global_b_CTRL',
        )[0]
        shape_b = secondary_ctrl.getShape()
        shape_b.overrideEnabled.set(1)
        shape_b.overrideColor.set(17)
        pm.parent(shape_b, global_ctrl, r=True, s=True)
        pm.delete(secondary_ctrl)
        pm.select(global_ctrl, r=True)
        return global_ctrl

    # ------------------------------------------------------------------
    # Flexiplane assembly
    def _build_flexiplane(  # pylint: disable=too-many-locals,too-many-statements
        self,
        prefix: str = '',
    ) -> None:
        fp_name = f'{prefix}flexiPlane'
        fp_name = name_check.name_check(f'{fp_name}*_GRP').replace('_GRP', '', 1)

        fp_surface = self.create_plane(f'{fp_name}_NURBS')[0]
        fp_surface.overrideEnabled.set(1)
        fp_surface.overrideDisplayType.set(2)
        self.create_lambert(
            fp_surface,
            color=(0.067, 0.737, 0.749),
            transparency=(0.75, 0.75, 0.75),
        )

        follicles = []
        u_value = 0.1
        for index in range(5):
            follicle = self.create_follicle(
                fp_surface,
                f'{fp_name}_flc_{ascii_letters[index + 26]}_FLC',
                u_value,
                0.5,
            )
            if follicle:
                follicles.append(follicle)
            u_value += 0.2

        follicle_group = pm.group(follicles, name=f'{fp_name}_flcs_GRP')

        self.ctrl_a = self.ctrl_square(name=f'{fp_name}_ctrl_a_CTRL', pos=[-5, 0, 0])
        pm.rename(self.ctrl_a.getShape(), f'{self.ctrl_a}Shape')

        self.ctrl_b = self.ctrl_square(name=f'{fp_name}_ctrl_b_CTRL', pos=[5, 0, 0])
        pm.rename(self.ctrl_b.getShape(), f'{self.ctrl_b}Shape')

        fp_blendshape = pm.duplicate(fp_surface, n=f'{fp_name}_bshp_NURBS')[0]
        pm.move(0, 0, -5, fp_blendshape)

        blendshape_node = pm.blendShape(fp_blendshape, fp_surface, n=f'{fp_name}_BSHP')[0]
        pm.setAttr(f'{blendshape_node}.{fp_blendshape}', 1)

        fp_curve = pm.curve(
            d=2,
            p=[(-5, 0, -5), (0, 0, -5), (5, 0, -5)],
            k=[0, 0, 1, 1],
            n=f'{fp_name}_wire_CV',
        )
        cluster_a, cluster_b, cluster_mid = self.cluster_curve(fp_curve, fp_name)

        pm.select(fp_blendshape)
        twist_nodes = pm.nonLinear(type='twist', lowBound=-1, highBound=1)
        pm.rename(twist_nodes[0], f'{fp_name}_twistAttr_surface_NURBS')
        pm.rename(twist_nodes[1], f'{fp_name}_twist_Handle_DEFORMER')
        twist_nodes[1].rz.set(90)
        pm.connectAttr(self.ctrl_b.rx, twist_nodes[0].startAngle, f=True)
        pm.connectAttr(self.ctrl_a.rx, twist_nodes[0].endAngle, f=True)

        wire_nodes = pm.wire(
            fp_blendshape,
            w=fp_curve,
            gw=False,
            en=1,
            ce=0,
            li=0,
            n=f'{fp_name}_wireAttrs_DEFORMER',
        )
        wire_deformer = wire_nodes[0]
        wire_base = wire_nodes[1]
        wire_deformer.dropoffDistance[0].set(20)
        history = pm.listHistory(fp_surface)
        tweaks = [node for node in history if 'tweak' in node.nodeName()]
        if len(tweaks) >= 3:
            pm.rename(tweaks[2], f'{fp_name}_cl_cluster_tweak')
            pm.rename(tweaks[0], f'{fp_name}_wireAttrs_tweak')
            pm.rename(tweaks[1], f'{fp_name}_extra_tweak')

        cluster_group = pm.group(cluster_a[1], cluster_b[1], cluster_mid[1], n=f'{fp_name}_cls_GRP')
        util.lock_and_hide_all(cluster_group)

        self.ctrl_mid = self.flexiplane_mid_ctrl(name=f'{fp_name}_ctrl_mid_CTRL')
        ctrl_mid_group = pm.group(self.ctrl_mid, n=f'{fp_name}_grp_midBend_GRP')
        pm.pointConstraint(self.ctrl_a, self.ctrl_b, ctrl_mid_group, o=[0, 0, 0], w=1)

        control_group = pm.group(self.ctrl_a, self.ctrl_b, ctrl_mid_group, n=f'{fp_name}_ctrl_GRP')
        util.lock_and_hide_all(control_group)

        pm.connectAttr(self.ctrl_a.t, cluster_a[1].t, f=True)
        pm.connectAttr(self.ctrl_b.t, cluster_b[1].t, f=True)
        pm.connectAttr(self.ctrl_mid.t, cluster_mid[1].t, f=True)

        util.no_render(fp_surface)
        util.no_render(fp_blendshape)
        util.no_render(self.ctrl_mid)

        self.fp_grp = pm.group(
            fp_surface,
            follicle_group,
            fp_blendshape,
            wire_deformer,
            wire_base,
            cluster_group,
            control_group,
            n=f'{fp_name}_GRP',
        )
        util.lock_and_hide_all(self.fp_grp)

        global_move_group = pm.group(fp_surface, control_group, n=f'{fp_name}_globalMove_GRP')
        extra_nodes_group = pm.group(
            follicle_group,
            fp_blendshape,
            wire_deformer,
            wire_base,
            f'{fp_name}_wire_CVBaseWire',
            cluster_group,
            n=f'{fp_name}_extraNodes_GRP',
        )
        pm.parent(twist_nodes, extra_nodes_group)
        pm.parent(extra_nodes_group, self.fp_grp)
        extra_nodes_group.overrideEnabled.set(1)
        extra_nodes_group.overrideDisplayType.set(2)

        for follicle in follicles:
            pm.scaleConstraint(global_move_group, follicle.getParent())

        self.fp_gm_ctrl = self.global_ctrl(name=fp_name)
        pm.parent(self.fp_gm_ctrl, self.fp_grp)
        pm.parent(global_move_group, self.fp_gm_ctrl)

        joints = []
        for index, follicle in enumerate(follicles):
            pos_x = round(follicle.getParent().translateX.get(), 4)
            joint = pm.joint(
                p=(pos_x, 0, 0),
                rad=0.5,
                n=f'{fp_name}bind_{ascii_letters[index + 26]}_JNT',
            )
            joints.append(joint)
            pm.parent(joint, follicle.getParent())

        util.lock_and_hide_all(fp_surface)
        twist_nodes[1].visibility.set(0)
        cluster_group.visibility.set(0)
        fp_blendshape.visibility.set(0)
        fp_curve.visibility.set(0)

        length_node = pm.arclen(fp_curve, ch=1)
        length_node.rename(f'{fp_name}curveInfo_DEFORMER')

        div_node = pm.createNode('multiplyDivide', n=f'{fp_name}div_squashStretch_length')
        div_node.operation.set(2)

        volume_div = pm.createNode('multiplyDivide', n=f'{fp_name}div_volume')
        volume_div.operation.set(2)
        volume_div.input1X.set(1)

        condition_node = pm.createNode('condition', n=f'{fp_name}cond_volume')
        condition_node.secondTerm.set(1)

        pm.connectAttr(length_node.arcLength, div_node.input1.input1X, f=True)
        div_node.input2.input2X.set(10)
        pm.connectAttr(div_node.outputX, volume_div.input2.input2X, f=True)
        pm.connectAttr(self.fp_gm_ctrl.enable, condition_node.firstTerm, f=True)
        pm.connectAttr(volume_div.outputX, condition_node.colorIfTrueR, f=True)

        for joint in joints:
            pm.connectAttr(condition_node.outColorR, joint.sy, f=True)
            pm.connectAttr(condition_node.outColorR, joint.sz, f=True)
        for follicle in follicles:
            follicle.visibility.set(0)

        twist_nodes[1].visibility.set(0)
        cluster_group.visibility.set(0)
        fp_blendshape.visibility.set(0)
        fp_curve.visibility.set(0)

        pm.select(self.fp_gm_ctrl, r=True)

    # ------------------------------------------------------------------
    def get_controls(self):
        """Return the flexiplane global and bend controls."""
        return self.fp_gm_ctrl, self.ctrl_a, self.ctrl_b, self.ctrl_mid

    def get_top_group(self):
        """Return the top-level flexiplane group transform."""
        return self.fp_grp


if __name__ == '__main__':
    Flexiplane()
