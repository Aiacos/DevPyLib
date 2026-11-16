"""
Constraint utility functions.
"""

from typing import List, Optional, Tuple

import maya.cmds as cmds


class ConstraintUtils:
    """Utility class for constraint operations."""

    @staticmethod
    def parent_constraint(
        driver: str,
        driven: str,
        maintain_offset: bool = True,
        skip_translate: Optional[List[str]] = None,
        skip_rotate: Optional[List[str]] = None,
    ) -> str:
        """
        Create a parent constraint.

        Args:
            driver: Driver transform
            driven: Driven transform
            maintain_offset: Maintain offset
            skip_translate: Axes to skip for translate
            skip_rotate: Axes to skip for rotate

        Returns:
            Constraint name
        """
        kwargs = {"maintainOffset": maintain_offset}

        if skip_translate:
            kwargs["skipTranslate"] = skip_translate
        if skip_rotate:
            kwargs["skipRotate"] = skip_rotate

        constraint = cmds.parentConstraint(driver, driven, **kwargs)[0]
        return constraint

    @staticmethod
    def point_constraint(drivers: List[str], driven: str, maintain_offset: bool = True) -> str:
        """
        Create a point constraint.

        Args:
            drivers: Driver transforms
            driven: Driven transform
            maintain_offset: Maintain offset

        Returns:
            Constraint name
        """
        constraint = cmds.pointConstraint(drivers, driven, maintainOffset=maintain_offset)[0]
        return constraint

    @staticmethod
    def orient_constraint(
        drivers: List[str],
        driven: str,
        maintain_offset: bool = True,
        skip: Optional[List[str]] = None,
    ) -> str:
        """
        Create an orient constraint.

        Args:
            drivers: Driver transforms
            driven: Driven transform
            maintain_offset: Maintain offset
            skip: Axes to skip

        Returns:
            Constraint name
        """
        kwargs = {"maintainOffset": maintain_offset}
        if skip:
            kwargs["skip"] = skip

        constraint = cmds.orientConstraint(drivers, driven, **kwargs)[0]
        return constraint

    @staticmethod
    def scale_constraint(drivers: List[str], driven: str, maintain_offset: bool = True) -> str:
        """
        Create a scale constraint.

        Args:
            drivers: Driver transforms
            driven: Driven transform
            maintain_offset: Maintain offset

        Returns:
            Constraint name
        """
        constraint = cmds.scaleConstraint(drivers, driven, maintainOffset=maintain_offset)[0]
        return constraint

    @staticmethod
    def aim_constraint(
        driver: str,
        driven: str,
        aim_vector: Tuple[float, float, float] = (1, 0, 0),
        up_vector: Tuple[float, float, float] = (0, 1, 0),
        world_up_type: str = "objectrotation",
        world_up_object: Optional[str] = None,
        maintain_offset: bool = False,
    ) -> str:
        """
        Create an aim constraint.

        Args:
            driver: Driver transform (target to aim at)
            driven: Driven transform
            aim_vector: Local aim axis
            up_vector: Local up axis
            world_up_type: World up type
            world_up_object: World up object
            maintain_offset: Maintain offset

        Returns:
            Constraint name
        """
        kwargs = {
            "maintainOffset": maintain_offset,
            "aimVector": aim_vector,
            "upVector": up_vector,
            "worldUpType": world_up_type,
        }

        if world_up_object:
            kwargs["worldUpObject"] = world_up_object
            kwargs["worldUpVector"] = (0, 1, 0)

        constraint = cmds.aimConstraint(driver, driven, **kwargs)[0]
        return constraint

    @staticmethod
    def geometry_constraint(geometry: str, driven: str) -> str:
        """
        Create a geometry constraint.

        Args:
            geometry: Target geometry
            driven: Driven transform

        Returns:
            Constraint name
        """
        constraint = cmds.geometryConstraint(geometry, driven)[0]
        return constraint

    @staticmethod
    def normal_constraint(
        geometry: str,
        driven: str,
        aim_vector: Tuple[float, float, float] = (0, 0, 1),
        up_vector: Tuple[float, float, float] = (0, 1, 0),
    ) -> str:
        """
        Create a normal constraint.

        Args:
            geometry: Target geometry
            driven: Driven transform
            aim_vector: Local aim axis
            up_vector: Local up axis

        Returns:
            Constraint name
        """
        constraint = cmds.normalConstraint(
            geometry,
            driven,
            weight=1,
            aimVector=aim_vector,
            upVector=up_vector,
            worldUpType="vector",
            worldUpVector=(0, 1, 0),
        )[0]
        return constraint

    @staticmethod
    def pole_vector_constraint(driver: str, ik_handle: str) -> str:
        """
        Create a pole vector constraint.

        Args:
            driver: Pole vector target
            ik_handle: IK handle

        Returns:
            Constraint name
        """
        constraint = cmds.poleVectorConstraint(driver, ik_handle)[0]
        return constraint

    @staticmethod
    def matrix_constraint(
        driver: str, driven: str, translate: bool = True, rotate: bool = True, scale: bool = True
    ) -> str:
        """
        Create a matrix-based constraint using decomposeMatrix.

        Args:
            driver: Driver transform
            driven: Driven transform
            translate: Constrain translation
            rotate: Constrain rotation
            scale: Constrain scale

        Returns:
            DecomposeMatrix node name
        """
        # Create multMatrix for parent offset
        mult = cmds.createNode("multMatrix", name=f"{driven}_MM")
        decomp = cmds.createNode("decomposeMatrix", name=f"{driven}_DM")

        cmds.connectAttr(f"{driver}.worldMatrix[0]", f"{mult}.matrixIn[0]")
        cmds.connectAttr(f"{driven}.parentInverseMatrix[0]", f"{mult}.matrixIn[1]")
        cmds.connectAttr(f"{mult}.matrixSum", f"{decomp}.inputMatrix")

        if translate:
            cmds.connectAttr(f"{decomp}.outputTranslate", f"{driven}.translate")
        if rotate:
            cmds.connectAttr(f"{decomp}.outputRotate", f"{driven}.rotate")
        if scale:
            cmds.connectAttr(f"{decomp}.outputScale", f"{driven}.scale")

        return decomp

    @staticmethod
    def blend_constraint(
        drivers: List[str], driven: str, constraint_type: str = "parent"
    ) -> Tuple[str, str]:
        """
        Create a blended constraint with weight attribute.

        Args:
            drivers: List of driver transforms (2)
            driven: Driven transform
            constraint_type: Type of constraint

        Returns:
            Tuple of (constraint_name, weight_attr)
        """
        if constraint_type == "parent":
            constraint = cmds.parentConstraint(drivers, driven, maintainOffset=True)[0]
        elif constraint_type == "point":
            constraint = cmds.pointConstraint(drivers, driven, maintainOffset=True)[0]
        elif constraint_type == "orient":
            constraint = cmds.orientConstraint(drivers, driven, maintainOffset=True)[0]
        else:
            raise ValueError(f"Unknown constraint type: {constraint_type}")

        # Get weight attributes
        weights = cmds.parentConstraint(constraint, query=True, weightAliasList=True)
        return constraint, weights[0] if weights else None

    @staticmethod
    def delete_constraint(constraint: str):
        """
        Safely delete a constraint.

        Args:
            constraint: Constraint node name
        """
        if cmds.objExists(constraint):
            cmds.delete(constraint)

    @staticmethod
    def get_constraint_targets(constraint: str) -> List[str]:
        """
        Get target list from constraint.

        Args:
            constraint: Constraint node

        Returns:
            List of target names
        """
        constraint_type = cmds.nodeType(constraint)

        if constraint_type == "parentConstraint":
            return cmds.parentConstraint(constraint, query=True, targetList=True) or []
        elif constraint_type == "pointConstraint":
            return cmds.pointConstraint(constraint, query=True, targetList=True) or []
        elif constraint_type == "orientConstraint":
            return cmds.orientConstraint(constraint, query=True, targetList=True) or []
        elif constraint_type == "scaleConstraint":
            return cmds.scaleConstraint(constraint, query=True, targetList=True) or []

        return []
