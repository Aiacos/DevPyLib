"""Utility to apply override colours based on control prefixes."""

from __future__ import annotations

import pymel.core as pm


def color_control(controls=None):
    """Colour controls based on naming convention.

    Args:
        controls: Iterable of control transforms to colour. Defaults to all `*_CTRL`.
    """
    if controls is None:
        controls = pm.ls("*_CTRL", type="nurbsCurve")
    for ctrl_object in controls:
        name = str(ctrl_object.name())
        ctrl_object.getShape().ove.set(0)
        ctrl_object.ove.set(1)

        if "L_" in name:
            ctrl_object.overrideColor.set(6)
        elif "R_" in name:
            ctrl_object.overrideColor.set(13)
        else:
            ctrl_object.overrideColor.set(22)


if __name__ == "__main__":
    raise SystemExit("Run inside Maya to colour controls.")
