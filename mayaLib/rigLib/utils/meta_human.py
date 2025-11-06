"""MetaHuman scene cleanup and skeleton reorganization utilities.

Provides tools for fixing imported MetaHuman rigs including skeleton hierarchy
reorganization, axis alignment, and removal of unnecessary groups and lights.
"""

import pymel.core as pm


def meta_human_scene_fix(
    root_grp_name="MetaHuman_rig_grp", delete_lights=True, delete_unused_grps=True
):
    """Fix and reorganize imported MetaHuman rig structure.

    Reorganizes the MetaHuman skeleton hierarchy, aligns axis orientation to
    Y-up, removes unnecessary groups and lights, and creates a clean rig structure.

    Args:
        root_grp_name: Name for the main rig group. Defaults to 'MetaHuman_rig_grp'.
        delete_lights: Remove lighting groups from scene. Defaults to True.
        delete_unused_grps: Remove unused export geometry groups. Defaults to True.

    Example:
        >>> meta_human_scene_fix('Character_rig_grp')
    """
    driver_skeleton_root = pm.ls("root_drv")[-1]
    head_skeleton_root = pm.ls("DHIhead:spine_04")[-1]
    body_skeleton_root = pm.ls("DHIbody:root")[-1]

    rig_grp = pm.ls("rig")[-1]
    head_rig_grp = pm.ls("headRig_grp")[-1]
    # driver_skeleton_root = pm.ls('')[-1]

    if delete_unused_grps:
        pm.delete("export_geo_GRP")
    if delete_lights:
        pm.delete("Lights")

    pm.upAxis(ax="y")

    driver_skeleton_root.jointOrientX.set(-90)
    head_rig_grp.rotateX.set(-90)

    pm.group(
        driver_skeleton_root, head_skeleton_root, body_skeleton_root, n="skeleton_grp", p=rig_grp
    )
    pm.rename(rig_grp, root_grp_name)


if __name__ == "__main__":
    meta_human_scene_fix()
