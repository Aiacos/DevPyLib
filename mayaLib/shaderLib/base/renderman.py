__author__ = 'Lorenzo Argentieri'

from pymel import core as pm
from mayaLib.shaderLib.base.shader_base import Shader_base
from mayaLib.shaderLib.utils import config


class PxrSurface_shaderBase(Shader_base):
    """
    Create PxrSurface shader
    """

    def __init__(self, shader_name, file_node_dict, shader_type='PxrSurface', physicalSpecular=True):
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
        if physicalSpecular:
            self.shader.specularFresnelMode.set(1)
        else:
            self.shader.specularFresnelMode.set(0)
        # init faceColor
        self.shader.specularEdgeColor.set((1.0, 1.0, 1.0))
        # connect texture
        self.makePxrSurface(file_node_dict, physicalSpecular)

    def makePxrSurface(self, pxrtexture_node, physicalSpecular):
        connect_diffuse = self.connect_color_pxrtexture

        if physicalSpecular:
            connect_specularFaceColor = self.connect_physical_specular
        else:
            connect_specularFaceColor = self.connect_artistic_specular

        connect_specularRoughness = self.connect_luminance_pxrtexture
        connect_normal = self.connect_pxrnormal
        connect_emission = self.connect_color_pxrtexture

        try:
            connect_diffuse(pxrtexture_node[config.diffuse], slot_name='diffuseColor')
        except:
            pass
        try:
            if physicalSpecular:
                connect_specularFaceColor(pxrtexture_node[config.specularColor], pxrtexture_node[config.metallic], slot_name='specularExtinctionCoeff')
            else:
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

        #self.pxrnormalmap_node.invertBump.set(directx_normal) # OLD

        if directx_normal:
            self.pxrnormalmap_node.orientation.set(1)
        else:
            self.pxrnormalmap_node.orientation.set(0)

        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrnormalmap_node.inputRGB)

        if not adjustNormal:
            pm.connectAttr(self.pxrnormalmap_node.resultN, '%s.%s' % (self.shader, slot_name))
        else:
            self.pxradjustnormal_node = pm.shadingNode("PxrAdjustNormal", asTexture=True)
            pm.connectAttr(self.pxrnormalmap_node.resultN, self.pxradjustnormal_node.inputNormal)
            pm.connectAttr(self.pxradjustnormal_node.resultN, '%s.%s' % (self.shader, slot_name))

    def connect_physical_specular(self, pxrtexture_node, pxrtexture_metallic_node, slot_name):
        # blend
        self.pxrblend = pm.shadingNode("PxrBlend", asTexture=True)
        self.pxrblend.operation.set(18)# 18 multiply

        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrblend.topRGB)
        pm.connectAttr(pxrtexture_metallic_node.resultRGB, self.pxrblend.bottomRGB)

        pm.connectAttr(self.pxrblend.resultRGB, '%s.%s' % (self.shader, slot_name))

    def connect_artistic_specular(self, pxrtexture_node, pxrtexture_metallic_node, slot_name):
        # blend
        self.pxrblend = pm.shadingNode("PxrBlend", asTexture=True)
        self.pxrblend.operation.set(19)# 19 normal

        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrblend.topRGB)
        pm.connectAttr(pxrtexture_metallic_node.resultR, self.pxrblend.topA)
        pm.setAttr(self.pxrblend.bottomRGB, 0.039, 0.039, 0.039, type="double3")

        pm.connectAttr(self.pxrblend.resultRGB, '%s.%s' % (self.shader, slot_name))
