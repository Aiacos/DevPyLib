__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def getDriverDrivenFromConstraint(constraint):
    driver = pm.listConnections(constraint+'.target[0].targetParentMatrix', destination=False)
    driven = pm.listConnections(constraint, source=False)[0]

    return driver, driven

def moveShape(source, destination):
    pn = pm.PyNode
    if isinstance(source, pn):
        pm.parent(source, destination[0], r=True, s=True)
    else:
        pm.parent(pm.PyNode(source[0]).getShape(), destination, r=True, s=True)

def get_distance(obj1, obj2):
    """
    Return distance between two objects
    :param obj1:
    :param obj2:
    :return: distance
    """

    loc0 = pm.spaceLocator()
    loc1 = pm.spaceLocator()
    constraint0 = pm.pointConstraint(obj1, loc0)
    constraint1 = pm.pointConstraint(obj2, loc1)

    def ctr_dist(objA, objB):
        Ax, Ay, Az = objA.getTranslation(space="world")
        Bx, By, Bz = objB.getTranslation(space="world")
        return ((Ax - Bx) ** 2 + (Ay - By) ** 2 + (Az - Bz) ** 2) ** 0.5

    distance = ctr_dist(loc0, loc1)
    # distance = pm.distanceDimension(loc0, loc1)
    pm.delete(constraint0, constraint1, loc0, loc1)
    return distance


# function to lock and hide attributes
def lock_and_hide_all(node):
    """
    lock and hide all transform attributes of selected node
    :param node: node to be affected
    """
    node.tx.set(l=1, k=0, cb=0)
    node.ty.set(l=1, k=0, cb=0)
    node.tz.set(l=1, k=0, cb=0)
    node.rx.set(l=1, k=0, cb=0)
    node.ry.set(l=1, k=0, cb=0)
    node.rz.set(l=1, k=0, cb=0)
    node.sx.set(l=1, k=0, cb=0)
    node.sy.set(l=1, k=0, cb=0)
    node.sz.set(l=1, k=0, cb=0)

# function to unlock and unhide attributes
def unlock_and_unhide_all(node):
    """
    unlock and unhide all transform attributes of selected node
    :param node: node to be affected
    """
    node.tx.set(l=0, k=1, cb=0)
    node.ty.set(l=0, k=1, cb=0)
    node.tz.set(l=0, k=1, cb=0)
    node.rx.set(l=0, k=1, cb=0)
    node.ry.set(l=0, k=1, cb=0)
    node.rz.set(l=0, k=1, cb=0)
    node.sx.set(l=0, k=1, cb=0)
    node.sy.set(l=0, k=1, cb=0)
    node.sz.set(l=0, k=1, cb=0)

# function to make surface not render
def no_render(tgt):
    """
    makes selected node non-renderable
    :param tgt: node to be affected
    """
    tgt.castsShadows.set(0)
    tgt.receiveShadows.set(0)
    tgt.motionBlur.set(0)
    tgt.primaryVisibility.set(0)
    tgt.smoothShading.set(0)
    tgt.visibleInReflections.set(0)
    tgt.visibleInRefractions.set(0)
