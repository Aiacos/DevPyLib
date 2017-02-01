import pymel.core as pm

controls = pm.ls('*_ctrl*', type='nurbsCurve')
print controls

for ctrlObject in controls:
    print ctrlObject
    name = ctrlObject.name().encode('utf8')
    ctrlShape = pm.listRelatives(name, s=1)
    pm.setAttr(name + '.ove', 1)
    if name.startswith('L_'):
        pm.setAttr(name + '.ovc', 6)
    elif name.startswith('R_'):
        pm.setAttr(name + '.ovc', 13)
    else:
        pm.setAttr(name + '.ovc', 22)