"""Build a Tension Map Bifrost graph with a per-vertex ``for_each`` loop.

This module creates a pure-Bifrost implementation of mesh tension visualization
that matches the ``mayaLib.plugin.tension_map`` Python plugin algorithm.  It
compares edge lengths between a rest-pose mesh and a deformed mesh and maps the
difference to vertex colors (green = stretch, black = neutral, red = compress).

The key technique is a ``Core::Iterators,for_each`` loop that iterates over
every vertex index.  Inside the loop body, the ``face_vertex`` topology array
is filtered to isolate the face-vertices belonging to the current vertex, their
edge lengths are summed and averaged, and a tension scalar is computed.

Algorithm (per vertex *V*)::

    mask        = (face_vertex == V)
    rest_avg    = sum(rest_edge_len[mask]) / count(mask)
    def_avg     = sum(def_edge_len[mask])  / count(mask)
    tension     = clamp((rest_avg - def_avg) / max(rest_avg, eps)
                        * sensitivity + offset, 0, 1)

Color mapping::

    0.0  ->  green   (stretch: deformed edges longer than rest)
    0.5  ->  black   (neutral: no length change)
    1.0  ->  red     (compression: deformed edges shorter than rest)

Usage inside the Maya Script Editor (Python tab)::

    from mayaLib.bifrostLib.utilities.build_tension_map import TensionMapGraph
    graph = TensionMapGraph()

    # Then in the Attribute Editor or Node Editor, connect:
    #   rest_mesh      <- original mesh shape (or Orig intermediate object)
    #   deformed_mesh  <- deformed mesh shape (skin cluster output, etc.)

Graph hierarchy::

    Tension_map (compound)
    |-- mesh_data          extracts topology + point positions
    |-- next_vertex        computes next/prev vertex index per face-vertex
    |-- edge_lengths       per-face-vertex average of fwd + bwd edge lengths
    |-- vertex_tension     FOR_EACH vertex: filter, sum, average, tension
    +-- color_output       maps tension array to green-black-red vertex colors

Note:
    For **closed meshes** (characters, spheres, tori) every edge is shared by
    exactly two faces, so each vertex's face-vertex entries cover all its
    connected edges and the result matches the Python plugin exactly.

    For **open meshes** (planes, patches) boundary edges appear in only one
    face, causing a slight weighting bias toward interior edges.
"""

from mayaLib.pyfrost.src.pyfrost import main


