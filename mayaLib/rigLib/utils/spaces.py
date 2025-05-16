__author__ = "Lorenzo Argentieri"

import pymel.core as pm

from mayaLib.rigLib.utils import common


def spaces(
    driverList,
    driverNames,
    destinationConstraint,
    destinationAttribute,
    name="space",
    maintainOffset=True,
):
    """
    Create a space system on the given destinationConstraint with the given list
    of drivers and names. The given destinationAttribute is used to store the value
    of the active space. The value of the active space is used to set the weight of
    the parent constraint on the destinationConstraint. The optional maintainOffset
    parameter is used to set the maintainOffset flag on the parent constraint.

    Args:
        driverList (list): List of objects that will drive the space system
        driverNames (list): List of names associated with the drivers
        destinationConstraint (str): Name of the constraint that will be controlled
            by the space system
        destinationAttribute (str): Name of the attribute that will store the value
            of the active space
        name (str): Name of the attribute that will be added to the destination
            attribute. Defaults to "space"
        maintainOffset (bool): Whether to maintain the offset of the parent
            constraint. Defaults to True

    Returns:
        None
    """
    pm.addAttr(
        destinationAttribute,
        longName=name,
        attributeType="enum",
        enumName=":".join(driverNames),
        k=1,
        dv=0,
    )

    constraintList = []
    for driver in driverList:
        cnst = pm.parentConstraint(driver, destinationConstraint, mo=maintainOffset)
        constraintList.append(cnst)

    for counter, cnst in enumerate(constraintList):
        sourceValue = list(range(0, len(constraintList)))
        targetValue = [0] * len(constraintList)
        targetValue[counter] = 1

        target = pm.listConnections(
            cnst.target[counter].targetWeight, source=True, plugs=True
        )[0]
        common.setDrivenKey(
            destinationAttribute + "." + name, sourceValue, target, targetValue
        )


if __name__ == "__main__":
    pass
    # spaces()
