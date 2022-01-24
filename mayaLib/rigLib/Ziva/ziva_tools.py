import maya.mel as mel
import pymel.core as pm
import zBuilder.builders.ziva as zva
import zBuilder.zMaya as zMaya
import zBuilder.utils as utils


def zPolyCombine(geos):
    pm.select(pm.ls(geos))
    zPolyCombine_node, zPolyCombine_mesh = pm.ls(mel.eval('zPolyCombine;'))

    return zPolyCombine_mesh

def harmonic_warp(source, destination, transfer_geos, tet_size=1):
    source_string = str(pm.ls(source)[-1].name())
    destination_string = str(pm.ls(destination)[-1].name())
    transfer_list = []
    for geo in pm.ls(transfer_geos):
        name = str(geo.name())
        transfer_list.append(name)
    transfer_string = ' '.join(transfer_list)

    zArmonicWarp = pm.ls(mel.eval('zHarmonicWarp ' + source_string + ' ' + destination_string + ' ' + transfer_string + ';'))[0]
    zArmonicWarp.maxResolution.set(512)
    zArmonicWarp.tetSize.set(tet_size)

def bone_warp(source, destination, transfer_geos, tet_size=1):
    source_string = str(pm.ls(source)[-1].name())
    destination_string = str(pm.ls(destination)[-1].name())
    transfer_list = []
    for geo in pm.ls(transfer_geos):
        name = str(geo.name())
        transfer_list.append(name)
    transfer_string = ' '.join(transfer_list)

    zBoneWarp = pm.ls(mel.eval('zBoneWarp ' + source_string + ' ' + destination_string + ' ' + transfer_string + ';'))[0]
    zBoneWarp.maxResolution.set(512)
    zBoneWarp.tetSize.set(tet_size)


def ziva_check_intersection(geo1, geo2):
    pm.select(geo1, geo2)
    mel.eval('ZivaSelectIntersections;')

    return pm.ls(sl=True)

# Rename
def zivaRenameAll():
    zMaya.rename_ziva_nodes()

# Mirror
def zivaMirror(from_side='L_', to_side='R_', suffix='_GEO'):
    pm.select(pm.ls(from_side + '*' + suffix))
    zObj = zva.Ziva()

    if pm.ls(sl=True):
        zObj.retrieve_from_scene_selection()
    else:
        zObj.retrieve_from_scene()

    zObj.string_replace('^' + from_side, to_side)
    zObj.build()


if __name__ == "__main__":
    zivaRenameAll()
    zivaMirror('R_', 'L_')
