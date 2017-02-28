__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from shaderLib.base import texture
from shaderLib.base import shader


class ShaderManager():
    def __init__(self):
        self.file_manager = texture.TextureFileManager(dirname='/Users/lorenzoargentieri/Desktop/testTexture')
        self.texture_dict = self.file_manager.texture_dict

        # filenode
        for geo_key in self.texture_dict.keys():
            for texture_set in self.texture_dict[geo_key].keys():
                if texture_set == geo_key + '_udim':
                    print 'UDIM TEXTURE'
                    for channel_key in self.texture_dict[geo_key][texture_set].keys():
                        self.texture_dict[geo_key][texture_set][channel_key] = \
                            texture.TextureFileNode(path=self.file_manager.path,
                                                    filename=self.texture_dict[geo_key][texture_set][channel_key])

                else:
                    for channel_key in self.texture_dict[geo_key][texture_set].keys():
                        print self.texture_dict[geo_key][texture_set][channel_key]
                        self.texture_dict[geo_key][texture_set][channel_key] = \
                            texture.TextureFileNode(path=self.file_manager.path,
                                                    filename=self.texture_dict[geo_key][texture_set][channel_key])

                        ######################################
                        mfile_node = pm.shadingNode("file", name='test', asTexture=True, isColorManaged=True)
                        mfile_node.colorSpace.set('Raw')
                        # pm.setAttr(file_node + '.fileTextureName', '_path', type='string')
                        mfile_node.fileTextureName.set('gooool')
                        tex = {'Normal': mfile_node}

                        # shader
                        # sh = shader.aiStandard_shader(shader_name='testShader', file_node=fnode[])


if __name__ == "__main__":
    shm = ShaderManager()