class TensionMapGraph(main.Graph):
    """Bifrost graph that visualises per-vertex mesh tension via vertex colors.

    Inherits from :class:`~mayaLib.pyfrost.src.pyfrost.main.Graph` so the
    instance *is* the bifrostBoard Maya node.  On construction the full node
    network is built automatically.

    Attributes:
        board_name: Board identifier written to the Maya node
            (``"tensionMap"``).

    Args:
        *args: Forwarded to :class:`Graph.__init__` (optional board name).
        **kwargs: Forwarded to :class:`Graph.__init__`.

    Example::

        graph = TensionMapGraph()
        # graph.board  ->  "tensionMap" (Maya node name)
    """

    board_name = "tensionMap"

    def __init__(self, *args, **kwargs):
        """Create the bifrostBoard and build the tension map graph."""
        super().__init__(*args, **kwargs)
        self.create_graph()

    # ─────────────────────────────────────────────────────────────────
    # Main graph assembly
    # ─────────────────────────────────────────────────────────────────

    def create_graph(self):
        """Build the complete tension map node network.

        Creates a top-level ``Tension_map`` compound with exposed inputs
        (``rest_mesh``, ``deformed_mesh``, ``sensitivity``, etc.) and
        outputs (``out_mesh``, ``tension_weights``).  Five sub-compounds
        are wired together inside it.

        Returns:
            The ``Tension_map`` :class:`~main.Node`.
        """
        tm = self.create_node("compound", name="Tension_map")

        # ── Compound input ports ─────────────────────────────────────
        tm["/input.rest_mesh"].add("output", "Object")
        tm["/input.deformed_mesh"].add("output", "Object")

        tm["/input.face_size"].add("output", "long")
        tm["/input"]["face_size"].value = 4

        tm["/input.sensitivity"].add("output", "float")
        tm["/input"]["sensitivity"].value = 1

        tm["/input.offset"].add("output", "float")
        tm["/input"]["offset"].value = 0.5

        tm["/input.epsilon"].add("output", "float")
        tm["/input"]["epsilon"].value = 0.0001

        tm["/input.plus_one"].add("output", "long")
        tm["/input"]["plus_one"].value = 1

        tm["/input.face_size_minus_one"].add("output", "long")
        tm["/input"]["face_size_minus_one"].value = 3

        # ── Compound output ports ────────────────────────────────────
        tm["/output.out_mesh"].add("input", "Object")
        tm["/output.tension_weights"].add("input", "auto")

        # ── Build sub-compounds ──────────────────────────────────────
        mesh_data = self._build_mesh_data(tm)
        next_vtx = self._build_next_vertex(tm)
        edge_lens = self._build_edge_lengths(tm)
        vtx_tension = self._build_vertex_tension(tm)
        color_out = self._build_color_output(tm)

        # ── Wire: mesh_data ──────────────────────────────────────────
        tm["/input"]["rest_mesh"].connect(mesh_data["rest_mesh"])
        tm["/input"]["deformed_mesh"].connect(mesh_data["deformed_mesh"])

        # ── Wire: next_vertex ────────────────────────────────────────
        mesh_data["face_vertex"].connect(next_vtx["face_vertex"])
        mesh_data["face_vertex_count"].connect(next_vtx["face_vertex_count"])
        tm["/input"]["face_size"].connect(next_vtx["face_size"])
        tm["/input"]["plus_one"].connect(next_vtx["plus_one"])
        tm["/input"]["face_size_minus_one"].connect(next_vtx["face_size_minus_one"])

        # ── Wire: edge_lengths ───────────────────────────────────────
        mesh_data["rest_positions"].connect(edge_lens["rest_positions"])
        mesh_data["def_positions"].connect(edge_lens["def_positions"])
        mesh_data["face_vertex"].connect(edge_lens["face_vertex"])
        next_vtx["next_vert_index"].connect(edge_lens["next_vert_index"])
        next_vtx["prev_vert_index"].connect(edge_lens["prev_vert_index"])

        # ── Wire: vertex_tension (for_each loop) ────────────────────
        mesh_data["point_count"].connect(vtx_tension["max_iterations"])
        mesh_data["face_vertex"].connect(vtx_tension["face_vertex"])
        edge_lens["rest_len"].connect(vtx_tension["rest_fv_len"])
        edge_lens["def_len"].connect(vtx_tension["def_fv_len"])
        tm["/input"]["sensitivity"].connect(vtx_tension["sensitivity"])
        tm["/input"]["offset"].connect(vtx_tension["offset"])
        tm["/input"]["epsilon"].connect(vtx_tension["epsilon"])

        # ── Wire: color_output ───────────────────────────────────────
        vtx_tension["tension"].connect(color_out["tension_per_vertex"])
        tm["/input"]["deformed_mesh"].connect(color_out["deformed_mesh"])

        # ── Wire: final outputs ──────────────────────────────────────
        color_out["out_mesh"].connect(tm["/output"]["out_mesh"])
        vtx_tension["tension"].connect(tm["/output"]["tension_weights"])

        return tm

    # ─────────────────────────────────────────────────────────────────
    # Sub-compound builders
    # ─────────────────────────────────────────────────────────────────

    def _build_mesh_data(self, root):
        """Extract topology from the rest mesh and positions from both meshes.

        Uses ``Geometry::Mesh,get_mesh_structure`` for the rest mesh to
        obtain ``point_position``, ``face_vertex``, ``face_vertex_count``,
        and ``point_count``.  Uses ``Geometry::Properties,get_point_position``
        for the deformed mesh.

        Args:
            root: Parent compound :class:`~main.Node`.

        Returns:
            The ``mesh_data`` compound :class:`~main.Node` with outputs:
            ``rest_positions``, ``face_vertex``, ``face_vertex_count``,
            ``def_positions``, ``point_count``.
        """
        c = root.create_node("compound", name="mesh_data")

        c["/input.rest_mesh"].add("output", "Object")
        c["/input.deformed_mesh"].add("output", "Object")
        c["/output.rest_positions"].add("input", "auto")
        c["/output.face_vertex"].add("input", "auto")
        c["/output.face_vertex_count"].add("input", "auto")
        c["/output.def_positions"].add("input", "auto")
        c["/output.point_count"].add("input", "auto")

        get_rest = c.create_node("Geometry::Mesh,get_mesh_structure", name="get_rest")
        c["/input"]["rest_mesh"].connect(get_rest["mesh"])

        get_def = c.create_node("Geometry::Properties,get_point_position", name="get_def")
        c["/input"]["deformed_mesh"].connect(get_def["geometry"])

        get_rest["point_position"].connect(c["/output"]["rest_positions"])
        get_rest["face_vertex"].connect(c["/output"]["face_vertex"])
        get_rest["face_vertex_count"].connect(c["/output"]["face_vertex_count"])
        get_def["point_position"].connect(c["/output"]["def_positions"])
        get_rest["point_count"].connect(c["/output"]["point_count"])

        return c

    def _build_next_vertex(self, root):
        """Compute next and previous vertex index per face-vertex.

        For a face with vertices ``[A, B, C, D]`` and face-vertex index *i*
        pointing to vertex *B*, this compound computes:

        - **next** = *C*  (``(local + 1) % face_size``)
        - **prev** = *A*  (``(local + face_size - 1) % face_size``)

        The modulo wrapping ensures the last vertex in a face wraps to the
        first, and vice versa.

        Args:
            root: Parent compound :class:`~main.Node`.

        Returns:
            The ``next_vertex`` compound with outputs:
            ``next_vert_index``, ``prev_vert_index``.
        """
        c = root.create_node("compound", name="next_vertex")

        c["/input.face_vertex"].add("output", "auto")
        c["/input.face_vertex_count"].add("output", "auto")
        c["/input.face_size"].add("output", "long")
        c["/input.plus_one"].add("output", "long")
        c["/input.face_size_minus_one"].add("output", "long")
        c["/output.next_vert_index"].add("input", "auto")
        c["/output.prev_vert_index"].add("input", "auto")

        # Shared: flat indices and local position within face
        fv_indices = c.create_node("Core::Array,get_array_indices", name="fv_indices")
        c["/input"]["face_vertex"].connect(fv_indices["array"])

        local_idx = c.create_node("Core::Math,modulo", name="local_idx")
        fv_indices["indices"].connect(local_idx["value"])
        c["/input"]["face_size"].connect(local_idx["divisor"])

        face_start = c.create_node("Core::Math,subtract", name="face_start")
        fv_indices["indices"].connect(face_start["indices"])
        local_idx["remainder"].connect(face_start["local"])

        # NEXT vertex: (local + 1) % face_size
        local_plus1 = c.create_node("Core::Math,add", name="local_plus1")
        local_idx["remainder"].connect(local_plus1["local"])
        c["/input"]["plus_one"].connect(local_plus1["one"])

        next_local = c.create_node("Core::Math,modulo", name="next_local")
        local_plus1["output"].connect(next_local["value"])
        c["/input"]["face_size"].connect(next_local["divisor"])

        next_fv_idx = c.create_node("Core::Math,add", name="next_fv_idx")
        face_start["output"].connect(next_fv_idx["fs"])
        next_local["remainder"].connect(next_fv_idx["nl"])

        next_idx_uint = c.create_node("Core::Math,modulo", name="next_idx_uint")
        next_fv_idx["output"].connect(next_idx_uint["value"])
        c["/input"]["face_vertex_count"].connect(next_idx_uint["divisor"])

        next_vert = c.create_node("Core::Array,get_from_array", name="next_vert")
        c["/input"]["face_vertex"].connect(next_vert["array"])
        next_idx_uint["remainder"].connect(next_vert["index"])

        # PREV vertex: (local + face_size - 1) % face_size
        local_plus_fsm1 = c.create_node("Core::Math,add", name="local_plus_fsm1")
        local_idx["remainder"].connect(local_plus_fsm1["local"])
        c["/input"]["face_size_minus_one"].connect(local_plus_fsm1["fsm1"])

        prev_local = c.create_node("Core::Math,modulo", name="prev_local")
        local_plus_fsm1["output"].connect(prev_local["value"])
        c["/input"]["face_size"].connect(prev_local["divisor"])

        prev_fv_idx = c.create_node("Core::Math,add", name="prev_fv_idx")
        face_start["output"].connect(prev_fv_idx["fs"])
        prev_local["remainder"].connect(prev_fv_idx["pl"])

        prev_idx_uint = c.create_node("Core::Math,modulo", name="prev_idx_uint")
        prev_fv_idx["output"].connect(prev_idx_uint["value"])
        c["/input"]["face_vertex_count"].connect(prev_idx_uint["divisor"])

        prev_vert = c.create_node("Core::Array,get_from_array", name="prev_vert")
        c["/input"]["face_vertex"].connect(prev_vert["array"])
        prev_idx_uint["remainder"].connect(prev_vert["index"])

        next_vert["value"].connect(c["/output"]["next_vert_index"])
        prev_vert["value"].connect(c["/output"]["prev_vert_index"])

        return c

    def _build_edge_lengths(self, root):
        """Compute the average of forward and backward edge lengths.

        For each face-vertex *i* pointing to vertex *V*:

        - **forward** edge length  = ``|pos[next_vert] - pos[V]|``
        - **backward** edge length = ``|pos[prev_vert] - pos[V]|``
        - **average** = ``(forward + backward) / 2``

        Averaging both directions reduces directional bias.  On closed
        meshes every edge is measured exactly twice (once from each
        endpoint), so the per-vertex average equals the true mean of
        all connected edge lengths.

        Args:
            root: Parent compound :class:`~main.Node`.

        Returns:
            The ``edge_lengths`` compound with outputs:
            ``rest_len``, ``def_len`` (both ``array<float>`` of size
            ``face_vertex_count``).
        """
        c = root.create_node("compound", name="edge_lengths")

        c["/input.rest_positions"].add("output", "auto")
        c["/input.def_positions"].add("output", "auto")
        c["/input.face_vertex"].add("output", "auto")
        c["/input.next_vert_index"].add("output", "auto")
        c["/input.prev_vert_index"].add("output", "auto")
        c["/output.rest_len"].add("input", "auto")
        c["/output.def_len"].add("input", "auto")

        # Position lookups
        rest_fv = c.create_node("Core::Array,get_from_array", name="rest_fv_pos")
        c["/input"]["rest_positions"].connect(rest_fv["array"])
        c["/input"]["face_vertex"].connect(rest_fv["index"])

        def_fv = c.create_node("Core::Array,get_from_array", name="def_fv_pos")
        c["/input"]["def_positions"].connect(def_fv["array"])
        c["/input"]["face_vertex"].connect(def_fv["index"])

        rest_next = c.create_node("Core::Array,get_from_array", name="rest_next_pos")
        c["/input"]["rest_positions"].connect(rest_next["array"])
        c["/input"]["next_vert_index"].connect(rest_next["index"])

        def_next = c.create_node("Core::Array,get_from_array", name="def_next_pos")
        c["/input"]["def_positions"].connect(def_next["array"])
        c["/input"]["next_vert_index"].connect(def_next["index"])

        rest_prev = c.create_node("Core::Array,get_from_array", name="rest_prev_pos")
        c["/input"]["rest_positions"].connect(rest_prev["array"])
        c["/input"]["prev_vert_index"].connect(rest_prev["index"])

        def_prev = c.create_node("Core::Array,get_from_array", name="def_prev_pos")
        c["/input"]["def_positions"].connect(def_prev["array"])
        c["/input"]["prev_vert_index"].connect(def_prev["index"])

        # Forward edges (current -> next)
        rest_fwd = c.create_node("Core::Math,subtract", name="rest_fwd_edge")
        rest_next["value"].connect(rest_fwd["a"])
        rest_fv["value"].connect(rest_fwd["b"])

        rest_fwd_len = c.create_node("Core::Math,length", name="rest_fwd_len")
        rest_fwd["output"].connect(rest_fwd_len["vector"])

        def_fwd = c.create_node("Core::Math,subtract", name="def_fwd_edge")
        def_next["value"].connect(def_fwd["a"])
        def_fv["value"].connect(def_fwd["b"])

        def_fwd_len = c.create_node("Core::Math,length", name="def_fwd_len")
        def_fwd["output"].connect(def_fwd_len["vector"])

        # Backward edges (current -> prev)
        rest_bwd = c.create_node("Core::Math,subtract", name="rest_bwd_edge")
        rest_prev["value"].connect(rest_bwd["a"])
        rest_fv["value"].connect(rest_bwd["b"])

        rest_bwd_len = c.create_node("Core::Math,length", name="rest_bwd_len")
        rest_bwd["output"].connect(rest_bwd_len["vector"])

        def_bwd = c.create_node("Core::Math,subtract", name="def_bwd_edge")
        def_prev["value"].connect(def_bwd["a"])
        def_fv["value"].connect(def_bwd["b"])

        def_bwd_len = c.create_node("Core::Math,length", name="def_bwd_len")
        def_bwd["output"].connect(def_bwd_len["vector"])

        # Average: (fwd + bwd) / 2
        rest_sum = c.create_node("Core::Math,add", name="rest_sum")
        rest_fwd_len["length"].connect(rest_sum["fwd"])
        rest_bwd_len["length"].connect(rest_sum["bwd"])

        rest_avg = c.create_node("Core::Math,half_of", name="rest_avg")
        rest_sum["output"].connect(rest_avg["value"])

        def_sum = c.create_node("Core::Math,add", name="def_sum")
        def_fwd_len["length"].connect(def_sum["fwd"])
        def_bwd_len["length"].connect(def_sum["bwd"])

        def_avg = c.create_node("Core::Math,half_of", name="def_avg")
        def_sum["output"].connect(def_avg["value"])

        rest_avg["half_value"].connect(c["/output"]["rest_len"])
        def_avg["half_value"].connect(c["/output"]["def_len"])

        return c

    def _build_vertex_tension(self, root):
        """Create a ``for_each`` loop that computes per-vertex tension.

        Adds a ``Core::Iterators,for_each`` node whose ``max_iterations``
        port is driven by ``point_count`` and whose ``current_index``
        auto-increments from 0 to *V*-1.

        Inside the loop body the algorithm is:

        1. Convert ``face_vertex`` to long to match ``current_index`` type.
        2. ``equal(face_vertex_long, current_index)`` -> boolean mask.
        3. ``filter_array(rest_fv_len, mask)`` + ``filter_array(def_fv_len, mask)``
        4. ``sum_array`` each filtered array; ``array_size`` for count.
        5. ``safe_count = max(count_as_float, 1.0)`` to avoid division by zero.
        6. ``rest_avg = sum_rest / safe_count``; ``def_avg = sum_def / safe_count``.
        7. ``tension = clamp((rest_avg - def_avg) / max(rest_avg, eps)
           * sensitivity + offset, 0, 1)``.

        The for_each automatically collects the per-iteration ``tension``
        scalar into an ``array<float>`` of size ``point_count``.

        Args:
            root: Parent compound :class:`~main.Node`.

        Returns:
            The ``vertex_tension`` for_each :class:`~main.Node` with
            inputs ``max_iterations``, ``face_vertex``, ``rest_fv_len``,
            ``def_fv_len``, ``sensitivity``, ``offset``, ``epsilon``
            and output ``tension``.
        """
        c = root.create_node("Core::Iterators,for_each", name="vertex_tension")

        # Pass-through inputs (full arrays, not iterated)
        c["/input.face_vertex"].add("output", "auto")
        c["/input.rest_fv_len"].add("output", "auto")
        c["/input.def_fv_len"].add("output", "auto")
        c["/input.sensitivity"].add("output", "float")
        c["/input.offset"].add("output", "float")
        c["/input.epsilon"].add("output", "float")

        # Output: tension per vertex (for_each collects into array)
        c["/output.tension"].add("input", "auto")

        # Step 1: type conversion so equal() can compare face_vertex with index
        fv_to_long = c.create_node("Core::Type_Conversion,to_long", name="fv_to_long")
        c["/input"]["face_vertex"].connect(fv_to_long["from"])

        # Step 2: boolean mask
        make_mask = c.create_node("Core::Logic,equal", name="equal")
        fv_to_long["long"].connect(make_mask["first"])
        c["/input"]["current_index"].connect(make_mask["second"])

        # Step 3: filter edge lengths by mask
        filter_rest = c.create_node("Core::Array,filter_array", name="filter_rest")
        c["/input"]["rest_fv_len"].connect(filter_rest["array"])
        make_mask["output"].connect(filter_rest["boolean_array"])

        filter_def = c.create_node("Core::Array,filter_array", name="filter_def")
        c["/input"]["def_fv_len"].connect(filter_def["array"])
        make_mask["output"].connect(filter_def["boolean_array"])

        # Step 4a: sum filtered edge lengths
        sum_rest = c.create_node("Core::Array,sum_array", name="sum_rest")
        filter_rest["filtered_array"].connect(sum_rest["array"])

        sum_def = c.create_node("Core::Array,sum_array", name="sum_def")
        filter_def["filtered_array"].connect(sum_def["array"])

        # Step 4b: count via array_size + convert to float
        count_node = c.create_node("Core::Array,array_size", name="count")
        filter_rest["filtered_array"].connect(count_node["array"])

        count_float = c.create_node("Core::Type_Conversion,to_float", name="count_float")
        count_node["size"].connect(count_float["from"])

        # Step 5: safe_count = max(count, 1.0)
        one_const = c.create_node("Core::Constants,float", name="one_const")
        one_const["output"].value = 1.0

        safe_count = c.create_node("Core::Math,max", name="safe_count")
        count_float["float"].connect(safe_count["count"])
        one_const["output"].connect(safe_count["one"])

        # Step 6: per-vertex averages
        rest_avg = c.create_node("Core::Math,divide", name="rest_avg")
        sum_rest["sum"].connect(rest_avg["total"])
        safe_count["maximum"].connect(rest_avg["cnt"])

        def_avg = c.create_node("Core::Math,divide", name="def_avg")
        sum_def["sum"].connect(def_avg["total"])
        safe_count["maximum"].connect(def_avg["cnt"])

        # Step 7: tension formula
        safe_rest = c.create_node("Core::Math,max", name="safe_rest")
        rest_avg["output"].connect(safe_rest["rest"])
        c["/input"]["epsilon"].connect(safe_rest["eps"])

        edge_diff = c.create_node("Core::Math,subtract", name="edge_diff")
        rest_avg["output"].connect(edge_diff["rest"])
        def_avg["output"].connect(edge_diff["deformed"])

        edge_ratio = c.create_node("Core::Math,divide", name="edge_ratio")
        edge_diff["output"].connect(edge_ratio["diff"])
        safe_rest["maximum"].connect(edge_ratio["safe"])

        scaled = c.create_node("Core::Math,multiply", name="scaled")
        edge_ratio["output"].connect(scaled["ratio"])
        c["/input"]["sensitivity"].connect(scaled["sensitivity"])

        tension_raw = c.create_node("Core::Math,add", name="tension_raw")
        scaled["output"].connect(tension_raw["value"])
        c["/input"]["offset"].connect(tension_raw["off"])

        tension_clamped = c.create_node("Core::Math,clamp", name="tension_clamped")
        tension_raw["output"].connect(tension_clamped["value"])
        tension_clamped["min"].value = 0
        tension_clamped["max"].value = 1

        tension_clamped["clamped"].connect(c["/output"]["tension"])

        return c

    def _build_color_output(self, root):
        """Map per-vertex tension values to green-black-red vertex colors.

        Two ``change_range`` nodes remap the [0, 1] tension range:

        - **Red channel** (compression): ``0.5 -> 1.0`` maps to ``0.0 -> 1.0``
        - **Green channel** (stretch):   ``0.5 -> 0.0`` maps to ``0.0 -> 1.0``

        The resulting RGB is written via ``set_geo_property`` with
        ``target = "point_component"`` so each vertex gets its own color.

        Args:
            root: Parent compound :class:`~main.Node`.

        Returns:
            The ``color_output`` compound with inputs
            ``tension_per_vertex`` and ``deformed_mesh``, and output
            ``out_mesh``.
        """
        c = root.create_node("compound", name="color_output")

        c["/input.tension_per_vertex"].add("output", "auto")
        c["/input.deformed_mesh"].add("output", "Object")
        c["/output.out_mesh"].add("input", "Object")

        # Red: compression (0.5->1 maps to 0->1)
        red_ramp = c.create_node("Core::Math,change_range", name="red_ramp")
        c["/input"]["tension_per_vertex"].connect(red_ramp["value"])
        red_ramp["from_start"].value = 0.5
        red_ramp["from_end"].value = 1.0
        red_ramp["to_start"].value = 0.0
        red_ramp["to_end"].value = 1.0
        red_ramp["clamp"].value = True

        # Green: stretch (0.5->0 maps to 0->1)
        green_ramp = c.create_node("Core::Math,change_range", name="green_ramp")
        c["/input"]["tension_per_vertex"].connect(green_ramp["value"])
        green_ramp["from_start"].value = 0.5
        green_ramp["from_end"].value = 0.0
        green_ramp["to_start"].value = 0.0
        green_ramp["to_end"].value = 1.0
        green_ramp["clamp"].value = True

        # Compose RGB color
        tension_color = c.create_node("Core::Conversion,scalar_to_vector3", name="tension_color")
        red_ramp["result"].connect(tension_color["x"])
        green_ramp["result"].connect(tension_color["y"])

        # Write per-vertex colors (point_component)
        set_color = c.create_node("Geometry::Properties,set_geo_property", name="set_color")
        c["/input"]["deformed_mesh"].connect(set_color["geometry"])
        tension_color["vector3"].connect(set_color["data"])
        set_color["property"].value = "color"
        set_color["target"].value = "point_component"

        set_color["out_geometry"].connect(c["/output"]["out_mesh"])

        return c
