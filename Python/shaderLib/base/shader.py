__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from rigLib.utils import config


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


class Shader():
    def __init__(self, shader_name, shader_type='aiStandard'):
        # create a shader
        self.shader_name = shader_name
        self.shader = pm.shadingNode(shader_type, asShader=True, name=shader_name)

        # create a shading group
        self.shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.shader_name)
        # connect shader to sg surface shader
        pm.connectAttr(self.shader.outColor, self.shading_group.surfaceShader)

    def get_shader(self):
        return self.shader

    def assign_shader(self, geo):
        """
        Assign Shader to selected objects
        :param geo: geometry list (list)
        :return:
        """
        pm.select(geo)
        pm.hyperShade(assign=self.shader)

    def connect_texture(self, file_node, slot_name):
        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name))


    def connect_fresnel(self, file_node, slot_name):
        file_node.alphaIsLuminance.set(True)
        pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, slot_name))

    def connect_normal(self, file_node, slot_name):
        # create bump_node
        self.bump_node = pm.shadingNode("bump2d", asUtility=True)
        self.bump_node.bumpInterp.set(1)
        self.bump_node.aiFlipR.set(0)
        self.bump_node.aiFlipG.set(0)

        # connect file_node to bump_node
        file_node.alphaIsLuminance.set(True)
        pm.connectAttr(file_node.outAlpha,  self.bump_node.bumpValue)

        # connect bump_node to shader
        pm.connectAttr(self.bump_node.outNormal, '%s.%s' % (self.shader, slot_name))



class aiStandard_shader(Shader):
    def __init__(self, shader_name, file_node, shader_type='aiStandard'):
        # init base class
        Shader.__init__(self, shader_name, shader_type=shader_type)
        self.shader = Shader.get_shader(self)
        self.shader.specularFresnel.set(True)

        # connect texture
        self.makeAiStandard(file_node)

    def makeAiStandard(self, file_node):
        connect_diffuse = Shader.connect_texture
        connect_backlighting = Shader.connect_texture
        connect_specularColor = Shader.connect_texture
        connect_specularWeight = Shader.connect_texture
        connect_specularRoughness = Shader.connect_texture
        connect_fresnel = Shader.connect_fresnel
        connect_normal = Shader.connect_normal

        try:
            connect_diffuse(self, file_node[config.diffuse], slot_name='color')
        except:
            pass
        try:
            connect_backlighting(self, file_node[config.backlight], slot_name='Kb')
        except:
            pass
        try:
            connect_specularColor(self, file_node[config.specularColor], slot_name='KsColor')
        except:
            pass
        try:
            connect_specularWeight(self, file_node[config.specularWeight], slot_name='Ks')
        except:
            self.shader.Ks.set(0.8)
        try:
            connect_specularRoughness(self, file_node[config.specularRoughness], slot_name='specularRoughness')
        except:
            pass
        try:
            connect_fresnel(self, file_node[config.fresnel], slot_name='Ksn')
        except:
            self.shader.Ksn.set(0.04)
        try:
            connect_normal(self, file_node[config.normal], slot_name='normalCamera')
        except:
            pass



if __name__ == "__main__":

    mfile_node = pm.shadingNode("file", name='test', asTexture=True, isColorManaged=True)
    mfile_node.colorSpace.set('Raw')
    # pm.setAttr(file_node + '.fileTextureName', '_path', type='string')
    mfile_node.fileTextureName.set('gooool')
    tex = {'Normal': mfile_node}

    sh = aiStandard_shader(shader_name='testShader', file_node=tex)
