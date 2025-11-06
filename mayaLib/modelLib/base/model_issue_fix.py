"""modelIssueFix.py
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

    import mayaLib.modelLib.base.model_issue_fix as model_issue_fix

    geo = pm.ls(sl=True)[0]
    modelFix = model_issue_fix.ModelFix(geo)
    modelFix.autoFix()

"""

import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils.util import list_objects_under_group, unlock_and_unhide_all


def merge_duplicated_vertex(geo, threshold=0.001, only_2_vertex=False):
    """Merge duplicated vertex in a Maya node.

    Args:
        geo (str or PyNode): The Maya node to merge duplicated vertex.
        threshold (float): The maximum distance between two vertices to be
            considered the same vertex. Defaults to 0.001.
        only_2_vertex (bool): If True, only merge two vertices. Defaults to False.

    Returns:
        None
    """
    pm.polyMergeVertex(geo, am=only_2_vertex, ch=False, distance=threshold)


def fix_face_with_more_than_4_sides(geo, query=True):
    """Fix faces with more than 4 sides in a Maya node.

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


def fix_concave_faces(geo, query=True):
    """Fix concave faces in a Maya node.

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


def fix_face_with_holes(geo, query=True):
    """Fix faces with holes in a Maya node.

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


def fix_non_planar_faces(geo, query=True):
    """Fix non-planar faces in a Maya node.

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


def remove_lamina_faces(geo, query=True):
    """Remove lamina faces in a Maya node.

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


def remove_nonmanifold_geometry(geo, query=True):
    """Remove non-manifold geometry in a Maya node.

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


