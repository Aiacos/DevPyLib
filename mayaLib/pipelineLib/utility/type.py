__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def getAllGroups():
    geoList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(type='mesh')]
    grpList = [o for o in pm.listRelatives(type='transform') if o not in geoList]
    return  grpList

def getAllLocators():
    locList = [l.getParent() for l in pm.ls(type='locator')]
    return locList

def getAllMesh():
    meshList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(type='mesh')]
    return meshList

def getAllCurves():
    curveList = [cv.getParent() for cv in pm.ls(type='nurbsCurve')]
    return curveList

def getAllJoints():
    jntList = pm.ls(type='joint')
    return jntList

def getAllIKHandles():
    ikhList = pm.ls(type='ikHandle')
    return ikhList

def getAllLights():
    lgtList = pm.ls(lights=True)
    return lgtList

def getAllMaterials():
    matList = pm.ls(materials=True)
    return matList

def getAllTextures():
    texList = pm.ls(textures=True)
    return texList
