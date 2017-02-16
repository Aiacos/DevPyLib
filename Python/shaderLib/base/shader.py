__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def build_lambert(shaderType='lambert', shaderName='tmp-shader', color=(0.5, 0.5, 0.5), transparency=(0.0, 0.0, 0.0)):
    """
    Build basic lambert Shader
    :param shaderType: type (string)
    :param shaderName: name (string)
    :param color: es. (0.5,0.5,0.5)
    :param transparency: es. (0.5,0.5,0.5)
    :return: shader node
    """
    # create a shader
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.color.set(color)
    shader.transparency.set(transparency)

    return shader


def build_surfaceshader(shaderType='surfaceShader', shaderName='tmp-shader', color=(0.5, 0.5, 0.5)):
    """
    Build basic surfaceShader
    :param shaderType: type (string)
    :param shaderName: name (string)
    :param color: es. (0.5,0.5,0.5)
    :return: shader node
    """
    # create a shader
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.outColor.set(color)

    return shader


def assign_shader(geo, shader):
    """
    Assign Shader to selected objects
    :param geo: geometry list (list)
    :param shader: shader name (string)
    :return:
    """
    pm.select(geo)
    pm.hyperShade(assign=shader)


if __name__ == "__main__":
    print build_lambert()