def remove_edges_with_zero_length(geo, query=True):
    """Remove edges with zero length in a Maya node.

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


def remove_faces_with_zero_geometry_area(geo, query=True):
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


def remove_faces_with_zero_map_area(geo, query=True):
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


def remove_invalid_components(geo, query=True):
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
        check_face_with_more_than_4_sides (list): List of faces with more than 4 sides.
        check_concave_faces (list): List of concave faces.
        check_face_with_holes (list): List of faces with holes.
        check_non_planar_faces (list): List of non-planar faces.
        check_lamina_faces (list): List of lamina faces.
        check_nonmanifold_geometry (list): List of non-manifold geometry.
        check_edges_with_zero_lenght (list): List of edges with zero length.
        check_faces_with_zero_geometry_area (list): List of faces with zero geometry
            area.
        check_faces_with_zero_map_area (list): List of faces with zero map area.
        check_invalid_components (list): List of invalid components.
    """
    def __init__(self, geo, check=True):
        """Initialize the ModelFix object.

        Args:
            geo (str or PyNode): The Maya node to fix modeling issues.
            check (bool): If True, run the checks. Defaults to True.
        """
        self.geo = pm.ls(geo)[0]

        unlock_and_unhide_all(self.geo)
        merge_duplicated_vertex(self.geo)

        if check:
            self.check_face_with_more_than_4_sides = fix_face_with_more_than_4_sides(self.geo, query=True)
            self.check_concave_faces = fix_concave_faces(self.geo, query=True)
            self.check_face_with_holes = fix_face_with_holes(self.geo, query=True)
            self.check_non_planar_faces = fix_non_planar_faces(self.geo, query=True)
            self.check_lamina_faces = remove_lamina_faces(self.geo, query=True)
            self.check_nonmanifold_geometry = remove_nonmanifold_geometry(self.geo, query=True)
            self.check_edges_with_zero_lenght = remove_edges_with_zero_length(self.geo, query=True)
            self.check_faces_with_zero_geometry_area = remove_faces_with_zero_geometry_area(self.geo, query=True)
            self.check_faces_with_zero_map_area = remove_faces_with_zero_map_area(self.geo, query=True)
            self.check_invalid_components = remove_invalid_components(self.geo, query=True)

    def auto_fix(self,
                face_with_more_than_4_sides=False,
                concave_faces=True,
                face_with_holes=True,
                non_planar_faces=False,
                lamina_faces=True,
                nonmanifold_geometry=True,
                edges_with_zero_lenght=True,
                faces_with_zero_geometry_area=True,
                faces_with_zero_map_area=False,
                invalid_components=True):
        """Auto fix the model based on the given options.

        Args:
            face_with_more_than_4_sides (bool): If True, fix faces with more than 4 sides.
            concave_faces (bool): If True, fix concave faces.
            face_with_holes (bool): If True, fix faces with holes.
            non_planar_faces (bool): If True, fix non planar faces.
            lamina_faces (bool): If True, remove lamina faces.
            nonmanifold_geometry (bool): If True, remove non-manifold geometry.
            edges_with_zero_lenght (bool): If True, remove edges with zero length.
            faces_with_zero_geometry_area (bool): If True, remove faces with zero geometry area.
            faces_with_zero_map_area (bool): If True, remove faces with zero map area.
            invalid_components (bool): If True, remove invalid components.
        """
        if face_with_more_than_4_sides:
            self.fix_face_with_more_than_4_sides()
        if concave_faces:
            self.fix_concave_faces()
        if face_with_holes:
            self.fix_face_with_holes()
        if non_planar_faces:
            self.fix_non_planar_faces()

        if lamina_faces:
            self.remove_lamina_faces()
        if nonmanifold_geometry:
            self.remove_nonmanifold_geometry()
        if edges_with_zero_lenght:
            self.remove_edges_with_zero_length()
        if faces_with_zero_geometry_area:
            self.remove_faces_with_zero_geometry_area()
        if faces_with_zero_map_area:
            self.remove_faces_with_zero_map_area()
        if invalid_components:
            self.remove_invalid_components()

        self.finalize()

    def fix_face_with_more_than_4_sides(self):
        """Fix faces with more than 4 sides."""
        fix_face_with_more_than_4_sides(self.geo, query=False)

    def fix_concave_faces(self):
        """Fix concave faces."""
        fix_concave_faces(self.geo, query=False)

    def fix_face_with_holes(self):
        """Fix faces with holes."""
        fix_face_with_holes(self.geo, query=False)

    def fix_non_planar_faces(self):
        """Fix non planar faces."""
        fix_non_planar_faces(self.geo, query=False)

    def remove_lamina_faces(self):
        """Remove lamina faces."""
        remove_lamina_faces(self.geo, query=False)

    def remove_nonmanifold_geometry(self):
        """Remove non-manifold geometry."""
        remove_nonmanifold_geometry(self.geo, query=False)

    def remove_edges_with_zero_length(self):
        """Remove edges with zero length."""
        remove_edges_with_zero_length(self.geo, query=False)

    def remove_faces_with_zero_geometry_area(self):
        """Remove faces with zero geometry area."""
        remove_faces_with_zero_geometry_area(self.geo, query=False)

    def remove_faces_with_zero_map_area(self):
        """Remove faces with zero map area."""
        remove_faces_with_zero_map_area(self.geo, query=False)

    def remove_invalid_components(self):
        """Remove invalid components."""
        remove_invalid_components(self.geo, query=False)

    def finalize(self):
        """Finalize the model after fixing all the issues."""
        pm.makeIdentity(self.geo, apply=True, t=1, r=1, s=1, n=0)
        pm.delete(self.geo, ch=1)
        pm.xform(self.geo, ws=True, pivots=[0, 0, 0])

    def get_face_with_more_than_4_sides(self):
        """Get the list of faces with more than 4 sides."""
        return self.check_face_with_more_than_4_sides

    def get_concave_faces(self):
        """Get the list of concave faces."""
        return self.check_concave_faces

    def get_face_with_holes(self):
        """Get the list of faces with holes."""
        return self.check_face_with_holes

    def get_non_planar_faces(self):
        """Get the list of non planar faces."""
        return self.check_non_planar_faces

    def get_lamina_faces(self):
        """Get the list of lamina faces."""
        return self.check_lamina_faces

    def get_nonmanifold_geometry(self):
        """Get the list of non-manifold geometry."""
        return self.check_nonmanifold_geometry

    def get_edges_with_zero_length(self):
        """Get the list of edges with zero length."""
        return self.check_edges_with_zero_lenght

    def get_faces_with_zero_geometry_area(self):
        """Get the list of faces with zero geometry area."""
        return self.check_faces_with_zero_geometry_area

    def get_faces_with_zero_map_area(self):
        """Get the list of faces with zero map area."""
        return self.check_faces_with_zero_map_area

    def get_invalid_components(self):
        """Get the list of invalid components."""
        return self.check_invalid_components


if __name__ == "__main__":
    geo_list = list_objects_under_group(pm.ls(sl=True)[0])
    for geo in geo_list:
        print((geo.name()))
        model_fix = ModelFix(geo)
        model_fix.auto_fix()
