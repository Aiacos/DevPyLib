#!/usr/bin/env python

"""Interactive quad mesh patching tool for Maya.

Provides a UI-driven workflow for patching holes in quad meshes with clean topology.
Uses edge loops and polyBridge to create quad-flow patches that match surrounding geometry.

Version: 1.0
Compatibility: Maya 2020+
"""

import random
from dataclasses import dataclass, field

import maya.cmds as mc
import maya.mel as mel
from maya import OpenMaya

WINDOW_NAME = "quadPatcher"


@dataclass
class QuadPatcherState:
    """Encapsulates all runtime state for the quad patcher tool.

    This replaces 42+ global variables with a single state object
    that can be passed to functions or stored as a window attribute.
    """

    # Object names
    obj_name_dup: str = ""
    obj_name_orig: str = ""
    sel_obj: str = ""

    # Bridge nodes
    side_a_bridge_node: tuple = ()
    side_b_bridge_node: tuple = ()
    side_c_bridge_node: tuple = ()
    close_bridge_node: tuple = ()
    close_side_a_bridge_node: tuple = ()
    close_side_b_bridge_node: tuple = ()
    close_side_c_bridge_node: tuple = ()
    inset_node: tuple = ()
    fm_transfer_attributes_node: tuple = ()

    # Edge data
    ordered_edges: list = field(default_factory=list)
    ordered_edge_components: list = field(default_factory=list)
    ordered_edges_extended: list = field(default_factory=list)
    ordered_edges_components_extended: list = field(default_factory=list)
    ordered_whole_border: list = field(default_factory=list)
    ordered_whole_border_components: list = field(default_factory=list)
    ordered_whole_border_components_ext: list = field(default_factory=list)
    whole_border: list = field(default_factory=list)

    side_a_edges: list = field(default_factory=list)
    side_a_edge_components: list = field(default_factory=list)
    side_b1_edges: list = field(default_factory=list)
    side_c1_edges: list = field(default_factory=list)
    sel_edges: list = field(default_factory=list)
    sel_edges_orig: list = field(default_factory=list)

    # Vertex and face data
    dup_base_verts: list = field(default_factory=list)
    new_created_verts: list = field(default_factory=list)
    dup_faces_to_hide: list = field(default_factory=list)

    # Sets
    dup_edges_set: str | None = None
    side_b_remove_set: str | None = None
    side_c_remove_set: str | None = None
    face_mode_edge_components_orig_set: str | None = None

    # Deformer nodes
    relax_nodes: list = field(default_factory=list)
    smooth_nodes: list = field(default_factory=list)
    wrap_base_mesh: list = field(default_factory=list)
    live_obj: list = field(default_factory=list)

    # Numeric parameters
    side_a_len: int = 0
    side_b_len: int = 0
    div_offset: int = 0
    end_offset: int = 0

    # Originals for extrude mode
    end_a_orig: str = ""
    end_b_orig: str = ""

    # Mode flags
    is_face_mode: bool = False


# Global state instance - accessed by UI callbacks
_state = QuadPatcherState()


def _get_state() -> QuadPatcherState:
    """Get the global state instance."""
    global _state
    return _state


def _reset_state():
    """Reset the global state to initial values."""
    global _state
    _state = QuadPatcherState()


def face_checker(_unused_arg=None):
    """Check the selected faces in Maya for various conditions.

    1. Ensures faces are selected.
    2. Checks that no face is adjacent to a border edge.
    3. Ensures the selection edge perimeter count is even.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    sel = mc.ls(sl=True, fl=True)

    # Check if any faces are selected
    if mc.polyEvaluate(sel, ec=True) or mc.polyEvaluate(sel, vc=True) > 0:
        mc.error("No Faces are selected")
    if mc.polyEvaluate(sel, fc=True) == 0:
        mc.error("No faces are selected")

    mc.select(sel)

    # Check for adjacency to border edges
    for each in mc.ls(mc.polyListComponentConversion(sel, te=True), fl=True):
        current_edge = mc.polySelect(eb=int(each.split("[")[1].split("]")[0]), q=True)
        if current_edge is not None:
            mc.error("Face cannot be adjacent to the border")

    mc.ConvertSelectionToEdgePerimeter()

    # Ensure the selection edge perimeter count is even
    if len(mc.ls(sl=True, fl=True)) % 2 != 0:
        mc.select(sel)
        mc.error("Selection edge perimeter count is odd. Needs even for quads.")

    mc.select(sel)


def edge_checker(_unused_arg=None):
    """Check the selected edges in Maya for various conditions.

    1. Ensures edges are selected.
    2. Verifies that the complete edge border is selected.
    3. Ensures the selection count is even.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    sel = mc.ls(sl=True, fl=True)

    # Check if any edges are selected
    if mc.polyEvaluate(sel, fc=True) or mc.polyEvaluate(sel, vc=True) > 0:
        mc.error("None edges selected for Edge Border Mode")
    if mc.polyEvaluate(sel, ec=True) == 0:
        mc.error("No Edges are selected for Edge Border Mode")

    # Verify that the complete edge border is selected
    first_edge_index = int(sel[0].split("[")[1].split("]")[0])
    complete_border_edges = mc.polySelect(q=True, eb=first_edge_index, ass=True)
    if len(mc.ls(complete_border_edges, fl=True)) != len(sel):
        mc.error("Complete edge border is not selected")

    # Ensure the selection count is even
    if len(sel) % 2 != 0:
        mc.error("Edge count is odd. Needs even for quads.")


