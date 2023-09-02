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

    def __init__(self, shader_name, folder, shader_textures, shader_type='standardSurface', single_place_node=True):

        # create a shader
        self.shader_name = shader_name
        self.shader = pm.shadingNode(shader_type, asShader=True, name=shader_name)

        # create a shading group
        self.shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=self.shader_name)
        # connect shader to sg surface shader
        pm.connectAttr(self.shader.outColor, self.shading_group.surfaceShader)

        if single_place_node:
            self.place_node = self.create_place_node()

        self.folder = folder
        self.shader_textures = shader_textures

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

    def connect_color(self, texture, slot_name, colorspace=True):
        file_node = self.create_file_node(self.path, texture, color=colorspace)
        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name))
        self.connect_placement(self.place_node, file_node)

    def connect_noncolor(self, texture, slot_name, colorspace=False):
        file_node = self.create_file_node(self.path, texture, color=colorspace)
        file_node.alphaIsLuminance.set(True)
        pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, slot_name))

    def connect_normal(self, texture, slot_name, colorspace=False):
        file_node = self.create_file_node(self.path, texture, color=colorspace)

        # create bump_node
        self.bump_node = pm.shadingNode("bump2d", asUtility=True)
        self.bump_node.bumpInterp.set(1)
        #self.bump_node.aiFlipR.set(0)
        #self.bump_node.aiFlipG.set(0)

        # connect file_node to bump_node
        pm.connectAttr(file_node.outAlpha, self.bump_node.bumpValue)

        # connect bump_node to shader
        pm.connectAttr(self.bump_node.outNormal, '%s.%s' % (self.shader, slot_name))

    def create_place_node(self):
        return pm.shadingNode('place2dTexture', asUtility=True)

    def connect_placement(self, place_node, file_node):
        pm.connectAttr('%s.coverage' % place_node, '%s.coverage' % file_node)
        pm.connectAttr('%s.translateFrame' % place_node, '%s.translateFrame' % file_node)
        pm.connectAttr('%s.rotateFrame' % place_node, '%s.rotateFrame' % file_node)
        pm.connectAttr('%s.mirrorU' % place_node, '%s.mirrorU' % file_node)
        pm.connectAttr('%s.mirrorV' % place_node, '%s.mirrorV' % file_node)
        pm.connectAttr('%s.stagger' % place_node, '%s.stagger' % file_node)
        pm.connectAttr('%s.wrapU' % place_node, '%s.wrapU' % file_node)
        pm.connectAttr('%s.wrapV' % place_node, '%s.wrapV' % file_node)
        pm.connectAttr('%s.repeatUV' % place_node, '%s.repeatUV' % file_node)
        pm.connectAttr('%s.offset' % place_node, '%s.offset' % file_node)
        pm.connectAttr('%s.rotateUV' % place_node, '%s.rotateUV' % file_node)
        pm.connectAttr('%s.noiseUV' % place_node, '%s.noiseUV' % file_node)
        pm.connectAttr('%s.vertexUvOne' % place_node, '%s.vertexUvOne' % file_node)
        pm.connectAttr('%s.vertexUvTwo' % place_node, '%s.vertexUvTwo' % file_node)
        pm.connectAttr('%s.vertexUvThree' % place_node, '%s.vertexUvThree' % file_node)
        pm.connectAttr('%s.vertexCameraOne' % place_node, '%s.vertexCameraOne' % file_node)
        pm.connectAttr('%s.outUV' % place_node, '%s.uv' % file_node)
        pm.connectAttr('%s.outUvFilterSize' % place_node, '%s.uvFilterSize' % file_node)

    def create_file_node(self, path, name, color=True):
        print(name, type(name))
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

        self.connect_placement(self.place_node, file_node)

        return plug


if __name__ == "__main__":
    pass

# ToDo: gui for signle shader maker main passing geo name
