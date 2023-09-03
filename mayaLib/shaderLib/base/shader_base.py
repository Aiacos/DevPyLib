__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def build_lambert(shaderType='lambert', shaderName='tmp-shader', color=(0.5, 0.5, 0.5), transparency=(0.0, 0.0, 0.0)):
    """
    Build basic lambert Shader
    :param shaderType: type (string)
    :param shaderName: name (string)
    :param color: es. (0.5,0.5,0.5)
    :param transparency: es. (0.5,0.5,0.5)
    :return: shader node
    """
    # create a shader
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.color.set(color)
    shader.transparency.set(transparency)

    return shader


def build_surfaceshader(shaderType='surfaceShader', shaderName='tmp-shader', color=(0.5, 0.5, 0.5)):
    """
    Build basic surfaceShader
    :param shaderType: type (string)
    :param shaderName: name (string)
    :param color: es. (0.5,0.5,0.5)
    :return: shader node
    """
    # create a shader
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.outColor.set(color)

    return shader


def assign_shader(geo, shader):
    """
    Assign Shader to selected objects
    :param geo: geometry list (list)
    :param shader: shader name (string)
    :return:
    """
    pm.select(geo)
    pm.hyperShade(assign=shader)


def connect_shader_to_shading_node(shader, shading_engine):
    pm.connectAttr(shader.outColor, shading_engine.surfaceShader, f=True)


