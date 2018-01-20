__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def nameCheck(name):
    """
    Return new univocal Name
    :param name: str
    :return: str
    """
    nameList = pm.ls(name)
    nameCount = len(nameList)

    newNameRPart = str(name).rpartition('_')
    newName = newNameRPart[0] + str(nameCount + 1) + newNameRPart[1] + newNameRPart[2]
    return newName
