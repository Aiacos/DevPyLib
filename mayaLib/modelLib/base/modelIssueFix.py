"""
modelIssueFix.py
================

This module provides a class `ModelFix` that can be used to fix various issues
with a Maya model. The class takes a Maya node as an argument and provides methods
to fix issues such as faces with more than 4 sides, concave faces, faces with
holes, non-planar faces, lamina faces, non-manifold geometry, edges with zero
length, faces with zero geometry area, faces with zero map area, and invalid
components.

The class also provides a method to check if a model has any of these issues and
to get the list of components that have the issue.

The module also provides some functions to fix the issues.

Example
-------

.. code-block:: python

    import mayaLib.modelLib.base.modelIssueFix as modelIssueFix

    geo = pm.ls(sl=True)[0]
    modelFix = modelIssueFix.ModelFix(geo)
    modelFix.autoFix()

"""

import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils.util import unlock_and_unhide_all, getAllObjectUnderGroup


def mergeDuplicatedVertex(geo, threshold=0.001, only2Vertex=False):
    """
    Merge duplicated vertex in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to merge duplicated vertex.
        threshold (float): The maximum distance between two vertices to be
            considered the same vertex. Defaults to 0.001.
        only2Vertex (bool): If True, only merge two vertices. Defaults to False.

    Returns:
        None
    """
    pm.polyMergeVertex(geo, am=only2Vertex, ch=False, distance=threshold)


def fixFaceWithMoreThan4Sides(geo, query=True):
    """
    Fix faces with more than 4 sides in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to fix faces with more than 4 sides.
        query (bool): If True, return the list of faces with more than 4 sides.
            Defaults to True.

    Returns:
        list or None: The list of faces with more than 4 sides if query is True,
            None otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def fixConcaveFaces(geo, query=True):
    """
    Fix concave faces in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to fix concave faces.
        query (bool): If True, return the list of concave faces. Defaults to True.

    Returns:
        list or None: The list of concave faces if query is True, None otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def fixFaceWithHoles(geo, query=True):
    """
    Fix faces with holes in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to fix faces with holes.
        query (bool): If True, return the list of faces with holes. Defaults to True.

    Returns:
        list or None: The list of faces with holes if query is True, None otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def fixNonPlanarFaces(geo, query=True):
    """
    Fix non-planar faces in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to fix non-planar faces.
        query (bool): If True, return the list of non-planar faces. Defaults to True.

    Returns:
        list or None: The list of non-planar faces if query is True, None otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def removeLaminaFaces(geo, query=True):
    """
    Remove lamina faces in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to remove lamina faces.
        query (bool): If True, return the list of lamina faces. Defaults to True.

    Returns:
        list or None: The list of lamina faces if query is True, None otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" }; '))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" }; '))


def removeNonmanifoldGeometry(geo, query=True):
    """
    Remove non-manifold geometry in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to remove non-manifold geometry.
        query (bool): If True, return the list of non-manifold geometry.
            Defaults to True.

    Returns:
        list or None: The list of non-manifold geometry if query is True, None
            otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))


def removeEdgesWithZeroLenght(geo, query=True):
    """
    Remove edges with zero length in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to remove edges with zero length.
        query (bool): If True, return the list of edges with zero length.
            Defaults to True.

    Returns:
        list or None: The list of edges with zero length if query is True, None
            otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))


def removeFacesWithZeroGeometryArea(geo, query=True):
    """Remove faces with zero geometry area in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to remove faces with zero geometry
            area.
        query (bool): If True, return the list of faces with zero geometry area.
            Defaults to True.

    Returns:
        list or None: The list of faces with zero geometry area if query is True,
            None otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))


