"""
Skinning utility functions.
"""

from typing import List, Optional

import maya.cmds as cmds


class SkinningUtils:
    """Utility class for skinning operations."""

    @staticmethod
    def get_skin_cluster(geometry: str) -> Optional[str]:
        """
        Get skin cluster from geometry.

        Args:
            geometry: Geometry name

        Returns:
            Skin cluster name or None
        """
        shapes = cmds.listRelatives(geometry, shapes=True, noIntermediate=True)
        if not shapes:
            return None

        history = cmds.listHistory(shapes[0], pruneDagObjects=True)
        if not history:
            return None

        skin_clusters = cmds.ls(history, type="skinCluster")
        return skin_clusters[0] if skin_clusters else None

    @staticmethod
    def add_influence(
        skin_cluster: str, joint: str, lock_weights: bool = False, weight: float = 0.0
    ):
        """
        Add a joint as influence to skin cluster.

        Args:
            skin_cluster: Skin cluster name
            joint: Joint to add
            lock_weights: Lock influence weights
            weight: Initial weight value
        """
        cmds.skinCluster(
            skin_cluster,
            edit=True,
            addInfluence=joint,
            weight=weight,
            lockWeights=lock_weights,
            dropoffRate=4,
        )

    @staticmethod
    def remove_unused_influences(skin_cluster: str):
        """
        Remove influences with zero weights.

        Args:
            skin_cluster: Skin cluster name
        """
        cmds.skinCluster(skin_cluster, edit=True, removeUnusedInfluence=True)

    @staticmethod
    def set_weights(skin_cluster: str, vertices: List[str], joint: str, weight: float):
        """
        Set skin weights for vertices.

        Args:
            skin_cluster: Skin cluster name
            vertices: List of vertices
            joint: Target joint
            weight: Weight value (0-1)
        """
        for vtx in vertices:
            cmds.skinPercent(skin_cluster, vtx, transformValue=[(joint, weight)])

    @staticmethod
    def get_weight(skin_cluster: str, vertex: str, joint: str) -> float:
        """
        Get weight of a joint on a vertex.

        Args:
            skin_cluster: Skin cluster name
            vertex: Vertex name
            joint: Joint name

        Returns:
            Weight value
        """
        return cmds.skinPercent(skin_cluster, vertex, transform=joint, query=True)

    @staticmethod
    def copy_weights(
        source_geo: str,
        target_geo: str,
        surface_association: str = "closestPoint",
        influence_association: str = "closestJoint",
    ):
        """
        Copy skin weights between geometries.

        Args:
            source_geo: Source geometry
            target_geo: Target geometry
            surface_association: Surface association method
            influence_association: Influence association method
        """
        cmds.select(source_geo, target_geo)
        cmds.copySkinWeights(
            noMirror=True,
            surfaceAssociation=surface_association,
            influenceAssociation=influence_association,
        )

    @staticmethod
    def lock_influence(skin_cluster: str, joint: str, lock: bool = True):
        """
        Lock or unlock influence weights.

        Args:
            skin_cluster: Skin cluster name
            joint: Joint to lock/unlock
            lock: Whether to lock
        """
        cmds.setAttr(f"{joint}.lockInfluenceWeights", lock)

    @staticmethod
    def lock_all_influences(
        skin_cluster: str, lock: bool = True, exclude: Optional[List[str]] = None
    ):
        """
        Lock all influences in skin cluster.

        Args:
            skin_cluster: Skin cluster name
            lock: Whether to lock
            exclude: Joints to exclude from locking
        """
        exclude = exclude or []
        influences = cmds.skinCluster(skin_cluster, query=True, influence=True)

        for inf in influences:
            if inf not in exclude:
                cmds.setAttr(f"{inf}.lockInfluenceWeights", lock)

    @staticmethod
    def transfer_weights_to_joint(
        skin_cluster: str,
        source_joint: str,
        target_joint: str,
        vertices: Optional[List[str]] = None,
    ):
        """
        Transfer weights from one joint to another.

        Args:
            skin_cluster: Skin cluster name
            source_joint: Source joint
            target_joint: Target joint
            vertices: Vertices to affect (None = all)
        """
        if vertices is None:
            # Get all vertices affected by source joint
            cmds.skinCluster(skin_cluster, edit=True, selectInfluenceVerts=source_joint)
            vertices = cmds.ls(selection=True, flatten=True)

        for vtx in vertices:
            source_weight = cmds.skinPercent(skin_cluster, vtx, transform=source_joint, query=True)
            if source_weight > 0:
                target_weight = cmds.skinPercent(
                    skin_cluster, vtx, transform=target_joint, query=True
                )
                cmds.skinPercent(
                    skin_cluster,
                    vtx,
                    transformValue=[
                        (target_joint, source_weight + target_weight),
                        (source_joint, 0),
                    ],
                )

    @staticmethod
    def smooth_weights(skin_cluster: str, vertices: List[str], iterations: int = 5):
        """
        Smooth weights on vertices.

        Args:
            skin_cluster: Skin cluster name
            vertices: Vertices to smooth
            iterations: Smoothing iterations
        """
        cmds.select(vertices)
        for _ in range(iterations):
            cmds.WeightHammer()

    @staticmethod
    def normalize_weights(skin_cluster: str):
        """
        Normalize all weights in skin cluster.

        Args:
            skin_cluster: Skin cluster name
        """
        cmds.skinCluster(skin_cluster, edit=True, normalize=True)

    @staticmethod
    def create_skin_cluster(
        geometry: str,
        joints: List[str],
        name: Optional[str] = None,
        max_influences: int = 3,
        bind_method: int = 0,
    ) -> str:
        """
        Create a new skin cluster.

        Args:
            geometry: Geometry to skin
            joints: Joints to bind
            name: Optional skin cluster name
            max_influences: Maximum influences per vertex
            bind_method: Bind method (0=closest distance, 1=closest in hierarchy)

        Returns:
            Skin cluster name
        """
        cmds.select(joints, geometry)
        result = cmds.skinCluster(
            toSelectedBones=True,
            maximumInfluences=max_influences,
            dropoffRate=4,
            removeUnusedInfluence=False,
            bindMethod=bind_method,
        )
        skin_cluster = result[0]

        if name:
            skin_cluster = cmds.rename(skin_cluster, name)

        return skin_cluster

    @staticmethod
    def get_influences(skin_cluster: str) -> List[str]:
        """
        Get all influences in a skin cluster.

        Args:
            skin_cluster: Skin cluster name

        Returns:
            List of influence joint names
        """
        return cmds.skinCluster(skin_cluster, query=True, influence=True) or []

    @staticmethod
    def prune_weights(
        skin_cluster: str, threshold: float = 0.01, vertices: Optional[List[str]] = None
    ):
        """
        Prune small weights below threshold.

        Args:
            skin_cluster: Skin cluster name
            threshold: Weight threshold
            vertices: Optional vertices to prune (None = all)
        """
        if vertices:
            cmds.select(vertices)
        cmds.skinPercent(skin_cluster, pruneWeights=threshold, normalize=True)
