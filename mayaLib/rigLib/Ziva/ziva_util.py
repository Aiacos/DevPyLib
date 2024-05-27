import pymel.core as pm
from mayaLib.rigLib.utils import deform, common


def mirror_geo(geo_list):
    geo_list = pm.ls(geo_list)
    
    mirror_geo_list = []
    for geo in geo_list:
        geo_name = str(geo.name()).replace('L_', 'R_') + '_mirror'
        duplicate_geo = pm.duplicate(geo, n=geo_name)[-1]
        pm.parent(duplicate_geo, w=True)
        mirror_geo_list.append(duplicate_geo)
        
    duplicate_grp = pm.group(mirror_geo_list)
    duplicate_grp.scaleX.set(-1)
    common.freezeTranform(duplicate_grp)
    common.deleteHistory(duplicate_grp)
    
    for geo in mirror_geo_list:
        mirror_geo_name = str(geo.name()).replace('_mirror', '')
        deform.blendShapeDeformer(mirror_geo_name, [geo], mirror_geo_name + '_tmp_BS')
        common.deleteHistory(mirror_geo_name)
        
    pm.delete(duplicate_grp)


#mirror_geo(geo_list=pm.ls(sl=True))