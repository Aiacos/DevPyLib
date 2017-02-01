import pymel.core as pm

selection = pm.ls(sl=True)

print selection[0].colorSpace.set('sRGB')
print pm.listAttr( selection[0].name() )
print selection[0].uvTilingMode.set(3)
#setAttr "file1.uvTilingMode" 3;

print pm.shadingNode('place2dTexture',asUtility=True)