def quad_patch_init(_unused_arg=None):
    """Initialize quad patching process on selected mesh.

    Duplicates the selected object, creates edge bridges for each border,
    and configures the UI for interactive patching.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()

    if not state.is_face_mode:
        edge_checker()

    # Disable buttons and sliders in the UI
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("extrudeSlider", en=0, e=True)

    # Source object
    state.sel_edges_orig = mc.ls(sl=True, fl=True)
    mc.polyListComponentConversion(state.sel_edges_orig, tv=True)
    state.obj_name_orig = state.sel_edges_orig[0].split(".")[0]

    # Duplicate the original object
    state.obj_name_dup = mc.duplicate(
        state.obj_name_orig,
        n=f"quadPatcher{random.randint(1000, 9999)}_{state.obj_name_orig}",
    )[0]

    # Prepare the duplicated edges
    sel_edges = [f"{state.obj_name_dup}.{each.split('.')[1]}" for each in state.sel_edges_orig]
    mc.select(sel_edges)
    state.dup_edges_set = mc.sets(n=f"quadPatcher{random.randint(1000, 9999)}_dupSet")
    sel_verts = mc.ls(mc.polyListComponentConversion(sel_edges, tv=True), fl=True)
    sel_faces = mc.ls(mc.polyListComponentConversion(sel_verts, tf=True), fl=True)

    # Remove unnecessary faces from the duplicated object
    dup_face_delete_set = [
        x
        for x in mc.ls(mc.polyListComponentConversion(state.obj_name_dup, tf=True), fl=True)
        if x not in sel_faces
    ]
    mc.delete(dup_face_delete_set)
    mc.select(state.dup_edges_set)

    sel_edges = mc.ls(sl=True, fl=True)
    state.dup_base_verts = mc.ls(
        mc.polyListComponentConversion(state.obj_name_dup, tv=True), fl=True
    )

    # Calculate side lengths
    state.side_a_len = int(len(sel_edges) / 4)
    state.side_b_len = int((len(sel_edges) - (state.side_a_len * 2)) / 2)
    if len(sel_edges) == 12:
        state.side_a_len = 1
        state.side_b_len = 5
    elif len(sel_edges) == 10:
        state.side_a_len = 1
        state.side_b_len = 4
    elif len(sel_edges) == 8:
        state.side_a_len = 1
        state.side_b_len = 3

    # Order edges for processing
    state.ordered_edges = initiate(sel_edges)
    state.ordered_edge_components = [
        f"{state.obj_name_dup}.e[{each}]" for each in state.ordered_edges
    ]

    # Wrap duplicated edges to the original object
    mc.select(sel_edges, state.obj_name_orig)
    mc.CreateWrap()
    wrap_node = mc.listConnections(state.obj_name_orig, type="wrap")[0]
    state.wrap_base_mesh = mc.listConnections(f"{wrap_node}.basePoints")
    mc.setAttr(f"{wrap_node}.weightThreshold", 0)
    mc.setAttr(f"{wrap_node}.maxDistance", 1)
    mc.setAttr(f"{wrap_node}.autoWeightThreshold", 1)
    mc.setAttr(f"{wrap_node}.exclusiveBind", 0)

    # Setup for SideA
    state.ordered_edges_extended = state.ordered_edges * 3
    state.ordered_edges_components_extended = state.ordered_edge_components * 3

    mc.intSliderGrp("rotationSlider", e=True, v=state.side_a_len)
    offset_num = state.side_a_len * 2
    mc.intSliderGrp("rotationSlider", e=True, v=offset_num)

    state.side_a_edges = (
        state.ordered_edges_extended[offset_num : state.side_a_len + offset_num]
        + state.ordered_edges_extended[
            state.side_a_len + state.side_b_len + offset_num : state.side_a_len * 2
            + state.side_b_len
            + offset_num
        ]
    )
    state.side_a_edge_components = (
        state.ordered_edges_components_extended[offset_num : state.side_a_len + offset_num]
        + state.ordered_edges_components_extended[
            state.side_a_len + state.side_b_len + offset_num : state.side_a_len * 2
            + state.side_b_len
            + offset_num
        ]
    )

    # Remove edges for SideB
    side_b_remove = [
        state.ordered_edges_components_extended[offset_num + state.side_a_len],
        state.ordered_edges_components_extended[
            state.side_a_len + offset_num + state.side_b_len - 1
        ],
    ]
    mc.select(side_b_remove)
    state.side_b_remove_set = mc.sets(n=f"quadPatcher{random.randint(1000, 9999)}_sideBRemoveSet")

    # Remove edges for SideC
    side_c_remove = [
        state.ordered_edges_components_extended[
            offset_num + (2 * state.side_a_len) + state.side_b_len
        ],
        state.ordered_edges_components_extended[
            (2 * state.side_a_len) + offset_num + (2 * state.side_b_len) - 1
        ],
    ]
    mc.select(side_c_remove)
    state.side_c_remove_set = mc.sets(n=f"quadPatcher{random.randint(1000, 9999)}_sideCRemoveSet")

    # Transform components
    state.smooth_nodes = [
        mc.polyMoveEdge(state.sel_edges_orig, ch=1, random=0, localCenter=0, lsx=1)[0]
        for _ in range(3)
    ]

    # Create edge bridges
    mc.select(state.side_a_edge_components, r=True)
    state.side_a_bridge_node = mc.polyBridgeEdge(
        divisions=state.side_b_len - 3,
        ch=True,
        twist=0,
        taper=1,
        curveType=0,
        smoothingAngle=30,
    )

    side_b_edge_loop = mc.ls(
        mc.polySelect(
            q=True, eb=state.ordered_edges_extended[offset_num + state.side_a_len], ass=True
        ),
        fl=True,
    )
    side_b_edge_remove = mc.sets(state.side_b_remove_set, q=True)
    side_b_edge_components = [x for x in side_b_edge_loop if x not in side_b_edge_remove]
    mc.select(side_b_edge_components, r=True)
    state.side_b_bridge_node = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    side_c_edge_loop = mc.ls(
        mc.polySelect(
            q=True,
            eb=state.ordered_edges_extended[offset_num + (2 * state.side_a_len) + state.side_b_len],
            ass=True,
        ),
        fl=True,
    )
    side_c_edge_remove = mc.sets(state.side_c_remove_set, q=True)
    side_c_edge_components = [x for x in side_c_edge_loop if x not in side_c_edge_remove]
    mc.select(side_c_edge_components, r=True)
    state.side_c_bridge_node = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Configure UI sliders
    mc.select(cl=True)
    mc.intSliderGrp(
        "rotationSlider", e=True, v=state.side_a_len * 2, max=len(state.ordered_edges), min=0
    )
    mc.intSliderGrp(
        "divisionSlider",
        e=True,
        v=mc.getAttr(f"{state.side_a_bridge_node[0]}.divisions"),
        max=(state.side_b_len - 2) * 2 - (state.side_b_len - state.side_a_len),
    )
    state.div_offset = 0

    # Identify newly created vertices and faces
    state.new_created_verts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(state.obj_name_dup, tv=True), fl=True)
        if x not in state.dup_base_verts
    ]
    new_created_faces = mc.ls(
        mc.polyListComponentConversion(state.new_created_verts, tf=True), fl=True
    )

    # Apply inset extrusion to new faces
    state.inset_node = mc.polyExtrudeFacet(new_created_faces, nds=1, off=0, d=0)

    # Relax vertices by averaging
    state.relax_nodes = [
        mc.polyAverageVertex(state.new_created_verts, i=10, ch=1)[0] for _ in range(10)
    ]

    # Transfer attributes in face mode
    if state.is_face_mode:
        state.fm_transfer_attributes_node = mc.transferAttributes(
            state.live_obj,
            state.obj_name_dup,
            pos=1,
            nml=0,
            uvs=1,
            suv="map1",
            tuv="map1",
            col=2,
            spa=0,
            sus="map1",
            tus="map1",
            sm=0,
            fuv=0,
            clb=1,
        )
        mc.transferAttributes(
            state.live_obj,
            state.sel_edges_orig,
            pos=1,
            nml=0,
            uvs=1,
            suv="map1",
            tuv="map1",
            col=2,
            spa=0,
            sus="map1",
            tus="map1",
            sm=3,
            fuv=0,
            clb=1,
        )

    # Hide faces to be hidden
    state.dup_faces_to_hide = [
        x
        for x in mc.ls(mc.polyListComponentConversion(state.obj_name_dup, tf=True), fl=True)
        if x not in new_created_faces
    ]
    mc.select(state.dup_faces_to_hide)
    mc.HideSelectedObjects()
    mc.select(cl=True)


def rotate_slider(_unused_arg=None):
    """Update bridge component inputs when the rotation slider changes.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)

    offset_num = mc.intSliderGrp("rotationSlider", q=True, v=True)

    # Node state off B and C bridges and inset
    mc.setAttr(f"{state.side_b_bridge_node[0]}.nodeState", 1)
    mc.setAttr(f"{state.side_c_bridge_node[0]}.nodeState", 1)
    mc.setAttr(f"{state.inset_node[0]}.nodeState", 1)
    if state.is_face_mode:
        mc.setAttr(f"{state.fm_transfer_attributes_node[0]}.nodeState", 0)

    # sideA Bridge First
    side_a_edges = (
        state.ordered_edges_extended[
            0 + offset_num : state.side_a_len + offset_num + state.div_offset
        ]
        + state.ordered_edges_extended[
            state.side_a_len + state.side_b_len + offset_num : state.side_a_len * 2
            + state.side_b_len
            + offset_num
            + state.div_offset
        ]
    )
    side_a_edges_string = " ".join(f'"e[{each}]"' for each in side_a_edges)
    if side_a_edges_string:
        side_a_edges_string = " " + side_a_edges_string
    component_count = len(side_a_edges)
    input_component_str_a = (
        f'setAttr -type "componentList" ( "{state.side_a_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_a_edges_string}"
    )

    mel.eval(input_component_str_a)

    # sideB Adjust
    side_b_edge_remove = [
        state.ordered_edges_components_extended[
            0 + offset_num + state.side_a_len + state.div_offset
        ],
        state.ordered_edges_components_extended[
            state.side_a_len + offset_num + state.side_b_len - 1
        ],
    ]
    side_b_edge_loop = mc.ls(
        mc.polySelect(
            state.obj_name_dup,
            q=True,
            eb=state.ordered_edges_extended[offset_num + state.side_a_len + state.div_offset],
            ass=True,
        ),
        fl=True,
    )
    side_b_edge_components = [x for x in side_b_edge_loop if x not in side_b_edge_remove]
    side_b_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in side_b_edge_components)
    if side_b_edges_string:
        side_b_edges_string = " " + side_b_edges_string
    component_count = len(side_b_edge_components)
    input_component_str_b = (
        f'setAttr -type "componentList" ( "{state.side_b_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_b_edges_string}"
    )

    # sideC Adjust
    side_c_edge_remove = [
        state.ordered_edges_components_extended[
            0 + offset_num + (2 * state.side_a_len) + state.side_b_len + state.div_offset
        ],
        state.ordered_edges_components_extended[
            (2 * state.side_a_len) + offset_num + (2 * state.side_b_len) - 1
        ],
    ]
    side_c_edge_loop = mc.ls(
        mc.polySelect(
            state.obj_name_dup,
            q=True,
            eb=state.ordered_edges_extended[
                offset_num + (2 * state.side_a_len) + state.side_b_len + 1 + state.div_offset
            ],
            ass=True,
        ),
        fl=True,
    )
    side_c_edge_components = [x for x in side_c_edge_loop if x not in side_c_edge_remove]
    side_c_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in side_c_edge_components)
    if side_c_edges_string:
        side_c_edges_string = " " + side_c_edges_string
    component_count = len(side_c_edge_components)
    input_component_str_c = (
        f'setAttr -type "componentList" ( "{state.side_c_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_c_edges_string}"
    )

    # Execute Adjustment
    mel.eval(input_component_str_b)
    mc.setAttr(f"{state.side_b_bridge_node[0]}.nodeState", 0)
    mel.eval(input_component_str_c)
    mc.setAttr(f"{state.side_c_bridge_node[0]}.nodeState", 0)
    # Inset status check
    inset_status = mc.checkBox("insetCheckbox", q=True, v=True)
    if inset_status:
        mc.setAttr(f"{state.inset_node[0]}.nodeState", 0)
    if state.is_face_mode:
        mc.setAttr(f"{state.fm_transfer_attributes_node[0]}.nodeState", 0)


