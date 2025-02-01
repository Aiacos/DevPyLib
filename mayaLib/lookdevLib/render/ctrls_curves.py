"""Set Maya's render engine to hardware rendering.

This script sets Maya's render engine to hardware rendering (mayaHardware2) and
configures the render options to use anti-aliasing, holdout mode, and depth of
field. It also enables NURBS curves in the object type filter.

"""
import pymel.core as pm
import maya.mel as mel


def set_render_engine(engine='mayaHardware2'):
    """Set Maya's render engine.

    Args:
        engine (str): The render engine to use. Defaults to 'mayaHardware2'.

    """
    # Set render engine
    pm.setAttr("defaultRenderGlobals.currentRenderer", engine, type="string")

    # Set anti-aliasing
    pm.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
    pm.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
    pm.setAttr("hardwareRenderingGlobals.aasc ", 16)

    # Render options
    pm.setAttr("hardwareRenderingGlobals.holdOutMode", 1)
    pm.setAttr("hardwareRenderingGlobals.holdOutDetailMode", 2)

    # Update holdout mode
    mel.eval('updateHoldOutMode;')
    mel.eval('updateHoldOutMode;')

    # Print holdout attributes
    for attr in pm.listAttr("hardwareRenderingGlobals"):
        if 'holdOut' in attr:
            print(attr)

    # Set render mode
    pm.setAttr("hardwareRenderingGlobals.renderMode", 5)

    # Set depth of field
    pm.setAttr("hardwareRenderingGlobals.renderDepthOfField", 1)

    # Enable NURBS curves in object type filter
    mel.eval('objectTypeFilterOnCallback 0;')


if __name__ == '__main__':
    set_render_engine()