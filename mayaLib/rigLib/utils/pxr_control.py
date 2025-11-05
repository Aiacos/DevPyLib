"""Pixar-style geometry controls creation from skinned meshes.

Provides the PxrStyleCtrl class which creates geometry-based rig controls
(like Pixar rigs) by duplicating skinned meshes and distributing geometry
to controls based on joint influence weights.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import skin
from mayaLib.rigLib.utils import util


def invert_selection(shape, faces):
    pm.select(shape + '.f[*]')
    pm.select(faces, deselect=True)
    # mel.eval('InvertSelection;')
    return pm.ls(sl=True)


class PxrStyleCtrl():
    """
    Create Geometry control like PIXAR
    """

    def __init__(self, obj, delete_old_shape_grp=True):
        # Create backup Group
        self.shapeGrp = pm.group(n='oldShape_GRP', em=True)
        self.shapeGrp.visibility.set(0)

        # Get Shape and skin from Object
        skinCluster = skin.findRelatedSkinCluster(obj)
        if skinCluster:
            self.skin = skinCluster
        else:
            print('Missing SkinCluster')

        # Get joint influence of the skin
        influnces = self.skin.getInfluence(q=True)  # influences is joint
        for joint in influnces:
            constraint = pm.listRelatives(joint, children=True, type='constraint')
            if constraint:
                ctrl, jnt = util.get_driver_driven_from_constraint(constraint[0])
                # duplicate mesh for a control
                emptyTransform, ctrlShape = self.duplicate_source_mesh(obj=obj, ctrl=ctrl)

                # move new shape under control and delete empty transform
                self.move_shape_and_back_up(source=ctrlShape, destination=ctrl)
                pm.delete(emptyTransform)

                # connect control shape to skinCluster
                self.connect_skin_cluster(ctrlShape, ctrl)

                # delete faces in the new shape based on selected joint
                self.delete_vertex(joint=joint, new_shape=ctrlShape)

                # delete non deformer history
                common.deleteNonDeformerHistory(ctrlShape)

                # prevent chidlren selection hilight
                shape = ctrl[0].getShape()
                ctrl[0].selectionChildHighlighting.set(0)
                shape.selectionChildHighlighting.set(0)

        if delete_old_shape_grp:
            pm.delete(self.shapeGrp)

        print('DONE!')

    def duplicate_source_mesh(self, obj, ctrl):
        """

        :param obj:
        :param ctrl:
        :return: Mesh Shape for the Control
        """
        dupliObj = pm.duplicate(obj)
        pm.rename(dupliObj, ctrl[0].name())

        return dupliObj[0], dupliObj[0].getShape()

    def move_shape_and_back_up(self, source, destination):
        # Remove and backUp oldShape
        oldShape = destination[0].getShape()
        pm.parent(oldShape, self.shapeGrp, r=True, s=True)
        # pm.delete(oldShape)

        # Replace Shape
        util.move_shape(source=source, destination=destination)

    def connect_skin_cluster(self, new_shape, ctrl):
        transformGeo = pm.createNode("transformGeometry")
        pm.connectAttr(self.skin.outputGeometry[0], transformGeo.inputGeometry, f=True)
        pm.connectAttr(ctrl[0].worldInverseMatrix[0], transformGeo.transform, f=True)
        pm.connectAttr(transformGeo.outputGeometry, new_shape.inMesh, f=True)

    def delete_vertex(self, joint, new_shape, threshold=0.45):
        verts = []
        for x in range(pm.polyEvaluate(new_shape, v=1)):
            v = pm.skinPercent(self.skin, '%s.vtx[%d]' % (new_shape, x), transform=joint, q=1)
            if v > threshold:
                verts.append('%s.vtx[%d]' % (new_shape, x))
        pm.select(verts)

        faces = pm.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        # pm.select(faces)
        toDelete = invert_selection(new_shape, faces)
        pm.polyDelFacet(toDelete, ch=False)

    def delete_vertex_old(self, joint, new_shape, threshold=0.45):
        deleteVert_list = []

        vert_list, values = self.skin.getPointsAffectedByInfluence(joint)
        vert_list = vert_list.getSelectionStrings()

        index = 0
        for vtxs in vert_list:
            vtxs = pm.PyNode(vtxs)
            for vert in vtxs:
                if values[index] > threshold:
                    shapeVertex = new_shape.vtx[index]
                    deleteVert_list.append(shapeVertex)
                index += 1

        faces = pm.polyListComponentConversion(deleteVert_list, fromVertex=True, toFace=True)
        pm.select(faces)
        util.invert_selection()
        pm.polyDelFacet(ch=False)


if __name__ == "__main__":
    pxr_ctrl = PxrStyleCtrl()
