"""Opacity ramp utilities for fluid simulations.

This module provides helper functions for creating and configuring opacity
ramps on Maya fluid containers. These functions abstract common patterns
used across different fluid presets (explosion, fire, smoke, etc.).
"""

from __future__ import annotations

__author__ = "Lorenzo Argentieri"

import pymel.core as pm

from mayaLib.fluidLib.utility import math_function

__all__ = ["setup_repart_opacity_ramp", "setup_manual_opacity_ramp"]


def setup_repart_opacity_ramp(
    fluid_container: pm.PyNode,
    sampling: int = 20,
    curve_parameter: float = 15.0,
) -> None:
    """Configure fluid opacity using a repart function curve.

    The repart function creates a smooth bell-curve-like opacity distribution
    that starts at 0, rises to 1, and returns to 0. This is ideal for creating
    natural-looking fluid effects like explosions and thick smoke.

    Args:
        fluid_container: The Maya fluid shape node to configure.
        sampling: Number of sample points along the opacity ramp (higher = smoother).
        curve_parameter: The 'l' parameter for the repart function controlling curve shape.
            Higher values create steeper transitions.

    Example:
        >>> import pymel.core as pm
        >>> fluid = pm.ls('fluidShape1')[0]
        >>> setup_repart_opacity_ramp(fluid, sampling=20, curve_parameter=15.0)

    Note:
        This function modifies the fluid's opacity attribute array directly.
        It sets position, value, and interpolation for each sample point.
    """
    step = int(100 / sampling)
    for i in [round(x * 0.01, 4) for x in range(0, 100 + 1, step)]:
        y = math_function.repart_function(i, l=curve_parameter)
        fluid_container.opacity[int(i * sampling)].opacity_Position.set(i)
        fluid_container.opacity[int(i * sampling)].opacity_FloatValue.set(y)
        fluid_container.opacity[int(i * sampling)].opacity_Interp.set(1)


def setup_manual_opacity_ramp(
    fluid_container: pm.PyNode,
    ramp_points: list[tuple[float, float, int]],
) -> None:
    """Configure fluid opacity using manually specified control points.

    This function provides fine-grained control over the opacity curve by
    allowing direct specification of position, value, and interpolation
    for each control point.

    Args:
        fluid_container: The Maya fluid shape node to configure.
        ramp_points: List of (position, value, interpolation) tuples where:
            - position: float in range [0.0, 1.0] - position along ramp
            - value: float in range [0.0, 1.0] - opacity at this position
            - interpolation: int - Maya interpolation type:
                0 = None, 1 = Linear, 2 = Smooth, 3 = Spline

    Example:
        >>> import pymel.core as pm
        >>> fluid = pm.ls('fluidShape1')[0]
        >>> points = [
        ...     (0.0, 0.0, 3),    # Start: transparent, spline interp
        ...     (0.25, 0.1, 3),   # Low opacity
        ...     (0.5, 0.5, 3),    # Mid opacity
        ...     (0.75, 0.1, 3),   # Low opacity
        ...     (1.0, 0.0, 3),    # End: transparent
        ... ]
        >>> setup_manual_opacity_ramp(fluid, points)

    Note:
        The index in the opacity array corresponds to the position value.
        For example, position 0.25 uses index 25 (when positions are percentages).
    """
    for index, (position, value, interpolation) in enumerate(ramp_points):
        fluid_container.opacity[index].opacity_Position.set(position)
        fluid_container.opacity[index].opacity_FloatValue.set(value)
        fluid_container.opacity[index].opacity_Interp.set(interpolation)


if __name__ == "__main__":
    raise SystemExit("This module must be imported within Maya.")
