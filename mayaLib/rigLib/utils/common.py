__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya.mel as mel


def centerPivot(obj, targetPivot=None):
    if targetPivot is None:
        pm.xform(obj, cp=1)
    else:
        pivotTranslate = pm.xform(targetPivot, q=True, ws=True, rotatePivot=True)
        pm.xform(obj, ws=True, pivots=pivotTranslate)


def freezeTranform(obj):
    pm.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0)


def deleteHistory(obj):
    pm.delete(obj, ch=True)

def deleteNonDeformerHistory(obj):
    pm.bakePartialHistory(obj, pre=True) # prePostDeformers=True
