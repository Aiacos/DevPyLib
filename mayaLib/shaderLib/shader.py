__author__ = 'Lorenzo Argentieri'

import pathlib

from pymel import core as pm

from mayaLib.shaderLib.base import texture
from mayaLib.shaderLib.base.shader_base import Shader_base, UsdPreviewSurface
from mayaLib.shaderLib.base.arnold import aiStandardSurface
from mayaLib.shaderLib.base.renderman import PxrDisneyBSDF
from mayaLib.shaderLib.base.delight import Principled_3dl


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

        return aiStandardSurface(shader_name=geo_name, file_node_dict=self.filenode_dict)

    def build_pxrDisneyBSDF(self, texture_path, geo_name, textureset_dict, pxrTextureNode=True, single_place_node=True):
        for texture_channel in textureset_dict:
            fn = texture.TexturePxrTexture(path=texture_path,
                                           filename=textureset_dict[texture_channel])
            self.filenode_dict[texture_channel] = fn.filenode

        return PxrDisneyBSDF(shader_name, folder, shader_textures)

    def getShader(self):
        return self.shader

class BuildAllShaders(object):
    def __init__(self,  folder):
        # Build Texture List
        texture_manager = texture.TextureFolder()
        texture_dict = texture_manager.build_texture_catalog()

        for key, value in texture_dict.items():
            TextureShader()

class ConvertShaders(object):
    def __init__(self, to_shader_type):
        """
        Convert current shader to another renderer
        :param to_shader_type: (str) standard, usd, 3delight, renderman
        """

        self.shader_list = self.get_materials_in_scene()

        for shader in self.shader_list:
            shader_name = str(shader.name())
            shading_engine = shader.connections(type='shadingEngine')[-1]
            assigned_geometry = shading_engine.connections(type='mesh')

            pm.rename(shader, shader_name + '_OLD')
            #pm.rename(shading_engine, str(shading_engine.name()) + '_OLD')

            folder, texture_list = self.get_main_texture(shader)

            if to_shader_type == 'standard':
                base_shader = Shader_base(shader_name, folder, texture_list, shading_engine=shading_engine)
                # base_shader.assign_shader(assigned_geometry)
            elif to_shader_type == 'usd':
                usd_shader = UsdPreviewSurface(shader_name, folder, texture_list, shading_engine=shading_engine)
                # usd_shader.assign_shader(assigned_geometry)
            elif to_shader_type == '3delight':
                delight_shader = Principled_3dl(shader_name, folder, texture_list, shading_engine=shading_engine)
                # delight_shader.assign_shader(assigned_geometry)
            elif to_shader_type == 'renderaman':
                renderman_shader = UsdPreviewSurface(shader_name, folder, texture_list, shading_engine=shading_engine)
                # renderman_shader.assign_shader(assigned_geometry)
            else:
                print('No valid Shader')
                pass

            pm.mel.MLdeleteUnused()



    def get_materials_in_scene(self):
        # No need to pass in a string to `type`, if you don't want to.
        for shading_engine in pm.ls(type=pm.nt.ShadingEngine):
            # ShadingEngines are collections, so you can check against their length
            if len(shading_engine):
                # You can call listConnections directly on the attribute you're looking for.
                for material in shading_engine.surfaceShader.listConnections():
                    yield material

    def get_main_texture(self, shader):
        file_node_list = pm.listConnections(shader, source=True, type='file')
        bump_node_list = pm.listConnections(shader, source=True, type='bump2d')
        if bump_node_list:
            file_node_list.extend(pm.listConnections(bump_node_list, source=True, type='file'))
        texture_file_path = file_node_list[0].fileTextureName.get()
        file_path = pathlib.Path(texture_file_path).parent.absolute()

        texture_list = []
        for file_node in file_node_list:
            texture_full_path = file_node.fileTextureName.get()
            texture = pathlib.Path(texture_full_path).name
            texture_list.append(texture)

        return str(file_path), texture_list


if __name__ == "__main__":
    path = '/Users/lorenzoargentieri/Desktop/testTexture'
    # tx = file.TextureFileManager(dirname=path)
    # texdict = tx.texture_dict['Skull']
    # shaderdict = texdict['Skull']
    # ts = TextureShader(texture_path=path, geo_name='Skull', textureset_dict=shaderdict)
