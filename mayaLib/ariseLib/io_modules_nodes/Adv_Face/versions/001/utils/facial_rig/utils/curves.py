"""
Curve utility functions.
"""

from typing import List, Optional, Tuple

import maya.cmds as cmds


class CurveUtils:
    """Utility class for curve operations."""

    @staticmethod
    def create_curve_from_vertices(
        vertices: List[str], name: str, degree: int = 3, close: bool = False
    ) -> str:
        """
        Create a curve passing through vertex positions.

        Args:
            vertices: List of vertex names
            name: Curve name
            degree: Curve degree
            close: Whether to close the curve

        Returns:
            Curve name
        """
        positions = []
        for vtx in vertices:
            pos = cmds.xform(vtx, query=True, worldSpace=True, translation=True)
            positions.append(pos)

        if close and positions:
            positions.append(positions[0])

        curve = cmds.curve(name=name, degree=degree, point=positions)
        return curve

    @staticmethod
    def rebuild_curve(curve: str, spans: int = 5, degree: int = 3, keep_range: bool = False):
        """
        Rebuild a curve with specified parameters.

        Args:
            curve: Curve name
            spans: Number of spans
            degree: Curve degree
            keep_range: Keep original parameter range
        """
        cmds.rebuildCurve(
            curve,
            constructionHistory=False,
            replaceOriginal=True,
            rebuildType=0,
            endKnots=1,
            keepRange=1 if keep_range else 0,
            keepControlPoints=False,
            keepEndPoints=True,
            keepTangents=False,
            spans=spans,
            degree=degree,
            tolerance=0.01,
        )

    @staticmethod
    def get_curve_cv_count(curve: str) -> int:
        """
        Get the number of CVs on a curve.

        Args:
            curve: Curve name

        Returns:
            Number of CVs
        """
        spans = cmds.getAttr(f"{curve}.spans")
        degree = cmds.getAttr(f"{curve}.degree")
        return spans + degree

    @staticmethod
    def get_point_on_curve(
        curve: str, parameter: float, use_percentage: bool = True
    ) -> List[float]:
        """
        Get position on curve at parameter.

        Args:
            curve: Curve name
            parameter: Parameter value (0-1 if percentage)
            use_percentage: Whether parameter is percentage

        Returns:
            Position [x, y, z]
        """
        poci = cmds.createNode("pointOnCurveInfo", name="tempPOCI")
        cmds.connectAttr(f"{curve}.worldSpace[0]", f"{poci}.inputCurve")
        cmds.setAttr(f"{poci}.turnOnPercentage", use_percentage)
        cmds.setAttr(f"{poci}.parameter", parameter)

        position = cmds.getAttr(f"{poci}.position")[0]
        cmds.delete(poci)
        return list(position)

    @staticmethod
    def get_nearest_parameter(curve: str, position: List[float]) -> float:
        """
        Get the nearest parameter on curve to a position.

        Args:
            curve: Curve name
            position: World space position

        Returns:
            Parameter value
        """
        npoc = cmds.createNode("nearestPointOnCurve", name="tempNPOC")
        cmds.connectAttr(f"{curve}.worldSpace[0]", f"{npoc}.inputCurve")
        cmds.setAttr(f"{npoc}.inPosition", *position, type="float3")

        param = cmds.getAttr(f"{npoc}.parameter")
        cmds.delete(npoc)
        return param

    @staticmethod
    def attach_to_curve(obj: str, curve: str, parameter: float, use_percentage: bool = True) -> str:
        """
        Attach an object to a curve using pointOnCurveInfo.

        Args:
            obj: Object to attach
            curve: Target curve
            parameter: Curve parameter
            use_percentage: Whether to use percentage parameter

        Returns:
            Name of pointOnCurveInfo node
        """
        poci = cmds.createNode("pointOnCurveInfo")
        cmds.connectAttr(f"{curve}.worldSpace[0]", f"{poci}.inputCurve")
        cmds.setAttr(f"{poci}.turnOnPercentage", use_percentage)
        cmds.setAttr(f"{poci}.parameter", parameter)
        cmds.connectAttr(f"{poci}.position", f"{obj}.translate")
        return poci

    @staticmethod
    def create_locators_on_curve(curve: str, count: int, name_base: str) -> List[str]:
        """
        Create locators distributed along curve.

        Args:
            curve: Curve name
            count: Number of locators
            name_base: Base name for locators

        Returns:
            List of locator names
        """
        locators = []
        for i in range(count):
            param = i / (count - 1) if count > 1 else 0.5
            pos = CurveUtils.get_point_on_curve(curve, param)

            loc = cmds.spaceLocator(name=f"{name_base}{i}")[0]
            cmds.xform(loc, worldSpace=True, translation=pos)
            locators.append(loc)

        return locators

    @staticmethod
    def skin_curve_to_joints(curve: str, joints: List[str], name: Optional[str] = None) -> str:
        """
        Create skin cluster for curve with joints.

        Args:
            curve: Curve name
            joints: List of joint names
            name: Optional skin cluster name

        Returns:
            Skin cluster name
        """
        cmds.select(joints, curve)
        result = cmds.newSkinCluster(
            "-toSelectedBones",
            "-maximumInfluences",
            3,
            "-dropoffRate",
            4,
            "-removeUnusedInfluence",
            False,
        )
        skin_cluster = result[0]

        if name:
            skin_cluster = cmds.rename(skin_cluster, name)

        return skin_cluster

    @staticmethod
    def create_wire_deformer(curve: str, geometry: str, dropoff: float = 1.0) -> Tuple[str, str]:
        """
        Create a wire deformer.

        Args:
            curve: Driver curve
            geometry: Target geometry
            dropoff: Dropoff distance

        Returns:
            Tuple of (wire_node, base_curve)
        """
        result = cmds.wire(geometry, wire=curve, dropoffDistance=[0, dropoff], envelope=1)
        return result[0], f"{curve}BaseWire"

    @staticmethod
    def mirror_curve(curve: str, axis: str = "x") -> str:
        """
        Mirror curve across specified axis.

        Args:
            curve: Source curve
            axis: Mirror axis ("x", "y", or "z")

        Returns:
            Mirrored curve name
        """
        mirrored = cmds.duplicate(curve)[0]

        # Get scale values based on axis
        scale = [-1, 1, 1] if axis == "x" else [1, -1, 1] if axis == "y" else [1, 1, -1]

        # Scale CVs
        num_cvs = CurveUtils.get_curve_cv_count(mirrored)
        cmds.scale(
            scale[0],
            scale[1],
            scale[2],
            f"{mirrored}.cv[0:{num_cvs}]",
            relative=True,
            pivot=(0, 0, 0),
        )

        return mirrored

    @staticmethod
    def loft_curves_to_surface(curves: List[str], name: str, degree: int = 3) -> str:
        """
        Loft curves into a nurbs surface.

        Args:
            curves: List of profile curves
            name: Surface name
            degree: Surface degree

        Returns:
            Surface name
        """
        surface = cmds.loft(
            curves,
            name=name,
            constructionHistory=False,
            uniform=True,
            close=False,
            degree=degree,
            sectionSpans=1,
            range=False,
            polygon=0,
        )[0]
        return surface
