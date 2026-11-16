"""
Geometry utility functions.
"""

from typing import List, Optional, Tuple

import maya.cmds as cmds


class GeometryUtils:
    """Utility class for geometry operations."""

    @staticmethod
    def get_bounding_box(obj: str) -> Tuple[List[float], List[float]]:
        """
        Get the bounding box of an object.

        Args:
            obj: Object name

        Returns:
            Tuple of (min_point, max_point)
        """
        bb = cmds.xform(obj, query=True, worldSpace=True, boundingBox=True)
        min_point = [bb[0], bb[1], bb[2]]
        max_point = [bb[3], bb[4], bb[5]]
        return min_point, max_point

    @staticmethod
    def get_center(obj: str) -> List[float]:
        """
        Get the center point of an object's bounding box.

        Args:
            obj: Object name

        Returns:
            Center point [x, y, z]
        """
        min_pt, max_pt = GeometryUtils.get_bounding_box(obj)
        return [
            (min_pt[0] + max_pt[0]) / 2,
            (min_pt[1] + max_pt[1]) / 2,
            (min_pt[2] + max_pt[2]) / 2,
        ]

    @staticmethod
    def get_skin_cluster(geometry: str) -> Optional[str]:
        """
        Get the skin cluster attached to geometry.

        Args:
            geometry: Geometry name

        Returns:
            Skin cluster name or None
        """
        # Get shape node
        shapes = cmds.listRelatives(geometry, shapes=True, noIntermediate=True)
        if not shapes:
            return None

        # Find skin cluster in history
        history = cmds.listHistory(shapes[0], pruneDagObjects=True)
        if not history:
            return None

        skin_clusters = cmds.ls(history, type="skinCluster")
        return skin_clusters[0] if skin_clusters else None

    @staticmethod
    def get_vertex_position(vertex: str) -> List[float]:
        """
        Get world space position of a vertex.

        Args:
            vertex: Vertex name (e.g., "pSphere1.vtx[0]")

        Returns:
            Position [x, y, z]
        """
        return cmds.xform(vertex, query=True, worldSpace=True, translation=True)

    @staticmethod
    def set_vertex_position(vertex: str, position: List[float]):
        """
        Set world space position of a vertex.

        Args:
            vertex: Vertex name
            position: Target position [x, y, z]
        """
        cmds.xform(vertex, worldSpace=True, translation=position)

    @staticmethod
    def get_closest_vertex(geometry: str, position: List[float]) -> Tuple[str, int]:
        """
        Find the closest vertex to a position.

        Args:
            geometry: Geometry name
            position: World space position

        Returns:
            Tuple of (vertex_name, vertex_index)
        """
        # Create closestPointOnMesh node
        cpom = cmds.createNode("closestPointOnMesh")
        shape = cmds.listRelatives(geometry, shapes=True)[0]

        cmds.connectAttr(f"{shape}.outMesh", f"{cpom}.inMesh")
        cmds.setAttr(f"{cpom}.inPosition", *position, type="float3")

        vertex_id = cmds.getAttr(f"{cpom}.closestVertexIndex")
        vertex_name = f"{geometry}.vtx[{vertex_id}]"

        cmds.delete(cpom)
        return vertex_name, vertex_id

    @staticmethod
    def get_vertices_from_selection(selection: str) -> List[str]:
        """
        Get flat list of vertices from a selection string.

        Args:
            selection: Selection string

        Returns:
            List of vertex names
        """
        cmds.select(selection)
        return cmds.ls(selection=True, flatten=True)

    @staticmethod
    def grow_selection(vertices: List[str], iterations: int = 1) -> List[str]:
        """
        Grow vertex selection.

        Args:
            vertices: Initial vertices
            iterations: Number of grow iterations

        Returns:
            Expanded vertex list
        """
        cmds.select(vertices)
        for _ in range(iterations):
            cmds.polySelectConstraint(pp=1, type=0x0001)
        return cmds.ls(selection=True, flatten=True)

    @staticmethod
    def get_shell_vertices(start_vertex: str) -> List[str]:
        """
        Get all vertices in the same shell as the start vertex.

        Args:
            start_vertex: Starting vertex

        Returns:
            List of all shell vertices
        """
        cmds.select(start_vertex)
        cmds.ConvertSelectionToShell()
        return cmds.ls(selection=True, flatten=True)

    @staticmethod
    def combine_meshes(meshes: List[str], name: str) -> str:
        """
        Combine multiple meshes into one.

        Args:
            meshes: List of mesh names
            name: Name for combined mesh

        Returns:
            Name of combined mesh
        """
        if len(meshes) == 1:
            return cmds.duplicate(meshes[0], name=name)[0]

        combined = cmds.polyUnite(meshes, name=name, mergeUVSets=1)[0]
        cmds.delete(combined, constructionHistory=True)
        return combined

    @staticmethod
    def offset_curve_to_mesh(curve: str, mesh: str, offset: float = 0.1):
        """
        Offset curve CVs toward mesh surface.

        Args:
            curve: Curve name
            mesh: Target mesh
            offset: Offset distance
        """
        cpom = cmds.createNode("closestPointOnMesh", name="tempCPOM")
        shape = cmds.listRelatives(mesh, shapes=True)[0]
        cmds.connectAttr(f"{shape}.outMesh", f"{cpom}.inMesh")

        num_cvs = cmds.getAttr(f"{curve}.spans") + cmds.getAttr(f"{curve}.degree")
        for i in range(num_cvs):
            cv = f"{curve}.cv[{i}]"
            pos = cmds.xform(cv, query=True, worldSpace=True, translation=True)
            cmds.setAttr(f"{cpom}.inPosition", *pos, type="float3")

            closest_pos = cmds.getAttr(f"{cpom}.position")[0]
            normal = cmds.getAttr(f"{cpom}.normal")[0]

            new_pos = [
                closest_pos[0] + normal[0] * offset,
                closest_pos[1] + normal[1] * offset,
                closest_pos[2] + normal[2] * offset,
            ]
            cmds.xform(cv, worldSpace=True, translation=new_pos)

        cmds.delete(cpom)