def divide_slider(_unused_arg=None):
    """Adjust the divisions and rotation offsets for bridge nodes.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)

    div_num = mc.intSliderGrp("divisionSlider", q=True, v=True)
    offset_num = mc.intSliderGrp("rotationSlider", q=True, v=True)

    # Turn off node state for B and C bridges and inset
    mc.setAttr(f"{state.side_b_bridge_node[0]}.nodeState", 1)
    mc.setAttr(f"{state.side_c_bridge_node[0]}.nodeState", 1)
    mc.setAttr(f"{state.inset_node[0]}.nodeState", 1)

    # Set divisions for sideA bridge
    mc.setAttr(f"{state.side_a_bridge_node[0]}.divisions", div_num)

    # Calculate division offset
    state.div_offset = state.side_a_len - 3 - div_num + (state.side_b_len - state.side_a_len)

    # Prepare sideA edges for input
    side_a_edges = (
        state.ordered_edges_extended[
            0 + offset_num : state.side_a_len + offset_num + state.div_offset
        ]
        + state.ordered_edges_extended[
            state.side_a_len + state.side_b_len + offset_num : state.side_a_len * 2
            + state.side_b_len
            + offset_num
            + state.div_offset
        ]
    )
    side_a_edges_string = " ".join(f'"e[{each}]"' for each in side_a_edges)
    if side_a_edges_string:
        side_a_edges_string = " " + side_a_edges_string
    component_count = len(side_a_edges)
    input_component_str_a = (
        f'setAttr -type "componentList" ( "{state.side_a_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_a_edges_string}"
    )

    mel.eval(input_component_str_a)

    # Prepare sideB edges for input
    side_b_edge_remove = [
        state.ordered_edges_components_extended[
            0 + offset_num + state.side_a_len + state.div_offset
        ],
        state.ordered_edges_components_extended[
            state.side_a_len + offset_num + state.side_b_len - 1
        ],
    ]
    side_b_edge_loop = mc.ls(
        mc.polySelect(
            state.obj_name_dup,
            q=True,
            eb=state.ordered_edges_extended[offset_num + state.side_a_len + state.div_offset],
            ass=True,
        ),
        fl=True,
    )
    side_b_edge_components = [x for x in side_b_edge_loop if x not in side_b_edge_remove]
    side_b_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in side_b_edge_components)
    if side_b_edges_string:
        side_b_edges_string = " " + side_b_edges_string
    component_count = len(side_b_edge_components)
    input_component_str_b = (
        f'setAttr -type "componentList" ( "{state.side_b_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_b_edges_string}"
    )

    # Prepare sideC edges for input
    side_c_edge_remove = [
        state.ordered_edges_components_extended[
            0 + offset_num + (2 * state.side_a_len) + state.side_b_len + state.div_offset
        ],
        state.ordered_edges_components_extended[
            (2 * state.side_a_len) + offset_num + (2 * state.side_b_len) - 1
        ],
    ]
    side_c_edge_loop = mc.ls(
        mc.polySelect(
            state.obj_name_dup,
            q=True,
            eb=state.ordered_edges_extended[
                offset_num + (2 * state.side_a_len) + state.side_b_len + 1 + state.div_offset
            ],
            ass=True,
        ),
        fl=True,
    )
    side_c_edge_components = [x for x in side_c_edge_loop if x not in side_c_edge_remove]
    side_c_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in side_c_edge_components)
    if side_c_edges_string:
        side_c_edges_string = " " + side_c_edges_string
    component_count = len(side_c_edge_components)
    input_component_str_c = (
        f'setAttr -type "componentList" ( "{state.side_c_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_c_edges_string}"
    )

    # Execute adjustments for sideB and sideC
    mel.eval(input_component_str_b)
    mc.setAttr(f"{state.side_b_bridge_node[0]}.nodeState", 0)
    mel.eval(input_component_str_c)
    mc.setAttr(f"{state.side_c_bridge_node[0]}.nodeState", 0)

    # Check and update inset status
    inset_status = mc.checkBox("insetCheckbox", q=True, v=True)
    if inset_status == 1:
        mc.setAttr(f"{state.inset_node[0]}.nodeState", 0)

    update_relax()
    update_inset()


def relax_slider(_unused_arg=None):
    """Adjust the relaxation iterations for each node in relax_nodes based on the slider value.

    This function retrieves the current value from the "relaxSlider" integer slider group
    and sets the "iterations" attribute of each node in the relax_nodes list to this value.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)  # Disable undo queue flushing
    relax_num = mc.intSliderGrp("relaxSlider", q=True, v=True)  # Get slider value

    for each in state.relax_nodes:
        # Set the iterations attribute for each node
        mc.setAttr(f"{each}.iterations", relax_num)


