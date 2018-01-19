__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import util
from mayaLib.rigLib.utils import common


class PxrStyleCtrl():
    """
    Create Geometry control like PIXAR
    """

    def __init__(self, obj):
        # Create backup Group
        self.shapeGrp = pm.group(n='oldShape_GRP', em=True)
        self.shapeGrp.visibility.set(0)

        # Get Shape and skin from Object
        shape = pm.ls(obj)[0].getShape()
        skinCluster = pm.listConnections(shape + '.inMesh', destination=False)
        if len(skinCluster) > 0:
            self.skin = pm.PyNode(skinCluster[0])
        else:
            print 'Missing SkinCluster'

        # Get joint influence of the skin
        influnces = self.skin.getInfluence(q=True)  # influences is joint
        for joint in influnces:
            constraint = pm.listRelatives(joint, children=True, type='constraint')
            if constraint:
                ctrl, jnt = util.getDriverDrivenFromConstraint(constraint[0])
                # duplicate mesh for a control
                emptyTransform, ctrlShape = self.duplicateSourceMesh(obj=obj, ctrl=ctrl)

                # move new shape under control and delete empty transform
                self.moveShapeAndbackUp(source=ctrlShape, destination=ctrl)
                pm.delete(emptyTransform)

                # connect control shape to skinCluster
                self.connectSkinCluster(ctrlShape, ctrl)

                # delete faces in the new shape based on selected joint
                self.deleteVertex(joint=joint, newShape=ctrlShape)

                # delete non deformer history
                common.deleteNonDeformerHistory(ctrlShape)

        print 'DONE!'

    def duplicateSourceMesh(self, obj, ctrl):
        """

        :param obj:
        :param ctrl:
        :return: Mesh Shape for the Control
        """
        dupliObj = pm.duplicate(obj)
        pm.rename(dupliObj, ctrl[0].name())

        return dupliObj[0], dupliObj[0].getShape()

    def moveShapeAndbackUp(self, source, destination):
        # Remove and backUp oldShape
        oldShape = destination[0].getShape()
        pm.parent(oldShape, self.shapeGrp, r=True, s=True)
        # pm.delete(oldShape)

        # Replace Shape
        util.moveShape(source=source, destination=destination)

    def connectSkinCluster(self, newShape, ctrl):
        transformGeo = pm.createNode("transformGeometry")
        pm.connectAttr(self.skin.outputGeometry[0], transformGeo.inputGeometry, f=True)
        pm.connectAttr(ctrl[0].worldInverseMatrix[0], transformGeo.transform, f=True)
        pm.connectAttr(transformGeo.outputGeometry, newShape.inMesh, f=True)

    def deleteVertex(self, joint, newShape, threshold=0.45):
        verts = []
        for x in range(pm.polyEvaluate(newShape, v=1)):
            v = pm.skinPercent(self.skin, '%s.vtx[%d]' % (newShape, x), transform=joint, q=1)
            if v > threshold:
                verts.append('%s.vtx[%d]' % (newShape, x))
        pm.select(verts)

        faces = pm.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        pm.select(faces)
        toDelete = util.invertSelection()
        pm.polyDelFacet(toDelete)

    def deleteVertex_OLD(self, joint, newShape, threshold=0.45):
        deleteVert_list = []

        vert_list, values = self.skin.getPointsAffectedByInfluence(joint)
        vert_list = vert_list.getSelectionStrings()

        index = 0
        for vtxs in vert_list:
            vtxs = pm.PyNode(vtxs)
            for vert in vtxs:
                if values[index] > threshold:
                    shapeVertex = newShape.vtx[index]
                    deleteVert_list.append(shapeVertex)
                index += 1

        faces = pm.polyListComponentConversion(deleteVert_list, fromVertex=True, toFace=True)
        pm.select(faces)
        util.invertSelection()
        pm.polyDelFacet(ch=False)


if __name__ == "__main__":
    pxrCtrl = PxrStyleCtrl()

