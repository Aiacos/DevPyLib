"""Muscle jiggle weight setting utilities for cMuscle systems.

Provides functions to batch set jiggle weight values on cMuscle control
objects for dynamic muscle simulation.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def set_muscle_weight(selection=pm.ls('iControlMid*'), jiggle=0.2):
    for item in selection:
        if '_crossSection' not in item.name().encode('utf8'):
            if 'Constraint' not in item.name().encode('utf8'):
                item.jiggle.set(jiggle)


if __name__ == "__main__":
    set_muscle_weight()
