"""Muscle jiggle weight setting utilities for cMuscle systems.

Provides functions to batch set jiggle weight values on cMuscle control
objects for dynamic muscle simulation.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def set_muscle_weight(selection=pm.ls('iControlMid*'), jiggle=0.2):
    """Set jiggle weight values on cMuscle control objects.

    Batch sets the jiggle attribute on cMuscle control objects, excluding
    cross-section controls and constraint objects. Used to quickly configure
    dynamic muscle simulation parameters.

    Args:
        selection (list, optional): List of PyMEL nodes to process. Defaults to all 'iControlMid*' objects.
        jiggle (float, optional): Jiggle weight value to set (0.0-1.0). Defaults to 0.2.

    Returns:
        None
    """
    for item in selection:
        if '_crossSection' not in item.name().encode('utf8'):
            if 'Constraint' not in item.name().encode('utf8'):
                item.jiggle.set(jiggle)


if __name__ == "__main__":
    set_muscle_weight()
