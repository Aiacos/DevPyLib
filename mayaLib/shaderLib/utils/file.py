__author__ = 'Lorenzo Argentieri'

import os

import pymel.core as pm


class TextureFile(object):  # ToDo: move in util?
    """Class to handle texture files."""

    def __init__(self, path, filename):
        """Initialize the TextureFile object.

        Args:
            path (str): Path to the texture file.
            filename (str): Name of the texture file.
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
            print('No matching pattern for texture')

    def _partition(self):
        """Split the filename into mesh, texture_set, channel and extension."""
        name, self.texture_set, self.ext = self.filename.split('.')
        self.mesh, sep, self.channel = name.rpartition('_')
        # dict = {'channel': path}
        # self.texture_list.append()

    def get_channels(self):
        """Return a list of channel name that the texture has

        The channel name is the last part of the filename, before the extension.
        For example, if the filename is "myTexture_diffuse.1001.exr", the channel
        name will be "diffuse".

        Returns:
            list: List of channel names
        """
        if self.texture_set.isdigit():
            return self.mesh, self.channel, self.udim, self.ext
        else:
            return self.mesh, self.channel, self.texture_set, self.ext


class TextureFileManager(object):
    """Search all texture in source folder and place it in a dictionary sorted by geo, channel and texture_set"""

    def __init__(self, dirname=pm.workspace(q=True, dir=True, rd=True) + '/sourceimages/', ext='exr'):
        """
        Initialize the TextureFileManager object.

        Args:
            dirname (str): Directory path. Defaults to the 'sourceimages' directory in the current workspace.
            ext (str): File extension to search for. Defaults to 'exr'.
        """
        self.ext = ext
        self.path = dirname
        self.fileList = self.search_in_directory(dirname, ext)
        self.tex_list = []
        self.texture_dict = self.build_dict()

    def search_in_directory(self, dirname, ext):
        """Search all files with the given extension in the given directory.

        Args:
            dirname (str): Directory path.
            ext (str): File extension.

        Returns:
            list: List of files with the given extension.
        """
        ext = ext.lower()
        texList = []
        for file in os.listdir(dirname):
            if file.endswith(ext):
                texList.append(file)
        return texList

    def build_dict(self):
        """Build a dictionary of textures organized by geo, channel and texture_set."""
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
        for geo_key in list(geo_dict.keys()):
            d[geo_key] = {}
            for textureset_key in list(material_dict.keys()):
                if textureset_key.isdigit():
                    d[geo_key]['UDIM'] = {}
                else:
                    d[geo_key][textureset_key] = {}
                for channel_key in list(channel_dict.keys()):
                    d[geo_key][textureset_key][channel_key] = {}

        for texture in self.tex_list:

            if texture.texture_set.isdigit():
                d[texture.mesh]['UDIM'][texture.channel] = texture.filename
            else:
                d[texture.mesh][texture.texture_set][texture.channel] = texture.filename

        # clean up dict
        for geo_key in list(geo_dict.keys()):
            for textureset_key in list(material_dict.keys()):
                if d[geo_key][textureset_key]['Diffuse'] == {}:
                    try:
                        d[geo_key].pop(textureset_key)
                    except:
                        pass
        return d

    def get_path(self):
        """Return the path to the texture folder."""
        return self.path


if __name__ == "__main__":
    path = 'testPath'
    test_dict = TextureFileManager()  # PATH
    print((test_dict.texture_dict))
