__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from shaderLib.base import texture
from shaderLib.base import shader


class ShadersManager():
    def __init__(self, path):
        self.file_manager = texture.TextureFileManager(dirname=path)
        self.texture_dict = self.file_manager.texture_dict

        # for all geo
        for geo_key in self.texture_dict.keys():

            # check if is UDIM or, for all texture set
            for texture_set in self.texture_dict[geo_key].keys():
                if texture_set.isdigit():
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    shader.TextureShader(texture_path=self.file_manager.path,
                                         geo_name=geo_key,
                                         textureset_dict=textureset_dict)
                    break
                else:
                    textureset_dict = self.texture_dict[geo_key][texture_set]
                    shader.TextureShader(texture_path=self.file_manager.path,
                                         geo_name=geo_key,
                                         textureset_dict=textureset_dict)

if __name__ == "__main__":
    shm = ShadersManager(path='/Users/lorenzoargentieri/Desktop/testTexture')
