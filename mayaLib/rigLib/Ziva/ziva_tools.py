import maya.mel as mel
import pymel.core as pm
import zBuilder.builders.ziva as zva
import zBuilder.zMaya as zMaya


def addTissue(obj):
    pm.select(obj)
    mel.eval('ziva -t;')

def addBone(obj):
    pm.select(obj)
    mel.eval('ziva -b;')

def addCloth(obj):
    pm.select(obj)
    mel.eval('ziva -c;')

# Rename
def zivaRenameAll():
    zMaya.rename_ziva_nodes()

def harmonic_transfer(source, destination, transfer_geos, tet_size=1):
    pm.select(source)
    pm.select(destination, add=True)
    pm.hide(source, destination)
    pm.select(transfer_geos, tgl=True)

    zArmonicWrap = pm.ls(mel.eval('zHarmonicWarp;'))[0]
    zArmonicWrap.maxResolution.set(512)
    zArmonicWrap.tetSize.set(tet_size)

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