def smooth_border_slider(_unused_arg=None):
    """Adjusts the smooth border scale for each node in smooth_nodes based on the slider value.

    This function retrieves the current value from the "smoothBorderSlider" float slider
    group, converts it to a negative value, and sets the "localScaleX" attribute of each
    node in the smooth_nodes list to this value.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)  # Disable undo queue flushing
    smooth_num = (mc.floatSliderGrp("smoothBorderSlider", q=True, v=True) - 1) * -1
    # Set the localScaleX attribute for each node
    for each in state.smooth_nodes:
        mc.setAttr(f"{each}.localScaleX", smooth_num)


def activate_inset(_unused_arg=None):
    """Toggle inset node activation and update the relaxation and inset settings.

    This function is called when the inset checkbox is toggled. It updates the
    inset node's state and offset attributes, and calls the update_relax and
    update_inset functions to update the relaxation and inset settings.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)
    update_inset()
    inset_status = mc.checkBox("insetCheckbox", q=True, v=True)

    if inset_status:
        # Activate inset node and set offset and divisions to 0 and 1
        mc.setAttr(f"{state.inset_node[0]}.nodeState", 0)
        mc.setAttr(f"{state.inset_node[0]}.offset", 0)
        mc.setAttr(f"{state.inset_node[0]}.divisions", 1)
    else:
        # Deactivate inset node
        mc.setAttr(f"{state.inset_node[0]}.nodeState", 1)

    # Update relaxation settings
    update_relax()
    mc.undoInfo(swf=True)


