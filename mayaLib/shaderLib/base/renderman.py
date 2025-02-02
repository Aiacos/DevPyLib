"""
Create PxrDisneyBSDF shader

This class creates a PxrDisneyBSDF shader, assigns the shader to the object
and connects the textures to the shader.

"""

from pymel import core as pm

from mayaLib.shaderLib.base.shader_base import Shader_base


class PxrDisneyBSDF(Shader_base):
    """
    Create PxrDisneyBSDF shader

    This class creates a PxrDisneyBSDF shader, assigns the shader to the object
    and connects the textures to the shader.

    Attributes:
        diffuse (str): Name of the diffuse color attribute
        subsurface (str): Name of the subsurface scattering attribute
        metallic (str): Name of the metallic attribute
        specular (str): Name of the specular attribute
        roughness (str): Name of the roughness attribute
        trasmission (str): Name of the transmission attribute
        emission (str): Name of the emission attribute
        alpha (str): Name of the alpha attribute
        normal (str): Name of the normal attribute
    """

    diffuse = 'baseColor'
    subsurface = None

    metallic = 'metallic'
    specular = None

    roughness = 'roughness'

    trasmission = None
    emission = 'emitColor'
    alpha = 'presence'
    normal = 'bumpNormal'

    def __init__(self, shader_name, folder, shader_textures, shader_type='PxrDisneyBsdf', standard=True, shading_engine=None):
        """
        Initialize the class

        Args:
            shader_name (str): Name of the shader
            folder (str): Folder path of the textures
            shader_textures (list): List of textures
            shader_type (str): Type of the shader
            standard (bool): If the shader is a standard shader
            shading_engine (str): Name of the shading engine
        """
        # init base class
        Shader_base.__init__(self, shader_name, folder, shader_textures, shader_type=shader_type, shading_engine=shading_engine)
        self.shader = Shader_base.get_shader(self)

        self.folder = folder

        # init faceColor
        self.shader.baseColor.set((0.2, 0.5, 0.8))

        # connect texture
        if standard:
            self.connect_textures(shader_textures)
        else:
            self.connect_textures_renderman(shader_textures)

    def connect_textures_renderman(self, textures):
        """
        Connect textures to the shader

        Args:
            textures (list): List of textures
        """
        for tex in textures:
            channel = str(tex.split('.')[0]).split('_')[-1]

            print('Texture: ', tex, ' -- Channel: ', channel)
            if channel.lower() in self.base_color_name_list:
                self.connect_color_renderman(tex, self.diffuse)
            if channel.lower() in self.metallic_name_list:
                self.connect_noncolor_renderman(tex, self.metallic)
            if channel.lower() in self.specular_name_list:
                self.connect_noncolor_renderman(tex, self.specular)
            if channel.lower() in self.roughness_name_list:
                self.connect_noncolor_renderman(tex, self.roughness)
            if channel.lower() in self.gloss_name_list:
                self.connect_noncolor_renderman(tex, self.roughness)
            if channel.replace('-OGL', '').lower() in self.normal_name_list:
                self.connect_normal_renderman(tex)
            if channel.lower() in self.trasmission_name_list:
                self.connect_noncolor_renderman(tex, self.trasmission)
            if channel.lower() in self.displacement_name_list:
                self.connect_displace_renderman(self.shader_name, tex)

    def create_file_node_renderman(self, path, name, linearize=True):
        """
        Create a file node

        Args:
            path (str): Path of the texture
            name (str): Name of the texture
            linearize (bool): If the texture should be linearized

        Returns:
            pxrTextureNode: The created file node
        """
        tex_name, texture_set, ext = name.split('.')

        # creation node
        pxrtexture_node = pm.shadingNode("PxrTexture", name=tex_name + '_tex', asTexture=True)
        pxrtexture_node.filename.set(path + '/' + name)

        pxrtexture_node.linearize.set(linearize)

        return pxrtexture_node

    def connect_color_renderman(self, texture, slot_name):
        """
        Connect a color texture to the shader

        Args:
            texture (str): Name of the texture
            slot_name (str): Name of the attribute
        """
        pxrtexture_node = self.create_file_node(self.folder, texture, linearize=True)
        pm.connectAttr(pxrtexture_node.resultRGB, '%s.%s' % (self.shader, slot_name))

    def connect_noncolor_renderman(self, texture, slot_name):
        """
        Connect a non color texture to the shader

        Args:
            texture (str): Name of the texture
            slot_name (str): Name of the attribute
        """
        pxrtexture_node = self.create_file_node(self.folder, texture, linearize=False)
        pm.connectAttr(pxrtexture_node.resultA, '%s.%s' % (self.shader, slot_name))

    def connect_normal_renderman(self, texture, slot_name=normal, directx_normal=True):
        """
        Connect a normal texture to the shader

        Args:
            texture (str): Name of the texture
            slot_name (str): Name of the attribute
            directx_normal (bool): If the texture should be a DirectX normal map
        """
        pxrtexture_node = self.create_file_node(self.folder, texture, linearize=False)
        self.pxrnormalmap_node = pm.shadingNode("PxrNormalMap", asTexture=True)

        if directx_normal:
            self.pxrnormalmap_node.orientation.set(1)
        else:
            self.pxrnormalmap_node.orientation.set(0)

        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrnormalmap_node.inputRGB)

        pm.connectAttr(self.pxrnormalmap_node.resultN, '%s.%s' % (self.shader, slot_name))

    def connect_displace_renderman(self, shader_name, texture):
        """
        Connect a displacement texture to the shader

        Args:
            shader_name (str): Name of the shader
            texture (str): Name of the texture
        """
        pxrTexture = self.create_file_node(self.folder, texture, linearize=False)
        pxrDisplace = pm.shadingNode('PxrDisplace', asShader=True, name=shader_name + 'Displace')
        pxrDispTransform = pm.shadingNode('PxrDispTransform', asTexture=True, name=shader_name + 'DispTransform')

        pm.connectAttr(pxrDispTransform.resultF, pxrDisplace.dispScalar)
        pm.connectAttr(pxrTexture.resultA, pxrDispTransform.dispScalar)

        pxrDisplace.dispAmount.set(0.1)

        pm.connectAttr(pxrDisplace.outColor, self.shading_group.displacementShader)

        return pxrDisplace

    def connect_textures(self, textures):
        """
        Connect a list of textures to the shader

        Args:
            textures (list): List of texture paths

        The textures are connected to the shader based on their name.
        The base color textures are connected to the diffuse attribute
        and optionally to the alpha attribute if the texture has an alpha channel.
        The metallic, specular, and roughness textures are connected to the
        respective attributes.
        The normal textures are connected to the normal attribute.
        The transmission textures are connected to the transmission attribute.
        """
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
