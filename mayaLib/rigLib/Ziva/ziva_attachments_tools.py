import maya.mel as mel
import pymel.core as pm


def getAllObjectUnderGroup(group, type='mesh'):
    """
    Return all object of given type under group
    :param group: str, group name
    :param type: str, object type
    :return: object list
    """
    objList = None

    if type == 'mesh':
        objList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type=type)]

    if type == 'transform':
        geoList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type='mesh')]
        objList = [o for o in pm.listRelatives(group, ad=1, type=type) if o not in geoList]

    objList = list(set(objList))
    objList.sort()

    return objList


def zivaFixedAttachment(stiffness=8):
    zAttachment = pm.ls(mel.eval('ziva -a;'))[0]
    zAttachment.stiffnessExp.set(stiffness)

    return zAttachment


def zivaSlidingAttachment(stiffness=8):
    zAttachment = pm.ls(mel.eval('ziva -a;'))[0]
    zAttachment.attachmentMode.set(2)
    zAttachment.stiffnessExp.set(stiffness)

    return zAttachment


def paintProximity(zAttachement, min=0.0001, max=1):
    pm.select(zAttachement)
    mel.eval('zPaintAttachmentsByProximity -min ' + str(min) + ' -max ' + str(max) + ';')


def addAttachment(source, dest, value, fixed=True):
    pm.select(source)
    pm.select(dest, add=True)

    if fixed:
        current_zAttachemnt = zivaFixedAttachment()
    else:
        current_zAttachemnt = zivaSlidingAttachment(6)

    paintProximity(current_zAttachemnt, 0.0001, value)


if __name__ == "__main__":
    source, dest = pm.ls(sl=True)
    addAttachment(source, dest, 0.5, fixed=False)
