__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm


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
    pm.bakePartialHistory(obj, pre=True)  # prePostDeformers=True


def deleteConnection(objAttrList):
    objAttrList = pm.ls(objAttrList)
    for objAttr in objAttrList:
        mel.eval("CBdeleteConnection " + str(objAttr.name()) + ";")


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
        pm.setDrivenKeyframe(driven, currentDriver=driver, driverValue=driverV, value=drivenV, inTangentType=cvType,
                             outTangentType=cvType)

def delete_unknow_nodes():
    unknow_list = pm.ls(mel.eval('ls -type unknown -type unknownDag -type unknownTransform'))
    while len(unknow_list) > 0:
        for node in unknow_list:
            pm.lockNode(node, lock=False)
            pm.delete(node)
