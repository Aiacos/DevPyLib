"""Proxy geometry generation from skinned meshes for fast viewport display.

Provides the ProxyGeo class which creates per-joint proxy geometry from
a skinned mesh by duplicating and removing faces based on skin weights,
useful for creating fast/medium/slow display hierarchy levels.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import skin


def invert_selection(shape, faces):
    pm.select(shape + '.f[*]')
    pm.select(faces, deselect=True)
    # mel.eval('InvertSelection;')
    return pm.ls(sl=True)


class ProxyGeo():
    def __init__(self, geo, do_parent_cnst=True, threshold=0.45):
        self.proxyGeoList = []
        pivotLocator = pm.spaceLocator(n='pivotGeo_LOC')
        # Create proxy geo Group
        self.shapeGrp = pm.group(n='fastGeo_GRP', em=True)

        # Get Shape and skin from Object
        skinCluster = skin.findRelatedSkinCluster(geo)
        if not skinCluster:
            print('Missing SkinCluster')
        else:
            self.skin = skinCluster

            # Get joint influence of the skin
            influnces = self.skin.getInfluence(q=True)  # influences is joint
            for joint in influnces:
                # duplicate mesh for a control
                transform, dupliShape = self.duplicate_source_mesh(obj=geo, joint=joint)
                common.centerPivot(transform, pivotLocator)

                # copy skinCluster
                skin.copyBind(pm.ls(geo)[0], transform)

                # delete faces in the new shape based on selected joint
                self.delete_vertex(joint=joint, new_shape=dupliShape, threshold=threshold)

                # delete non deformer history
                common.deleteHistory(dupliShape)

                # parent under proxy group
                pm.parent(transform, self.shapeGrp)
                self.proxyGeoList.append(transform)

                # parentConstraint with joint
                if do_parent_cnst:
                    pm.parentConstraint(joint, transform, mo=True)

            # delete pivot locator
            pm.delete(pivotLocator)

    def duplicate_source_mesh(self, obj, joint):
        """

        :param obj:
        :param ctrl:
        :return: Mesh Shape for the Control
        """
        dupliObj = pm.duplicate(obj)
        pm.rename(dupliObj, name.remove_suffix(joint) + '_PRX')

        return dupliObj[0], dupliObj[0].getShape()

    def delete_vertex(self, joint, new_shape, threshold=0.45):
        verts = []
        skincluster = skin.findRelatedSkinCluster(new_shape)
        for x in range(pm.polyEvaluate(new_shape, v=1)):
            v = pm.skinPercent(skincluster, '%s.vtx[%d]' % (new_shape, x), transform=joint, q=1)
            if v > threshold:
                verts.append('%s.vtx[%d]' % (new_shape, x))
        pm.select(verts)

        faces = pm.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        # pm.select(faces)
        toDelete = invert_selection(new_shape, faces)
        pm.polyDelFacet(toDelete, ch=False)

    def get_proxy_geo_list(self):
        return self.proxyGeoList

    def get_fast_geo_group(self):
        return self.shapeGrp


if __name__ == "__main__":
    prxGeo = ProxyGeo()
