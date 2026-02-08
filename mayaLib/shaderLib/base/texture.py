"""Texture node creation and management utilities.

Provides utilities for creating and connecting Maya texture nodes including
file textures, place2dTexture, and PxrTexture nodes for different renderers.
"""

__author__ = "Lorenzo Argentieri"

import os
import pathlib

import pymel.core as pm

from mayaLib.shaderLib.utils import config, file


class TextureFolder:
    """Class to manage texture folders and their contents."""

    def __init__(
        self,
        folder=None,
        workspace=None,
        sourceimages="sourceimages",
        scenes="scenes",
    ):
        """Initialize the TextureFolder object.

        Args:
            folder (str): Custom folder path. Defaults to None.
            workspace (str | None): Maya workspace directory. Defaults to current workspace directory.
            sourceimages (str): Name of the source images folder. Defaults to 'sourceimages'.
            scenes (str): Name of the scenes folder. Defaults to 'scenes'.
        """
        if workspace is None:
            workspace = pm.workspace(q=True, dir=True, rd=True)
        self.home = pathlib.Path.home()
        self.scenes_folder = self.home / workspace / scenes

        self.texture_folder = (
            pathlib.Path(folder) if folder else self.home / workspace / sourceimages
        )

        self.img_list = self.build_img_list()

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
        return self.img_list

    def build_img_list(self, search_extension="png"):
        """Build a list of all images in the folder with the given extension.

        Args:
            search_extension (str): File extension to search for. Defaults to 'png'.

        Returns:
            list: List of image filenames.
        """
        img_list = []
        # Use Path.glob() instead of os.chdir() to avoid changing global state
        pattern = f"*.{search_extension}"
        for filepath in self.texture_folder.glob(pattern):
            img_list.append(filepath.name)

        return img_list

    def get_texture_base_name(self, texture_stem):
        """Get the base name of a texture file without '_BaseColor'.

        Args:
            texture_stem (str): Texture file stem.

        Returns:
            str: Base name of the texture.
        """
        texture = str(texture_stem)
        return "_".join(texture.split("_")[:-1])

    def build_texture_catalog(self):
        """Build a catalog of textures organized by base name.

        Returns:
            dict: Dictionary mapping texture base names to lists of texture files.
        """
        texture_dict = {}
        for img in self.img_list:
            texture = pathlib.Path(img)
            texture_base_name = self.get_texture_base_name(texture.stem)
            try:
                txt_tmp_list = texture_dict[texture_base_name]
            except KeyError:
                txt_tmp_list = []

            txt_tmp_list.append(img)
            texture_dict[texture_base_name] = txt_tmp_list
        return texture_dict


def get_texture_from_node(file):
    """Get texture file path as a pathlib object.

    Args:
        file (str): File path.

    Returns:
        pathlib.Path: Base color texture path.
    """
    return pathlib.Path(file)