class Shader_base(object):
    """
    Create general Shader
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
    subsurface = 'subsurfaceColor'

    metallic = 'metalness'
    specular = None

    roughness = 'specularRoughness'

    trasmission = 'trasmission'
    emission = 'emission'
    alpha = 'opacity'
    normal = 'normalCamera'

    def __init__(self, shader_name, folder, shader_textures, shader_type='standardSurface', single_place_node=True, shading_engine=None):
        self.shader_name = shader_name
        self.folder = folder
        self.shader_textures = shader_textures

        # create a shader
        self.shader = pm.shadingNode(shader_type, asShader=True, name=shader_name)

        # create a shading group
        if not shading_engine:
            self.shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.shader_name)
        else:
            self.shading_group = shading_engine

        # connect shader to sg surface shader
        pm.connectAttr(self.shader.outColor, self.shading_group.surfaceShader, f=True)

        if single_place_node:
            self.place_node = self.create_place_node()

    def get_shader(self):
        return self.shader

    def assign_shader(self, geo):
        """
        Assign Shader to selected objects
        :param geo: geometry list (list)
        :return:
        """
        pm.select(geo)
        pm.hyperShade(assign=self.shader)

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
                self.connect_normal(tex)
            if channel.lower() in self.trasmission_name_list:
                self.connect_noncolor(tex, self.trasmission)
            if channel.lower() in self.displacement_name_list:
                self.connect_displace(self.shader_name, tex)

    def connect_color(self, texture, slot_name, colorspace=True, alpha_slot=None):
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name), f=True)

        if alpha_slot:
            pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, alpha_slot), f=True)

    def connect_noncolor(self, texture, slot_name, colorspace=False):
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        file_node.alphaIsLuminance.set(True)
        pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, slot_name), f=True)

    def connect_normal(self, texture, slot_name, colorspace=False):
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        # create bump_node
        self.bump_node = pm.shadingNode("bump2d", asUtility=True)
        self.bump_node.bumpInterp.set(1)
        #self.bump_node.aiFlipR.set(0)
        #self.bump_node.aiFlipG.set(0)

        # connect file_node to bump_node
        pm.connectAttr(file_node.outAlpha, self.bump_node.bumpValue, f=True)

        # connect bump_node to shader
        pm.connectAttr(self.bump_node.outNormal, '%s.%s' % (self.shader, slot_name), f=True)

    def connect_displace(self, texture, slot_name, colorspace=False):
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

    def create_place_node(self):
        return pm.shadingNode('place2dTexture', asUtility=True)

    def connect_placement(self, place_node, file_node):
        pm.connectAttr('%s.coverage' % place_node, '%s.coverage' % file_node, f=True)
        pm.connectAttr('%s.translateFrame' % place_node, '%s.translateFrame' % file_node, f=True)
        pm.connectAttr('%s.rotateFrame' % place_node, '%s.rotateFrame' % file_node, f=True)
        pm.connectAttr('%s.mirrorU' % place_node, '%s.mirrorU' % file_node, f=True)
        pm.connectAttr('%s.mirrorV' % place_node, '%s.mirrorV' % file_node, f=True)
        pm.connectAttr('%s.stagger' % place_node, '%s.stagger' % file_node, f=True)
        pm.connectAttr('%s.wrapU' % place_node, '%s.wrapU' % file_node, f=True)
        pm.connectAttr('%s.wrapV' % place_node, '%s.wrapV' % file_node, f=True)
        pm.connectAttr('%s.repeatUV' % place_node, '%s.repeatUV' % file_node, f=True)
        pm.connectAttr('%s.offset' % place_node, '%s.offset' % file_node, f=True)
        pm.connectAttr('%s.rotateUV' % place_node, '%s.rotateUV' % file_node, f=True)
        pm.connectAttr('%s.noiseUV' % place_node, '%s.noiseUV' % file_node, f=True)
        pm.connectAttr('%s.vertexUvOne' % place_node, '%s.vertexUvOne' % file_node, f=True)
        pm.connectAttr('%s.vertexUvTwo' % place_node, '%s.vertexUvTwo' % file_node, f=True)
        pm.connectAttr('%s.vertexUvThree' % place_node, '%s.vertexUvThree' % file_node, f=True)
        pm.connectAttr('%s.vertexCameraOne' % place_node, '%s.vertexCameraOne' % file_node, f=True)
        pm.connectAttr('%s.outUV' % place_node, '%s.uv' % file_node, f=True)
        pm.connectAttr('%s.outUvFilterSize' % place_node, '%s.uvFilterSize' % file_node, f=True)

    def create_file_node(self, path, name, color=True):
        tex_name, ext = name.split('.')

        file_node = pm.shadingNode("file", name=tex_name + '_tex', asTexture=True, isColorManaged=True)
        file_node.fileTextureName.set(path + '/' + name)

        if color:
            file_node.colorSpace.set('sRGB')
            plug = file_node.outColor
        else:
            file_node.colorSpace.set('Raw')
            file_node.alphaIsLuminance.set(1)
            plug = file_node.outAlpha

        if '.10' in name:
            file_node.uvTilingMode.set(3)

        self.connect_placement(self.place_node, file_node)

        return file_node

class UsdPreviewSurface(Shader_base):
    diffuse = 'diffuseColor'
    subsurface = 'subsurfaceColor'

    metallic = 'metallic'
    specular = None

    roughness = 'roughness'

    trasmission = 'trasmission'
    emission = 'emission'
    alpha = 'opacity'
    normal = 'normal'

    def __init__(self, shader_name, folder, shader_textures, shader_type='usdPreviewSurface', standard=True, shading_engine=None):
        """
        Create usdPreviewSurface shader
        :param shader_name: Geo or Texture set (String)
        :param folder: Texture forlder Path (String/Path)
        :param shader_textures: Texture List (List od String/Path)
        :param shader_type:
        """
        # init base class
        Shader_base.__init__(self, shader_name, folder, shader_textures, shader_type=shader_type, shading_engine=shading_engine)
        self.shader = Shader_base.get_shader(self)

        # init faceColor
        self.shader.diffuseColor.set((0.2, 0.5, 0.8))

        # place node
        self.place_node = pm.shadingNode('place2dTexture', asUtility=True)

        # connect texture
        self.connect_textures(shader_textures)


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
            if channel.lower() in self.displacement_name_list:
                self.connect_displace(self.shader_name, tex)

    def connect_normal(self, texture, slot_name, colorspace=False):
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name))


if __name__ == "__main__":
    pass

# ToDo: gui for signle shader maker main passing geo name
