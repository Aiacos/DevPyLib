__author__ = 'Lorenzo Argentieri'

import os
import pymel.core as pm

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

    def __init__(self, dirname=pm.workspace(q=True, dir=True, rd=True) + '/sourceimages/', ext='exr'):
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
    path = 'testPath'
    test_dict = TextureFileManager() #PATH
    print test_dict.texture_dict