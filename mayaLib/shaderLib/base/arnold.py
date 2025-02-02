__author__ = 'Lorenzo Argentieri'

from mayaLib.shaderLib.base.shader_base import Shader_base


class aiStandardSurface(Shader_base):
    """
    Class for creating an aiStandardSurface shader.
    """

    def __init__(self, shader_name, folder, shader_textures, shader_type='aiStandardSurface', standard=True, shading_engine=None):
        """
        Initializes an aiStandardSurface shader.

        Args:
            shader_name (str): Name of the geometry or texture set.
            folder (str or Path): Path to the texture folder.
            shader_textures (list of str or Path): List of texture paths.
            shader_type (str): Type of the shader. Default is 'aiStandardSurface'.
            standard (bool): Flag to determine texture connection method. Default is True.
            shading_engine: Shading engine to use. Default is None.
        """
        # Initialize the base class
        Shader_base.__init__(self, shader_name, folder, shader_textures, shader_type=shader_type, shading_engine=shading_engine)
        self.shader = Shader_base.get_shader(self)

        self.folder = folder

        # Initialize base color
        self.shader.baseColor.set((0.2, 0.5, 0.8))

        # Connect textures if standard flag is set
        if standard:
            self.connect_textures(shader_textures)