"""Maya plugin: 'springChainSolver', a chain of springs that trails behind its first points.

Used by the Arise 'Spring_Chain' node. It reproduces the Control Rig "dynamic chain" (a Spring Interpolate
per bone, each one fed by the bone before it) as a single node that keeps its own state, like mGear's
'mgear_springNode' does for one point.

Every frame, point 'k' moves with a damped spring towards where it would be if the chain was rigid from
the point before it: target = solved[k - 1] + (rigid[k] - rigid[k - 1]). The first 'rigidCount' points
are not delayed. The node only solves positions: keeping the bones length and orienting the joints is
done by the node network that reads 'outPoint'.

State rules (the same idea as mGear):
    - time moved forward by up to one frame: one spring step.
    - time jumped (backwards, or more than one frame): the chain resets on its rigid pose.
    - same frame, same inputs: the step is solved again from its start state, so evaluating a frame
      twice (viewport, bake, attribute editor) never advances the simulation.
    - same frame, inputs moved (a ctrl dragged on a paused frame): a new step, so the chain reacts.

Attributes:
    time (time): connect 'time1.outTime'.
    lag (double): frames of delay each point adds on top of the point before it. 0 = rigid.
    damping (double): damping ratio. 1 = no overshoot, lower values bounce.
    weight (double): 0 = rigid points, 1 = solved points.
    rigidCount (int): number of leading points that are not delayed.
    spaceMatrix (matrix): world matrix of the space the springs live in. Motion of this space is not
        delayed. Identity = world.
    inPoint (double3 array): world positions of the rigid chain.
    outPoint (double3 array): world positions of the solved chain.
"""

import math

import maya.api.OpenMaya as om

NODE_NAME = "springChainSolver"
NODE_ID = om.MTypeId(0x86019)
NODE_CLASSIFY = "utility/general"
MIN_DAMPING = 0.05
MAX_DAMPING = 0.999  # the closed form below is the under-damped one, 0.999 is critical for any eye.
MIN_LAG = 1e-4
SAME_FRAME = 1e-6
MOVED_TOLERANCE = 1e-7


def maya_useNewAPI():  # noqa: N802
    """Tell Maya this plugin uses the Python API 2.0."""


def spring_step(position, velocity, target, omega, damping, delta):
    """Advance a damped spring towards a fixed target. Exact for any step size (never explodes).

    Args:
        position (float): current value.
        velocity (float): current velocity, per frame.
        target (float): value the spring is pulled to.
        omega (float): natural angular frequency, in radians per frame.
        damping (float): damping ratio, below 1.
        delta (float): step size in frames.

    Returns:
        tuple: (new position, new velocity).
    """
    damped = omega * math.sqrt(1.0 - damping * damping)
    offset = position - target
    slope = (velocity + damping * omega * offset) / damped
    decay = math.exp(-damping * omega * delta)
    cosine, sine = math.cos(damped * delta), math.sin(damped * delta)
    new_position = target + decay * (offset * cosine + slope * sine)
    new_velocity = decay * (
        (slope * damped - damping * omega * offset) * cosine
        - (offset * damped + damping * omega * slope) * sine
    )
    return new_position, new_velocity


def solve_chain(rigid, start_positions, start_velocities, rigid_count, lag, damping, delta):
    """Solve one step of the whole chain.

    Args:
        rigid (list): of [x, y, z], the rigid chain positions.
        start_positions (list): of [x, y, z], the solved positions at the start of the step.
        start_velocities (list): of [x, y, z], the velocities at the start of the step.
        rigid_count (int): number of leading points that follow the rigid chain exactly.
        lag (float): frames of delay each point adds.
        damping (float): damping ratio.
        delta (float): step size in frames.

    Returns:
        tuple: (positions, velocities), lists of [x, y, z].
    """
    positions, velocities = [], []
    damping = min(max(damping, MIN_DAMPING), MAX_DAMPING)
    omega = 2.0 * damping / max(lag, MIN_LAG)
    for index, point in enumerate(rigid):
        if index < rigid_count or lag < MIN_LAG:
            positions.append(list(point))
            velocities.append([0.0, 0.0, 0.0])
            continue

        new_position, new_velocity = [], []
        for axis in range(3):
            target = positions[index - 1][axis] + point[axis] - rigid[index - 1][axis]
            value, speed = spring_step(
                start_positions[index][axis],
                start_velocities[index][axis],
                target,
                omega,
                damping,
                delta,
            )
            new_position.append(value)
            new_velocity.append(speed)
        positions.append(new_position)
        velocities.append(new_velocity)

    return positions, velocities