def inset_div_minus(_unused_arg=None):
    """Decrease the number of inset divisions by one.

    This function is called when the user clicks the inset division minus button.
    It decreases the number of inset divisions by one, and updates the relaxation
    settings using the update_relax function.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)
    current_div_num = mc.getAttr(f"{state.inset_node[0]}.divisions")

    if current_div_num > 1:
        mc.setAttr(f"{state.inset_node[0]}.divisions", current_div_num - 1)

    update_relax()
    mc.undoInfo(swf=True)


def inset_div_plus(_unused_arg=None):
    """Increase the number of inset divisions by one.

    This function is called when the user clicks the inset division plus button.
    It increases the number of inset divisions by one, and updates the relaxation
    settings using the update_relax function.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)  # Disable undo queue flushing
    current_div_num = mc.getAttr(f"{state.inset_node[0]}.divisions")

    # Increase the number of inset divisions
    mc.setAttr(f"{state.inset_node[0]}.divisions", current_div_num + 1)

    # Update relaxation settings
    update_relax()
    mc.undoInfo(swf=True)  # Enable undo queue flushing


def update_relax(_unused_arg=None):
    """Updates the input components of each node in relax_nodes to the newly created vertices.

    This function retrieves the newly created vertices by comparing the current vertex list
    with the original vertex list. It then sets the "inputComponents" attribute of each node
    in the relax_nodes list to the new vertices.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()

    # Get the new vertices
    new_created_verts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(state.obj_name_dup, tv=True), fl=True)
        if x not in state.dup_base_verts
    ]

    # Create a string of the new vertices
    new_verts_string = " ".join(f'"{each.split(".")[1]}"' for each in new_created_verts)
    if new_verts_string:
        new_verts_string = " " + new_verts_string

    # Update the input components of each node in relax_nodes
    for each in state.relax_nodes:
        component_count = len(new_created_verts)
        input_component_string = (
            f'setAttr -type "componentList" ( "{each}.inputComponents" ) '
            f"{component_count}{new_verts_string}"
        )
        mel.eval(input_component_string)


def update_inset(_unused_arg=None):
    """Updates the input components of the inset node with the newly created faces.

    This function retrieves the newly created vertices and faces by comparing the
    current vertex and face lists with the original lists. It then sets the
    "inputComponents" attribute of the inset node to the new faces.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()

    # Get the new vertices
    new_created_verts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(state.obj_name_dup, tv=True), fl=True)
        if x not in state.dup_base_verts
    ]

    # Get the new faces
    new_created_faces = mc.ls(mc.polyListComponentConversion(new_created_verts, tf=True), fl=True)

    # Create a string of the new faces
    new_faces_string = " ".join(f'"{each.split(".")[1]}"' for each in new_created_faces)
    if new_faces_string:
        new_faces_string = " " + new_faces_string

    # Update the input components of the inset node
    component_count = len(new_created_faces)
    input_component_string = (
        f'setAttr -type "componentList" ( "{state.inset_node[0]}.inputComponents" ) '
        f"{component_count}{new_faces_string}"
    )
    mel.eval(input_component_string)


def undo_info_on(_unused_arg=None):
    """Enable undo queue flushing.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    mc.undoInfo(swf=True)


def initiate(edges):
    """Get the ordered list of edges in a mesh.

    Takes an MSelectionList of edges and returns an ordered list of the edges.

    Args:
        edges (MSelectionList): The list of edges to traverse.

    Returns:
        list: The ordered list of edge indices.
    """
    mc.select(edges)
    sel = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(sel)

    dag = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    sel.getDagPath(0, dag, component)

    m_it_edge = OpenMaya.MItMeshEdge(dag, component)

    checked_edge = [int(m_it_edge.index())]
    current_edge = m_it_edge.index()
    ordered_list = [m_it_edge.index()]
    for _count in range(m_it_edge.count()):
        while not m_it_edge.isDone():
            # Check if the edge is connected to the current edge
            if m_it_edge.connectedToEdge(current_edge):
                if m_it_edge.index() not in checked_edge:
                    # Add the edge to the ordered list and mark it as checked
                    ordered_list.append(m_it_edge.index())
                    current_edge = m_it_edge.index()
                    checked_edge.append(int(m_it_edge.index()))
                    break
            m_it_edge.next()
        m_it_edge.reset()
    return ordered_list


def patch_it(_unused_arg=None):
    """Patch the duplicated edges and merge the two objects.

    Delete the faces to hide and select the merged object.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()

    # Delete the faces to hide
    mc.delete(state.dup_faces_to_hide)
    # Get the original faces
    edges_to_merge = []
    # Iterate over the original edges and get their indices
    for each in state.sel_edges_orig:
        edges_to_merge.append(each.split(".")[1])
    # Unite the two objects, merge UV sets and center the pivot
    merged_obj = mc.polyUnite(
        [state.obj_name_orig, state.obj_name_dup], ch=1, mergeUVSets=1, centerPivot=True
    )[0]
    # Rename the new object
    obj_name_new = mc.rename(merged_obj, state.obj_name_orig)
    # Iterate over the duplicated edges and get their indices
    for each in mc.sets(state.dup_edges_set, q=True):
        if each != "transform*":
            edges_to_merge.append(each.split(".")[1])
    # Delete the set if it exists
    if mc.objExists("quadPatcher*_*Set"):
        mc.delete("quadPatcher*_*Set")
    # Delete history
    mc.DeleteHistory()
    verts_to_merge = []

    # Iterate over the edges to merge and get their vertices
    for each in edges_to_merge:
        verts_to_merge.append(f"{obj_name_new}.{each}")
    # Merge the vertices
    mc.polyMergeVertex(verts_to_merge, d=0.001, am=1, ch=1)

    # Delete the live object if it exists
    if state.is_face_mode:
        mc.delete(state.live_obj)
    # Delete the wrap base mesh if it exists
    if mc.objExists(state.wrap_base_mesh[0]):
        mc.delete(state.wrap_base_mesh)
    # Delete the merged object set if it exists
    if mc.objExists("mergedObjSet"):
        mc.delete("mergedObjeSet")
    # Delete history
    mc.DeleteHistory()
    # Select the new object
    mc.select(obj_name_new)

    # Reset the UI
    reset_ui(WINDOW_NAME)


