__author__ = 'Lorenzo Argentieri'

import os
import pymel.core as pm
from shaderLib.utils import config


class TextureFileNode():
    def __init__(self, path, filename, single_place_node=None):
        """
        Create File Node and connect it with Place Node
        :param path:
        :param filename:
        :param single_place_node:
        """
        self.texture_recongition = TextureFile(path=path, filename=filename)

        if single_place_node is None:
            self.place_node = False
        else:
            self.place_node = single_place_node  # pm.shadingNode('place2dTexture', asUtility=True)

        self.filenode = self.connect_file_node(path=path, name=filename, single_place_node=single_place_node)

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


class TextureFile():  # ToDo: move in util?
    """
    $mesh_Diffuse.$textureSet.$ext
    """

    def __init__(self, path, filename):
        """
        Recongize texture name pattern
        :param path: path of texture
        :param filename: texture filename
        """
        self.path = path
        self.filename = filename
        self.mesh = ''
        self.texture_set = ''
        self.channel = ''
        self.ext = ''
        self.udim = '<UDIM>'

        try:
            self._partition()
        except:
            print 'No matching pattern for texture'

    def _partition(self):
        name, self.texture_set, self.ext = self.filename.split('.')
        self.mesh, sep, self.channel = name.rpartition('_')
        # dict = {'channel': path}
        # self.texture_list.append()

    def get_channels(self):
        if self.texture_set.isdigit():
            return self.mesh, self.channel, self.udim, self.ext
        else:
            return self.mesh, self.channel, self.texture_set, self.ext


class TextureFileManager():
    """
    Search all texture in surcefolder
    """

    def __init__(self, dirname=pm.workspace(q=True, dir=True) + '/sourceimages/', ext='exr'):
        """
        Search all texture in surceimages and place it in a dictionary sorted by geo, channel and texture_set
        ($mesh_Diffuse.$textureSet.$ext)
        :param dirname: source folder
        :param ext: extension
        :return texture_dict: dictionary
        """
        self.ext = ext
        self.path = dirname
        self.fileList = self.search_in_directory(dirname, ext)
        self.tex_list = []
        self.texture_dict = self.build_dict()

    def search_in_directory(self, dirname, ext):
        ext = ext.lower()
        texList = []
        for file in os.listdir(dirname):
            if file.endswith(ext):
                texList.append(file)
        return texList

    def build_dict(self):
        geo_dict = {}
        channel_dict = {}
        material_dict = {}

        for tex_name in self.fileList:
            tex = TextureFile(self.path, tex_name)
            geo_dict[tex.mesh] = {}
            if tex.texture_set.isdigit():
                material_dict['UDIM'] = {}
            else:
                material_dict[tex.texture_set] = {}
            channel_dict[tex.channel] = {}

            self.tex_list.append(tex)

        # build dictionary
        d = {}
        for geo_key in geo_dict.keys():
            d[geo_key] = {}
            for textureset_key in material_dict.keys():
                if textureset_key.isdigit():
                    d[geo_key]['UDIM'] = {}
                else:
                    d[geo_key][textureset_key] = {}
                for channel_key in channel_dict.keys():
                    d[geo_key][textureset_key][channel_key] = {}

        for texture in self.tex_list:

            if texture.texture_set.isdigit():
                d[texture.mesh]['UDIM'][texture.channel] = texture.filename
            else:
                d[texture.mesh][texture.texture_set][texture.channel] = texture.filename

        # clean up dict
        for geo_key in geo_dict.keys():
            for textureset_key in material_dict.keys():
                if d[geo_key][textureset_key]['Diffuse'] == {}:
                    try:
                        d[geo_key].pop(textureset_key)
                    except:
                        pass

        return d

    def get_path(self):
        return self.path


if __name__ == "__main__":
    path = '/Users/lorenzoargentieri/Desktop/testTexture'
    test_dict = TextureFileManager(dirname=path)
    print test_dict.texture_dict
