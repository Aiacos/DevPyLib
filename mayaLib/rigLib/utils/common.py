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

def disconnect(objAttr):
    if(False):
        myattr = mycube.translateX

        # get and set values
        myattr.get()
        myattr.set(4)

        # break connections
        myattr.disconnect(mysphere.translateY)

    # disconnect all outputs
    myattr.disconnect(outputs=True)

def setDrivenKey(driver, driverValueList, driven, drivenValueList, cvType='linear'):
    """
    Set Driven Key utility
    :param driver: str, driver + driving attribute (ctrl.attr)
    :param driverValueList: list, value list
    :param driven: str, driven + driven attribute (ctrl.attr)
    :param drivenValueList: list, value list
    :param cvType: str, auto, clamped, fast, flat, linear, plateau, slow, spline, step, and stepnext
    :return:
    """
    for driverV, drivenV in zip(driverValueList, drivenValueList):
        pm.setDrivenKeyframe(driven, currentDriver=driver, driverValue=driverV, value=drivenV, inTangentType=cvType, outTangentType=cvType)
