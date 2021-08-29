import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils.util import unlock_and_unhide_all, getAllObjectUnderGroup


def mergeDuplicatedVertex(geo, threshold=0.001, only2Vertex=False):
    pm.polyMergeVertex(geo, am=only2Vertex, ch=False, distance=threshold)


def fixFaceWithMoreThan4Sides(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def fixConcaveFaces(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def fixFaceWithHoles(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def fixNonPlanarFaces(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def removeLaminaFaces(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" }; '))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" }; '))


def removeNonmanifoldGeometry(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))


def removeEdgesWithZeroLenght(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))


def removeFacesWithZeroGeometryArea(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def removeFacesWithZeroMapArea(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'))


def removeInvalidComponents(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","1" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","1" };'))


class ModelFix():
    def __init__(self, geo, check=True):
        self.geo = pm.ls(geo)[0]

        unlock_and_unhide_all(self.geo)
        mergeDuplicatedVertex(self.geo)

        if check:
            self.checkFaceWithMoreThan4Sides = fixFaceWithMoreThan4Sides(self.geo, query=True)
            self.checkConcaveFaces = fixConcaveFaces(self.geo, query=True)
            self.checkFaceWithHoles = fixFaceWithHoles(self.geo, query=True)
            self.checkNonPlanarFaces = fixNonPlanarFaces(self.geo, query=True)
            self.checkLaminaFaces = removeLaminaFaces(self.geo, query=True)
            self.checkNonmanifoldGeometry = removeNonmanifoldGeometry(self.geo, query=True)
            self.checkEdgesWithZeroLenght = removeEdgesWithZeroLenght(self.geo, query=True)
            self.checkFacesWithZeroGeometryArea = removeFacesWithZeroGeometryArea(self.geo, query=True)
            self.checkFacesWithZeroMapArea = removeFacesWithZeroMapArea(self.geo, query=True)
            self.checkInvalidComponents = removeInvalidComponents(self.geo, query=True)

    def autoFix(self,
                faceWithMoreThan4Sides=False,
                concaveFaces=True,
                faceWithHoles=True,
                nonPlanarFaces=False,
                laminaFaces=True,
                nonmanifoldGeometry=True,
                edgesWithZeroLenght=True,
                facesWithZeroGeometryArea=True,
                facesWithZeroMapArea=False,
                invalidComponents=True):

        if faceWithMoreThan4Sides:
            self.fixFaceWithMoreThan4Sides()
        if concaveFaces:
            self.fixConcaveFaces()
        if faceWithHoles:
            self.fixFaceWithHoles()
        if nonPlanarFaces:
            self.fixNonPlanarFaces()

        if laminaFaces:
            self.removeLaminaFaces()
        if nonmanifoldGeometry:
            self.removeNonmanifoldGeometry()
        if edgesWithZeroLenght:
            self.removeEdgesWithZeroLenght()
        if facesWithZeroGeometryArea:
            self.removeFacesWithZeroGeometryArea()
        if facesWithZeroMapArea:
            self.removeFacesWithZeroMapArea()
        if invalidComponents:
            self.removeInvalidComponents()

        self.finalize()

    def fixFaceWithMoreThan4Sides(self):
        fixFaceWithMoreThan4Sides(self.geo, query=False)

    def fixConcaveFaces(self):
        fixConcaveFaces(self.geo, query=False)

    def fixFaceWithHoles(self):
        fixFaceWithHoles(self.geo, query=False)

    def fixNonPlanarFaces(self):
        fixNonPlanarFaces(self.geo, query=False)

    def removeLaminaFaces(self):
        removeLaminaFaces(self.geo, query=False)

    def removeNonmanifoldGeometry(self):
        removeNonmanifoldGeometry(self.geo, query=False)

    def removeEdgesWithZeroLenght(self):
        removeEdgesWithZeroLenght(self.geo, query=False)

    def removeFacesWithZeroGeometryArea(self):
        removeFacesWithZeroGeometryArea(self.geo, query=False)

    def removeFacesWithZeroMapArea(self):
        removeFacesWithZeroMapArea(self.geo, query=False)

    def removeInvalidComponents(self):
        removeInvalidComponents(self.geo, query=False)

    def finalize(self):
        pm.makeIdentity(self.geo, apply=True, t=1, r=1, s=1, n=0)
        pm.delete(self.geo, ch=1)
        pm.xform(self.geo, ws=True, pivots=[0, 0, 0])

    def getFaceWithMoreThan4Sides(self):
        return self.checkFaceWithMoreThan4Sides

    def getConcaveFaces(self):
        return self.checkConcaveFaces

    def getFaceWithHoles(self):
        return self.checkFaceWithHoles

    def getNonPlanarFaces(self):
        return self.checkNonPlanarFaces

    def getLaminaFaces(self):
        return self.checkLaminaFaces

    def getNonmanifoldGeometry(self):
        return self.checkNonmanifoldGeometry

    def getEdgesWithZeroLenght(self):
        return self.checkEdgesWithZeroLenght

    def getFacesWithZeroGeometryArea(self):
        return self.checkFacesWithZeroGeometryArea

    def getFacesWithZeroMapArea(self):
        return self.checkFacesWithZeroMapArea

    def getInvalidComponents(self):
        return self.checkInvalidComponents


if __name__ == "__main__":
    geoList = getAllObjectUnderGroup(pm.ls(sl=True)[0])
    for geo in geoList:
        print(geo.name())
        modelFix = ModelFix(geo)
        modelFix.autoFix()
