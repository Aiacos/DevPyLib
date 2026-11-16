"""Check of the Spring_Chain node network and its solver plugin. Run with mayapy, not with pytest.

    mayapy mayaLib/test/spring_chain_mayapy_check.py

Builds the network of 'spring_network.py' on plain transforms (no Arise needed), with the
'springChainSolver' plugin, and checks it in DG and in Parallel evaluation. Prints
'SPRING_CHAIN_CHECK PASSED' and exits 0 on success.
"""

import importlib.util
import math
import sys
from pathlib import Path

import maya.standalone

maya.standalone.initialize(name="python")

import maya.api.OpenMaya as om  # noqa: E402
import maya.cmds as cmds  # noqa: E402

MAYALIB = Path(__file__).resolve().parents[1]
UTILS = MAYALIB / "ariseLib" / "io_modules_nodes" / "Spring_Chain" / "versions" / "001" / "utils"
PLUGIN = MAYALIB / "plugin" / "spring_chain_solver.py"
FRAMES = [5, 12, 20, 33, 45]
FAILURES = []
RECORDED = {}


def load(name):
    """Load a module of the node 'utils' folder by path ('001' is not an importable package)."""
    spec = importlib.util.spec_from_file_location(name, UTILS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


spring_network = load("spring_network")


def world_matrix(node):
    """Return the world matrix of 'node' as an MMatrix."""
    return om.MMatrix(cmds.xform(node, query=True, worldSpace=True, matrix=True))


def position(node):
    """Return the world position of 'node' as an MVector."""
    matrix = world_matrix(node)
    return om.MVector(matrix[12], matrix[13], matrix[14])


def axis(node, index):
    """Return a world axis (0 = X, 1 = Y, 2 = Z) of 'node' as an MVector (not normalized)."""
    matrix = world_matrix(node)
    return om.MVector(matrix[index * 4], matrix[index * 4 + 1], matrix[index * 4 + 2])


def matrix_error(node_a, node_b):
    """Return the biggest difference between the world matrices of two nodes."""
    matrix_a, matrix_b = world_matrix(node_a), world_matrix(node_b)
    return max(abs(matrix_a[index] - matrix_b[index]) for index in range(16))


def check(label, name, condition, detail=""):
    """Record a failed check."""
    if not condition:
        FAILURES.append(f"{label} | {name} | {detail}")


def advance(frame):
    """Go to 'frame' and evaluate every joint, like the viewport does on each frame of a playback.

    The solver keeps state: a frame nobody evaluates is a jump in time for it, and it resets.
    """
    cmds.currentTime(frame)
    for joint in cmds.ls(type="joint"):
        cmds.getAttr(joint + ".translateX")


def play(start, end):
    """Step through the frames one by one, like playback does."""
    for frame in range(start, end + 1):
        advance(frame)


def build_scene(joint_count, delayed_twist, animate_space=False, mirrored=False, tag=""):
    """Create a lead with a zig-zag chain under it and build the spring network on it.

    Returns:
        dict: with 'lead', 'space', 'rest' (list), 'joints' (list).
    """
    space = cmds.group(empty=True, name=f"{tag}space_grp")
    if mirrored:
        cmds.setAttr(space + ".scaleX", -1)
    lead = cmds.parent(cmds.spaceLocator(name=f"{tag}lead")[0], space)[0]
    cmds.setAttr(lead + ".translate", 0, 10, 0, type="double3")
    cmds.addAttr(
        lead, longName="spring_weight", minValue=0, maxValue=1, defaultValue=1, keyable=True
    )
    cmds.addAttr(lead, longName="lag", minValue=0, defaultValue=2, keyable=True)
    cmds.addAttr(lead, longName="damping", minValue=0.05, maxValue=1, defaultValue=1, keyable=True)

    points = [om.MVector(0.5 * (index % 2), -2.0 * index, 0) for index in range(joint_count)]
    rest, ups = [], []
    for index, point in enumerate(points):
        if index < joint_count - 1:
            y_axis = (points[index + 1] - point).normal()
        else:
            y_axis = (point - points[index - 1]).normal()
        x_axis = (y_axis ^ om.MVector(0, 0, 1)).normal()
        matrix = [x_axis.x, x_axis.y, x_axis.z, 0, y_axis.x, y_axis.y, y_axis.z, 0]
        matrix += [0, 0, 1, 0, point.x, point.y, point.z, 1]
        node = cmds.parent(cmds.group(empty=True, name=f"{tag}rest_{index}"), lead)[0]
        cmds.xform(node, objectSpace=True, matrix=matrix)
        rest.append(node)

        up = cmds.parent(cmds.group(empty=True, name=f"{tag}up_{index}"), node)[0]
        cmds.xform(up, objectSpace=True, matrix=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1])
        ups.append(up)

    joints = []
    for index in range(joint_count):
        cmds.select(clear=True)
        joint = cmds.joint(name=f"{tag}chain_{index}")
        if joints:
            joint = cmds.parent(joint, joints[-1])[0]
        joints.append(joint)

    spring_network.build_spring_chain(
        prefix=f"{tag}sc",
        rest_points=rest,
        up_points=ups if delayed_twist else None,
        joints=joints,
        lead=lead,
        lag_attr=lead + ".lag",
        damping_attr=lead + ".damping",
        weight_attr=lead + ".spring_weight",
        space=space if animate_space is not None else None,
    )

    for attr, value in (("translateX", 20.0), ("rotateY", 180.0)):
        cmds.setKeyframe(lead, attribute=attr, time=1, value=0.0)
        cmds.setKeyframe(lead, attribute=attr, time=40, value=value)
    cmds.keyTangent(lead, inTangentType="linear", outTangentType="linear")

    if animate_space:
        cmds.setKeyframe(space, attribute="translateZ", time=1, value=0.0)
        cmds.setKeyframe(space, attribute="translateZ", time=40, value=30.0)
        cmds.keyTangent(space, inTangentType="linear", outTangentType="linear")

    return {"lead": lead, "space": space, "rest": rest, "joints": joints}


