__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import common


def spaces(driverList, driverNames, destinationConstraint, destinationAttribute, name='Space', maintainOffset=True):
    """
    Add spaces
    :param driverList: list(str), driver object list
    :param driverNames: list(str), attrviute value name for each driver
    :param destination: str, destination obj
    :param name: str, name of the attribute
    :param maintainOffset: bool, constraint maintainOffset
    :return:
    """
    pm.addAttr(destinationAttribute, longName=name, attributeType='enum', enumName=':'.join(driverNames), k=1, dv=0)

    constraintList = []
    for driver in driverList:
        cnst = pm.parentConstraint(driver, destinationConstraint, mo=maintainOffset)
        constraintList.append(cnst)

    for counter, cnst in enumerate(constraintList):
        sourceValue = range(0, len(constraintList))
        targetValue = [0] * len(constraintList)
        targetValue[counter] = 1

        target = pm.listConnections(cnst.target[counter].targetWeight, source=True, plugs=True)[0]
        common.setDrivenKey(destinationAttribute + '.' + name, sourceValue, target, targetValue)


if __name__ == "__main__":
    pass
    #spaces()