__author__ = 'Lorenzo Argentieri'

import glob
import os
import pathlib

import pymel.core as pm

from mayaLib.shaderLib.utils import config
from mayaLib.shaderLib.utils import file


class TextureFolder(object):
    """Class to manage texture folders and their contents."""

    def __init__(self, folder=None, workspace=pm.workspace(q=True, dir=True, rd=True), sourceimages='sourceimages', scenes='scenes'):
        """Initialize the TextureFolder object.

        Args:
            folder (str): Custom folder path. Defaults to None.
            workspace (str): Maya workspace directory. Defaults to current workspace directory.
            sourceimages (str): Name of the source images folder. Defaults to 'sourceimages'.
            scenes (str): Name of the scenes folder. Defaults to 'scenes'.
        """
        self.home = pathlib.Path.home()
        self.scenes_folder = self.home / workspace / scenes

        self.texture_folder = pathlib.Path(folder) if folder else self.home / workspace / sourceimages

        self.imgList = self.buildImgList()

    def get_texture_folder(self):
        """Get the 'sourceimages' folder path.

        Returns:
            str: Path to the 'sourceimages' folder.
        """
        return str(self.texture_folder)

    def get_images(self):
        """Get a list of all textures in the 'sourceimages' folder.

        Returns:
            list: List of image filenames.
        """
        return self.imgList

    def buildImgList(self, search_extension='png'):
        """Build a list of all images in the folder with the given extension.

        Args:
            search_extension (str): File extension to search for. Defaults to 'png'.

        Returns:
            list: List of image filenames.
        """
        imgList = []
        os.chdir(self.get_texture_folder())
        for file in glob.glob('*.' + search_extension):
            imgList.append(file)

        return imgList

    def getTextureBaseName(self, texture_stem):
        """Get the base name of a texture file without '_BaseColor'.

        Args:
            texture_stem (str): Texture file stem.

        Returns:
            str: Base name of the texture.
        """
        texture = str(texture_stem)
        return '_'.join(texture.split('_')[:-1])

    def build_texture_catalog(self):
        """Build a catalog of textures organized by base name.

        Returns:
            dict: Dictionary mapping texture base names to lists of texture files.
        """
        texture_dict = {}
        for img in self.imgList:
            texture = pathlib.Path(img)
            texture_base_name = self.getTextureBaseName(texture.stem)
            try:
                txt_tmp_list = texture_dict[texture_base_name]
            except:
                txt_tmp_list = []

            txt_tmp_list.append(img)
            texture_dict[texture_base_name] = txt_tmp_list
        return texture_dict

def getTextureFromNode(file):
    """Get texture file path as a pathlib object.

    Args:
        file (str): File path.

    Returns:
        pathlib.Path: Base color texture path.
    """
    return pathlib.Path(file)

class TextureFileNode():
    """Class to manage Maya File nodes."""

    def __init__(self, path, filename, single_place_node=None):
        """Initialize the TextureFileNode.

        Args:
            path (str): Path to the texture file.
            filename (str): Name of the texture file.
            single_place_node (optional): Place node for texture. Defaults to None.
        """
        self.texture_recongition = file.TextureFile(path=path, filename=filename)

        self.place_node = single_place_node if single_place_node else False

        file_name_filenode = (self.texture_recongition.mesh + '_' + self.texture_recongition.channel + '.' +
                              self.texture_recongition.texture_set + '.' + self.texture_recongition.ext)

        self.filenode = self.connect_file_node(path=path, name=file_name_filenode, single_place_node=single_place_node)

    def connect_placement(self, place_node, file_node):
        """Connect place node to file node.

        Args:
            place_node: Place2D texture node.
            file_node: File node.
        """
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
        """Create and connect a file node.

        Args:
            path (str): Path to the texture file.
            name (str): Name of the texture file.
            single_place_node: Place node for texture.
            gammaCorrect (bool): Apply gamma correction. Defaults to True.
            alphaIsLuminance (bool): Use alpha as luminance. Defaults to True.

        Returns:
            node: File node object.
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

        # Color Space
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
    """Class to manage Renderman PxrTexture nodes."""

    def __init__(self, path, filename):
        """Initialize the TexturePxrTexture.

        Args:
            path (str): Path to the texture file.
            filename (str): Name of the texture file.
        """
        self.texture_recongition = file.TextureFile(path=path, filename=filename)

        file_name_filenode = (self.texture_recongition.mesh + '_' + self.texture_recongition.channel + '.' +
                              self.texture_recongition.texture_set + '.' + self.texture_recongition.ext)

        self.filenode = self.connect_file_node(path=path, name=file_name_filenode)

    def connect_file_node(self, path, name, linearize=True, artistic=True):
        """Create and connect a PxrTexture node.

        Args:
            path (str): Path to the texture file.
            name (str): Name of the texture file.
            linearize (bool): Linearize texture. Defaults to True.
            artistic (bool): Artistic setting. Defaults to True.

        Returns:
            node: PxrTexture node object.
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

        # Color Space
        if (self.texture_recongition.channel == config.diffuse
                or self.texture_recongition.channel == config.specularColor):
            pxrtexture_node.linearize.set(True)
        else:
            pxrtexture_node.linearize.set(False)

        return pxrtexture_node