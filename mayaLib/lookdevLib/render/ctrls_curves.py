import pymel.core as pm
import maya.mel as mel


def set_render_engine(engine='mayaHardware2'):
    pm.setAttr("defaultRenderGlobals.currentRenderer", engine, type="string")
    
    # set Anti-Aliasing
    pm.setAttr("hardwareRenderingGlobals.lineAAEnable", 1)
    pm.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
    pm.setAttr("hardwareRenderingGlobals.aasc ", 16)
    
    # Render Options
    pm.setAttr("hardwareRenderingGlobals.holdOutMode", 1)
    pm.setAttr("hardwareRenderingGlobals.holdOutDetailMode", 2)
    mel.eval('updateHoldOutMode;')
    mel.eval('updateHoldOutMode;')
    for attr in pm.listAttr("hardwareRenderingGlobals"):
        if 'holdOut' in attr:
            print(attr)
    
    pm.setAttr("hardwareRenderingGlobals.renderMode", 5)
    pm.setAttr("hardwareRenderingGlobals.renderDepthOfField", 1)
    
    # Object Type Filter - Enable NURBS Curves
    mel.eval('objectTypeFilterOnCallback 0;')
    
set_render_engine()