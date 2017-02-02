import pymel.core as pm


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
