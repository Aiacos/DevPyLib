__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def replacePath(fileName, oldPath, newPath):
    """Replace a string in a filename with a new string.

    Args:
        fileName (str): The full path of the file to modify.
        oldPath (str): The string to replace in the filename.
        newPath (str): The new string to insert in the filename.

    Returns:
        str: The modified filename.
    """
    newString = fileName.replace(oldPath, newPath)
    return newString


def changeExtension(filename, newExtension):
    """Change the extension of a filename.

    Args:
        filename (str): The full path of the file to modify.
        newExtension (str): The new extension to apply to the filename.

    Returns:
        str: The modified filename.
    """
    (prefix, sep, suffix) = filename.rpartition('.')
    return prefix + newExtension


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
        new_tex = changeExtension(texture_filename, ext)
        pm.setAttr(f + file_name_attribute, new_tex, type="string")


def replace_path(oldPath, path, file_name_attribute, file_type):
    """Replace all file path in a given list.

    Args:
        oldPath (str): The string to replace in the filename.
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
        new_tex = replacePath(texture_filename, oldPath, path)
        pm.setAttr(f + file_name_attribute, new_tex, type="string")