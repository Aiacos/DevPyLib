import pymel.core as pm


def metaHuman_scene_fix(root_grp_name='MetaHuman_rig_grp'):
    driver_skeleton_root = pm.ls('root_drv')[-1]
    head_skeleton_root = pm.ls('DHIhead:spine_04')[-1]
    body_skeleton_root = pm.ls('DHIbody:root')[-1]

    rig_grp = pm.ls('rig')[-1]
    headRig_grp = pm.ls('headRig_grp')[-1]
    # driver_skeleton_root = pm.ls('')[-1]

    # pm.delete('export_geo_GRP', 'Lights')

    pm.upAxis(ax='y')

    driver_skeleton_root.jointOrientX.set(-90)
    headRig_grp.rotateX.set(-90)


if __name__ == "__main__":
    metaHuman_scene_fix()