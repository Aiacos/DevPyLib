__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from shaderLib.utils import config
from shaderLib.base import texture


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
    """
    Create general Shader
    """

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

    def connect_color_texture(self, file_node, slot_name):
        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name))

    def connect_luminance_texture(self, file_node, slot_name):
        file_node.alphaIsLuminance.set(True)
        pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, slot_name))

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
        pm.connectAttr(file_node.outAlpha, self.bump_node.bumpValue)

        # connect bump_node to shader
        pm.connectAttr(self.bump_node.outNormal, '%s.%s' % (self.shader, slot_name))


class aiStandard_shader(Shader):
    """
    Create aiStandard shader
    """

    def __init__(self, shader_name, file_node_dict, shader_type='aiStandard'):
        """
        Create aiStandard shader
        :param shader_name: Geo or Texture set (String)
        :param file_node_dict: file node (instance)
        :param shader_type:
        """
        # init base class
        Shader.__init__(self, shader_name, shader_type=shader_type)
        self.shader = Shader.get_shader(self)
        self.shader.specularFresnel.set(True)

        # connect texture
        self.makeAiStandard(file_node_dict)

    def makeAiStandard(self, file_node):
        connect_diffuse = Shader.connect_color_texture
        connect_backlighting = Shader.connect_luminance_texture
        connect_specularColor = Shader.connect_color_texture
        connect_specularWeight = Shader.connect_luminance_texture
        connect_specularRoughness = Shader.connect_luminance_texture
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


class TextureShader():
    def __init__(self, texture_path, geo_name, textureset_dict, single_place_node=True):
        """
        Create Shader and Connect it with all associated texture
        :param texture_path: path to textures
        :param geo_name: Geometry name
        :param textureset_dict: material IDs used in Substance Painter or UDIM
        :param single_place_node: (bool)
        """
        self.filenode_dict = {}

        if single_place_node:
            self.place_node = pm.shadingNode('place2dTexture', asUtility=True)
        else:
            self.place_node = None

        for texture_channel in textureset_dict:
            fn = texture.TextureFileNode(path=texture_path,
                                         filename=textureset_dict[texture_channel],
                                         single_place_node=self.place_node)
            self.filenode_dict[texture_channel] = fn.filenode

        aiStandard_shader(shader_name=geo_name, file_node_dict=self.filenode_dict)


if __name__ == "__main__":
    path = '/Users/lorenzoargentieri/Desktop/testTexture'
    tx = texture.TextureFileManager(dirname=path)
    texdict = tx.texture_dict['Skull']
    shaderdict = texdict['Skull']
    ts = TextureShader(texture_path=path, geo_name='Skull', textureset_dict=shaderdict)
