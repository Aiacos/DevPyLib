__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import util, common
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import skin

def invertSelection(shape, faces):
    pm.select(shape+'.f[*]')
    pm.select(faces, deselect=True)
    #mel.eval('InvertSelection;')
    return pm.ls(sl=True)

class ProxyGeo():
    def __init__(self, geo, doParentCnst=True, threshold=0.45):
        self.proxyGeoList = []
        pivotLocator = pm.spaceLocator(n='pivotGeo_LOC')
        # Create proxy geo Group
        self.shapeGrp = pm.group(n='fastGeo_GRP', em=True)

        # Get Shape and skin from Object
        shape = pm.ls(geo)[0].getShape()
        skinCluster = pm.listConnections(shape + '.inMesh', destination=False)
        if len(skinCluster) > 0:
            self.skin = pm.PyNode(skinCluster[0])
        else:
            print 'Missing SkinCluster'

        # Get joint influence of the skin
        influnces = self.skin.getInfluence(q=True)  # influences is joint
        for joint in influnces:
            # duplicate mesh for a control
            transform, dupliShape = self.duplicateSourceMesh(obj=geo, joint=joint)
            common.centerPivot(transform, pivotLocator)

            # copy skinCluster
            skin.copyBind(pm.ls(geo)[0], transform)

            # delete faces in the new shape based on selected joint
            self.deleteVertex(joint=joint, newShape=dupliShape, threshold=threshold)

            # delete non deformer history
            common.deleteHistory(dupliShape)

            # parent under proxy group
            pm.parent(transform, self.shapeGrp)
            self.proxyGeoList.append(transform)

            # parentConstraint with joint
            if doParentCnst:
                pm.parentConstraint(joint, transform, mo=True)

        # delete pivot locator
        pm.delete(pivotLocator)


    def duplicateSourceMesh(self, obj, joint):
        """

        :param obj:
        :param ctrl:
        :return: Mesh Shape for the Control
        """
        dupliObj = pm.duplicate(obj)
        pm.rename(dupliObj, name.removeSuffix(joint)+'_PRX')

        return dupliObj[0], dupliObj[0].getShape()

    def deleteVertex(self, joint, newShape, threshold=0.45):
        verts = []
        skincluster = skin.findRelatedSkinCluster(newShape)
        for x in range(pm.polyEvaluate(newShape, v=1)):
            v = pm.skinPercent(skincluster, '%s.vtx[%d]' % (newShape, x), transform=joint, q=1)
            if v > threshold:
                verts.append('%s.vtx[%d]' % (newShape, x))
        pm.select(verts)

        faces = pm.polyListComponentConversion(verts, fromVertex=True, toFace=True)
        # pm.select(faces)
        toDelete = invertSelection(newShape, faces)
        pm.polyDelFacet(toDelete, ch=False)

    def getProxyGeoList(self):
        return self.proxyGeoList




if __name__ == "__main__":
    prxGeo = ProxyGeo()