def reset_ui(win_name):
    """Reset the UI by deleting the current window and opening a new one.

    Args:
        win_name (str): The name of the window to reset.
    """
    # Get all the windows of type "window"
    all_windows = mc.lsUI(type="window")
    # Iterate over each window and if it matches the window name,
    # delete it
    for win in all_windows:
        if win == win_name:
            mc.deleteUI(win)
    # Eval deferred to open a new instance of the UI
    mc.evalDeferred(quad_patcher_ui)


def face_mode_init(_unused_arg=None):
    """Initialize face mode for quad patching.

    This function sets up the environment for face mode by performing the
    following tasks:
    - Checks the selected faces.
    - Disables certain UI buttons.
    - Duplicates the selected object and prepares it for quad patching.
    - Converts the selection to an edge perimeter and creates a set of edge
      components.
    - Initiates the quad patching process.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()

    # Ensure that faces are selected and meet necessary conditions
    face_checker()

    # Disable specific UI buttons for edge and extrude modes
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("extrudeSlider", en=0, e=True)

    # Update state
    state.is_face_mode = True

    # Get the original selected faces and object name
    sel_faces_orig = mc.ls(sl=True, fl=True)
    obj_name_orig = sel_faces_orig[0].split(".")[0]

    # Duplicate the original object for live manipulation
    state.live_obj = mc.duplicate(obj_name_orig, n=f"quadPatcher{random.randint(1000, 9999)}_live")

    # Prepare the duplicated object by keeping only the selected faces
    live_obj_faces = [f"{state.live_obj[0]}.{each.split('.')[1]}" for each in sel_faces_orig]
    mc.delete(
        [
            x
            for x in mc.ls(mc.polyListComponentConversion(state.live_obj, tf=True), fl=True)
            if x not in live_obj_faces
        ]
    )

    # Hide the duplicated object
    mc.hide(state.live_obj)

    # Convert the selection to an edge perimeter and create a set
    mc.ConvertSelectionToEdgePerimeter()
    state.face_mode_edge_components_orig_set = mc.sets(
        n=f"quadPatcher{random.randint(1000, 9999)}_{obj_name_orig}Set"
    )

    # Delete the original selected faces and select the edge component set
    mc.delete(sel_faces_orig)
    mc.select(state.face_mode_edge_components_orig_set)

    # Initiate the quad patching process
    quad_patch_init()


def extrude_slider(_unused_arg=None):
    """Adjust the number of extrusions for the extrusion mode.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()
    mc.undoInfo(swf=False)
    state.end_offset = mc.intSliderGrp("extrudeSlider", q=True, v=True)

    # Set the node state for the closing bridge nodes
    mc.setAttr(f"{state.close_side_a_bridge_node[0]}.nodeState", 1)
    mc.setAttr(f"{state.close_side_b_bridge_node[0]}.nodeState", 1)
    mc.setAttr(f"{state.close_side_c_bridge_node[0]}.nodeState", 1)

    # Calculate the number of divisions for the closing bridge
    div_num_ii = state.end_offset - 1

    # Set the initial bridge
    side_components = [
        state.side_b1_edges[state.end_offset].split(".")[1],
        state.side_c1_edges[state.end_offset].split(".")[1],
    ]
    side_a_edges_string = " ".join(f'"{component}"' for component in side_components)
    if side_a_edges_string:
        side_a_edges_string = " " + side_a_edges_string
    input_component_str_i = (
        f'setAttr -type "componentList" ( "{state.close_bridge_node[0]}.inputComponents" ) '
        f"2{side_a_edges_string}"
    )
    mel.eval(input_component_str_i)

    # Side A
    new_whole_border = mc.ls(
        mc.polySelect(state.sel_obj, q=True, eb=state.ordered_edges[0], ass=True), fl=True
    )
    temp_x_edges = (
        state.side_b1_edges[0 : state.end_offset] + state.side_c1_edges[0 : state.end_offset]
    )
    temp_x_edges = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(temp_x_edges, tv=True), te=True
        ),
        fl=True,
    )
    new_bridge_edges = [x for x in new_whole_border if x not in temp_x_edges]
    side_a_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in new_bridge_edges)
    if side_a_edges_string:
        side_a_edges_string = " " + side_a_edges_string
    component_count = len(new_bridge_edges)
    input_component_str_a = (
        f'setAttr -type "componentList" ( "{state.close_side_a_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_a_edges_string}"
    )

    mel.eval(input_component_str_a)
    mc.setAttr(f"{state.close_side_a_bridge_node[0]}.divisions", div_num_ii)
    mc.setAttr(f"{state.close_side_a_bridge_node[0]}.nodeState", 0)

    # Side B
    ext_side_b_edges_i = state.side_b1_edges[0 : state.end_offset]
    ext_side_b_edges_whole = mc.ls(
        mc.polySelect(
            state.sel_obj,
            q=True,
            eb=int(ext_side_b_edges_i[0].split("[")[1].split("]")[0]),
            ass=True,
        ),
        fl=True,
    )
    ext_side_b_remove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(ext_side_b_edges_i, tv=True), te=True
        ),
        fl=True,
    )
    ext_side_b_edges_ii = [x for x in ext_side_b_edges_whole if x not in ext_side_b_remove]
    side_b_edge_components = ext_side_b_edges_i + ext_side_b_edges_ii
    side_b_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in side_b_edge_components)
    if side_b_edges_string:
        side_b_edges_string = " " + side_b_edges_string
    component_count = len(side_b_edge_components)
    input_component_str_b = (
        f'setAttr -type "componentList" ( "{state.close_side_b_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_b_edges_string}"
    )
    mel.eval(input_component_str_b)
    mc.setAttr(f"{state.close_side_b_bridge_node[0]}.nodeState", 0)

    # Side C
    ext_side_c_edges_i = state.side_c1_edges[0 : state.end_offset]
    ext_side_c_edges_whole = mc.ls(
        mc.polySelect(
            state.sel_obj,
            q=True,
            eb=int(ext_side_c_edges_i[0].split("[")[1].split("]")[0]),
            ass=True,
        ),
        fl=True,
    )
    ext_side_c_remove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(ext_side_c_edges_i, tv=True), te=True
        ),
        fl=True,
    )
    ext_side_c_edges_ii = [x for x in ext_side_c_edges_whole if x not in ext_side_c_remove]
    side_c_edge_components = ext_side_c_edges_i + ext_side_c_edges_ii
    side_c_edges_string = " ".join(f'"{each.split(".")[1]}"' for each in side_c_edge_components)
    if side_c_edges_string:
        side_c_edges_string = " " + side_c_edges_string
    component_count = len(side_c_edge_components)
    input_component_str_c = (
        f'setAttr -type "componentList" ( "{state.close_side_c_bridge_node[0]}.inputComponents" ) '
        f"{component_count}{side_c_edges_string}"
    )
    mel.eval(input_component_str_c)
    mc.setAttr(f"{state.close_side_c_bridge_node[0]}.nodeState", 0)


