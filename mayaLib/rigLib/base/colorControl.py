__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def color_control(controls=pm.ls('*_CTRL', type='nurbsCurve')):
    """
    Color all selected control based on their prefix (L_ , R_)
    :param controls:
    :return:

    Usage: color_control(controls=pm.listRelatives('controlShapes_GRP', c=True))
    """
    for ctrlObject in controls:
        name = str(ctrlObject.name())
        ctrlObject.getShape().ove.set(0)
        ctrlObject.ove.set(1)

        print(ctrlObject.overrideColor.get())

        if 'L_' in name:
            ctrlObject.overrideColor.set(6)
        elif 'R_' in name:
            ctrlObject.overrideColor.set(13)
        else:
            ctrlObject.overrideColor.set(22)


if __name__ == "__main__":
    color_control()
