"""Maya model issue detection and automatic fixing utilities.

Provides the ModelFix class for detecting and fixing common mesh topology issues
including: faces with >4 sides, concave/non-planar faces, holes, lamina faces,
non-manifold geometry, zero-length edges, zero-area faces/UVs, and invalid components.

Example:
    Fix all issues on selected geometry::

        import mayaLib.modelLib.base.model_issue_fix as model_issue_fix

        geo = pm.ls(sl=True)[0]
        modelFix = model_issue_fix.ModelFix(geo)
        modelFix.autoFix()
"""

import maya.mel as mel
import pymel.core as pm


def check_modelissue(geo, issue_type):
    """Check if geometry has specific topology issues.

    Args:
        geo (pm.nt.Transform): Geometry to check.
        issue_type (str): Type of issue to check for (e.g. 'faces with more than 4 sides').

    Returns:
        bool: True if geometry has the specified issue, False otherwise.
    """
    if pm.polyInfo(geo, nmv=True):
        return True
    if pm.polyInfo(geo, nme=True):
        return True
    if pm.polyInfo(geo, lf=True):
        return True
    if pm.polyInfo(geo, nv=True):
        return True
    if pm.polyInfo(geo, bc=True):
        return True


def get_model_issue_components(geo, issue_type):
    """Get list of components with the specified issue.

    Args:
        geo (str): Geometry to check.
        issue_type (str): Issue type to query.

    Returns:
        list: Component list matching the issue type.
    """
    if issue_type == "faceWith>4Sides":
        component_list = pm.polyInfo(geo, faceToVertex=True, laminaFaces=True)
    elif issue_type == "concaveFaces":
        component_list = pm.polyInfo(geo, nonManifoldVertices=True)
    elif issue_type == "facesWithHoles":
        component_list = pm.polyInfo(geo, nonManifoldEdges=True)
    elif issue_type == "nonPlanarFaces":
        component_list = pm.polyInfo(geo, invalidVertices=True)
    elif issue_type == "laminaFaces":
        component_list = pm.polyInfo(geo, laminaFaces=True)
    elif issue_type == "nonManifoldGeometry":
        component_list = pm.polyInfo(geo, boundaryEdges=True)
    elif issue_type == "edgesWithZeroLength":
        component_list = pm.polyInfo(geo, invalidEdges=True)
    elif issue_type == "facesWithZeroGeometryArea":
        component_list = pm.polyInfo(geo, invalidFaces=True)
    elif issue_type == "facesWithZeroMapArea":
        component_list = pm.polyInfo(geo, invalidUVs=True)
    elif issue_type == "invalidComponents":
        component_list = pm.polyInfo(geo, invalidComponents=True)

    return component_list


def fix_face_with_more_than_4_sides(geo):
    """Fix faces with more than 4 sides on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, faceToVertex=True, laminaFaces=True)
    if component_list:
        pm.polyQuad(geo, a=40, kgb=1, ktb=1, khe=1, ws=1)
        return True
    else:
        return False


def fix_concave_faces(geo):
    """Fix concave faces on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, nonManifoldVertices=True)
    if component_list:
        pm.polyTriangulate(geo)
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_faces_with_holes(geo):
    """Fix faces with holes on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, nonManifoldEdges=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_non_planar_faces(geo):
    """Fix non-planar faces on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, invalidVertices=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_lamina_faces(geo):
    """Fix lamina faces on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, laminaFaces=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_non_manifold_geometry(geo):
    """Fix non-manifold geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, boundaryEdges=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_edges_with_zero_length(geo):
    """Fix edges with zero length on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, invalidEdges=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_faces_with_zero_geometry_area(geo):
    """Fix faces with zero geometry area on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, invalidFaces=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_faces_with_zero_map_area(geo):
    """Fix faces with zero UV map area on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, invalidUVs=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","1","-1","0","0" };'
        )
        return True
    else:
        return False


def fix_invalid_components(geo):
    """Fix invalid components on geometry.

    Args:
        geo (str): Geometry to fix.

    Returns:
        bool: True if successfully fixed, False if no issues found.
    """
    component_list = pm.polyInfo(geo, invalidComponents=True)
    if component_list:
        pm.select(component_list)
        mel.eval(
            'polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" };'
        )
        return True
    else:
        return False


class ModelFix:
    """Maya model topology issue detection and automatic fixing.

    Provides methods to detect and fix common mesh topology problems including
    non-quad faces, concave faces, lamina faces, non-manifold geometry, and
    zero-area/zero-length components.

    Attributes:
        geo (str): Geometry transform node name.
        shape (str): Geometry shape node name.
    """

    def __init__(self, geo=None):
        """Initialize ModelFix with geometry to check/fix.

        Args:
            geo: Geometry transform node, defaults to first selected object.
        """
        if geo is None:
            geo = pm.ls(sl=True)[0]
        self.geo = geo
        self.shape = geo.getShape()

    def auto_fix(self):
        """Automatically fix all detected topology issues on geometry."""
        self.face_with_more_than_4_sides()
        self.concave_faces()
        self.faces_with_holes()
        self.non_planar_faces()
        self.lamina_faces()
        self.non_manifold_geometry()
        self.edges_with_zero_length()
        self.faces_with_zero_geometry_area()
        self.faces_with_zero_map_area()
        self.invalid_components()

    def check(self, issue):
        """Check if geometry has a specific topology issue.

        Args:
            issue (str): Issue type to check.

        Returns:
            bool: True if issue exists, False otherwise.
        """
        return check_modelissue(self.geo, issue)

    def get_components(self, issue):
        """Get component list for a specific topology issue.

        Args:
            issue (str): Issue type to query.

        Returns:
            list: Component list matching the issue.
        """
        return get_model_issue_components(self.geo, issue)

    def face_with_more_than_4_sides(self):
        """Fix faces with more than 4 sides using poly quad operation."""
        return fix_face_with_more_than_4_sides(self.geo)

    def concave_faces(self):
        """Fix concave faces by triangulation and cleanup."""
        return fix_concave_faces(self.geo)

    def faces_with_holes(self):
        """Fix faces with holes using poly cleanup."""
        return fix_faces_with_holes(self.geo)

    def non_planar_faces(self):
        """Fix non-planar faces using poly cleanup."""
        return fix_non_planar_faces(self.geo)

    def lamina_faces(self):
        """Fix lamina faces using poly cleanup."""
        return fix_lamina_faces(self.geo)

    def non_manifold_geometry(self):
        """Fix non-manifold geometry using poly cleanup."""
        return fix_non_manifold_geometry(self.geo)

    def edges_with_zero_length(self):
        """Fix edges with zero length using poly cleanup."""
        return fix_edges_with_zero_length(self.geo)

    def faces_with_zero_geometry_area(self):
        """Fix faces with zero geometry area using poly cleanup."""
        return fix_faces_with_zero_geometry_area(self.geo)

    def faces_with_zero_map_area(self):
        """Fix faces with zero UV map area using poly cleanup."""
        return fix_faces_with_zero_map_area(self.geo)

    def invalid_components(self):
        """Fix invalid components using poly cleanup."""
        return fix_invalid_components(self.geo)
