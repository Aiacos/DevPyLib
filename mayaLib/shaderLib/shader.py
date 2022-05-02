__author__ = 'Lorenzo Argentieri'

from pymel import core as pm

from mayaLib.shaderLib.base import texture
from mayaLib.shaderLib.base.arnold import aiStandard_shaderBase
from mayaLib.shaderLib.base.renderman import PxrDisneyBSDF


class TextureShader():
    def __init__(self, texture_path, geo_name, textureset_dict, single_place_node=True):
        """
        Create Shader and Connect it with all associated texture
        :param texture_path: path to textures
        :param geo_name: Geometry name
        :param textureset_dict: material IDs used in Substance Painter or UDIM
        :param single_place_node: (bool)
        """

        # See active Renderer
        # renderManRIS, arnold
        self.renderer = pm.ls('defaultRenderGlobals')[0].currentRenderer.get()

        if self.renderer == 'arnold':
            self.shader = self.build_aiStandard(texture_path, geo_name, textureset_dict, single_place_node=True)
        elif self.renderer == 'renderman':
            self.shader = self.build_pxrDisneyBSDF(texture_path, geo_name, textureset_dict)
        else:
            print('No valid active render engine')

    def build_aiStandard(self, texture_path, geo_name, textureset_dict, single_place_node=True):
        if single_place_node:
            self.place_node = pm.shadingNode('place2dTexture', asUtility=True)
        else:
            self.place_node = None

        for texture_channel in textureset_dict:
            fn = texture.TextureFileNode(path=texture_path,
                                         filename=textureset_dict[texture_channel],
                                         single_place_node=self.place_node)
            self.filenode_dict[texture_channel] = fn.filenode

        return aiStandard_shaderBase(shader_name=geo_name, file_node_dict=self.filenode_dict)

    def build_pxrDisneyBSDF(self, texture_path, geo_name, textureset_dict, pxrTextureNode=True, single_place_node=True):
        for texture_channel in textureset_dict:
            fn = texture.TexturePxrTexture(path=texture_path,
                                           filename=textureset_dict[texture_channel])
            self.filenode_dict[texture_channel] = fn.filenode

        return PxrDisneyBSDF(shader_name, folder, shader_textures)

    def getShader(self):
        return self.shader

class BuildAllShaders(object):
    def __init__(self,  sourceimages, workspace=pm.workspace(q=True, dir=True, rd=True)):
        # Build Texture List
        texture_manager = texture.TextureFolder()
        texture_dict = texture_manager.build_texture_catalog()

        for key, value in texture_dict.items():
            TextureShader()

class ConvertShaders(object):
    def __init__(self,  sourceimages, workspace=pm.workspace(q=True, dir=True, rd=True)):
        # Build Texture List
        texture_manager = texture.TextureFolder()
        texture_dict = texture_manager.build_texture_catalog()

        # Shader List


        for key, value in texture_dict.items():
            TextureShader()


if __name__ == "__main__":
    path = '/Users/lorenzoargentieri/Desktop/testTexture'
    # tx = file.TextureFileManager(dirname=path)
    # texdict = tx.texture_dict['Skull']
    # shaderdict = texdict['Skull']
    # ts = TextureShader(texture_path=path, geo_name='Skull', textureset_dict=shaderdict)
