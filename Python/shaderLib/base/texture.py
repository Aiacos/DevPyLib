__author__ = 'Lorenzo Argentieri'

from rigLib.utils import config
import pymel.core as pm
import os


class TextureFileNode():
    def __init__(self, path, filename, single_place_node=True):
        if single_place_node:
            self.place_node = pm.shadingNode('place2dTexture', asUtility=True)
        else:
            self.place_node = False

        self.connect_file_node(path=path, name=filename)

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

    def connect_file_node(self, path, name, gammaCorrect=True, alphaIsLuminance=True, single_place_node=True):
        # creation node
        file_node = pm.shadingNode("file", name=name + '_tex', asTexture=True, isColorManaged=True)
        file_node.fileTextureName.set(path + '/' + name)

        # uvTilingMode -- UDIM -> 3
        tex_name, texture_set, ext = name.split('.')
        if texture_set.isdigit():
            file_node.uvTilingMode.set(3)

        # alphaIsLuminance
        if alphaIsLuminance:
            file_node.alphaIsLuminance.set(True)
        else:
            file_node.alphaIsLuminance.set(False)

        # connection node
        if gammaCorrect:
            file_node.colorSpace.set('sRGB')
        else:
            file_node.colorSpace.set('Raw')

        # place node connect
        if single_place_node:
            self.connect_placement(single_place_node, file_node)
        else:
            place_node_normal = pm.shadingNode('place2dTexture', asUtility=True)
            self.connect_placement(place_node_normal, file_node)

        return file_node


class TextureFile():
    """
    $mesh_Diffuse.$textureSet.$ext
    """

    def __init__(self, path, filename):
        self.path = path
        self.filename = filename
        self.mesh = ''
        self.texture_set = ''
        self.channel = ''
        self.ext = ''
        self.udim = '<UDIM>'

        self._partition()

    def _partition(self):
        name, self.texture_set, self.ext = self.filename.split('.')
        self.mesh, sep, self.channel = name.rpartition('_')
        # dict = {'channel': path}
        # self.texture_list.append()

    def get_channels(self):  # ToDO
        if self.texture_set.isdigit():
            return self.mesh, self.channel, self.udim, self.ext
        else:
            return self.mesh, self.channel, self.texture_set, self.ext


class TextureFileManager():
    """
    Search all texture in surcefolder
    """

    def __init__(self, dirname=pm.workspace(q=True, dir=True) + '/sourceimages/', ext='exr'):
        self.texture_dict_list = []
        self.ext = ext
        self.path = dirname
        self.fileList = self.search_in_directory(dirname, ext)
        self.tex_list = []

        self.texture_dict = self.build_dict()
        self.filenode_dict = {}

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
            material_dict[tex.texture_set] = {}
            channel_dict[tex.channel] = {}

            self.tex_list.append(tex)

        # build dictionary
        d = {}
        for geo_key in geo_dict.keys():
            d[geo_key] = {}
            for textureset_key in material_dict.keys():
                d[geo_key][textureset_key] = {}
                for channel_key in channel_dict.keys():
                    d[geo_key][textureset_key][channel_key] = {}

        for texture in self.tex_list:
            if texture.texture_set.isdigit():
                d[texture.mesh][texture.mesh + '_udim'][texture.channel] = texture.filename
            else:
                d[texture.mesh][texture.texture_set][texture.channel] = texture.filename
        print d

        #return self.texture_dict_list
        return d

    def get_path(self):
        return self.path


if __name__ == "__main__":
    path = '/Users/lorenzoargentieri/Desktop/testTexture'
    tx = TextureFileManager(dirname=path)
