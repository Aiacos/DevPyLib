__author__ = 'Lorenzo Argentieri'

from pymel import core as pm
from mayaLib.shaderLib.base.shader_base import Shader_base
from mayaLib.shaderLib.utils import config


class PxrSurface_shaderBase(Shader_base):
    """
    Create PxrSurface shader
    """

    def __init__(self, shader_name, file_node_dict, shader_type='PxrSurface', use_pxrtexture=True):
        """
        Create PxrSurface shader
        :param shader_name: Geo or Texture set (String)
        :param pxrtexture_node: file node (instance)
        :param shader_type:
        """
        # init base class
        Shader_base.__init__(self, shader_name, shader_type=shader_type)
        self.shader = Shader_base.get_shader(self)

        # init Specular model type
        self.shader.specularModelType.set(1)
        # init faceColor
        self.shader.specularEdgeColor.set((1.0, 1.0, 1.0))
        # connect texture
        self.makePxrSurface(file_node_dict, use_pxrtexture)

    def makePxrSurface(self, pxrtexture_node, use_pxrtexture):
        if use_pxrtexture:
            connect_diffuse = self.connect_color_pxrtexture
            connect_specularFaceColor = self.connect_facecolor_pxrblend
            connect_specularRoughness = self.connect_luminance_pxrtexture
            connect_normal = self.connect_pxrnormal
            connect_emission = self.connect_color_pxrtexture
        else:
            connect_diffuse = self.connect_color_texture
            connect_specularFaceColor = self.connect_facecolor_multiplydivide
            connect_specularRoughness = self.connect_luminance_texture
            connect_normal = self.connect_normal
            connect_emission = self.connect_color_texture

        try:
            connect_diffuse(pxrtexture_node[config.diffuse], slot_name='diffuseColor')
        except:
            pass
        try:
            connect_specularFaceColor(pxrtexture_node[config.specularColor], pxrtexture_node[config.metallic], slot_name='specularFaceColor')
        except:
            pass
        try:
            connect_specularRoughness(pxrtexture_node[config.specularRoughness], slot_name='specularRoughness')
        except:
            pass
        try:
            connect_normal(pxrtexture_node[config.normal], slot_name='bumpNormal')
        except:
            pass
        try:
            connect_emission(pxrtexture_node[config.emission], slot_name='glowColor')
            # ToDo: rgb to luminance in gain
        except:
            pass

    def connect_color_pxrtexture(self, pxrtexture_node, slot_name):
        pm.connectAttr(pxrtexture_node.resultRGB, '%s.%s' % (self.shader, slot_name))

    def connect_luminance_pxrtexture(self, pxrtexture_node, slot_name):
        pm.connectAttr(pxrtexture_node.resultA, '%s.%s' % (self.shader, slot_name))

    def connect_pxrnormal(self, pxrtexture_node, slot_name, directx_normal=True, adjustNormal=True):
        self.pxrnormalmap_node = pm.shadingNode("PxrNormalMap", asTexture=True)
        self.pxrnormalmap_node.invertBump.set(directx_normal)
        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrnormalmap_node.inputRGB)

        if not adjustNormal:
            pm.connectAttr(self.pxrnormalmap_node.resultN, '%s.%s' % (self.shader, slot_name))
        else:
            self.pxradjustnormal_node = pm.shadingNode("PxrAdjustNormal", asTexture=True)
            pm.connectAttr(self.pxrnormalmap_node.resultN, self.pxradjustnormal_node.inputNormal)
            pm.connectAttr(self.pxradjustnormal_node.resultN, '%s.%s' % (self.shader, slot_name))


    def connect_facecolor_multiplydivide(self, pxrtexture_node, pxrtexture_metallic_node, slot_name):
        # multiplyDivide
        self.multiplydivide = pm.shadingNode("multiplyDivide", asUtility=True)

        pm.connectAttr(pxrtexture_node.outColor, self.multiplydivide.input1)
        pm.connectAttr(pxrtexture_metallic_node.outColor, self.multiplydivide.input2)

        pm.connectAttr(self.multiplydivide.output, '%s.%s' % (self.shader, slot_name))

    def connect_facecolor_pxrblend(self, pxrtexture_node, pxrtexture_metallic_node, slot_name):
        # blend
        self.pxrblend = pm.shadingNode("PxrBlend", asTexture=True)
        self.pxrblend.operation.set(18)

        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrblend.topRGB)
        pm.connectAttr(pxrtexture_metallic_node.resultRGB, self.pxrblend.bottomRGB)

        pm.connectAttr(self.pxrblend.resultRGB, '%s.%s' % (self.shader, slot_name))