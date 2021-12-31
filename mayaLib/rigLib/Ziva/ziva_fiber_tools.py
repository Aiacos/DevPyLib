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


def addZivaFiber(obj):
    pm.select(obj)
    zFiber = pm.ls(mel.eval('ziva -f;'))[0]
    return zFiber


def createLoACurve(obj):
    obj = pm.ls(obj)[-1]
    pm.select(obj)
    curve = pm.ls(mel.eval('zLineOfActionUtil;'))[0].getParent()

    cv_name = str(obj.name()).replace('_GEO', '_CV')
    pm.rename(curve, cv_name)

    return curve


def rivetCurve(curve, skeleton):
    rivet_list = []
    for cv, n in zip(curve.cv[:], list(range(0, len(pm.ls(curve.cv[:])) + 1))):
        pm.select(cv)
        pm.select(skeleton, add=True)
        zRivet = pm.ls(mel.eval('zRivetToBone;'))[-1]

        rivet_name = str(curve.name()).replace('_CV', '') + '_' + str(n)
        pm.rename(zRivet, rivet_name)

        rivet_list.append(zRivet)

    return rivet_list


def addLoA(curve, obj):
    pm.select(curve)
    pm.select(obj, add=True)

    zLineOfAction = pm.ls(mel.eval('ziva -loa;'))[-1]
    return zLineOfAction


def createLineOfAction(obj, skeleton):
    zFiber = addZivaFiber(obj)
    curve = createLoACurve(obj)
    rivets = rivetCurve(curve, skeleton)
    zLineOfAction = addLoA(curve, obj)

    if pm.objExists('loa_grp'):
        pass
    else:
        pm.group(n='loa_grp', em=True, p='Muscle_rig_grp')
        pm.group(n='curve_grp', em=True, p='loa_grp')
        pm.group(n='rivet_grp', em=True, p='loa_grp')

    pm.parent(curve, 'curve_grp')
    pm.parent(rivets, 'rivet_grp')


if __name__ == "__main__":
    for geo in getAllObjectUnderGroup('muscles_grp'):
        createLineOfAction(geo, 'C_charBison_skeleton_GEO')
