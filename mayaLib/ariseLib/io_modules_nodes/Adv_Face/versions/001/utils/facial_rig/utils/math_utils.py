"""
Math utility functions.
"""

import math
from typing import List


class MathUtils:
    """Utility class for math operations."""

    @staticmethod
    def distance(point_a: List[float], point_b: List[float]) -> float:
        """
        Calculate distance between two points.

        Args:
            point_a: First point [x, y, z]
            point_b: Second point [x, y, z]

        Returns:
            Distance value
        """
        return math.sqrt(
            (point_a[0] - point_b[0]) ** 2
            + (point_a[1] - point_b[1]) ** 2
            + (point_a[2] - point_b[2]) ** 2
        )

    @staticmethod
    def lerp(value_a: float, value_b: float, t: float) -> float:
        """
        Linear interpolation between two values.

        Args:
            value_a: Start value
            value_b: End value
            t: Interpolation factor (0-1)

        Returns:
            Interpolated value
        """
        return value_a + (value_b - value_a) * t

    @staticmethod
    def lerp_vector(point_a: List[float], point_b: List[float], t: float) -> List[float]:
        """
        Linear interpolation between two points.

        Args:
            point_a: Start point
            point_b: End point
            t: Interpolation factor (0-1)

        Returns:
            Interpolated point
        """
        return [
            MathUtils.lerp(point_a[0], point_b[0], t),
            MathUtils.lerp(point_a[1], point_b[1], t),
            MathUtils.lerp(point_a[2], point_b[2], t),
        ]

    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        Clamp value between min and max.

        Args:
            value: Value to clamp
            min_val: Minimum value
            max_val: Maximum value

        Returns:
            Clamped value
        """
        return max(min_val, min(value, max_val))

    @staticmethod
    def remap(
        value: float, old_min: float, old_max: float, new_min: float, new_max: float
    ) -> float:
        """
        Remap value from one range to another.

        Args:
            value: Input value
            old_min: Original minimum
            old_max: Original maximum
            new_min: New minimum
            new_max: New maximum

        Returns:
            Remapped value
        """
        if old_max - old_min == 0:
            return new_min
        return new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min)

    @staticmethod
    def smoothstep(edge0: float, edge1: float, x: float) -> float:
        """
        Smooth interpolation using smoothstep function.

        Args:
            edge0: Lower edge
            edge1: Upper edge
            x: Input value

        Returns:
            Smoothed value (0-1)
        """
        t = MathUtils.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    @staticmethod
    def normalize_vector(vector: List[float]) -> List[float]:
        """
        Normalize a vector.

        Args:
            vector: Input vector

        Returns:
            Normalized vector
        """
        magnitude = math.sqrt(sum(v**2 for v in vector))
        if magnitude == 0:
            return [0.0] * len(vector)
        return [v / magnitude for v in vector]

    @staticmethod
    def dot_product(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculate dot product of two vectors.

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Dot product value
        """
        return sum(a * b for a, b in zip(vec_a, vec_b))

    @staticmethod
    def cross_product(vec_a: List[float], vec_b: List[float]) -> List[float]:
        """
        Calculate cross product of two 3D vectors.

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Cross product vector
        """
        return [
            vec_a[1] * vec_b[2] - vec_a[2] * vec_b[1],
            vec_a[2] * vec_b[0] - vec_a[0] * vec_b[2],
            vec_a[0] * vec_b[1] - vec_a[1] * vec_b[0],
        ]

    @staticmethod
    def midpoint(point_a: List[float], point_b: List[float]) -> List[float]:
        """
        Calculate midpoint between two points.

        Args:
            point_a: First point
            point_b: Second point

        Returns:
            Midpoint
        """
        return [
            (point_a[0] + point_b[0]) / 2,
            (point_a[1] + point_b[1]) / 2,
            (point_a[2] + point_b[2]) / 2,
        ]

    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """
        Convert degrees to radians.

        Args:
            degrees: Angle in degrees

        Returns:
            Angle in radians
        """
        return degrees * math.pi / 180

    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """
        Convert radians to degrees.

        Args:
            radians: Angle in radians

        Returns:
            Angle in degrees
        """
        return radians * 180 / math.pi

    @staticmethod
    def angle_between_vectors(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Calculate angle between two vectors in degrees.

        Args:
            vec_a: First vector
            vec_b: Second vector

        Returns:
            Angle in degrees
        """
        dot = MathUtils.dot_product(
            MathUtils.normalize_vector(vec_a), MathUtils.normalize_vector(vec_b)
        )
        dot = MathUtils.clamp(dot, -1.0, 1.0)
        return MathUtils.radians_to_degrees(math.acos(dot))

    @staticmethod
    def mirror_point(point: List[float], axis: str = "x") -> List[float]:
        """
        Mirror point across axis.

        Args:
            point: Point to mirror
            axis: Mirror axis ("x", "y", or "z")

        Returns:
            Mirrored point
        """
        result = list(point)
        if axis == "x":
            result[0] *= -1
        elif axis == "y":
            result[1] *= -1
        elif axis == "z":
            result[2] *= -1
        return result

    @staticmethod
    def calculate_pole_vector_position(
        start_pos: List[float], mid_pos: List[float], end_pos: List[float], distance: float = 1.0
    ) -> List[float]:
        """
        Calculate pole vector position for IK chain.

        Args:
            start_pos: Start joint position
            mid_pos: Mid joint position
            end_pos: End joint position
            distance: Distance multiplier

        Returns:
            Pole vector position
        """
        # Calculate midpoint of line from start to end
        line_mid = MathUtils.midpoint(start_pos, end_pos)

        # Direction from line midpoint to mid joint
        direction = [mid_pos[0] - line_mid[0], mid_pos[1] - line_mid[1], mid_pos[2] - line_mid[2]]
        direction = MathUtils.normalize_vector(direction)

        # Calculate pole position
        return [
            mid_pos[0] + direction[0] * distance,
            mid_pos[1] + direction[1] * distance,
            mid_pos[2] + direction[2] * distance,
        ]
