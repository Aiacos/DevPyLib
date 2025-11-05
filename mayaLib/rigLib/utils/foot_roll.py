"""Foot roll builder utilities for rigging."""

from __future__ import annotations

import pymel.core as pm

from mayaLib.rigLib.utils import common, name

# pylint: disable=too-many-instance-attributes,too-many-arguments
# pylint: disable=too-many-positional-arguments,too-many-locals


class FootRoll:
    """Build foot roll hierarchies for a rigged limb."""

    def __init__(
        self,
        hip_joint,
        ankle_joint,
        ball_joint_list,
        toe_end_joint_list,
        do_smart_foot_roll=True,
    ):
        """Initialise the foot roll rig for the provided joints.

        Args:
            hip_joint: Hip joint name.
            ankle_joint: Ankle joint name.
            ball_joint_list: List of ball joints.
            toe_end_joint_list: List of toe end joints.
            do_smart_foot_roll: Whether to create smart roll groups.
        """
        self.side = name.get_side(hip_joint)

        self.ball_ik_handles: list[pm.PyNode] = []
        self.toe_ik_handles: list[pm.PyNode] = []
        self.prefix_joint_hip = name.remove_suffix(hip_joint)
        self.prefix_joint_ankle = name.remove_suffix(ankle_joint)
        self.ankle_ik_handle = pm.ikHandle(
            n=f'{self.prefix_joint_hip}_IKH', sj=hip_joint, ee=ankle_joint
        )[0]

        for ball_joint in ball_joint_list:
            ball_joint_parent = pm.ls(ball_joint)[0].getParent()
            prefix = name.remove_suffix(ball_joint)
            ball_ik = pm.ikHandle(
                n=f'{prefix}Ball_IKH', sj=ball_joint_parent, ee=ball_joint
            )[0]
            self.ball_ik_handles.append(ball_ik)

        for toe_joint, ball_joint in zip(toe_end_joint_list, ball_joint_list):
            prefix = name.remove_suffix(toe_joint)
            toe_ik = pm.ikHandle(
                n=f'{prefix}Fng_IKH', sj=ball_joint, ee=toe_joint
            )[0]
            self.toe_ik_handles.append(toe_ik)

        # set temporarily ON Sticky
        self.set_sticky(1)

        self.peel_heel()
        self.toe_tap()
        self.tippy_toe()

        if do_smart_foot_roll:
            front_roll_loc = f'{self.prefix_joint_ankle}_frontRoll_LOC'
            back_roll_loc = f'{self.prefix_joint_ankle}_backRoll_LOC'
            inner_roll_loc = f'{self.prefix_joint_ankle}_innerRoll_LOC'
            outer_roll_loc = f'{self.prefix_joint_ankle}_outerRoll_LOC'
            (
                self.front_roll_grp,
                self.back_roll_grp,
                self.inner_roll_grp,
                self.outer_roll_grp,
            ) = self.roll_groups(
                front_roll_loc,
                back_roll_loc,
                inner_roll_loc,
                outer_roll_loc,
            )
        else:
            self.front_roll_grp = self.back_roll_grp = None
            self.inner_roll_grp = self.outer_roll_grp = None

        self.move_grp()

        # Legacy attribute mirrors for compatibility.
        self.ballIkHandleList = self.ball_ik_handles  # pylint: disable=invalid-name
        self.toeIkHandleList = self.toe_ik_handles  # pylint: disable=invalid-name
        self.prefixJnt1 = self.prefix_joint_hip  # pylint: disable=invalid-name
        self.prefixJnt2 = self.prefix_joint_ankle  # pylint: disable=invalid-name
        self.ankleIkHandle = self.ankle_ik_handle  # pylint: disable=invalid-name

        self.peelHeelGrp = self.peel_heel_grp  # pylint: disable=invalid-name
        self.toeTapGrp = self.toe_tap_grp  # pylint: disable=invalid-name
        self.tippyToeGrp = self.tippy_toe_grp  # pylint: disable=invalid-name
        self.frontRollGrp = self.front_roll_grp  # pylint: disable=invalid-name
        self.backRollGrp = self.back_roll_grp  # pylint: disable=invalid-name
        self.innerRollGrp = self.inner_roll_grp  # pylint: disable=invalid-name
        self.outerRollGrp = self.outer_roll_grp  # pylint: disable=invalid-name
        self.moveGrp = self.move_grp_node  # pylint: disable=invalid-name

        # set OFF Sticky
        self.set_sticky(0)

    def set_sticky(self, val=0):
        """Toggle stickiness on all IK handles."""
        self.ankle_ik_handle.stickiness.set(val)
        for ball_ik_handle in self.ball_ik_handles:
            ball_ik_handle.stickiness.set(val)
        for toe_ik_handle in self.toe_ik_handles:
            toe_ik_handle.stickiness.set(val)

    def peel_heel(self):
        """Create the peel heel group and centre its pivot."""
        self.peel_heel_grp = pm.group(
            self.ankle_ik_handle,
            n=f'{self.prefix_joint_ankle}PeelHeel_GRP',
        )
        mid_index = int(round(len(self.ball_ik_handles) / 2.0)) - 1
        mid_ball_joint = self.ball_ik_handles[mid_index]
        common.center_pivot(self.peel_heel_grp, mid_ball_joint)

    def toe_tap(self):
        """Create the toe tap group and centre its pivot."""
        self.toe_tap_grp = pm.group(
            self.ball_ik_handles,
            self.toe_ik_handles,
            n=f'{self.prefix_joint_ankle}ToeTap_GRP',
        )
        mid_index = int(round(len(self.ball_ik_handles) / 2.0)) - 1
        mid_ball_joint = self.ball_ik_handles[mid_index]
        common.center_pivot(self.toe_tap_grp, mid_ball_joint)

    def tippy_toe(self):
        """Create the tippy toe group and centre its pivot."""
        self.tippy_toe_grp = pm.group(
            self.toe_tap_grp,
            self.peel_heel_grp,
            n=f'{self.prefix_joint_ankle}TippyToe_GRP',
        )
        mid_index = int(round(len(self.toe_ik_handles) / 2.0)) - 1
        mid_toe_joint = self.toe_ik_handles[mid_index]
        common.center_pivot(self.tippy_toe_grp, mid_toe_joint)

    def roll_groups(self, front_roll_loc, back_roll_loc, inner_roll_loc, outer_roll_loc):
        """Create optional roll groups aligned with locator references."""
        front_roll_grp = back_roll_grp = inner_roll_grp = outer_roll_grp = None
        locators = (
            front_roll_loc,
            back_roll_loc,
            inner_roll_loc,
            outer_roll_loc,
        )
        if all(pm.objExists(loc) for loc in locators):
            front_loc = pm.ls(front_roll_loc)[0]
            back_loc = pm.ls(back_roll_loc)[0]
            inner_loc = pm.ls(inner_roll_loc)[0]
            outer_loc = pm.ls(outer_roll_loc)[0]

            front_roll_grp = pm.group(
                self.tippy_toe_grp, n=f'{name.remove_suffix(front_loc)}_GRP'
            )
            back_roll_grp = pm.group(
                front_roll_grp, n=f'{name.remove_suffix(back_loc)}_GRP'
            )
            inner_roll_grp = pm.group(
                back_roll_grp, n=f'{name.remove_suffix(inner_loc)}_GRP'
            )
            outer_roll_grp = pm.group(
                inner_roll_grp, n=f'{name.remove_suffix(outer_loc)}_GRP'
            )

            common.center_pivot(front_roll_grp, front_loc)
            common.center_pivot(back_roll_grp, back_loc)
            common.center_pivot(inner_roll_grp, inner_loc)
            common.center_pivot(outer_roll_grp, outer_loc)

        return front_roll_grp, back_roll_grp, inner_roll_grp, outer_roll_grp

    def move_grp(self):
        """Create the final move group centred on the ankle IK handle."""
        if self.outer_roll_grp:
            group = pm.group(
                self.outer_roll_grp, n=f'{self.prefix_joint_ankle}Move_GRP'
            )
        else:
            group = pm.group(
                self.tippy_toe_grp, n=f'{self.prefix_joint_ankle}Move_GRP'
            )

        common.center_pivot(group, self.ankle_ik_handle)
        self.move_grp_node = group
        self.moveGrp = group  # pylint: disable=invalid-name

    def get_group_list(self):
        """Return the created group nodes in hierarchy order."""
        return (
            self.peel_heel_grp,
            self.toe_tap_grp,
            self.tippy_toe_grp,
            self.front_roll_grp,
            self.back_roll_grp,
            self.inner_roll_grp,
            self.outer_roll_grp,
            self.move_grp_node,
        )

    def get_ik_finger_list(self):
        """Return the toe IK handles."""
        return self.toe_ik_handles

    def get_ik_ball_list(self):
        """Return the ball IK handles."""
        return self.ball_ik_handles

    def get_limb_ik(self):
        """Return the limb IK handle anchored at the ankle."""
        return self.ankle_ik_handle


