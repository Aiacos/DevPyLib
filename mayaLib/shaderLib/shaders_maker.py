__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.shaderLib.utils import file
from mayaLib.shaderLib.utils import texture_ext_path
from mayaLib.shaderLib import shader


class ShadersManager():
    def __init__(self, path=str(pm.workspace(q=True, dir=True, rd=True) + 'sourceimages/')):
        # See active Renderer
        self.render_engine = pm.getAttr('defaultRenderGlobals.currentRenderer')
        self.file_manager = file.TextureFileManager(dirname=path)
        self.texture_dict = self.file_manager.texture_dict

        # for all geo
        for geo_key in self.texture_dict.keys():

            # check if is UDIM or, for all texture set
            for texture_set in self.texture_dict[geo_key].keys():
                if texture_set == 'UDIM':
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    shader.TextureShader(texture_path=self.file_manager.path,
                                              geo_name=geo_key,
                                              textureset_dict=textureset_dict)
                    break
                else:
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    shader.TextureShader(texture_path=self.file_manager.path,
                                              geo_name=texture_set,
                                              textureset_dict=textureset_dict)

        # set tx or tex file format
        if self.render_engine == 'arnold':
            # for arnold should be default, conversion is done by Maya
            #texture_ext_path.replace_ext(ext='.tx')
            pass
        elif self.render_engine == 'renderManRIS':
            texture_ext_path.replace_ext(ext='.tex', file_name_attribute='.filename', file_type='PxrTexture')


if __name__ == "__main__":
    print 'ok'
    shm = ShadersManager()
