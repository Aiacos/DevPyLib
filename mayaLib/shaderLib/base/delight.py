import pymel.core as pm
from mayaLib.shaderLib.base.shader_base import Shader_base


class Principled_3dl(Shader_base):
    """
    Create 3Delight Principled shader
    """

    diffuse = 'color'
    subsurface = None

    metallic = 'metallic'
    specular = None

    roughness = 'roughness'

    trasmission = None
    emission = 'incandescence'
    alpha = 'opacity'
    normal = 'disp_normal_bump_value'

    def __init__(self, shader_name, folder, shader_textures, shader_type='dlPrincipled', standard=True, shading_engine=None):
        """
        Create 3Delight Principled shader
        :param shader_name: Geo or Texture set (String)
        :param folder: Texture forlder Path (String/Path)
        :param shader_textures: Texture List (List od String/Path)
        :param shader_type:
        """
        # init base class
        Shader_base.__init__(self, shader_name, folder, shader_textures, shader_type=shader_type, shading_engine=shading_engine)
        self.shader = Shader_base.get_shader(self)

        # init faceColor
        self.shader.color.set((0.2, 0.5, 0.8))

        # place node
        self.place_node = pm.shadingNode('place2dTexture', asUtility=True)

        # connect texture
        if standard:
            self.connect_textures(shader_textures)
        else:
            self.connect_textures_3dl(shader_textures)

    def connect_textures_3dl(self, textures):
        for tex in textures:
            channel = str(tex.split('.')[0]).split('_')[-1]

            #print('Texture: ', tex, ' -- Channel: ', channel)
            if channel.lower() in self.base_color_name_list:
                self.connect_color_3dl(tex, self.diffuse)
            if channel.lower() in self.metallic_name_list:
                self.connect_noncolor_3dl(tex, self.metallic)
            if channel.lower() in self.specular_name_list:
                self.connect_noncolor_3dl(tex, self.specular)
            if channel.lower() in self.roughness_name_list:
                self.connect_noncolor_3dl(tex, self.roughness)
            if channel.lower() in self.gloss_name_list:
                self.connect_noncolor_3dl(tex, self.roughness)
            if channel.replace('-OGL', '').lower() in self.normal_name_list:
                self.connect_normal_3dl(tex)
            if channel.lower() in self.trasmission_name_list:
                self.connect_noncolor_3dl(tex, self.trasmission)
            if channel.lower() in self.displacement_name_list:
                self.connect_displace_3dl(self.shader_name, tex)

    def create_file_node_3dl(self, path, name, color=True):
        #print(name, type(name))
        tex_name, ext = name.split('.')

        file_node = pm.shadingNode('dlTexture', name=tex_name, asTexture=True)
        # place_node = pm.listConnections(file_node.uvCoord)[-1]

        file_node.textureFile.set(path + '/' + name)

        if color:
            file_node.textureFile_meta_colorspace.set('sRGB')
            plug = file_node.outColor
        else:
            file_node.textureFile_meta_colorspace.set('linear')
            file_node.alphaIsLuminance.set(1)
            plug = file_node.outAlpha

        return plug

    def connect_color_3dl(self, texture, slot_name):
        texture_node = self.create_file_node_3dl(self.folder, texture, color=True)
        pm.connectAttr(texture_node, '%s.%s' % (self.shader, slot_name))
        pm.connectAttr(self.place_node.outUV, texture_node.node().uvCoord, f=True)

    def connect_noncolor_3dl(self, texture, slot_name):
        texture_node = self.create_file_node_3dl(self.folder, texture, color=False)
        pm.connectAttr(texture_node, '%s.%s' % (self.shader, slot_name))
        pm.connectAttr(self.place_node.outUV, texture_node.node().uvCoord, f=True)

    def connect_normal_3dl(self, texture, slot_name=normal, directx_normal=True):
        texture_node = self.create_file_node_3dl(self.folder, texture, color=True)
        pm.connectAttr(texture_node, '%s.%s' % (self.shader, slot_name))
        texture_node.node().textureFile_meta_colorspace.set('linear')

        if directx_normal:
            self.shader.disp_normal_bump_type.set(1)
        else:
            self.shader.disp_normal_bump_type.set(2)

        pm.connectAttr(self.place_node.outUV, texture_node.node().uvCoord, f=True)

    def connect_normal(self, texture, slot_name, colorspace=False, directx_normal=True):
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        if directx_normal:
            self.shader.disp_normal_bump_type.set(1)
        else:
            self.shader.disp_normal_bump_type.set(2)

        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name))

    def connect_textures(self, textures):
        for tex in textures:
            channel = str(tex.split('.')[0]).split('_')[-1]

            #print('Texture: ', tex, ' -- Channel: ', channel)
            if channel.lower() in self.base_color_name_list:
                self.connect_color(tex, self.diffuse, alpha_slot=self.alpha)
            if channel.lower() in self.metallic_name_list:
                self.connect_noncolor(tex, self.metallic)
            if channel.lower() in self.specular_name_list:
                self.connect_noncolor(tex, self.specular)
            if channel.lower() in self.roughness_name_list:
                self.connect_noncolor(tex, self.roughness)
            if channel.lower() in self.gloss_name_list:
                self.connect_noncolor(tex, self.roughness)
            if channel.replace('-OGL', '').lower() in self.normal_name_list:
                self.connect_normal(tex, self.normal)
            if channel.lower() in self.trasmission_name_list:
                self.connect_noncolor(tex, self.trasmission)
