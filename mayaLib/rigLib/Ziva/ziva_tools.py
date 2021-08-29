import pymel.core as pm
import zBuilder.builders.ziva as zva
import zBuilder.zMaya as zMaya


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
