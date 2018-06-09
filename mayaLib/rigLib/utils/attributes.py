__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def addVectorAttribute(object, name, defaultValue=[0, 0, 0]):
    attributeList = pm.ls(object + '.' + name)
    if len(attributeList) == 0:
        pm.addAttr(object, longName=name, attributeType='double3')
        pm.addAttr(object, longName=name + 'X', attributeType='double', parent=name, dv=defaultValue[0])
        pm.addAttr(object, longName=name + 'Y', attributeType='double', parent=name, dv=defaultValue[1])
        pm.addAttr(object, longName=name + 'Z', attributeType='double', parent=name, dv=defaultValue[2])
    else:
        pm.setAttr(object + '.' + name + 'X', defaultValue[0])
        pm.setAttr(object + '.' + name + 'Y', defaultValue[1])
        pm.setAttr(object + '.' + name + 'Z', defaultValue[2])

    attribute = pm.Attribute(object + '.' + name)
    return attribute

def addFloatAttribute(object, name, defaultValue=0, keyable=False, minValue=None, maxValue=None):
    attributeList = pm.ls(object + '.' + name)
    if len(attributeList) == 0:
        if minValue and maxValue:
            pm.addAttr(object, longName=name, attributeType='float', k=keyable, dv=defaultValue, min=minValue, max=maxValue)
        else:
            pm.addAttr(object, longName=name, attributeType='float', k=keyable, dv=defaultValue)
    else:
        pm.setAttr(object + '.' + name, defaultValue)

    attribute = pm.Attribute(object + '.' + name)
    return attribute