class TextureFileNode:
    """Class to manage Maya File nodes."""

    def __init__(self, path, filename, single_place_node=None):
        """Initialize the TextureFileNode.

        Args:
            path (str): Path to the texture file.
            filename (str): Name of the texture file.
            single_place_node (optional): Place node for texture. Defaults to None.
        """
        self.texture_recognition = file.TextureFile(path=path, filename=filename)

        self.place_node = single_place_node if single_place_node else False

        file_name_filenode = (
            self.texture_recognition.mesh
            + "_"
            + self.texture_recognition.channel
            + "."
            + self.texture_recognition.texture_set
            + "."
            + self.texture_recognition.ext
        )

        self.filenode = self.connect_file_node(
            path=path, name=file_name_filenode, single_place_node=single_place_node
        )

    def connect_placement(self, place_node, file_node):
        """Connect place node to file node.

        Args:
            place_node: Place2D texture node.
            file_node: File node.
        """
        pm.connectAttr(f"{place_node}.coverage", f"{file_node}.coverage")
        pm.connectAttr(f"{place_node}.translateFrame", f"{file_node}.translateFrame")
        pm.connectAttr(f"{place_node}.rotateFrame", f"{file_node}.rotateFrame")
        pm.connectAttr(f"{place_node}.mirrorU", f"{file_node}.mirrorU")
        pm.connectAttr(f"{place_node}.mirrorV", f"{file_node}.mirrorV")
        pm.connectAttr(f"{place_node}.stagger", f"{file_node}.stagger")
        pm.connectAttr(f"{place_node}.wrapU", f"{file_node}.wrapU")
        pm.connectAttr(f"{place_node}.wrapV", f"{file_node}.wrapV")
        pm.connectAttr(f"{place_node}.repeatUV", f"{file_node}.repeatUV")
        pm.connectAttr(f"{place_node}.offset", f"{file_node}.offset")
        pm.connectAttr(f"{place_node}.rotateUV", f"{file_node}.rotateUV")
        pm.connectAttr(f"{place_node}.noiseUV", f"{file_node}.noiseUV")
        pm.connectAttr(f"{place_node}.vertexUvOne", f"{file_node}.vertexUvOne")
        pm.connectAttr(f"{place_node}.vertexUvTwo", f"{file_node}.vertexUvTwo")
        pm.connectAttr(f"{place_node}.vertexUvThree", f"{file_node}.vertexUvThree")
        pm.connectAttr(f"{place_node}.vertexCameraOne", f"{file_node}.vertexCameraOne")
        pm.connectAttr(f"{place_node}.outUV", f"{file_node}.uv")
        pm.connectAttr(f"{place_node}.outUvFilterSize", f"{file_node}.uvFilterSize")

    def connect_file_node(
        self, path, name, single_place_node, gamma_correct=True, alpha_is_luminance=True
    ):
        """Create and connect a file node.

        Args:
            path (str): Path to the texture file.
            name (str): Name of the texture file.
            single_place_node: Place node for texture.
            gamma_correct (bool): Apply gamma correction. Defaults to True.
            alpha_is_luminance (bool): Use alpha as luminance. Defaults to True.

        Returns:
            node: File node object.
        """
        tex_name, texture_set, ext = name.split(".")

        # creation node
        file_node = pm.shadingNode(
            "file", name=tex_name + "_tex", asTexture=True, isColorManaged=True
        )
        file_node.fileTextureName.set(path + "/" + name)

        # uvTilingMode -- UDIM -> 3
        if texture_set.isdigit():
            file_node.uvTilingMode.set(3)

        # alphaIsLuminance
        if (
            self.texture_recognition.channel == config.BACKLIGHT
            or self.texture_recognition.channel == config.SPECULAR_WEIGHT
            or self.texture_recognition.channel == config.SPECULAR_ROUGHNESS
            or self.texture_recognition.channel == config.FRESNEL
            or self.texture_recognition.channel == config.NORMAL
            or self.texture_recognition.channel == config.HEIGHT
        ):
            file_node.alphaIsLuminance.set(True)
        else:
            file_node.alphaIsLuminance.set(False)

        # Color Space
        if (
            self.texture_recognition.channel == config.DIFFUSE
            or self.texture_recognition.channel == config.SPECULAR_COLOR
        ):
            file_node.colorSpace.set("sRGB")
        else:
            file_node.colorSpace.set("Raw")

        # place node connect
        if single_place_node is None:
            multi_place_node = pm.shadingNode("place2dTexture", asUtility=True)
            self.connect_placement(multi_place_node, file_node)
        else:
            self.connect_placement(self.place_node, file_node)

        return file_node


class TexturePxrTexture:
    """Class to manage Renderman PxrTexture nodes."""

    def __init__(self, path, filename):
        """Initialize the TexturePxrTexture.

        Args:
            path (str): Path to the texture file.
            filename (str): Name of the texture file.
        """
        self.texture_recognition = file.TextureFile(path=path, filename=filename)

        file_name_filenode = (
            self.texture_recognition.mesh
            + "_"
            + self.texture_recognition.channel
            + "."
            + self.texture_recognition.texture_set
            + "."
            + self.texture_recognition.ext
        )

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
        tex_name, texture_set, ext = name.split(".")

        # creation node
        pxrtexture_node = pm.shadingNode("PxrTexture", name=tex_name + "_tex", asTexture=True)
        pxrtexture_node.filename.set(path + "/" + name)

        # uvTilingMode -- UDIM -> 3
        if texture_set.isdigit():
            pxrtexture_node.filename.set(path + "/" + tex_name + "." + "_MAPID_" + "." + ext)
            pxrtexture_node.atlasStyle.set(1)
        else:
            pxrtexture_node.filename.set(path + "/" + name)

        # Color Space
        if (
            self.texture_recognition.channel == config.DIFFUSE
            or self.texture_recognition.channel == config.SPECULAR_COLOR
        ):
            pxrtexture_node.linearize.set(True)
        else:
            pxrtexture_node.linearize.set(False)

        return pxrtexture_node
