__author__ = 'Lorenzo Argentieri'

from mayaLib.shaderLib.base.shader_base import Shader_base
from mayaLib.shaderLib.utils import config


class aiStandard_shaderBase(Shader_base):
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
        Shader_base.__init__(self, shader_name, shader_type=shader_type)
        self.shader = Shader_base.get_shader(self)
        self.shader.specularFresnel.set(True)

        # connect texture
        self.makeAiStandard(file_node_dict)

    def makeAiStandard(self, file_node):
        connect_diffuse = Shader_base.connect_color
        connect_backlighting = Shader_base.connect_luminance
        connect_specularColor = Shader_base.connect_color
        connect_specularWeight = Shader_base.connect_luminance
        connect_specularRoughness = Shader_base.connect_luminance
        connect_fresnel = Shader_base.connect_fresnel
        connect_normal = Shader_base.connect_normal

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