def create_limb_foot_roll_locators_reference(ankle_joint):
    """Create reference locators to drive smart foot roll groups."""
    prefix = name.remove_suffix(ankle_joint)
    locators = [
        pm.spaceLocator(n=f'{prefix}_frontRoll_LOC'),
        pm.spaceLocator(n=f'{prefix}_backRoll_LOC'),
        pm.spaceLocator(n=f'{prefix}_innerRoll_LOC'),
        pm.spaceLocator(n=f'{prefix}_outerRoll_LOC'),
    ]
    return pm.group(locators, n=f'{prefix}FootRollLocators_GRP')


def mirror_foot_roll_grp(foot_roll_locator_grp):
    """Duplicate and mirror a left foot roll locator group to the right side."""
    loc_grp = pm.ls(foot_roll_locator_grp)[0]
    new_grp_name = loc_grp.name().replace('l_', 'r_', 1)
    dupli_loc_grp = pm.duplicate(loc_grp, n=new_grp_name)[0]

    for obj in pm.listRelatives(dupli_loc_grp, c=True):
        pm.rename(obj, obj.name().replace('l_', 'r_', 1))

    dupli_loc_grp.scaleX.set(-1)
    common.freeze_transform(dupli_loc_grp)

    return dupli_loc_grp


if __name__ == "__main__":
    raise SystemExit('Invoke within Maya to build foot roll rigs.')
