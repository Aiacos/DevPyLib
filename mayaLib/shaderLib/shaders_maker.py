"""Batch shader creation from texture directories.

Provides tools for automatically creating shaders from organized
texture file hierarchies with naming conventions.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.shaderLib import shader
from mayaLib.shaderLib.utils import file, texture_ext_path


class ShadersManager:
    """Automatic shader manager for workspace textures.

    Scans a texture directory for organized texture sets, creates appropriate shaders
    based on the active renderer, and optionally assigns them to corresponding geometry.
    Handles renderer-specific texture format conversion (TX for Arnold, TEX for RenderMan).

    Attributes:
        render_engine: Detected render engine (arnold, renderman, etc.)
        file_manager: TextureFileManager instance for texture discovery
        texture_dict: Dictionary of discovered texture hierarchies

    Example:
        >>> manager = ShadersManager(path='/project/sourceimages/', ext='exr')
        >>> # Automatically creates and assigns shaders for all texture sets
    """
    def __init__(self, path=str(pm.workspace(q=True, dir=True, rd=True) + 'sourceimages/'), ext='exr',
                 auto_assing_shader=True):
        """Initialize the ShadersManager class.

        Args:
            path (str): Directory path where textures are located. Defaults to the 'sourceimages' directory in the current workspace.
            ext (str): File extension for texture files. Defaults to 'exr'.
            auto_assing_shader (bool): Flag to automatically assign shaders to geometry. Defaults to True.

        Initializes and manages shaders for geometry based on texture files found in the specified directory.
        Detects the active renderer and creates appropriate shaders for each geometry and texture set.
        Assigns shaders to the corresponding geometry if autoAssignShader is True.
        Also handles texture file format conversion based on the active renderer.
        """
        # See active Renderer
        self.render_engine = pm.ls('defaultRenderGlobals')[0].currentRenderer.get()
        self.file_manager = file.TextureFileManager(dirname=path, ext=ext)
        self.texture_dict = self.file_manager.texture_dict

        # for all geo
        for geo_key in list(self.texture_dict.keys()):
            # check if is UDIM or, for all texture set
            for texture_set in list(self.texture_dict[geo_key].keys()):
                if texture_set == 'UDIM':
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    current_shader = shader.TextureShader(texture_path=self.file_manager.path,
                                                         geo_name=geo_key,
                                                         textureset_dict=textureset_dict)

                    if auto_assing_shader:
                        current_shader.get_shader().assign_shader(geo_key)

                    break
                else:
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    current_shader = shader.TextureShader(texture_path=self.file_manager.path,
                                                         geo_name=texture_set,
                                                         textureset_dict=textureset_dict)

                    if auto_assing_shader:
                        current_shader.get_shader().assign_shader(geo_key)

        # set tx or tex file format
        if self.render_engine == 'arnold':
            # for arnold should be default, conversion is done by Maya
            # texture_ext_path.replace_ext(ext='.tx')
            pass
        elif self.render_engine == 'renderman':
            texture_ext_path.replace_ext(ext='.tex', file_name_attribute='.filename', file_type='PxrTexture')


if __name__ == "__main__":
    shm = ShadersManager()
