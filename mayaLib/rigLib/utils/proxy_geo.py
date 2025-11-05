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
    """Invert face selection on a mesh shape.

    Selects all faces on the shape except those specified, useful for
    deleting faces outside a region of influence.

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


class ProxyGeo():
    """Per-joint proxy geometry generator for fast viewport display.

    Automatically creates optimized proxy geometry from a skinned mesh by duplicating
    and removing faces based on skin weight influence. Useful for creating fast/medium/
    slow display hierarchy levels that maintain proper deformation while reducing
    viewport geometry for performance.

    Attributes:
        proxyGeoList: List of created proxy geometry transform nodes
        shapeGrp: Parent group containing all proxy geometry ('fastGeo_GRP')

    Example:
        >>> proxy = ProxyGeo('character_body', do_parent_cnst=True, threshold=0.5)
        >>> proxy_meshes = proxy.get_proxy_geo_list()
        >>> fast_group = proxy.get_fast_geo_group()
    """
    def __init__(self, geo, do_parent_cnst=True, threshold=0.45):
        """Create per-joint proxy geometry from a skinned mesh.

        Duplicates the source mesh for each joint influence, removes faces with
        low skin weights, and creates a fast-display geometry hierarchy useful
        for viewport performance optimization.

        Args:
            geo: Source skinned mesh to generate proxy geometry from
            do_parent_cnst: Parent constrain proxy geo to joints. Defaults to True.
            threshold: Skin weight threshold (0-1) for face inclusion. Defaults to 0.45.

        Attributes:
            proxyGeoList: List of created proxy geometry transform nodes
            shapeGrp: Parent group containing all proxy geometry ('fastGeo_GRP')

        Example:
            >>> proxy = ProxyGeo('character_body_GEO', threshold=0.5)
            >>> proxy_meshes = proxy.get_proxy_geo_list()
        """
        self.proxyGeoList = []
        pivot_locator = pm.spaceLocator(n='pivotGeo_LOC')
        # Create proxy geo Group
        self.shapeGrp = pm.group(n='fastGeo_GRP', em=True)

        # Get Shape and skin from Object
        skin_cluster = skin.findRelatedSkinCluster(geo)
        if not skin_cluster:
            print('Missing SkinCluster')
        else:
            self.skin = skin_cluster

            # Get joint influence of the skin
            influnces = self.skin.getInfluence(q=True)  # influences is joint
            for joint in influnces:
                # duplicate mesh for a control
                transform, dupli_shape = self.duplicate_source_mesh(obj=geo, joint=joint)
                common.centerPivot(transform, pivot_locator)

                # copy skinCluster
                skin.copyBind(pm.ls(geo)[0], transform)

                # delete faces in the new shape based on selected joint
                self.delete_vertex(joint=joint, new_shape=dupli_shape, threshold=threshold)

                # delete non deformer history
                common.deleteHistory(dupli_shape)

                # parent under proxy group
                pm.parent(transform, self.shapeGrp)
                self.proxyGeoList.append(transform)

                # parentConstraint with joint
                if do_parent_cnst:
                    pm.parentConstraint(joint, transform, mo=True)

            # delete pivot locator
            pm.delete(pivot_locator)

    def duplicate_source_mesh(self, obj, joint):
        """

        :param obj:
        :param ctrl:
        :return: Mesh Shape for the Control
        """
        dupli_obj = pm.duplicate(obj)
        pm.rename(dupli_obj, name.remove_suffix(joint) + '_PRX')

        return dupli_obj[0], dupli_obj[0].getShape()

    def delete_vertex(self, joint, new_shape, threshold=0.45):
        """Remove vertices with low skin weight influence from proxy mesh.

        Evaluates skin weights for each vertex and removes faces where the
        specified joint's influence is below the threshold.

        Args:
            joint: Joint to evaluate skin weights for
            new_shape: Proxy mesh shape to remove vertices from
            threshold: Minimum skin weight (0-1) to keep vertices. Defaults to 0.45.
        """
        verts = []
        skincluster = skin.findRelatedSkinCluster(new_shape)
        for x in range(pm.polyEvaluate(new_shape, v=1)):
            v = pm.skinPercent(skincluster, '%s.vtx[%d]' % (new_shape, x), transform=joint, q=1)
            if v > threshold:
                verts.append('%s.vtx[%d]' % (new_shape, x))
        pm.select(verts)

        faces = pm.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        # pm.select(faces)
        to_delete = invert_selection(new_shape, faces)
        pm.polyDelFacet(to_delete, ch=False)

    def get_proxy_geo_list(self):
        """Get list of created proxy geometry transforms.

        Returns:
            list: All proxy geometry transform nodes created during initialization
        """
        return self.proxyGeoList

    def get_fast_geo_group(self):
        """Get parent group containing all proxy geometry.

        Returns:
            PyNode: The 'fastGeo_GRP' group node containing all proxy meshes
        """
        return self.shapeGrp


if __name__ == "__main__":
    prxGeo = ProxyGeo()