def extrude_mode_init(_unused_arg=None):
    """Initialize the extrude mode by setting up UI components and creating bridge nodes.

    Args:
        _unused_arg: Unused callback parameter required by Maya UI callbacks.
    """
    state = _get_state()

    # Disable UI components for extrude mode
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("rotationSlider", en=0, e=True)
    mc.intSliderGrp("divisionSlider", en=0, e=True)
    mc.intSliderGrp("relaxSlider", en=0, e=True)
    mc.floatSliderGrp("smoothBorderSlider", en=0, e=True)
    mc.checkBox("insetCheckbox", en=0, e=True)
    mc.button("minusButton", l="-", en=0, e=True)
    mc.button("plusButton", l="+", en=0, e=True)
    mc.button("patchItButton", l="Patch It!", en=0, e=True)

    # Get the selected edges and object name
    state.sel_edges = mc.ls(sl=True, fl=True)
    state.sel_obj = state.sel_edges[0].split(".")[0]

    # Initialize ordered edges
    state.ordered_edges = initiate(state.sel_edges)
    if len(state.ordered_edges) < len(state.sel_edges):
        for _ in range(len(state.sel_edges) - len(state.ordered_edges)):
            options = mc.ls(
                mc.polyListComponentConversion(
                    mc.polyListComponentConversion(
                        f"{state.sel_obj}.e[{state.ordered_edges[0]}]", tv=True
                    ),
                    te=True,
                ),
                fl=True,
            )

            state.ordered_edge_components = [
                f"{state.sel_edges[0].split('.')[0]}.e[{each}]" for each in state.ordered_edges
            ]

            # Find the key edge that needs to be added
            key = [x for x in state.sel_edges if x not in state.ordered_edge_components]
            selected = [x for x in options if x in key]
            state.ordered_edges.insert(0, int(selected[0].split("[")[1].split("]")[0]))

    state.ordered_edge_components = [
        f"{state.sel_edges[0].split('.')[0]}.e[{each}]" for each in state.ordered_edges
    ]

    # Retrieve and extend the whole border edges
    state.whole_border = mc.polySelect(q=True, eb=state.ordered_edges[0], ass=True)
    state.ordered_whole_border = initiate(state.whole_border)
    state.ordered_whole_border_components = [
        f"{state.sel_edges[0].split('.')[0]}.e[{each}]" for each in state.ordered_whole_border
    ]
    state.ordered_whole_border_components_ext = state.ordered_whole_border_components * 3

    # Set extrudeSlider range
    mc.intSliderGrp(
        "extrudeSlider",
        e=True,
        min=1,
        max=(len(state.ordered_whole_border) - len(state.sel_edges)) / 2 - 2,
    )

    # Determine the start index for sideB1 edges
    if state.ordered_whole_border_components[0] == state.ordered_edge_components[0]:
        if state.ordered_whole_border_components.index(state.ordered_edge_components[1]) == 1:
            side_b1_start_index = (
                state.ordered_whole_border_components.index(state.ordered_edge_components[-1]) + 1
            )
        else:
            side_b1_start_index = (
                state.ordered_whole_border_components.index(state.ordered_edge_components[0]) + 1
            )
    elif state.ordered_whole_border_components.index(
        state.ordered_edge_components[-1]
    ) > state.ordered_whole_border_components.index(state.ordered_edge_components[0]):
        if state.ordered_whole_border_components[0] in state.ordered_edge_components:
            side_b1_start_index = (
                state.ordered_whole_border_components.index(state.ordered_edge_components[0]) + 1
            )
        else:
            side_b1_start_index = (
                state.ordered_whole_border_components.index(state.ordered_edge_components[-1]) + 1
            )
    else:
        if (
            state.ordered_whole_border_components.index(state.ordered_edge_components[0])
            == len(state.ordered_whole_border_components) - 1
        ):
            if state.ordered_whole_border_components[0] in state.ordered_edge_components:
                side_b1_start_index = (
                    state.ordered_whole_border_components.index(state.ordered_edge_components[-1])
                    + 1
                )
            else:
                side_b1_start_index = 0
        elif state.ordered_whole_border_components[0] in state.ordered_edge_components:
            side_b1_start_index = (
                state.ordered_whole_border_components.index(state.ordered_edge_components[-1]) + 1
            )
        else:
            side_b1_start_index = (
                state.ordered_whole_border_components.index(state.ordered_edge_components[0]) + 1
            )

    # Define sideB1 and sideC1 edges
    state.side_b1_edges = [
        state.ordered_whole_border_components[i % len(state.ordered_whole_border_components)]
        for i in range(
            side_b1_start_index,
            side_b1_start_index + len(state.ordered_whole_border_components) - len(state.sel_edges),
        )
    ]
    state.side_c1_edges = state.side_b1_edges[::-1]

    # Initial bridge setup
    div_num = len(state.sel_edges) - 1
    state.end_a_orig = state.ordered_edge_components[0]
    state.end_b_orig = state.ordered_edge_components[len(state.sel_edges) - 1]
    state.end_offset = mc.intSliderGrp("extrudeSlider", q=True, v=True)
    div_num_ii = state.end_offset - 1

    init_bridge_edges = [
        state.side_b1_edges[state.end_offset],
        state.side_c1_edges[state.end_offset],
    ]
    mc.select(init_bridge_edges)
    state.close_bridge_node = mc.polyBridgeEdge(
        divisions=div_num, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Create side A bridge
    new_whole_border = mc.ls(
        mc.polySelect(state.sel_obj, q=True, eb=state.ordered_edges[0], ass=True), fl=True
    )
    temp_x_edges = (
        state.side_b1_edges[0 : state.end_offset] + state.side_c1_edges[0 : state.end_offset]
    )
    temp_x_edges = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(temp_x_edges, tv=True), te=True
        ),
        fl=True,
    )
    new_bridge_edges = [x for x in new_whole_border if x not in temp_x_edges]
    mc.select(new_bridge_edges, state.ordered_edge_components[1 : len(state.sel_edges) - 1])
    state.close_side_a_bridge_node = mc.polyBridgeEdge(
        divisions=div_num_ii, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Create side B bridge
    ext_side_b_edges_i = state.side_b1_edges[0 : state.end_offset]
    ext_side_b_edges_whole = mc.ls(
        mc.polySelect(q=True, eb=int(ext_side_b_edges_i[0].split("[")[1].split("]")[0]), ass=True),
        fl=True,
    )
    ext_side_b_remove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(ext_side_b_edges_i, tv=True), te=True
        ),
        fl=True,
    )
    ext_side_b_edges_ii = [x for x in ext_side_b_edges_whole if x not in ext_side_b_remove]
    mc.select(ext_side_b_edges_i, ext_side_b_edges_ii)
    state.close_side_b_bridge_node = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Create side C bridge
    ext_side_c_edges_i = state.side_c1_edges[0 : state.end_offset]
    ext_side_c_edges_whole = mc.ls(
        mc.polySelect(q=True, eb=int(ext_side_c_edges_i[0].split("[")[1].split("]")[0]), ass=True),
        fl=True,
    )
    ext_side_c_remove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(ext_side_c_edges_i, tv=True), te=True
        ),
        fl=True,
    )
    ext_side_c_edges_ii = [x for x in ext_side_c_edges_whole if x not in ext_side_c_remove]
    mc.select(ext_side_c_edges_i, ext_side_c_edges_ii)
    state.close_side_c_bridge_node = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Clear selection
    mc.select(cl=True)


