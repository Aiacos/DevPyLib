__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class PoleVector():
    def __init__(self, ikHandle):
        if ikHandle:
            self.poleVector, self.poleVectorGrp = self.connect_poleVector(ikHandle)

    def createPV(self, ikHandle):
        '''
        Create a Locator in a correct plane to usa as Pole Vector
        :param ikHandle: select an ikHandle
        :return: grupped locator
        '''

        ikHandle_name = ikHandle
        selJoints = ikHandle.getJointList()
        pm.select(selJoints[-1])
        pm.pickWalk(d='down')
        newJoints = pm.ls(sl=True)
        selJoints.append(newJoints[0])

        # Create a locator and group it twice
        poleVector_locator = pm.spaceLocator(n=ikHandle_name + '_PV' + '_LOC')
        poleVector_group = pm.group(poleVector_locator, n=ikHandle_name + '_PV' + '_LOC' + '_GRP')

        # Point constrain it between the three joints
        pointConstraint = pm.pointConstraint(selJoints, poleVector_group)
        pm.delete(pointConstraint)

        # Create an aim constraint for the locator to aim at the middle joint
        aimConstraint = pm.aimConstraint(selJoints[1], poleVector_group)
        pm.delete(aimConstraint)

        ##Snap grupLocator to middle joint
        # snap = pm.pointConstraint( selJoints[1], poleVector_group, skip=('y','z'))

        return poleVector_group

    def getJointDistance(self, ikHandle):
        '''
        Return the lenght of ikHandle
        :param ikHandle: select an ikHandle
        :return: Return the lenght og ikHandle
        '''

        # Put all three joints in a variable based on a selected ikHandle
        selJoints = ikHandle.getJointList()
        pm.select(selJoints[-1])
        pm.pickWalk(d='down')
        newJoints = pm.ls(sl=True)
        selJoints.append(newJoints[0])
        loc0 = pm.spaceLocator()
        loc1 = pm.spaceLocator()
        constraint0 = pm.pointConstraint(selJoints[0],loc0)
        constraint1 = pm.pointConstraint(selJoints[2],loc1)
        def ctr_dist( objA, objB ):
            Ax, Ay, Az = objA.getTranslation(space="world")
            Bx, By, Bz = objB.getTranslation(space="world")
            return (  (Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2  )**0.5

        distance = ctr_dist(loc0, loc1)
        pm.delete(constraint0, constraint1, loc0, loc1)
        return distance

    def connect_poleVector(self, ikHandle):
        poleVector_locator_grp = self.createPV(ikHandle)

        # Calculate ikHandle lenght to set as pv -X axis
        distance = int(self.getJointDistance(ikHandle)/2)
        # Move the Locator Group in the -X axis (Object Space)
        pm.move(distance, 0, 0, poleVector_locator_grp, objectSpace=True, relative=True)

        # Connect PoleVector
        pm.select(poleVector_locator_grp)
        poleVector_loc = pm.pickWalk(d='down')
        pm.poleVectorConstraint(poleVector_loc, ikHandle)

        return poleVector_loc, poleVector_locator_grp

    def getPoleVector(self):
        return self.poleVector, self.poleVectorGrp


if __name__ == "__main__":
    PoleVector()