class SpringChainSolver(om.MPxNode):
    """Chain of springs with internal state. See the module docstring."""

    a_time = None
    a_lag = None
    a_damping = None
    a_weight = None
    a_rigid_count = None
    a_space_matrix = None
    a_in_point = None
    a_out_point = None

    def __init__(self):
        """Create the node with an empty state."""
        om.MPxNode.__init__(self)
        self._frame = None
        self._rigid = []
        self._positions = []
        self._velocities = []
        self._start_positions = []
        self._start_velocities = []
        self._delta = 0.0

    @staticmethod
    def creator():
        """Return a new instance of the node."""
        return SpringChainSolver()

    @staticmethod
    def initialize():
        """Create the node attributes."""
        cls = SpringChainSolver
        unit_fn = om.MFnUnitAttribute()
        numeric_fn = om.MFnNumericAttribute()
        matrix_fn = om.MFnMatrixAttribute()

        cls.a_time = unit_fn.create("time", "tm", om.MFnUnitAttribute.kTime, 0.0)

        cls.a_lag = numeric_fn.create("lag", "lg", om.MFnNumericData.kDouble, 2.0)
        numeric_fn.setMin(0.0)
        numeric_fn.keyable = True

        cls.a_damping = numeric_fn.create("damping", "dmp", om.MFnNumericData.kDouble, 1.0)
        numeric_fn.setMin(MIN_DAMPING)
        numeric_fn.setMax(1.0)
        numeric_fn.keyable = True

        cls.a_weight = numeric_fn.create("weight", "wgt", om.MFnNumericData.kDouble, 1.0)
        numeric_fn.setMin(0.0)
        numeric_fn.setMax(1.0)
        numeric_fn.keyable = True

        cls.a_rigid_count = numeric_fn.create("rigidCount", "rc", om.MFnNumericData.kInt, 2)
        numeric_fn.setMin(1)

        cls.a_space_matrix = matrix_fn.create("spaceMatrix", "spm", om.MFnMatrixAttribute.kDouble)

        cls.a_in_point = numeric_fn.create("inPoint", "ip", om.MFnNumericData.k3Double)
        numeric_fn.array = True
        numeric_fn.disconnectBehavior = om.MFnAttribute.kDelete

        cls.a_out_point = numeric_fn.create("outPoint", "op", om.MFnNumericData.k3Double)
        numeric_fn.array = True
        numeric_fn.usesArrayDataBuilder = True
        numeric_fn.writable = False
        numeric_fn.storable = False

        inputs = [
            cls.a_time,
            cls.a_lag,
            cls.a_damping,
            cls.a_weight,
            cls.a_rigid_count,
            cls.a_space_matrix,
            cls.a_in_point,
        ]
        for attr in inputs + [cls.a_out_point]:
            cls.addAttribute(attr)

        for attr in inputs:
            cls.attributeAffects(attr, cls.a_out_point)

    def compute(self, plug, data):
        """Solve the chain for the current frame and write 'outPoint'."""
        cls = SpringChainSolver
        if plug.isChild:
            plug = plug.parent()
        if plug.isElement:
            plug = plug.array()
        if plug != cls.a_out_point:
            return None

        frame = data.inputValue(cls.a_time).asTime().asUnits(om.MTime.uiUnit())
        lag = data.inputValue(cls.a_lag).asDouble()
        damping = data.inputValue(cls.a_damping).asDouble()
        weight = data.inputValue(cls.a_weight).asDouble()
        rigid_count = data.inputValue(cls.a_rigid_count).asInt()
        space = data.inputValue(cls.a_space_matrix).asMatrix()
        space_inverse = space.inverse()

        in_handle = data.inputArrayValue(cls.a_in_point)
        indices, world, rigid = [], [], []
        for physical in range(len(in_handle)):
            in_handle.jumpToPhysicalElement(physical)
            indices.append(in_handle.elementLogicalIndex())
            point = om.MPoint(in_handle.inputValue().asDouble3())
            world.append(point)
            local = point * space_inverse
            rigid.append([local.x, local.y, local.z])

        self._advance(frame, rigid, rigid_count, lag, damping)

        out_handle = data.outputArrayValue(cls.a_out_point)
        builder = out_handle.builder()
        for index, logical in enumerate(indices):
            solved = om.MPoint(self._positions[index]) * space
            blended = world[index] + (solved - world[index]) * weight
            builder.addElement(logical).set3Double(blended.x, blended.y, blended.z)

        out_handle.set(builder)
        out_handle.setAllClean()
        data.setClean(plug)
        return self

    def _advance(self, frame, rigid, rigid_count, lag, damping):
        """Update the state for 'frame'. See the module docstring for the rules."""
        elapsed = None if self._frame is None else frame - self._frame
        jumped = elapsed is None or elapsed < -SAME_FRAME or elapsed > 1.0 + SAME_FRAME
        if jumped or len(rigid) != len(self._positions):
            self._positions = [list(point) for point in rigid]
            self._velocities = [[0.0, 0.0, 0.0] for _ in rigid]
            self._start_positions = [list(point) for point in rigid]
            self._start_velocities = [[0.0, 0.0, 0.0] for _ in rigid]
            self._delta = 0.0
            self._frame = frame
            self._rigid = rigid
            return

        if elapsed > SAME_FRAME:
            new_step, delta = True, elapsed
        else:
            new_step = self._moved(rigid)
            delta = 1.0 if new_step else self._delta

        if new_step:
            self._start_positions = self._positions
            self._start_velocities = self._velocities

        self._frame = frame
        self._rigid = rigid
        self._delta = delta
        if delta <= 0.0:
            return

        self._positions, self._velocities = solve_chain(
            rigid, self._start_positions, self._start_velocities, rigid_count, lag, damping, delta
        )

    def _moved(self, rigid):
        """Return True if the rigid chain is not where it was at the last evaluation."""
        for point, last in zip(rigid, self._rigid):  # noqa: B905
            for axis in range(3):
                if abs(point[axis] - last[axis]) > MOVED_TOLERANCE:
                    return True

        return False


def initializePlugin(plugin):  # noqa: N802
    """Register the node."""
    om.MFnPlugin(plugin, "DevPyLib", "1.0").registerNode(
        NODE_NAME,
        NODE_ID,
        SpringChainSolver.creator,
        SpringChainSolver.initialize,
        om.MPxNode.kDependNode,
        NODE_CLASSIFY,
    )


def uninitializePlugin(plugin):  # noqa: N802
    """Deregister the node."""
    om.MFnPlugin(plugin).deregisterNode(NODE_ID)
