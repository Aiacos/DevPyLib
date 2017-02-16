__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def color_control(controls=pm.ls('*_ctrl*', type='nurbsCurve')):
    """
    Color all selected control based on theis prefix (L_ , R_)
    :param controls:
    :return:

    Usage: color_control(controls=pm.ls('*_ctrl*', type='nurbsCurve'))
    """
    for ctrlObject in controls:
        name = ctrlObject.name().encode('utf8')
        pm.setAttr(name + '.ove', 1)
        if name.startswith('L_'):
            pm.setAttr(name + '.ovc', 6)
        elif name.startswith('R_'):
            pm.setAttr(name + '.ovc', 13)
        else:
            pm.setAttr(name + '.ovc', 22)


if __name__ == "__main__":
    color_control()
