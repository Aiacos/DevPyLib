__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.shaderLib import shader
from mayaLib.shaderLib.utils import file
from mayaLib.shaderLib.utils import texture_ext_path


class ShadersManager():
    def __init__(self, path=str(pm.workspace(q=True, dir=True, rd=True) + 'sourceimages/'), ext='exr',
                 autoAssingShader=True):
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
                    currentShader = shader.TextureShader(texture_path=self.file_manager.path,
                                                         geo_name=geo_key,
                                                         textureset_dict=textureset_dict)

                    if autoAssingShader:
                        currentShader.getShader().assign_shader(geo_key)

                    break
                else:
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    currentShader = shader.TextureShader(texture_path=self.file_manager.path,
                                                         geo_name=texture_set,
                                                         textureset_dict=textureset_dict)

                    if autoAssingShader:
                        currentShader.getShader().assign_shader(geo_key)

        # set tx or tex file format
        if self.render_engine == 'arnold':
            # for arnold should be default, conversion is done by Maya
            # texture_ext_path.replace_ext(ext='.tx')
            pass
        elif self.render_engine == 'renderman':
            texture_ext_path.replace_ext(ext='.tex', file_name_attribute='.filename', file_type='PxrTexture')


if __name__ == "__main__":
    shm = ShadersManager()
