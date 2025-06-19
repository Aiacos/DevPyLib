import pymel.core as pm


class Collider(object):
    def __init__(
        self,
        module_name,
        ctrl=None,
        collision_point=None,
        collision_mesh=None,
        target_mesh=None,
    ):
        """
        Initialize the collision system.

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
        closestPointOnMesh = pm.createNode(
            "closestPointOnMesh", name=module_name + "_closestPointOnMesh"
        )

        decomposeMatrix_collisionPoint = pm.createNode(
            "decomposeMatrix", name=module_name + "_decomposeMatrix_collisionPoint"
        )

        vectorProductZ = pm.createNode(
            "vectorProduct", name=module_name + "_vectorProductZ"
        )
        pm.setAttr(vectorProductZ.operation, 2)
        pm.setAttr(vectorProductZ.input1X, 1)
        pm.setAttr(vectorProductZ.input1Y, 0)

        vectorProductX = pm.createNode(
            "vectorProduct", name=module_name + "_vectorProductX"
        )
        pm.setAttr(vectorProductX.operation, 2)

        fourByFourMatrix = pm.createNode(
            "fourByFourMatrix", name=module_name + "_fourByFourMatrix"
        )

        decomposeMatrix_fourByFour = pm.createNode(
            "decomposeMatrix", name=module_name + "_decomposeMatrixFourByFour"
        )

        decomposeMatrix_collisionPoint_Inverse = pm.createNode(
            "decomposeMatrix",
            name=module_name + "_decomposeMatrix_collisionPoint_Inverse",
        )

        plusMinusAverageMatrix_distanceFromCurve = pm.createNode(
            "plusMinusAverage",
            name=module_name + "_plusMinusAverageMatrix_distanceFromCurve",
        )
        pm.setAttr(plusMinusAverageMatrix_distanceFromCurve.operation, 1)

        condition_greaterThanZero = pm.createNode(
            "condition", name=module_name + "_condition_greaterThanZero"
        )
        pm.setAttr(condition_greaterThanZero.operation, 2)
        pm.setAttr(condition_greaterThanZero.secondTerm, 0)
        pm.setAttr(condition_greaterThanZero.colorIfTrueR, 1)
        pm.setAttr(condition_greaterThanZero.colorIfFalseR, 0)

        remapValue_FadeSnap = pm.createNode(
            "remapValue", name=module_name + "_remapValue_FadeSnap"
        )
        pm.setAttr(remapValue_FadeSnap.inputMin, -0.1)
        pm.setAttr(remapValue_FadeSnap.inputMax, 0)
        pm.setAttr(remapValue_FadeSnap.outputMin, 0)
        pm.setAttr(remapValue_FadeSnap.outputMax, 1)

        condition_FadeSnap = pm.createNode(
            "condition", name=module_name + "_condition_FadeSnap"
        )
        pm.setAttr(condition_FadeSnap.operation, 2)
        pm.setAttr(condition_FadeSnap.secondTerm, -0.1)

        decomposeMatrix_ctrl = pm.createNode(
            "decomposeMatrix", name=module_name + "_decomposeMatrix_ctrl"
        )

        plusMinusAverageMatrix_OffsetFromCtrl = pm.createNode(
            "plusMinusAverage",
            name=module_name + "_plusMinusAverageMatrix_OffsetFromCtrl",
        )
        pm.setAttr(plusMinusAverageMatrix_OffsetFromCtrl.operation, 1)

        pairBlend = pm.createNode("pairBlend", name=module_name + "_pairBlend")

        # Create Connection
        pm.connectAttr(
            self.collision_point.worldMatrix[0],
            decomposeMatrix_collisionPoint.inputMatrix,
            f=True,
        )

        pm.connectAttr(
            self.collision_mesh[0].getShape().outMesh, closestPointOnMesh.inMesh, f=True
        )
        pm.connectAttr(
            self.collision_mesh[0].worldMatrix[0],
            closestPointOnMesh.inputMatrix,
            f=True,
        )
        pm.connectAttr(
            decomposeMatrix_collisionPoint.outputTranslate,
            closestPointOnMesh.inPosition,
            f=True,
        )

        pm.connectAttr(closestPointOnMesh.result.normal, vectorProductZ.input2, f=True)

        pm.connectAttr(closestPointOnMesh.normal, vectorProductX.input1, f=True)
        pm.connectAttr(vectorProductZ.output, vectorProductX.input2, f=True)

        pm.connectAttr(vectorProductX.outputX, fourByFourMatrix.in00, f=True)
        pm.connectAttr(vectorProductX.outputY, fourByFourMatrix.in01, f=True)
        pm.connectAttr(vectorProductX.outputZ, fourByFourMatrix.in02, f=True)
        pm.connectAttr(closestPointOnMesh.normalX, fourByFourMatrix.in10, f=True)
        pm.connectAttr(closestPointOnMesh.normalY, fourByFourMatrix.in11, f=True)
        pm.connectAttr(closestPointOnMesh.normalZ, fourByFourMatrix.in12, f=True)
        pm.connectAttr(vectorProductZ.outputX, fourByFourMatrix.in20, f=True)
        pm.connectAttr(vectorProductZ.outputY, fourByFourMatrix.in21, f=True)
        pm.connectAttr(vectorProductZ.outputZ, fourByFourMatrix.in22, f=True)
        pm.connectAttr(closestPointOnMesh.positionX, fourByFourMatrix.in30, f=True)
        pm.connectAttr(closestPointOnMesh.positionY, fourByFourMatrix.in31, f=True)
        pm.connectAttr(closestPointOnMesh.positionZ, fourByFourMatrix.in32, f=True)

        pm.connectAttr(
            fourByFourMatrix.output, decomposeMatrix_fourByFour.inputMatrix, f=True
        )

        pm.connectAttr(
            self.collision_point.worldInverseMatrix[0],
            decomposeMatrix_collisionPoint_Inverse.inputMatrix,
            f=True,
        )

        pm.connectAttr(
            decomposeMatrix_fourByFour.outputTranslate,
            plusMinusAverageMatrix_distanceFromCurve.input3D[0],
            f=True,
        )
        pm.connectAttr(
            decomposeMatrix_collisionPoint_Inverse.outputTranslate,
            plusMinusAverageMatrix_distanceFromCurve.input3D[1],
            f=True,
        )

        pm.connectAttr(
            plusMinusAverageMatrix_distanceFromCurve.output3Dy,
            condition_greaterThanZero.firstTerm,
            f=True,
        )

        pm.connectAttr(
            plusMinusAverageMatrix_distanceFromCurve.output3Dy,
            remapValue_FadeSnap.inputValue,
            f=True,
        )

        pm.connectAttr(
            condition_greaterThanZero.outColorR,
            condition_FadeSnap.colorIfFalseR,
            f=True,
        )
        pm.connectAttr(
            remapValue_FadeSnap.outColorR, condition_FadeSnap.colorIfTrueR, f=True
        )
        pm.connectAttr(
            plusMinusAverageMatrix_distanceFromCurve.output3Dy,
            condition_FadeSnap.firstTerm,
            f=True,
        )

        pm.connectAttr(
            self.ctrl.worldMatrix[0], decomposeMatrix_ctrl.inputMatrix, f=True
        )

        pm.connectAttr(
            plusMinusAverageMatrix_distanceFromCurve.output3D,
            plusMinusAverageMatrix_OffsetFromCtrl.input3D[0],
            f=True,
        )
        pm.connectAttr(
            decomposeMatrix_ctrl.outputTranslate,
            plusMinusAverageMatrix_OffsetFromCtrl.input3D[1],
            f=True,
        )

        pm.connectAttr(condition_FadeSnap.outColorR, pairBlend.weight, f=True)
        pm.connectAttr(decomposeMatrix_ctrl.outputRotate, pairBlend.inRotate1, f=True)
        pm.connectAttr(
            decomposeMatrix_fourByFour.outputRotate, pairBlend.inRotate2, f=True
        )
        pm.connectAttr(
            decomposeMatrix_ctrl.outputTranslate, pairBlend.inTranslate1, f=True
        )
        pm.connectAttr(
            plusMinusAverageMatrix_OffsetFromCtrl.output3D,
            pairBlend.inTranslate2,
            f=True,
        )

        pm.connectAttr(pairBlend.outTranslate, self.target_mesh[0].translate, f=True)
        pm.connectAttr(pairBlend.outRotate, self.target_mesh[0].rotate, f=True)
