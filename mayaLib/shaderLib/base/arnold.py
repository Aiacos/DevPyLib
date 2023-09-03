__author__ = 'Lorenzo Argentieri'

from mayaLib.shaderLib.base.shader_base import Shader_base
from mayaLib.shaderLib.utils import config


class aiStandardSurface(Shader_base):
    """
    Create aiStandardSurface
    """

    def __init__(self, shader_name, folder, shader_textures, shader_type='aiStandardSurface', standard=True, shading_engine=None):
        """
        Create aiStandardSurface
        :param shader_name: Geo or Texture set (String)
        :param folder: Texture forlder Path (String/Path)
        :param shader_textures: Texture List (List od String/Path)
        :param shader_type:
        """
        # init base class
        Shader_base.__init__(self, shader_name, folder, shader_textures, shader_type=shader_type,
                             shading_engine=shading_engine)
        self.shader = Shader_base.get_shader(self)

        self.folder = folder

        # init faceColor
        self.shader.baseColor.set((0.2, 0.5, 0.8))

        # connect texture
        if standard:
            self.connect_textures(shader_textures)