def new_scene():
    """Start an empty scene at 24 fps."""
    cmds.file(new=True, force=True)
    cmds.currentUnit(time="film")
    cmds.playbackOptions(minTime=1, maxTime=60)


def rest_lengths(scene):
    """Return the world distance between consecutive rest points."""
    rest = scene["rest"]
    return [(position(rest[i + 1]) - position(rest[i])).length() for i in range(len(rest) - 1)]


def run_checks(mode, joint_count, delayed_twist, mirrored=False):
    """Run every check of one configuration."""
    label = f"{mode} joints={joint_count} twist={delayed_twist} mirrored={mirrored}"
    new_scene()
    scene = build_scene(joint_count, delayed_twist, animate_space=None, mirrored=mirrored)
    joints, rest, lead = scene["joints"], scene["rest"], scene["lead"]

    # jumping in time resets the chain on its rigid pose.
    for name, frame in (("rest_after_jump", 400), ("rest_before_start", -50)):
        cmds.currentTime(frame)
        for joint, point in zip(joints, rest):
            error = matrix_error(joint, point)
            check(label, name, error < 1e-3, f"{joint} error {error:.5f}")

    advance(1)
    first = {}
    for frame in range(2, 46):
        advance(frame)
        if frame not in FRAMES:
            continue
        first[frame] = [position(joint) for joint in joints]
        for index, length in enumerate(rest_lengths(scene)):
            current = (position(joints[index + 1]) - position(joints[index])).length()
            check(label, "lengths", abs(current - length) < 1e-3, f"frame {frame} bone {index}")
        for index in (0, 1):
            error = (position(joints[index]) - position(rest[index])).length()
            check(label, "root_rigid", error < 1e-3, f"frame {frame} joint {index}")

        if frame == 20:
            # evaluating the same frame again must not advance the simulation.
            cmds.dgdirty(allPlugs=True)
            cmds.refresh()
            error = max((position(j) - first[20][i]).length() for i, j in enumerate(joints))
            check(label, "same_frame_idempotent", error < 1e-6, f"error {error:.6f}")
            if joint_count == 8:
                offset = (position(joints[-1]) - position(rest[-1])).length()
                check(label, "lag_exists", offset > 0.5, f"tip offset {offset:.4f}")
                if delayed_twist:
                    joint_z, lead_z = axis(joints[-2], 2).normal(), axis(lead, 2).normal()
                    angle = math.degrees(joint_z.angle(lead_z))
                    check(label, "twist_lags", angle > 5.0, f"angle {angle:.3f}")

    # DG and Parallel must give the same simulation.
    key = (joint_count, delayed_twist, mirrored)
    if key in RECORDED:
        for frame in FRAMES:
            error = max((a - b).length() for a, b in zip(first[frame], RECORDED[key][frame]))
            check(label, "same_as_dg", error < 1e-4, f"frame {frame} error {error:.6f}")
    else:
        RECORDED[key] = first

    # playing the same range again gives the same result.
    advance(1)
    for frame in range(2, 46):
        advance(frame)
        if frame in FRAMES:
            error = max((position(j) - first[frame][i]).length() for i, j in enumerate(joints))
            check(label, "replay_deterministic", error < 1e-6, f"frame {frame} error {error:.6f}")

    # once the lead stops (frame 40) the chain settles on its rigid pose.
    play(46, 260)
    for joint, point in zip(joints, rest):
        error = matrix_error(joint, point)
        check(label, "settles", error < 2e-3, f"{joint} error {error:.5f}")

    # a ctrl dragged on a paused frame makes the chain react (and lag behind).
    cmds.setAttr(lead + ".translateZ", 6)
    offset = (position(joints[-1]) - position(rest[-1])).length()
    check(label, "drag_reacts", offset > 0.5, f"tip offset {offset:.4f}")
    for joint_index in (0, 1):
        error = (position(joints[joint_index]) - position(rest[joint_index])).length()
        check(label, "drag_root_rigid", error < 1e-3, f"joint {joint_index}")
    cmds.setAttr(lead + ".translateZ", 0)

    # weight 0 = rigid chain.
    advance(1)
    play(2, 20)
    cmds.setAttr(lead + ".spring_weight", 0)
    for joint, point in zip(joints, rest):
        error = matrix_error(joint, point)
        check(label, "weight_zero", error < 1e-3, f"{joint} error {error:.5f}")
    cmds.setAttr(lead + ".spring_weight", 1)

    # scaled lead: bones scale with it.
    cmds.setAttr(lead + ".scale", 2, 2, 2, type="double3")
    advance(1)
    play(2, 20)
    for index, length in enumerate(rest_lengths(scene)):
        current = (position(joints[index + 1]) - position(joints[index])).length()
        check(label, "scaled_lead", abs(current - length) < 2e-3, f"bone {index}")
    for joint in joints:
        for index in range(3):
            scale = axis(joint, index).length()
            check(
                label, "scaled_lead", abs(scale - 2.0) < 1e-3, f"{joint} axis {index} {scale:.5f}"
            )


