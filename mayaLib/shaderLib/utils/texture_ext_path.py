__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def replacePath(fileName, oldPath, newPath):
    newString = fileName.replace(oldPath,newPath)
    return newString


def changeExtension(filename,newExtension):
    (prefix, sep, suffix) = filename.rpartition('.')
    return prefix + newExtension


def replace_ext(ext, file_name_attribute, file_type):
    """
    Replace all file extension in a given list
    :param file_node_type: 'file' or 'PxrTexture'
    :param ext: '.tex' or '.tx'
    :param fileTextureAttribute: Arnold -> '.fileTextureName' or Renderman '.filename'
    :return:
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
    """
    Replace all file path in a given list
    :param file_node_type: 'file' or 'PxrTexture'
    :param path:
    :param fileTextureAttribute: Arnold -> '.fileTextureName' or Renderman '.filename'
    :return:
    """
    # Gets all 'file' nodes in maya
    file_list = pm.ls(type=file_type)

    # For each file node..
    for f in file_list:
        # Get the name of the image attached to it
        texture_filename = pm.getAttr(f + file_name_attribute)
        new_tex = replacePath(texture_filename, oldPath, path)
        pm.setAttr(f + file_name_attribute, new_tex, type="string")
