__author__ = 'Lorenzo Argentieri'

import os
import glob
import pathlib
import mayaLib.utility.json_tool as json_tool

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
    """
    Convert current shader to another renderer
    :param to_shader_type: (str) standard, usd, 3delight, renderman
    """
    def __init__(self, to_shader_type):
        self.shader_list = self.get_materials_in_scene()
        print('Shaders: ', self.shader_list)

        for shader in self.shader_list:
            shader_name = str(shader.name())
            shading_engine = shader.connections(type='shadingEngine')[-1]
            assigned_geometry = shading_engine.connections(type='mesh')

            pm.rename(shader, shader_name + '_OLD')
            #pm.rename(shading_engine, str(shading_engine.name()) + '_OLD')

            folder, texture_list = self.get_main_texture(shader)
            texture_list = self.search_texture(folder, texture_list)
            print('FOLDER: ', folder)
            print('TEXTURE LIST: ', texture_list)

            if to_shader_type == 'standard':
                base_shader = Shader_base(shader_name, folder, texture_list, shading_engine=shading_engine)
                #self.reconnect_filenode(shader, base_shader)
                # base_shader.assign_shader(assigned_geometry)
            elif to_shader_type == 'usd':
                usd_shader = UsdPreviewSurface(shader_name, folder, texture_list, shading_engine=shading_engine)
                #self.reconnect_filenode(shader, usd_shader)
                # usd_shader.assign_shader(assigned_geometry)
            elif to_shader_type == '3delight':
                delight_shader = Principled_3dl(shader_name, folder, texture_list, shading_engine=shading_engine)
                #self.reconnect_filenode(shader, delight_shader)
                # delight_shader.assign_shader(assigned_geometry)
            elif to_shader_type == 'renderaman':
                renderman_shader = UsdPreviewSurface(shader_name, folder, texture_list, shading_engine=shading_engine)
                #self.reconnect_filenode(shader, renderman_shader)
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

        if file_node_list:
            texture_file_path = file_node_list[0].fileTextureName.get()
            file_path = pathlib.Path(texture_file_path).parent.absolute()

            texture_list = []
            for file_node in file_node_list:
                texture_full_path = file_node.fileTextureName.get()
                texture = pathlib.Path(texture_full_path).name
                texture_list.append(texture)

            return str(file_path), texture_list
        else:
            return '', []

    def search_texture(self, path, texture_list):
        if texture_list:
            tex_name, extension = texture_list[-1].split('.')
            main_name = tex_name.split(' ')[0].split('_')[0]
            print('main name:', main_name)

            os.chdir(path)
            for file in glob.glob(main_name + '*.' + extension):
                texture_list.append(file)

            return texture_list
        else:
            return []

    def reconnect_filenode(self, shader, new_shader):
        if shader.type() == 'standardSurface':
            diffuse_socket = pm.PyNode(shader.name() + '.' + Shader_base.diffuse)
            metallic_socket = pm.PyNode(shader.name() + '.' + Shader_base.metallic)
            roughness_socket = pm.PyNode(shader.name() + '.' + Shader_base.roughness)
            emission_socket = pm.PyNode(shader.name() + '.' + Shader_base.emission)
            alpha_socket = pm.PyNode(shader.name() + '.' + Shader_base.alpha)
            normal_socket = pm.PyNode(shader.name() + '.' + Shader_base.normal)

        if shader.type() == 'usdPreviewSurface':
            diffuse_socket = pm.PyNode(shader.name() + '.' + UsdPreviewSurface.diffuse)
            metallic_socket = pm.PyNode(shader.name() + '.' + UsdPreviewSurface.metallic)
            roughness_socket = pm.PyNode(shader.name() + '.' + UsdPreviewSurface.roughness)
            emission_socket = pm.PyNode(shader.name() + '.' + UsdPreviewSurface.emission)
            alpha_socket = pm.PyNode(shader.name() + '.' + UsdPreviewSurface.alpha)
            normal_socket = pm.PyNode(shader.name() + '.' + UsdPreviewSurface.normal)

        if shader.type() == 'dlPrincipled':
            diffuse_socket = pm.PyNode(shader.name() + '.' + Principled_3dl.diffuse)
            metallic_socket = pm.PyNode(shader.name() + '.' + Principled_3dl.metallic)
            roughness_socket = pm.PyNode(shader.name() + '.' + Principled_3dl.roughness)
            emission_socket = pm.PyNode(shader.name() + '.' + Principled_3dl.emission)
            alpha_socket = pm.PyNode(shader.name() + '.' + Principled_3dl.alpha)
            normal_socket = pm.PyNode(shader.name() + '.' + Principled_3dl.normal)

        if shader.type() == 'PxrDisneyBsdf':
            diffuse_socket = pm.PyNode(shader.name() + '.' + PxrDisneyBSDF.diffuse)
            metallic_socket = pm.PyNode(shader.name() + '.' + PxrDisneyBSDF.metallic)
            roughness_socket = pm.PyNode(shader.name() + '.' + PxrDisneyBSDF.roughness)
            emission_socket = pm.PyNode(shader.name() + '.' + PxrDisneyBSDF.emission)
            alpha_socket = pm.PyNode(shader.name() + '.' + PxrDisneyBSDF.alpha)
            normal_socket = pm.PyNode(shader.name() + '.' + PxrDisneyBSDF.normal)

        if diffuse_socket.isConnected():
            print('---------------------------------------')
            print(diffuse_socket.listConnections(plugs=True))
            print(pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.diffuse))
            pm.connectAttr(diffuse_socket.listConnections(plugs=True)[-1], pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.diffuse), f=True)
        if metallic_socket.isConnected():
            pm.connectAttr(metallic_socket.listConnections(plugs=True)[-1], pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.metallic), f=True)
        if roughness_socket.isConnected():
            pm.connectAttr(roughness_socket.listConnections(plugs=True)[-1], pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.roughness), f=True)
        if emission_socket.isConnected():
            pm.connectAttr(emission_socket.listConnections(plugs=True)[-1], pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.emission), f=True)
        if alpha_socket.isConnected():
            pass
            try:
                pm.connectAttr(alpha_socket.listConnections(plugs=True)[-1], pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.alpha), f=True)
            except:
                print('Alpha Error')
                #pm.connectAttr(shader.name() + '.outAlpha', pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.alpha))
        if normal_socket.isConnected():
            pm.connectAttr(normal_socket.listConnections(plugs=True)[-1], pm.PyNode(new_shader.get_shader().name() + '.' + new_shader.normal), f=True)






class ShaderFromJson(object):
    """
    Create file Reading JSON File
    """

    def __init__(self, json_filepath, to_shader_type):
        data = json_tool.load_json_data(json_filepath)

        for key, value in data.items():
            shader_name = key
            shader_dict = value

            folder = shader_dict['path']
            texture_list = shader_dict['textures']
            shading_engine = pm.ls(shader_name)[-1].connections(type='shadingEngine')[-1]

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


if __name__ == "__main__":
    path = '/Users/lorenzoargentieri/Desktop/testTexture'
    # tx = file.TextureFileManager(dirname=path)
    # texdict = tx.texture_dict['Skull']
    # shaderdict = texdict['Skull']
    # ts = TextureShader(texture_path=path, geo_name='Skull', textureset_dict=shaderdict)
