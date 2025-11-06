"""Pixar-style geometry controls creation from skinned meshes.

Provides the PxrStyleCtrl class which creates geometry-based rig controls
(like Pixar rigs) by duplicating skinned meshes and distributing geometry
to controls based on joint influence weights.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import common, skin, util


def invert_selection(shape, faces):
    """Invert face selection on a mesh shape.

    Selects all faces on the shape except those specified.

    Args:
        shape: Mesh shape node to operate on
        faces: Face component list to exclude from selection

    Returns:
        list: Selected face components (inverse of input faces)
    """
    pm.select(shape + '.f[*]')
    pm.select(faces, deselect=True)
    # mel.eval('InvertSelection;')
    return pm.ls(sl=True)


class PxrStyleCtrl():
    """
    Create Geometry control like PIXAR
    """

    def __init__(self, obj, delete_old_shape_grp=True):
        """Create Pixar-style geometry-based rig controls from skinned mesh.

        Replaces control shapes with mesh geometry derived from the skinned mesh,
        distributing faces to controls based on joint influence weights. Similar
        to the geo-control approach used in Pixar character rigs.

        Args:
            obj: Source skinned mesh to generate control geometry from
            delete_old_shape_grp: Remove backup group after completion. Defaults to True.

        Attributes:
            shapeGrp: Group containing backed-up original control shapes
            skin: SkinCluster node from source mesh

        Example:
            >>> pxr = PxrStyleCtrl('character_body_GEO')
        """
        # Create backup Group
        self.shape_grp = pm.group(n='oldShape_GRP', em=True)
        self.shape_grp.visibility.set(0)

        # Get Shape and skin from Object
        skin_cluster = skin.findRelatedSkinCluster(obj)
        if skin_cluster:
            self.skin = skin_cluster
        else:
            print('Missing SkinCluster')

        # Get joint influence of the skin
        influnces = self.skin.getInfluence(q=True)  # influences is joint
        for joint in influnces:
            constraint = pm.listRelatives(joint, children=True, type='constraint')
            if constraint:
                ctrl, jnt = util.get_driver_driven_from_constraint(constraint[0])
                # duplicate mesh for a control
                empty_transform, ctrl_shape = self.duplicate_source_mesh(obj=obj, ctrl=ctrl)

                # move new shape under control and delete empty transform
                self.move_shape_and_back_up(source=ctrl_shape, destination=ctrl)
                pm.delete(empty_transform)

                # connect control shape to skinCluster
                self.connect_skin_cluster(ctrl_shape, ctrl)

                # delete faces in the new shape based on selected joint
                self.delete_vertex(joint=joint, new_shape=ctrl_shape)

                # delete non deformer history
                common.delete_non_deformer_history(ctrl_shape)

                # prevent chidlren selection hilight
                shape = ctrl[0].getShape()
                ctrl[0].selectionChildHighlighting.set(0)
                shape.selectionChildHighlighting.set(0)

        if delete_old_shape_grp:
            pm.delete(self.shape_grp)

        print('DONE!')

    def duplicate_source_mesh(self, obj, ctrl):
        """

        :param obj:
        :param ctrl:
        :return: Mesh Shape for the Control
        """
        dupli_obj = pm.duplicate(obj)
        pm.rename(dupli_obj, ctrl[0].name())

        return dupli_obj[0], dupli_obj[0].getShape()

    def move_shape_and_back_up(self, source, destination):
        """Move shape node to destination control and backup original.

        Args:
            source: Source shape node to move
            destination: Destination control transform to receive shape
        """
        # Remove and backUp oldShape
        old_shape = destination[0].getShape()
        pm.parent(old_shape, self.shape_grp, r=True, s=True)
        # pm.delete(old_shape)

        # Replace Shape
        util.move_shape(source=source, destination=destination)

    def connect_skin_cluster(self, new_shape, ctrl):
        """Connect skinCluster output to control shape with proper transform.

        Creates transformGeometry node to properly transform the skinned mesh
        into the control's local space.

        Args:
            new_shape: Shape node to receive skinCluster output
            ctrl: Control transform providing world inverse matrix
        """
        transform_geo = pm.createNode("transformGeometry")
        pm.connectAttr(self.skin.outputGeometry[0], transform_geo.inputGeometry, f=True)
        pm.connectAttr(ctrl[0].worldInverseMatrix[0], transform_geo.transform, f=True)
        pm.connectAttr(transform_geo.outputGeometry, new_shape.inMesh, f=True)

    def delete_vertex(self, joint, new_shape, threshold=0.45):
        """Remove vertices with low skin weight from control geometry.

        Evaluates skin weights and removes faces where the joint's influence
        is below the threshold, leaving only geometry influenced by this joint.

        Args:
            joint: Joint to evaluate skin weights for
            new_shape: Shape node to remove vertices from
            threshold: Minimum skin weight (0-1) to keep vertices. Defaults to 0.45.
        """
        verts = []
        for x in range(pm.polyEvaluate(new_shape, v=1)):
            v = pm.skinPercent(self.skin, '%s.vtx[%d]' % (new_shape, x), transform=joint, q=1)
            if v > threshold:
                verts.append('%s.vtx[%d]' % (new_shape, x))
        pm.select(verts)

        faces = pm.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        # pm.select(faces)
        to_delete = invert_selection(new_shape, faces)
        pm.polyDelFacet(to_delete, ch=False)

    def delete_vertex_old(self, joint, new_shape, threshold=0.45):
        """Legacy method for removing vertices (deprecated).

        Alternative vertex deletion approach using getPointsAffectedByInfluence.
        Kept for backward compatibility but delete_vertex() is preferred.

        Args:
            joint: Joint to evaluate skin weights for
            new_shape: Shape node to remove vertices from
            threshold: Minimum skin weight (0-1) to keep vertices. Defaults to 0.45.
        """
        delete_vert_list = []

        vert_list, values = self.skin.getPointsAffectedByInfluence(joint)
        vert_list = vert_list.getSelectionStrings()

        index = 0
        for vtxs in vert_list:
            vtxs = pm.PyNode(vtxs)
            for vert in vtxs:
                if values[index] > threshold:
                    shape_vertex = new_shape.vtx[index]
                    delete_vert_list.append(shape_vertex)
                index += 1

        faces = pm.polyListComponentConversion(delete_vert_list, fromVertex=True, toFace=True)
        pm.select(faces)
        util.invert_selection()
        pm.polyDelFacet(ch=False)


if __name__ == "__main__":
    pxr_ctrl = PxrStyleCtrl()