def removeFacesWithZeroMapArea(geo, query=True):
    """Remove faces with zero map area in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to remove faces with zero map area.
        query (bool): If True, return the list of faces with zero map area.
            Defaults to True.

    Returns:
        list or None: The list of faces with zero map area if query is True, None
            otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'))


def removeInvalidComponents(geo, query=True):
    """Remove invalid components in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to remove invalid components.
        query (bool): If True, return the list of invalid components. Defaults to
            True.

    Returns:
        list or None: The list of invalid components if query is True, None
            otherwise.
    """
    pm.select(geo)
    if query:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","1" };'))
    else:
        return pm.ls(mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","1" };'))


class ModelFix():
    """Class to fix common modeling issues in Maya.

    Attributes:
        geo (str or PyNode): The Maya node to fix modeling issues.
        checkFaceWithMoreThan4Sides (list): List of faces with more than 4 sides.
        checkConcaveFaces (list): List of concave faces.
        checkFaceWithHoles (list): List of faces with holes.
        checkNonPlanarFaces (list): List of non-planar faces.
        checkLaminaFaces (list): List of lamina faces.
        checkNonmanifoldGeometry (list): List of non-manifold geometry.
        checkEdgesWithZeroLenght (list): List of edges with zero length.
        checkFacesWithZeroGeometryArea (list): List of faces with zero geometry
            area.
        checkFacesWithZeroMapArea (list): List of faces with zero map area.
        checkInvalidComponents (list): List of invalid components.
    """
    def __init__(self, geo, check=True):
        """Initialize the ModelFix object.

        Args:
            geo (str or PyNode): The Maya node to fix modeling issues.
            check (bool): If True, run the checks. Defaults to True.
        """
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
        """Auto fix the model based on the given options.

        Args:
            faceWithMoreThan4Sides (bool): If True, fix faces with more than 4 sides.
            concaveFaces (bool): If True, fix concave faces.
            faceWithHoles (bool): If True, fix faces with holes.
            nonPlanarFaces (bool): If True, fix non planar faces.
            laminaFaces (bool): If True, remove lamina faces.
            nonmanifoldGeometry (bool): If True, remove non-manifold geometry.
            edgesWithZeroLenght (bool): If True, remove edges with zero length.
            facesWithZeroGeometryArea (bool): If True, remove faces with zero geometry area.
            facesWithZeroMapArea (bool): If True, remove faces with zero map area.
            invalidComponents (bool): If True, remove invalid components.
        """
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
        """Fix faces with more than 4 sides."""
        fixFaceWithMoreThan4Sides(self.geo, query=False)

    def fixConcaveFaces(self):
        """Fix concave faces."""
        fixConcaveFaces(self.geo, query=False)

    def fixFaceWithHoles(self):
        """Fix faces with holes."""
        fixFaceWithHoles(self.geo, query=False)

    def fixNonPlanarFaces(self):
        """Fix non planar faces."""
        fixNonPlanarFaces(self.geo, query=False)

    def removeLaminaFaces(self):
        """Remove lamina faces."""
        removeLaminaFaces(self.geo, query=False)

    def removeNonmanifoldGeometry(self):
        """Remove non-manifold geometry."""
        removeNonmanifoldGeometry(self.geo, query=False)

    def removeEdgesWithZeroLenght(self):
        """Remove edges with zero length."""
        removeEdgesWithZeroLenght(self.geo, query=False)

    def removeFacesWithZeroGeometryArea(self):
        """Remove faces with zero geometry area."""
        removeFacesWithZeroGeometryArea(self.geo, query=False)

    def removeFacesWithZeroMapArea(self):
        """Remove faces with zero map area."""
        removeFacesWithZeroMapArea(self.geo, query=False)

    def removeInvalidComponents(self):
        """Remove invalid components."""
        removeInvalidComponents(self.geo, query=False)

    def finalize(self):
        """Finalize the model after fixing all the issues."""
        pm.makeIdentity(self.geo, apply=True, t=1, r=1, s=1, n=0)
        pm.delete(self.geo, ch=1)
        pm.xform(self.geo, ws=True, pivots=[0, 0, 0])

    def getFaceWithMoreThan4Sides(self):
        """Get the list of faces with more than 4 sides."""
        return self.checkFaceWithMoreThan4Sides

    def getConcaveFaces(self):
        """Get the list of concave faces."""
        return self.checkConcaveFaces

    def getFaceWithHoles(self):
        """Get the list of faces with holes."""
        return self.checkFaceWithHoles

    def getNonPlanarFaces(self):
        """Get the list of non planar faces."""
        return self.checkNonPlanarFaces

    def getLaminaFaces(self):
        """Get the list of lamina faces."""
        return self.checkLaminaFaces

    def getNonmanifoldGeometry(self):
        """Get the list of non-manifold geometry."""
        return self.checkNonmanifoldGeometry

    def getEdgesWithZeroLenght(self):
        """Get the list of edges with zero length."""
        return self.checkEdgesWithZeroLenght

    def getFacesWithZeroGeometryArea(self):
        """Get the list of faces with zero geometry area."""
        return self.checkFacesWithZeroGeometryArea

    def getFacesWithZeroMapArea(self):
        """Get the list of faces with zero map area."""
        return self.checkFacesWithZeroMapArea

    def getInvalidComponents(self):
        """Get the list of invalid components."""
        return self.checkInvalidComponents


if __name__ == "__main__":
    geoList = getAllObjectUnderGroup(pm.ls(sl=True)[0])
    for geo in geoList:
        print((geo.name()))
        modelFix = ModelFix(geo)
        modelFix.autoFix()