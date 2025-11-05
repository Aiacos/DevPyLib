"""Pole vector creation and positioning utilities for IK chains.

Provides the PoleVector class for automatically creating and positioning
pole vector locators for IK handles based on joint chain geometry.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class PoleVector():
    def __init__(self, ik_handle):
        if ik_handle:
            ik_handle = pm.ls(ik_handle)[0]
            self.poleVector, self.poleVectorGrp = self.connect_pole_vector(ik_handle)

    def create_pv(self, ik_handle):
        '''
        Create a Locator in a correct plane to usa as Pole Vector
        :param ik_handle: select an ik_handle
        :return: grupped locator
        '''

        ik_handle_name = ik_handle.name()
        selJoints = ik_handle.getJointList()
        pm.select(selJoints[-1])
        pm.pickWalk(d='down')
        newJoints = pm.ls(sl=True)
        selJoints.append(newJoints[0])

        # Create a locator and group it twice
        poleVector_locator = pm.spaceLocator(n=ik_handle_name + '_PV' + '_LOC')
        poleVector_group = pm.group(poleVector_locator, n=ik_handle_name + '_PV' + '_LOC' + '_GRP')

        # Point constrain it between the three joints
        pointConstraint = pm.pointConstraint(selJoints, poleVector_group)
        pm.delete(pointConstraint)

        # Create an aim constraint for the locator to aim at the middle joint
        aimConstraint = pm.aimConstraint(selJoints[1], poleVector_group)
        pm.delete(aimConstraint)

        ##Snap grupLocator to middle joint
        # snap = pm.pointConstraint( selJoints[1], poleVector_group, skip=('y','z'))

        return poleVector_group

    def get_joint_distance(self, ik_handle):
        '''
        Return the length of ik_handle
        :param ik_handle: select an ik_handle
        :return: Return the length of ik_handle
        '''

        # Put all three joints in a variable based on a selected ik_handle
        selJoints = ik_handle.getJointList()
        pm.select(selJoints[-1])
        pm.pickWalk(d='down')
        newJoints = pm.ls(sl=True)
        selJoints.append(newJoints[0])
        loc0 = pm.spaceLocator()
        loc1 = pm.spaceLocator()
        constraint0 = pm.pointConstraint(selJoints[0], loc0)
        constraint1 = pm.pointConstraint(selJoints[2], loc1)

        def ctr_dist(obj_a, obj_b):
            Ax, Ay, Az = obj_a.getTranslation(space="world")
            Bx, By, Bz = obj_b.getTranslation(space="world")
            return ((Ax - Bx) ** 2 + (Ay - By) ** 2 + (Az - Bz) ** 2) ** 0.5

        distance = ctr_dist(loc0, loc1)
        pm.delete(constraint0, constraint1, loc0, loc1)
        return distance

    def connect_pole_vector(self, ik_handle):
        poleVector_locator_grp = self.create_pv(ik_handle)

        # Calculate ik_handle length to set as pv -X axis
        distance = int(self.get_joint_distance(ik_handle) / 2)
        # Move the Locator Group in the -X axis (Object Space)
        pm.move(distance, 0, 0, poleVector_locator_grp, objectSpace=True, relative=True)

        # Connect PoleVector
        poleVector_loc = pm.listRelatives(poleVector_locator_grp, children=True)[0]
        pm.poleVectorConstraint(poleVector_loc, ik_handle)

        return poleVector_loc, poleVector_locator_grp

    def get_pole_vector(self):
        return self.poleVector, self.poleVectorGrp


if __name__ == "__main__":
    PoleVector()
