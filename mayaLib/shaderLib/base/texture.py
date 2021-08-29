__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.shaderLib.utils import config
from mayaLib.shaderLib.utils import file


class TextureFileNode():
    def __init__(self, path, filename, single_place_node=None):
        """
        Create File Node and connect it with Place Node
        :param path:
        :param filename:
        :param single_place_node:
        """
        self.texture_recongition = file.TextureFile(path=path, filename=filename)

        if single_place_node is None:
            self.place_node = False
        else:
            self.place_node = single_place_node  # pm.shadingNode('place2dTexture', asUtility=True)

        # file node name
        file_name_filenode = self.texture_recongition.mesh + '_' + self.texture_recongition.channel + '.' + \
                             self.texture_recongition.texture_set + '.' + self.texture_recongition.ext

        self.filenode = self.connect_file_node(path=path, name=file_name_filenode, single_place_node=single_place_node)

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

    def connect_file_node(self, path, name, single_place_node, gammaCorrect=True, alphaIsLuminance=True):
        """
        Connect place node to file node
        :param path:
        :param name:
        :param single_place_node:
        :param gammaCorrect:
        :param alphaIsLuminance:
        :return: File Node object
        """

        tex_name, texture_set, ext = name.split('.')

        # creation node
        file_node = pm.shadingNode("file", name=tex_name + '_tex', asTexture=True, isColorManaged=True)
        file_node.fileTextureName.set(path + '/' + name)

        # uvTilingMode -- UDIM -> 3
        if texture_set.isdigit():
            file_node.uvTilingMode.set(3)

        # alphaIsLuminance
        if (self.texture_recongition.channel == config.backlight
                or self.texture_recongition.channel == config.specularWeight
                or self.texture_recongition.channel == config.specularRoughness
                or self.texture_recongition.channel == config.fresnel
                or self.texture_recongition.channel == config.normal
                or self.texture_recongition.channel == config.height):
            file_node.alphaIsLuminance.set(True)
        else:
            file_node.alphaIsLuminance.set(False)

        # Gamma
        if (self.texture_recongition.channel == config.diffuse
                or self.texture_recongition.channel == config.specularColor):
            file_node.colorSpace.set('sRGB')
        else:
            file_node.colorSpace.set('Raw')

        # place node connect
        if single_place_node is None:
            multi_place_node = pm.shadingNode('place2dTexture', asUtility=True)
            self.connect_placement(multi_place_node, file_node)
        else:
            self.connect_placement(self.place_node, file_node)

        return file_node


class TexturePxrTexture():
    def __init__(self, path, filename):
        """
        Create pxrTexture Node
        :param path:
        :param filename:
        """
        self.texture_recongition = file.TextureFile(path=path, filename=filename)

        # file node name
        file_name_filenode = self.texture_recongition.mesh + '_' + self.texture_recongition.channel + '.' + \
                             self.texture_recongition.texture_set + '.' + self.texture_recongition.ext

        self.filenode = self.connect_file_node(path=path, name=file_name_filenode)

    def connect_file_node(self, path, name, linearize=True, artistic=True):
        """
        Connect place node to file node
        :param path:
        :param name:
        :param linearize:
        :param artistic:
        :return: pxrTexture Node object
        """

        tex_name, texture_set, ext = name.split('.')

        # creation node
        pxrtexture_node = pm.shadingNode("PxrTexture", name=tex_name + '_tex', asTexture=True)
        pxrtexture_node.filename.set(path + '/' + name)

        # uvTilingMode -- UDIM -> 3
        if texture_set.isdigit():
            pxrtexture_node.filename.set(path + '/' + tex_name + '.' + '_MAPID_' + '.' + ext)
            pxrtexture_node.atlasStyle.set(1)
        else:
            pxrtexture_node.filename.set(path + '/' + name)

        # Gamma
        if (self.texture_recongition.channel == config.diffuse
                or self.texture_recongition.channel == config.specularColor):
            pxrtexture_node.linearize.set(True)
        else:
            pxrtexture_node.linearize.set(False)

        return pxrtexture_node
