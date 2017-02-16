__author__ = 'Lorenzo Argentieri'

import os
import glob
import pymel.core as pm
from qtshim import QtGui, QtCore, Signal

class Texture():
    """
    Manage a single file texture
    """
    def __init__(self, name, texType, udim, ext):
        self.Name = name
        self.Udim = udim
        self.Ext = ext
        self.Type = texType
        #self.Path = path

    def setName(self, name):
        self.Name = name
    def getName(self):
        return self.Name

    def setPath(self, path):
        self.Path = path
    def getPath(self):
        #return  self.Path
        #return self.Name + self.Type + self.Udim + self.Ext
        return self.Name + '_' + self.Type + '' + self.Udim + '.' + self.Ext

    def setExt(self, ext):
        self.Ext = ext
    def getExt(self):
        return  self.Ext

    def setType(self, texType):
        self.Type = texType
    def getType(self):
        return self.Type
    def setUdim(self, udim):
        self.Udim = udim
    def getUdim(self):
        return self.Udim


class SearchTexture():
    def __init__(self, dirname, ext, type='diffuse'):
        # self.name = None
        # self.path = None
        # self.ext = None
        # self.texType = None
        self.ext = ext
        self.fileList = self._searchInDirectory(dirname,ext)
        self.materialList = self.filterMaterialsName(dirname, ext, type)

    def _searchInDirectory(self, dirname, ext):
        ext = ext.lower()
        texList = []
        for file in os.listdir(dirname):
            if file.endswith(ext):
                texList.append(file)
        return texList

    def _filterType(self, file, type): # -- look for a common texture like a diffuse
        if file.find(type) > -1:
            return True
        else:
            return False

    def _searchMaterials(self, dirname, ext, type):
        fileList = self.fileList#fileList = self._searchInDirectory(dirname, ext)
        typeList = []
        for file in fileList:
            if self._filterType(file, type):
                typeList.append(file)

        return typeList

    def filterMaterialsName(self, dirname, ext, type): # -- build a a list with all material Name
        '''
        Build a list with all Material Name
        :param dirname: Directory of textures
        :param ext: Texture file extension
        :param type: Texture type (ex: Diffuse, Specular ecc.)
        :return: a list with all Material Name
        '''
        mList = self._searchMaterials(dirname, ext, type)
        materialList = []
        for mat in mList:
            tmp = str(mat).find('_'+type)#(material, udim, ext2)
            materialList.append(str(mat)[0:tmp])

        return materialList

    def filterMaterialsType(self): ### No non va bene, bisogna usare la calsse Texture subito
        for file in self.fileList:
            for name in self.materialList:
                (prefix, sep, suffix) = file.rpartition('.')
                if self._filterType(str(prefix), str(name)):
                    type = str(prefix)[len(name):]
                    return type

    def rPartititon(self, filename):##si puo aggiungere l'oggetto
        '''
        Return a partition of element in file texture name and extension
        :param filename:
        :return: matName, matType, udimPrefix, Ext
        '''
        (rpFilePrefix, rpFileSep, rpFileSuffix) = filename.rpartition('.')
        (matName, matSep, matType) = rpFilePrefix.rpartition('_')
        (udimPrefix, rpSep, rpExt) = rpFileSuffix.rpartition('.')
        if udimPrefix == '':
            return matName, matType, udimPrefix, rpExt
        else:
            return matName, matType, '.'+udimPrefix, rpExt

    def testRP(self):
        for file in self.fileList:
            print self.rPartititon(file)


class TextureManager():
    def __init__(self, workspace, ext, type):
        self.textureList = SearchTexture(workspace, ext, type)

        for file in self.textureList.fileList:##qui puoi creare il dizionario passando come chiave il nome del materiale
            Name, Type, Udim, Ext = self.textureList.rPartititon(file)
            self.texture = Texture(Name, Type, Udim, Ext)
            #print self.texture.getName() + '::' + self.texture.getType()
            print self.texture.getPath()

    def getTextureSet(self, Material):
        '''
        Return all texture for a given material
        :param Material: Name of passed material
        :return: List of string
        '''
        pass


class Material():
    def __init__(self, name, udim, ext, texType):##dovresti passare solo nome del materiale e workspace

        self.diffuse = Texture(name, udim, ext, texType)
        self.backlight = Texture(name, udim, ext, texType)
        self.specularColor = Texture(name, udim, ext, texType)
        self.specularWeight = Texture(name, udim, ext, texType)
        self.specularRoughness = Texture(name, udim, ext, texType)
        self.fresnel = Texture(name, udim, ext, texType)
        self.normal = Texture(name, udim, ext, texType)



test = TextureManager('/Users/lorenzoargentieri/MEGAsync/Lavori/Maya/Underwater/sourceimages',
                      'tx',
                      'Diffuse')

# diffuse = '_Diffuse' + imgFormat #Color
# backlighting = '_Backlighting' + imgFormat #Kb
# specularColor = '_Reflection' + imgFormat #KsColor
# specularWeight = '_SpecularWeight' + imgFormat #Ks
# specularRoughness = '_Roughness' + imgFormat #specularRoughness
# fresnel = '_f0' + imgFormat #Ksn
# normal = '_Normal' + imgFormat #normalCamera