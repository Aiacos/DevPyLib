import pymel.core as pm


def build_lambert(shaderType='lambert', shaderName='tmp-shader', color=(0.5,0.5,0.5), transparency=(0.0,0.0,0.0)):
    # create a shader
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.color.set(color)
    shader.transparency.set(transparency)

    return shader


if __name__ == "__main__":
    print build_lambert()
