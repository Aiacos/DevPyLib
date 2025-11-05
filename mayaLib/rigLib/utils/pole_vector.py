"""Pole vector creation and positioning utilities for IK chains.

Provides the PoleVector class for automatically creating and positioning
pole vector locators for IK handles based on joint chain geometry.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class PoleVector():
    """Automatic pole vector locator creation and positioning for IK chains.

    Automatically creates and positions a pole vector locator for IK handles based on
    the chain's geometry. Calculates optimal pole vector placement using the joint chain
    distance and creates proper constraints for intuitive control of IK limbs.

    Attributes:
        poleVector: The pole vector locator node
        poleVectorGrp: The group containing the pole vector

    Example:
        >>> pv = PoleVector('arm_IK')
        >>> pv_loc, pv_grp = pv.get_pole_vector()
    """
    def __init__(self, ik_handle):
        """Initialize pole vector setup for an IK handle.

        Creates and positions a pole vector locator for the given IK handle,
        automatically calculating optimal placement based on joint chain geometry.

        Args:
            ik_handle: Maya IK handle node to create pole vector for

        Attributes:
            poleVector: The created pole vector locator node
            poleVectorGrp: The group containing the pole vector locator
        """
        if ik_handle:
            ik_handle = pm.ls(ik_handle)[0]
            self.pole_vector, self.pole_vector_grp = self.connect_pole_vector(ik_handle)

    def create_pv(self, ik_handle):
        '''
        Create a Locator in a correct plane to usa as Pole Vector
        :param ik_handle: select an ik_handle
        :return: grupped locator
        '''

        ik_handle_name = ik_handle.name()
        sel_joints = ik_handle.getJointList()
        pm.select(sel_joints[-1])
        pm.pickWalk(d='down')
        new_joints = pm.ls(sl=True)
        sel_joints.append(new_joints[0])

        # Create a locator and group it twice
        pole_vector_locator = pm.spaceLocator(n=ik_handle_name + '_PV' + '_LOC')
        pole_vector_group = pm.group(pole_vector_locator, n=ik_handle_name + '_PV' + '_LOC' + '_GRP')

        # Point constrain it between the three joints
        point_constraint = pm.pointConstraint(sel_joints, pole_vector_group)
        pm.delete(point_constraint)

        # Create an aim constraint for the locator to aim at the middle joint
        aim_constraint = pm.aimConstraint(sel_joints[1], pole_vector_group)
        pm.delete(aim_constraint)

        ##Snap grupLocator to middle joint
        # snap = pm.pointConstraint( sel_joints[1], pole_vector_group, skip=('y','z'))

        return pole_vector_group

    def get_joint_distance(self, ik_handle):
        '''
        Return the length of ik_handle
        :param ik_handle: select an ik_handle
        :return: Return the length of ik_handle
        '''

        # Put all three joints in a variable based on a selected ik_handle
        sel_joints = ik_handle.getJointList()
        pm.select(sel_joints[-1])
        pm.pickWalk(d='down')
        new_joints = pm.ls(sl=True)
        sel_joints.append(new_joints[0])
        loc0 = pm.spaceLocator()
        loc1 = pm.spaceLocator()
        constraint0 = pm.pointConstraint(sel_joints[0], loc0)
        constraint1 = pm.pointConstraint(sel_joints[2], loc1)

        def ctr_dist(obj_a, obj_b):
            """Calculate Euclidean distance between two transform nodes.

            Args:
                obj_a: First transform node
                obj_b: Second transform node

            Returns:
                float: Distance in world space units
            """
            ax, ay, az = obj_a.getTranslation(space="world")
            bx, by, bz = obj_b.getTranslation(space="world")
            return ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5

        distance = ctr_dist(loc0, loc1)
        pm.delete(constraint0, constraint1, loc0, loc1)
        return distance

    def connect_pole_vector(self, ik_handle):
        """Create and connect pole vector to IK handle.

        Creates a pole vector locator, positions it based on the IK chain length,
        and constrains the IK handle to the locator.

        Args:
            ik_handle: Maya IK handle to connect pole vector to

        Returns:
            tuple: (pole_vector_locator, pole_vector_group) nodes
        """
        pole_vector_locator_grp = self.create_pv(ik_handle)

        # Calculate ik_handle length to set as pv -X axis
        distance = int(self.get_joint_distance(ik_handle) / 2)
        # Move the Locator Group in the -X axis (Object Space)
        pm.move(distance, 0, 0, pole_vector_locator_grp, objectSpace=True, relative=True)

        # Connect PoleVector
        pole_vector_loc = pm.listRelatives(pole_vector_locator_grp, children=True)[0]
        pm.poleVectorConstraint(pole_vector_loc, ik_handle)

        return pole_vector_loc, pole_vector_locator_grp

    def get_pole_vector(self):
        """Get the created pole vector nodes.

        Returns:
            tuple: (pole_vector_locator, pole_vector_group) created during initialization
        """
        return self.pole_vector, self.pole_vector_grp


if __name__ == "__main__":
    PoleVector()
