"""Matrix-based collision system for character rigging.

Provides the Collider class for creating collision detection and response
between controls and meshes using matrix operations for deformation.
"""

import pymel.core as pm


class Collider(object):
    """Matrix-based collision system for character rigging.

    Creates a collision rig using matrix operations to deform a target mesh based on
    a collision mesh and control point. Automatically constructs a complex node network
    with matrix decomposition, vector products, and pair blending for smooth collision
    response and weight-based fade effects.

    Attributes:
        ctrl: Control transform for the collision system
        collision_point: Point that detects collision surface position
        collision_mesh: Mesh that acts as the collision surface
        target_mesh: Mesh that is deformed by the collision

    Example:
        >>> collider = Collider('arm', ctrl='arm_CTRL', target_mesh='arm_mesh')
        >>> # Automatically sets up matrix-based collision detection and deformation
    """
    def __init__(
        self,
        module_name,
        ctrl=None,
        collision_point=None,
        collision_mesh=None,
        target_mesh=None,
    ):
        """Initialize the collision system.

        Args:
            module_name (str): The name of the module to be used for naming.
            ctrl (str): The name of the control to be used for the collision.
            collision_point (str): The name of the point to be used for the collision.
            collision_mesh (str): The name of the mesh to be used for the collision.
            target_mesh (str): The name of the mesh to be deformed by the collision.
        """
        if not ctrl:
            self.ctrl = pm.spaceLocator(name=module_name + "_ctrl")
        else:
            self.ctrl = pm.ls(ctrl)[-1]

        if not collision_point:
            self.collision_point = pm.spaceLocator(name=module_name + "_collisionPoint")
        else:
            self.collision_point = pm.ls(collision_point)[-1]

        pm.parent(self.collision_point, self.ctrl)

        if not collision_mesh:
            self.collision_mesh = pm.polyPlane(
                name=module_name + "_collisionMesh", w=50, h=50, sx=20, sy=20
            )
        else:
            self.collision_mesh = pm.ls(collision_mesh)[-1]

        if not target_mesh:
            self.target_mesh = pm.polyCube(name=module_name + "_targetMesh")
        else:
            self.target_mesh = pm.ls(target_mesh)[-1]

        # Create Nodes
        closest_point_on_mesh = pm.createNode(
            "closestPointOnMesh", name=module_name + "_closestPointOnMesh"
        )

        decompose_matrix_collision_point = pm.createNode(
            "decomposeMatrix", name=module_name + "_decomposeMatrix_collisionPoint"
        )

        vector_product_z = pm.createNode(
            "vectorProduct", name=module_name + "_vectorProductZ"
        )
        pm.setAttr(vector_product_z.operation, 2)
        pm.setAttr(vector_product_z.input1X, 1)
        pm.setAttr(vector_product_z.input1Y, 0)

        vector_product_x = pm.createNode(
            "vectorProduct", name=module_name + "_vectorProductX"
        )
        pm.setAttr(vector_product_x.operation, 2)

        four_by_four_matrix = pm.createNode(
            "fourByFourMatrix", name=module_name + "_fourByFourMatrix"
        )

        decompose_matrix_four_by_four = pm.createNode(
            "decomposeMatrix", name=module_name + "_decomposeMatrixFourByFour"
        )

        decompose_matrix_collision_point_inverse = pm.createNode(
            "decomposeMatrix",
            name=module_name + "_decomposeMatrix_collisionPoint_Inverse",
        )

        plus_minus_average_matrix_distance_from_curve = pm.createNode(
            "plusMinusAverage",
            name=module_name + "_plusMinusAverageMatrix_distanceFromCurve",
        )
        pm.setAttr(plus_minus_average_matrix_distance_from_curve.operation, 1)

        condition_greater_than_zero = pm.createNode(
            "condition", name=module_name + "_condition_greaterThanZero"
        )
        pm.setAttr(condition_greater_than_zero.operation, 2)
        pm.setAttr(condition_greater_than_zero.secondTerm, 0)
        pm.setAttr(condition_greater_than_zero.colorIfTrueR, 1)
        pm.setAttr(condition_greater_than_zero.colorIfFalseR, 0)

        remap_value_fade_snap = pm.createNode(
            "remapValue", name=module_name + "_remapValue_FadeSnap"
        )
        pm.setAttr(remap_value_fade_snap.inputMin, -0.1)
        pm.setAttr(remap_value_fade_snap.inputMax, 0)
        pm.setAttr(remap_value_fade_snap.outputMin, 0)
        pm.setAttr(remap_value_fade_snap.outputMax, 1)

        condition_fade_snap = pm.createNode(
            "condition", name=module_name + "_condition_FadeSnap"
        )
        pm.setAttr(condition_fade_snap.operation, 2)
        pm.setAttr(condition_fade_snap.secondTerm, -0.1)

        decompose_matrix_ctrl = pm.createNode(
            "decomposeMatrix", name=module_name + "_decomposeMatrix_ctrl"
        )

        plus_minus_average_matrix_offset_from_ctrl = pm.createNode(
            "plusMinusAverage",
            name=module_name + "_plusMinusAverageMatrix_OffsetFromCtrl",
        )
        pm.setAttr(plus_minus_average_matrix_offset_from_ctrl.operation, 1)

        pair_blend = pm.createNode("pairBlend", name=module_name + "_pairBlend")

        # Create Connection
        pm.connectAttr(
            self.collision_point.worldMatrix[0],
            decompose_matrix_collision_point.inputMatrix,
            f=True,
        )

        pm.connectAttr(
            self.collision_mesh[0].getShape().outMesh, closest_point_on_mesh.inMesh, f=True
        )
        pm.connectAttr(
            self.collision_mesh[0].worldMatrix[0],
            closest_point_on_mesh.inputMatrix,
            f=True,
        )
        pm.connectAttr(
            decompose_matrix_collision_point.outputTranslate,
            closest_point_on_mesh.inPosition,
            f=True,
        )

        pm.connectAttr(closest_point_on_mesh.result.normal, vector_product_z.input2, f=True)

        pm.connectAttr(closest_point_on_mesh.normal, vector_product_x.input1, f=True)
        pm.connectAttr(vector_product_z.output, vector_product_x.input2, f=True)

        pm.connectAttr(vector_product_x.outputX, four_by_four_matrix.in00, f=True)
        pm.connectAttr(vector_product_x.outputY, four_by_four_matrix.in01, f=True)
        pm.connectAttr(vector_product_x.outputZ, four_by_four_matrix.in02, f=True)
        pm.connectAttr(closest_point_on_mesh.normalX, four_by_four_matrix.in10, f=True)
        pm.connectAttr(closest_point_on_mesh.normalY, four_by_four_matrix.in11, f=True)
        pm.connectAttr(closest_point_on_mesh.normalZ, four_by_four_matrix.in12, f=True)
        pm.connectAttr(vector_product_z.outputX, four_by_four_matrix.in20, f=True)
        pm.connectAttr(vector_product_z.outputY, four_by_four_matrix.in21, f=True)
        pm.connectAttr(vector_product_z.outputZ, four_by_four_matrix.in22, f=True)
        pm.connectAttr(closest_point_on_mesh.positionX, four_by_four_matrix.in30, f=True)
        pm.connectAttr(closest_point_on_mesh.positionY, four_by_four_matrix.in31, f=True)
        pm.connectAttr(closest_point_on_mesh.positionZ, four_by_four_matrix.in32, f=True)

        pm.connectAttr(
            four_by_four_matrix.output, decompose_matrix_four_by_four.inputMatrix, f=True
        )

        pm.connectAttr(
            self.collision_point.worldInverseMatrix[0],
            decompose_matrix_collision_point_inverse.inputMatrix,
            f=True,
        )

        pm.connectAttr(
            decompose_matrix_four_by_four.outputTranslate,
            plus_minus_average_matrix_distance_from_curve.input3D[0],
            f=True,
        )
        pm.connectAttr(
            decompose_matrix_collision_point_inverse.outputTranslate,
            plus_minus_average_matrix_distance_from_curve.input3D[1],
            f=True,
        )

        pm.connectAttr(
            plus_minus_average_matrix_distance_from_curve.output3Dy,
            condition_greater_than_zero.firstTerm,
            f=True,
        )

        pm.connectAttr(
            plus_minus_average_matrix_distance_from_curve.output3Dy,
            remap_value_fade_snap.inputValue,
            f=True,
        )

        pm.connectAttr(
            condition_greater_than_zero.outColorR,
            condition_fade_snap.colorIfFalseR,
            f=True,
        )
        pm.connectAttr(
            remap_value_fade_snap.outColorR, condition_fade_snap.colorIfTrueR, f=True
        )
        pm.connectAttr(
            plus_minus_average_matrix_distance_from_curve.output3Dy,
            condition_fade_snap.firstTerm,
            f=True,
        )

        pm.connectAttr(
            self.ctrl.worldMatrix[0], decompose_matrix_ctrl.inputMatrix, f=True
        )

        pm.connectAttr(
            plus_minus_average_matrix_distance_from_curve.output3D,
            plus_minus_average_matrix_offset_from_ctrl.input3D[0],
            f=True,
        )
        pm.connectAttr(
            decompose_matrix_ctrl.outputTranslate,
            plus_minus_average_matrix_offset_from_ctrl.input3D[1],
            f=True,
        )

        pm.connectAttr(condition_fade_snap.outColorR, pair_blend.weight, f=True)
        pm.connectAttr(decompose_matrix_ctrl.outputRotate, pair_blend.inRotate1, f=True)
        pm.connectAttr(
            decompose_matrix_four_by_four.outputRotate, pair_blend.inRotate2, f=True
        )
        pm.connectAttr(
            decompose_matrix_ctrl.outputTranslate, pair_blend.inTranslate1, f=True
        )
        pm.connectAttr(
            plus_minus_average_matrix_offset_from_ctrl.output3D,
            pair_blend.inTranslate2,
            f=True,
        )

        pm.connectAttr(pair_blend.outTranslate, self.target_mesh[0].translate, f=True)
        pm.connectAttr(pair_blend.outRotate, self.target_mesh[0].rotate, f=True)