def run_edit_check(mode):
    """After a key is set on a frame that was already played, replaying shows the new animation."""
    label = f"{mode} edit"

    def edit(lead):
        cmds.currentTime(12)
        cmds.setAttr(lead + ".translateX", 15)
        cmds.setKeyframe(lead, attribute="translateX")

    new_scene()
    truth = build_scene(8, True, animate_space=None)
    edit(truth["lead"])
    advance(1)
    play(2, 20)
    expected = [position(joint) for joint in truth["joints"]]

    new_scene()
    scene = build_scene(8, True, animate_space=None)
    advance(1)
    play(2, 45)
    edit(scene["lead"])
    advance(1)
    play(2, 20)
    for index, joint in enumerate(scene["joints"]):
        error = (position(joint) - expected[index]).length()
        check(label, "edit_then_replay", error < 1e-4, f"{joint} error {error:.5f}")


def run_space_check(mode):
    """With a spring space, the motion of the space itself must not be delayed."""
    label = f"{mode} space"
    new_scene()
    still = build_scene(8, True, animate_space=False)
    advance(1)
    play(2, 20)
    expected = [position(joint) for joint in still["joints"]]

    new_scene()
    moving = build_scene(8, True, animate_space=True)
    advance(1)
    play(2, 20)
    shift = position(moving["space"])
    for index, joint in enumerate(moving["joints"]):
        error = (position(joint) - (expected[index] + shift)).length()
        check(label, "space_local", error < 1e-3, f"{joint} error {error:.5f}")


def run_two_chains_check(mode):
    """Two chains in the same scene keep separate states."""
    label = f"{mode} two chains"
    new_scene()
    single = build_scene(8, True, animate_space=None)
    advance(1)
    play(2, 20)
    expected = [position(joint) for joint in single["joints"]]

    new_scene()
    first = build_scene(8, True, animate_space=None, tag="a_")
    second = build_scene(8, True, animate_space=None, tag="b_")
    cmds.setAttr(second["lead"] + ".lag", 5)
    advance(1)
    play(2, 20)
    for index, joint in enumerate(first["joints"]):
        error = (position(joint) - expected[index]).length()
        check(label, "independent_state", error < 1e-4, f"{joint} error {error:.5f}")
    slower = (position(second["joints"][-1]) - position(first["joints"][-1])).length()
    check(label, "lag_attr_changes_motion", slower > 0.5, f"tip difference {slower:.4f}")


def main():
    """Run all configurations in DG and Parallel evaluation."""
    cmds.loadPlugin(str(PLUGIN))
    for mode in ("off", "parallel"):
        cmds.evaluationManager(mode=mode)
        actual = cmds.evaluationManager(query=True, mode=True)[0]
        print(f"evaluation mode requested '{mode}', active '{actual}'")
        for joint_count in (8, 3):
            for delayed_twist in (True, False):
                run_checks(actual, joint_count, delayed_twist)
                run_checks(actual, joint_count, delayed_twist, mirrored=True)
        run_edit_check(actual)
        run_space_check(actual)
        run_two_chains_check(actual)

    if FAILURES:
        print(f"SPRING_CHAIN_CHECK FAILED ({len(FAILURES)} failures)")
        for failure in FAILURES[:60]:
            print("  " + failure)
        return 1

    print("SPRING_CHAIN_CHECK PASSED")
    return 0


if __name__ == "__main__":
    code = main()
    sys.stdout.flush()
    maya.standalone.uninitialize()
    sys.exit(code)
