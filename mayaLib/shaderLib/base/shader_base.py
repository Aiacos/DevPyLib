__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def build_lambert(shaderType='lambert', shaderName='tmp-shader', color=(0.5, 0.5, 0.5), transparency=(0.0, 0.0, 0.0)):
    """Creates a Lambert shader with specified attributes.

    Args:
        shaderType (str): The type of shader to create.
        shaderName (str): The name to assign the shader.
        color (tuple): The RGB color of the shader.
        transparency (tuple): Transparency of the shader.

    Returns:
        pm.nt.Shader: The created shader node.
    """
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.color.set(color)
    shader.transparency.set(transparency)

    return shader


def build_surfaceshader(shaderType='surfaceShader', shaderName='tmp-shader', color=(0.5, 0.5, 0.5)):
    """Builds a basic surface shader.

    Args:
        shaderType (str): The type of shader to create.
        shaderName (str): The name to assign the shader.
        color (tuple): The RGB color to assign to the shader.

    Returns:
        pm.nt.Shader: The created shader node.
    """
    shader = pm.shadingNode(shaderType, asShader=True, name=shaderName)

    # a shading group
    shading_group = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    pm.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    shader.outColor.set(color)

    return shader


def assign_shader(geo, shader):
    """Assigns a shader to selected objects.

    Args:
        geo (list): List of geometry to apply the shader to.
        shader (str): Name of the shader to assign.
    """
    pm.select(geo)
    pm.hyperShade(assign=shader)


def connect_shader_to_shading_node(shader, shading_engine):
    """Connects a shader to a shading engine's surface shader.

    Args:
        shader (pm.nt.Shader): The shader node to connect.
        shading_engine (pm.nt.ShadingEngine): The shading engine to connect to.
    """
    pm.connectAttr(shader.outColor, shading_engine.surfaceShader, f=True)


class Shader_base(object):
    """Base class for creating shaders with texture connections."""

    base_color_name_list = str('diffuse diff albedo base col color basecolor d').split(' ')
    subsurface_color_name_list = str('sss subsurface').split(' ')
    metallic_name_list = str('metallic metalness metal mtl m').split(' ')
    specular_name_list = str('specularity specular spec spc').split(' ')
    roughness_name_list = str('roughness rough rgh r').split(' ')
    gloss_name_list = str('gloss glossy glossiness g').split(' ')
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
        """Initializes the shader base class.

        Args:
            shader_name (str): The name of the shader.
            folder (str): Path to the texture folder.
            shader_textures (list): List of texture paths.
            shader_type (str): The type of shader to create.
            single_place_node (bool): Whether to use a single place node for textures.
            shading_engine (pm.nt.ShadingEngine): Existing shading engine to use.
        """
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
        """Returns the shader node."""
        return self.shader

    def assign_shader(self, geo):
        """Assigns the shader to selected objects.

        Args:
            geo (list): List of geometry to apply the shader to.
        """
        pm.select(geo)
        pm.hyperShade(assign=self.shader)

    def connect_textures(self, textures):
        """Connects textures to the shader based on their channels.

        Args:
            textures (list): List of texture file paths.
        """
        for tex in textures:
            channel = str(tex.split('.')[0]).split(' ')[-1].split('_')[-1]

            if channel.lower() in self.base_color_name_list:
                self.connect_color(tex, self.diffuse, alpha_slot='')
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
        """Connects a color texture to a shader slot.

        Args:
            texture (str): The texture file path.
            slot_name (str): The shader slot to connect to.
            colorspace (bool): Whether the texture is in color space.
            alpha_slot (str): Optional alpha slot to connect to.
        """
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name), f=True)

        #if alpha_slot:
            #pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, alpha_slot), f=True)

    def connect_noncolor(self, texture, slot_name, colorspace=False):
        """Connects a non-color texture to a shader slot.

        Args:
            texture (str): The texture file path.
            slot_name (str): The shader slot to connect to.
            colorspace (bool): Whether the texture is in color space.
        """
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        file_node.alphaIsLuminance.set(True)
        pm.connectAttr(file_node.outAlpha, '%s.%s' % (self.shader, slot_name), f=True)

    def connect_normal(self, texture, slot_name, colorspace=False):
        """Connects a normal map texture to a shader slot.

        Args:
            texture (str): The texture file path.
            slot_name (str): The shader slot to connect to.
            colorspace (bool): Whether the texture is in color space.
        """
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
        """Connects a displacement texture.

        Args:
            texture (str): The texture file path.
            slot_name (str): The shader slot to connect to.
            colorspace (bool): Whether the texture is in color space.
        """
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

    def create_place_node(self):
        """Creates and returns a place2dTexture node."""
        return pm.shadingNode('place2dTexture', asUtility=True)

    def connect_placement(self, place_node, file_node):
        """Connects a place node to a file node.

        Args:
            place_node (pm.nt.Place2dTexture): The place node.
            file_node (pm.nt.File): The file node.
        """
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
        """Creates and returns a file node for a texture.

        Args:
            path (str): Path to the texture folder.
            name (str): Name of the texture file.
            color (bool): Whether the texture is in color space.

        Returns:
            pm.nt.File: The created file node.
        """
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
    """Class for creating a usdPreviewSurface shader."""

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
        # init base class
        """
        Initializes an usdPreviewSurface shader.

        Args:
            shader_name (str): Name of the geometry or texture set.
            folder (str or Path): Path to the texture folder.
            shader_textures (list of str or Path): List of texture paths.
            shader_type (str): Type of the shader. Default is 'usdPreviewSurface'.
            standard (bool): Flag to determine texture connection method. Default is True.
            shading_engine: Shading engine to use. Default is None.
        """
        Shader_base.__init__(self, shader_name, folder, shader_textures, shader_type=shader_type, shading_engine=shading_engine)
        self.shader = Shader_base.get_shader(self)

        # init faceColor
        self.shader.diffuseColor.set((0.2, 0.5, 0.8))

        # place node
        self.place_node = pm.shadingNode('place2dTexture', asUtility=True)

        # connect texture
        self.connect_textures(shader_textures)


    def connect_textures(self, textures):
        """
        Connects a list of textures to the shader.

        Args:
            textures (list): List of texture paths

        The textures are connected to the shader based on their name.
        The base color textures are connected to the diffuse attribute
        and optionally to the alpha attribute if the texture has an alpha channel.
        The metallic, specular, and roughness textures are connected to the
        respective attributes.
        The normal textures are connected to the normal attribute.
        The transmission textures are connected to the transmission attribute.
        The displacement textures are connected to the displacement attribute.
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
            if channel.lower() in self.displacement_name_list:
                self.connect_displace(self.shader_name, tex)

    def connect_normal(self, texture, slot_name, colorspace=False):
        """
        Connects a normal map texture to a shader slot.

        Args:
            texture (str): The texture file path.
            slot_name (str): The shader slot to connect to.
            colorspace (bool): Whether the texture is in color space. Defaults to False.
        """
        file_node = self.create_file_node(self.folder, texture, color=colorspace)
        self.connect_placement(self.place_node, file_node)

        pm.connectAttr(file_node.outColor, '%s.%s' % (self.shader, slot_name))


if __name__ == "__main__":
    pass

