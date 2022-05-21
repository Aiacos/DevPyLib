__author__ = 'Lorenzo Argentieri'

from pymel import core as pm

from mayaLib.shaderLib.base.shader_base import Shader_base


class PxrDisneyBSDF(Shader_base):
    """
    Create PxrSurface shader
    """
    base_color_name_list = str('diffuse diff albedo base col color basecolor').split(' ')
    subsurface_color_name_list = str('sss subsurface').split(' ')
    metallic_name_list = str('metallic metalness metal mtl').split(' ')
    specular_name_list = str('specularity specular spec spc').split(' ')
    roughness_name_list = str('roughness rough rgh').split(' ')
    gloss_name_list = str('gloss glossy glossiness').split(' ')
    normal_name_list = str('normal nor nrm nrml norm').split(' ')
    bump_name_list = str('bump bmp').split(' ')
    displacement_name_list = str('displacement displace disp dsp height heightmap').split(' ')
    trasmission_name_list = str('opacity').split(' ')
    alpha_name_list = str('alpha').split(' ')
    emission_name_list = str('emission').split(' ')

    diffuse = 'baseColor'
    subsurface = None

    metallic = 'metallic'
    specular = None

    roughness = 'roughness'

    trasmission = None
    emission = 'emitColor'
    alpha = 'presence'
    normal = 'bumpNormal'

    def __init__(self, shader_name, folder, shader_textures, shader_type='PxrDisneyBsdf'):
        """
        Create PxrSurface shader
        :param shader_name: Geo or Texture set (String)
        :param folder: Texture forlder Path (String/Path)
        :param shader_textures: Texture List (List od String/Path)
        :param shader_type:
        """
        # init base class
        Shader_base.__init__(self, shader_name, shader_type=shader_type)
        self.shader = Shader_base.get_shader(self)

        self.channel_list = [self.base_color_name_list,
                             self.subsurface_color_name_list,
                             self.metallic_name_list,
                             self.specular_name_list,
                             self.roughness_name_list,
                             self.gloss_name_list,
                             self.emission_name_list,
                             self.alpha_name_list,
                             self.bump_name_list,
                             self.normal_name_list,
                             self.displacement_name_list]
        
        self.folder = folder
        
        # init faceColor
        self.shader.baseColor.set((0.2, 0.5, 0.8))

        # connect texture
        self.connect_textures(shader_textures)


    def connect_textures(self, textures):
        for tex in textures:
            channel = str(tex.split('.')[0]).split('_')[-1]
            print('Texture: ', tex, ' -- Channel: ', channel)
            if channel.lower() in self.base_color_name_list:
                self.connect_color(tex, self.diffuse)
            if channel.lower() in self.metallic_name_list:
                self.connect_noncolor(tex, self.metallic)
            if channel.lower() in self.specular_name_list:
                self.connect_noncolor(tex, self.specular)
            if channel.lower() in self.roughness_name_list:
                self.connect_noncolor(tex, self.roughness)
            if channel.lower() in self.gloss_name_list:
                self.connect_noncolor(tex, self.roughness)
            if channel.replace('-OGL', '').lower() in self.normal_name_list:
                self.connect_normal(tex)
            if channel.lower() in self.trasmission_name_list:
                self.connect_noncolor(tex, self.trasmission)
            if channel.lower() in self.displacement_name_list:
                self.connect_displace(self.shader_name, tex)

    def create_file_node(self, path, name, linearize=True):
        """
        Connect place node to file node
        :param path:
        :param name:
        :param linearize:
        :return: pxrTexture Node object
        """

        tex_name, texture_set, ext = name.split('.')

        # creation node
        pxrtexture_node = pm.shadingNode("PxrTexture", name=tex_name + '_tex', asTexture=True)
        pxrtexture_node.filename.set(path + '/' + name)

        pxrtexture_node.linearize.set(linearize)

        return pxrtexture_node

    def connect_color(self, texture, slot_name):
        pxrtexture_node = self.create_file_node(self.folder, texture, linearize=True)
        pm.connectAttr(pxrtexture_node.resultRGB, '%s.%s' % (self.shader, slot_name))

    def connect_noncolor(self, texture, slot_name):
        pxrtexture_node = self.create_file_node(self.folder, texture, linearize=False)
        pm.connectAttr(pxrtexture_node.resultA, '%s.%s' % (self.shader, slot_name))

    def connect_normal(self, texture, slot_name=normal, directx_normal=True):
        pxrtexture_node = self.create_file_node(self.folder, texture, linearize=False)
        self.pxrnormalmap_node = pm.shadingNode("PxrNormalMap", asTexture=True)

        if directx_normal:
            self.pxrnormalmap_node.orientation.set(1)
        else:
            self.pxrnormalmap_node.orientation.set(0)

        pm.connectAttr(pxrtexture_node.resultRGB, self.pxrnormalmap_node.inputRGB)

        pm.connectAttr(self.pxrnormalmap_node.resultN, '%s.%s' % (self.shader, slot_name))
        
    def connect_displace(self, shader_name, texture):
        pxrTexture = self.create_file_node(self.folder, texture, linearize=False)
        pxrDisplace = pm.shadingNode('PxrDisplace', asShader=True, name=shader_name + 'Displace')
        pxrDispTransform = pm.shadingNode('PxrDispTransform', asTexture=True, name=shader_name + 'DispTransform')

        pm.connectAttr(pxrDispTransform.resultF, pxrDisplace.dispScalar)
        pm.connectAttr(pxrTexture.resultA, pxrDispTransform.dispScalar)

        pxrDisplace.dispAmount.set(0.1)

        pm.connectAttr(pxrDisplace.outColor, self.shading_group.displacementShader)

        return pxrDisplace
