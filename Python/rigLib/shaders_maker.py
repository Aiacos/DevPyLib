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
            print 'texture set for: -------------------'
            for texture_set in self.texture_dict[geo_key].keys():
                textureset_dict = self.texture_dict[geo_key][texture_set]
                print textureset_dict
                shader.TextureShader(texture_path=self.file_manager.path,
                                     geo_name=texture_set,
                                     textureset_dict=textureset_dict[texture_set])




                # if texture_set == geo_key + '_udim':
                #     print 'UDIM TEXTURE'
                #     for channel_key in self.texture_dict[geo_key][texture_set].keys():
                #         self.texture_dict[geo_key][texture_set][channel_key] = \
                #             texture.TextureFileNode(path=self.file_manager.path,
                #                                     filename=self.texture_dict[geo_key][texture_set][channel_key])
                #
                # else:
                #     for channel_key in self.texture_dict[geo_key][texture_set].keys():
                #         print self.texture_dict[geo_key][texture_set][channel_key]
                #         self.texture_dict[geo_key][texture_set][channel_key] = \
                #             texture.TextureFileNode(path=self.file_manager.path,
                #                                     filename=self.texture_dict[geo_key][texture_set][channel_key])


if __name__ == "__main__":
    shm = ShadersManager(path='/Users/lorenzoargentieri/Desktop/testTexture')
