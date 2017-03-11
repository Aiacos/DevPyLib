__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

# See active Renderer
render_engine = pm.getAttr('defaultRenderGlobals.currentRenderer')

if render_engine == 'arnold':
    new_ext = '.tx'
    file_node_type = 'file'
    fileTextureAttribute = '.fileTextureName'
elif render_engine == 'renderManRIS':
    new_ext = '.tex'
    file_node_type = 'PxrTexture'
    fileTextureAttribute = '.filename'
else:
    print 'No valid active render engine'


filename = '/home/user/somefile'

newPath = path = pm.workspace(q=True, dir=True)+''
oldPath = ''


def replacePath(fileName, oldPath, newPath):
    newString = fileName.replace(oldPath,newPath)
    return newString


def changeExtension(filename,newExtension):
    (prefix, sep, suffix) = filename.rpartition('.')
    return prefix + newExtension


def replace_ext(ext=new_ext, file_name_attribute=fileTextureAttribute, file_type=file_node_type):
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

def replace_path(path, file_name_attribute=fileTextureAttribute, file_type=file_node_type):
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