def quad_patcher_ui():
    """Create the Quad Patcher UI in Maya.

    This function initializes and displays a UI window for the Quad Patcher tool,
    allowing users to switch modes and adjust various parameters for quad patching.
    """
    # Reset state when opening new UI
    _reset_state()
    state = _get_state()

    # Initialize the face mode
    state.is_face_mode = False
    window_size = (400, 200)

    # Delete existing window if present
    if mc.window(WINDOW_NAME, exists=True):
        mc.deleteUI(WINDOW_NAME)

    # Create the main window
    quad_window = mc.window(
        WINDOW_NAME, title="Quad Patcher", widthHeight=(window_size[0], window_size[1])
    )
    mc.columnLayout("mainColumn", adjustableColumn=True)

    # Add buttons for mode selection
    mc.rowLayout(parent="mainColumn", nc=3)
    mc.button("edgeBorderMode", label="Edge Border Mode", c=quad_patch_init)
    mc.button("faceMode", label="Face Mode", c=face_mode_init)
    mc.button("extrudeMode", label="Extrude Mode", c=extrude_mode_init)

    # Rotation slider
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Rotation: ", w=80, al="left")
    mc.intSliderGrp(
        "rotationSlider",
        field=True,
        dc=rotate_slider,
        w=310,
        min=0,
        max=1,
        value=0,
        cc=undo_info_on,
    )

    # Proportion slider
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Proportion: ", w=80, al="left")
    mc.intSliderGrp(
        "divisionSlider",
        field=True,
        dc=divide_slider,
        w=310,
        min=1,
        max=2,
        value=0,
        cc=undo_info_on,
    )

    # Relax slider
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Relax: ", w=80, al="left")
    mc.intSliderGrp(
        "relaxSlider",
        field=True,
        dc=relax_slider,
        w=310,
        min=0,
        max=10,
        value=10,
        cc=undo_info_on,
    )

    # Smooth Border slider
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Smooth Border: ", w=80, al="left")
    mc.floatSliderGrp(
        "smoothBorderSlider",
        field=True,
        dc=smooth_border_slider,
        w=310,
        min=0,
        max=1,
        value=0,
        cc=undo_info_on,
    )

    # Extrude Mode slider
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Extrude Mode: ", w=80, al="left")
    mc.intSliderGrp(
        "extrudeSlider",
        field=True,
        dc=extrude_slider,
        w=310,
        min=0,
        max=1,
        value=1,
        cc=undo_info_on,
    )

    # Inset checkbox
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Inset: ")
    mc.checkBox("insetCheckbox", l="", cc=activate_inset)

    # Inset Divisions control
    mc.rowLayout(parent="mainColumn", nc=3)
    mc.text(l="Inset Divisions:")
    mc.button("minusButton", l="-", w=20, c=inset_div_minus)
    mc.button("plusButton", l="+", w=20, c=inset_div_plus)

    # Patch and Reset buttons
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.button("patchItButton", l="Patch It!", c=patch_it)
    mc.button("resetButton", l="RESET", c=reset_ui)

    # Display the window
    mc.showWindow(quad_window)


if __name__ == "__main__":
    quad_patcher_ui()
