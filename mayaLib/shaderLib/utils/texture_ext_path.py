__author__ = 'Lorenzo Argentieri'

"""Texture external path management.

Provides utilities for managing external texture file paths and
resolving texture references.
"""

import pymel.core as pm


def _replace_path_string(file_name, old_path, new_path):
    """Replace a string in a filename with a new string.

    Args:
        file_name (str): The full path of the file to modify.
        old_path (str): The string to replace in the filename.
        new_path (str): The new string to insert in the filename.

    Returns:
        str: The modified filename.
    """
    new_string = file_name.replace(old_path, new_path)
    return new_string


def change_extension(filename, new_extension):
    """Change the extension of a filename.

    Args:
        filename (str): The full path of the file to modify.
        new_extension (str): The new extension to apply to the filename.

    Returns:
        str: The modified filename.
    """
    (prefix, sep, suffix) = filename.rpartition('.')
    return prefix + new_extension


def replace_ext(ext, file_name_attribute, file_type):
    """Replace all file extension in a given list.

    Args:
        ext (str): The new extension to apply to all files.
        file_name_attribute (str): The attribute name of the file node where the filename is stored.
        file_type (str): The type of file node to search for, either 'file' or 'PxrTexture'.

    Returns:
        None
    """
    # Gets all 'file' nodes in maya
    file_list = pm.ls(type=file_type)

    # For each file node..
    for f in file_list:
        # Get the name of the image attached to it
        texture_filename = pm.getAttr(f + file_name_attribute)
        new_tex = change_extension(texture_filename, ext)
        pm.setAttr(f + file_name_attribute, new_tex, type="string")


def replace_path(old_path, path, file_name_attribute, file_type):
    """Replace all file path in a given list.

    Args:
        old_path (str): The string to replace in the filename.
        path (str): The new string to insert in the filename.
        file_name_attribute (str): The attribute name of the file node where the filename is stored.
        file_type (str): The type of file node to search for, either 'file' or 'PxrTexture'.

    Returns:
        None
    """
    # Gets all 'file' nodes in maya
    file_list = pm.ls(type=file_type)

    # For each file node..
    for f in file_list:
        # Get the name of the image attached to it
        texture_filename = pm.getAttr(f + file_name_attribute)
        new_tex = _replace_path_string(texture_filename, old_path, path)
        pm.setAttr(f + file_name_attribute, new_tex, type="string")
