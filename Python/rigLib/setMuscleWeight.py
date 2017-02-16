__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def setMuscleWeight(selection=pm.ls('iControlMid*'), jiggle=0.2):
    for item in selection:
        if '_crossSection' not in item.name().encode('utf8'):
            if 'Constraint' not in item.name().encode('utf8'):
                item.jiggle.set(jiggle)


if __name__ == "__main__":
    setMuscleWeight()
