"""Build a Tension Map SOP network in Houdini.

Replicates the algorithm from ``mayaLib.bifrostLib.utilities.build_tension_map``
using Houdini's native node graph.  The network compares edge lengths between a
rest-pose mesh (captured via ``@rest`` attribute) and the current deformed state
to produce three per-vertex outputs:

- **tension** (float 0-1): raw tension value
  (0.0 = full stretch, 0.5 = neutral, 1.0 = full compression).
- **compression** (float 0-1): isolated compression amount
  (0 = neutral, 1 = max compression).
- **tension_map_Cd** (vector): color visualization
  (green = stretch, black = neutral, red = compression).

Three implementation modes are available:

- **both** (default): Creates both Wrangle and VOP branches with a
  Switch SOP to toggle between them at any time.  Ideal for HDA
  authoring — lets the user pick their preferred workflow.
- **wrangle**: A single Attribute Wrangle SOP with VEX code.
  Compact, fast, easy to read and modify.
- **vop**: An Attribute VOP SOP with a visual node network.
  Better for learning, debugging, and non-programmers who prefer
  wiring nodes in the Network Editor.

Algorithm (per vertex *V*)::

    rest_avg    = mean(distance(@rest[V], @rest[nb]) for nb in neighbours(V))
    def_avg     = mean(distance(@P[V],    @P[nb])    for nb in neighbours(V))
    tension     = clamp((rest_avg - def_avg) / max(rest_avg, eps)
                        * sensitivity + offset, 0, 1)
    compression = fit(tension, 0.5 -> 1.0, 0.0 -> 1.0)
    tension_map_Cd = (compression, fit(tension, 0.5 -> 0.0, 1.0 -> 0.0), 0)

Usage inside Houdini (Python Shell or Shelf Tool)::

    from houdiniLib.utility.build_tension_map import TensionMapNetwork

    # Both modes with Switch (default — toggle in parameter editor)
    net = TensionMapNetwork("/obj/geo1")

    # VEX wrangle only
    net = TensionMapNetwork("/obj/geo1", mode="wrangle")

    # VOP nodes only
    net = TensionMapNetwork("/obj/geo1", mode="vop")

    # As HDA-ready subnet with exposed parameters
    net = TensionMapNetwork("/obj/geo1", as_subnet=True)

Note:
    The ``@rest`` attribute must exist on the input geometry.  The
    ``Rest Position SOP`` is automatically prepended to capture it.
    If the geometry already carries ``@rest`` from upstream, the
    Rest Position SOP is a harmless no-op.

Compatibility:
    Tested targeting Houdini 20.x / 21.x.  VOP node type names and
    parameter names may vary across major versions.

References:
    - `Rest Position SOP <https://www.sidefx.com/docs/houdini/nodes/sop/rest.html>`_
    - `Attribute Wrangle SOP <https://www.sidefx.com/docs/houdini/nodes/sop/attribwrangle.html>`_
    - `Attribute VOP SOP <https://www.sidefx.com/docs/houdini/nodes/sop/attribvop.html>`_
    - `Inline Code VOP <https://www.sidefx.com/docs/houdini/nodes/vop/inline.html>`_
    - `Bind VOP <https://www.sidefx.com/docs/houdini/nodes/vop/bind.html>`_
    - `VEX neighbour functions <https://www.sidefx.com/docs/houdini/vex/functions/neighbour.html>`_
"""

import textwrap

import hou

# ── VOP parmtype menu indices ────────────────────────────────────
# The Bind VOP ``parmtype`` menu uses integer indices, not strings.
# See: https://www.sidefx.com/docs/houdini/nodes/vop/bind.html
_PARMTYPE_INT = 0
_PARMTYPE_FLOAT = 1
_PARMTYPE_VECTOR = 6

# Known parameter names for "Run Over" across Houdini versions.
# Houdini 19.x-20.x may use different names; we try each in order.
_RUN_OVER_PARM_NAMES = ("bindrunover", "bindclass", "class")
_RUN_OVER_POINTS_VALUES = {"bindrunover": 1, "bindclass": 2, "class": 2}


def _set_run_over_points(node):
    """Set an Attribute VOP/Wrangle to run over points.

    Tries known parameter names across Houdini versions and falls back
    silently if none exist (the default is usually points anyway).

    Args:
        node: The SOP node to configure.
    """
    for name in _RUN_OVER_PARM_NAMES:
        parm = node.parm(name)
        if parm is not None:
            parm.set(_RUN_OVER_POINTS_VALUES[name])
            return


def _safe_parm_set(node, parm_name, value):
    """Set a parameter value, silently skipping if the parameter does not exist.

    Args:
        node: The hou.Node containing the parameter.
        parm_name (str): Parameter name.
        value: Value to set.

    Returns:
        True if the parameter was set, False if it was not found.
    """
    parm = node.parm(parm_name)
    if parm is not None:
        parm.set(value)
        return True
    return False


# ── VEX snippet ─────────────────────────────────────────────────
_TENSION_VEX = textwrap.dedent("""\
    // Tension Map — per-vertex edge-length comparison
    // Inputs:  @P (deformed), @rest (bind pose)
    // Outputs: f@tension, f@compression, v@tension_map_Cd

    float sensitivity = chf("sensitivity");
    float offset      = chf("offset");
    float epsilon     = chf("epsilon");

    // ── Neighbor edge accumulation ──────────────────
    int ncount = neighbourcount(0, @ptnum);
    float rest_total = 0;
    float def_total  = 0;

    for (int i = 0; i < ncount; i++) {
        int nb = neighbour(0, @ptnum, i);
        def_total  += distance(@P,    point(0, "P",    nb));
        rest_total += distance(@rest,  point(0, "rest", nb));
    }

    float safe_count = max(float(ncount), 1.0);
    float rest_avg = rest_total / safe_count;
    float def_avg  = def_total  / safe_count;

    // ── Tension formula ─────────────────────────────
    float safe_rest = max(rest_avg, epsilon);
    float ratio     = (rest_avg - def_avg) / safe_rest;
    f@tension       = clamp(ratio * sensitivity + offset, 0.0, 1.0);

    // ── Compression ─────────────────────────────────
    f@compression = clamp(fit(f@tension, 0.5, 1.0, 0.0, 1.0), 0.0, 1.0);

    // ── Color: red=compress, green=stretch, blue=0 ──
    float stretch = clamp(fit(f@tension, 0.0, 0.5, 1.0, 0.0), 0.0, 1.0);
    v@tension_map_Cd = set(f@compression, stretch, 0.0);
""")


class TensionMapNetwork:
    """Build a SOP-level tension map network inside a Houdini geo node.

    Args:
        parent_path (str): Path to the parent node (e.g. ``"/obj/geo1"``).
        mode (str): Implementation mode:
            - ``"both"`` (default): Wrangle + VOP with a Switch SOP.
            - ``"wrangle"``: Single Attribute Wrangle with VEX code.
            - ``"vop"``: Attribute VOP with visual node network.
        as_subnet (bool): When ``True``, wraps the network in a Subnet SOP
            suitable for promoting to an HDA.  Defaults to ``False``.
        dual_input (bool): When ``True`` (and ``as_subnet=True``), creates
            an HDA with **two inputs** — deformed mesh (input 1) and rest
            mesh (input 2).  An Attribute Copy SOP transfers ``@P`` from the
            rest mesh as ``@rest`` on the deformed mesh.  When ``False``,
            uses a single input with a Rest Position SOP.
            Defaults to ``False``.
        wire_after (str | None): Name of an existing SOP to wire into.
            When ``None``, connects to the display/render node.
        sensitivity (float): Default sensitivity parameter value.
        offset (float): Default offset parameter value.
        epsilon (float): Default epsilon parameter value.

    Attributes:
        parent: The parent ``hou.SopNode`` container.
        rest_sop: The Rest Position SOP node (single-input mode).
        attribcopy_sop: The Attribute Copy SOP (dual-input mode).
        calc_sop: The final output SOP node (Wrangle, VOP, or Switch).
        wrangle_sop: The Wrangle SOP (``"both"`` and ``"wrangle"`` modes).
        vop_sop: The Attribute VOP SOP (``"both"`` and ``"vop"`` modes).
        switch_sop: The Switch SOP (``"both"`` mode only).
        subnet: The wrapping Subnet node (only when *as_subnet* is ``True``).
    """

    _VALID_MODES = ("both", "wrangle", "vop")

    def __init__(
        self,
        parent_path,
        mode="both",
        as_subnet=False,
        dual_input=False,
        wire_after=None,
        sensitivity=1.0,
        offset=0.5,
        epsilon=0.0001,
    ):
        """Create the tension map node network inside *parent_path*."""
        if mode not in self._VALID_MODES:
            raise ValueError(f"Unknown mode {mode!r}. Choose from: {self._VALID_MODES}")

        self.parent = hou.node(parent_path)
        if self.parent is None:
            raise ValueError(f"Node not found: {parent_path!r}")

        self._mode = mode
        self._dual_input = dual_input
        self._sensitivity = sensitivity
        self._offset = offset
        self._epsilon = epsilon

        if as_subnet:
            self._build_as_subnet(wire_after)
        else:
            self._build_flat(wire_after)

    # ── public helpers ───────────────────────────────────────────

    def layout(self):
        """Auto-layout all created nodes in the network editor."""
        self.parent.layoutChildren()

    # ── build strategies ─────────────────────────────────────────

    def _build_flat(self, wire_after):
        """Build nodes directly inside *parent*."""
        upstream = self._resolve_upstream(wire_after)
        self.rest_sop = self._create_rest_sop(self.parent, upstream)
        self.calc_sop = self._create_calc_sop(self.parent, self.rest_sop)
        self.blur_sop = self._create_blur_sop(self.parent, self.calc_sop)
        self.blur_sop.setDisplayFlag(True)
        self.blur_sop.setRenderFlag(True)
        self.subnet = None
        self._init_missing_attrs()
        self.layout()

    def _build_as_subnet(self, wire_after):
        """Build nodes inside a Subnet SOP (HDA-ready).

        When ``dual_input`` is enabled, the subnet has two inputs:

        - **Input 1**: Deformed mesh (current @P).
        - **Input 2**: Rest mesh (its @P becomes @rest on the deformed mesh).

        An Attribute Wrangle copies positions from input 2 as ``@rest``.
        """
        upstream = self._resolve_upstream(wire_after)

        self.subnet = self.parent.createNode("subnet", "tension_map")
        self.subnet.setColor(hou.Color((0.3, 0.6, 0.3)))

        # Expose parameters on the subnet
        ptg = self.subnet.parmTemplateGroup()
        ptg.append(
            hou.FloatParmTemplate(
                "sensitivity",
                "Sensitivity",
                1,
                default_value=(self._sensitivity,),
                min=0.0,
                max=10.0,
            )
        )
        ptg.append(
            hou.FloatParmTemplate(
                "offset",
                "Offset",
                1,
                default_value=(self._offset,),
                min=0.0,
                max=1.0,
            )
        )
        ptg.append(
            hou.FloatParmTemplate(
                "epsilon",
                "Epsilon",
                1,
                default_value=(self._epsilon,),
                min=0.0,
                max=0.01,
            )
        )
        ptg.append(
            hou.IntParmTemplate(
                "blur_iterations",
                "Blur Iterations",
                1,
                default_value=(0,),
                min=0,
                max=50,
            )
        )
        self.subnet.setParmTemplateGroup(ptg)

        if upstream is not None:
            self.subnet.setInput(0, upstream)

        input1 = self.subnet.indirectInputs()[0]

        if self._dual_input:
            # Two-input mode: deformed (input 1) + rest (input 2)
            input2 = self.subnet.indirectInputs()[1]

            # Wrangle that copies @P from input 2 as @rest on input 1
            self.attribcopy_sop = self.subnet.createNode(
                "attribwrangle",
                "copy_rest_from_input2",
            )
            self.attribcopy_sop.setInput(0, input1)
            self.attribcopy_sop.setInput(1, input2)
            self.attribcopy_sop.parm("class").set(2)  # Run over points
            self.attribcopy_sop.parm("snippet").set('v@rest = point(1, "P", @ptnum);\n')
            self.rest_sop = None
            calc_upstream = self.attribcopy_sop
        else:
            # Single-input mode: Rest Position SOP captures @rest
            self.attribcopy_sop = None
            self.rest_sop = self._create_rest_sop(self.subnet, None)
            self.rest_sop.setInput(0, input1)
            calc_upstream = self.rest_sop

        self.calc_sop = self._create_calc_sop(
            self.subnet,
            calc_upstream,
            param_prefix="../../",
        )

        self.blur_sop = self._create_blur_sop(
            self.subnet,
            self.calc_sop,
            param_prefix="../",
        )

        out = self.subnet.createNode("output", "output0")
        out.setInput(0, self.blur_sop)
        self.subnet.layoutChildren()

        self.subnet.setDisplayFlag(True)
        self.subnet.setRenderFlag(True)
        self._init_missing_attrs()
        self.layout()

    # ── upstream resolution ──────────────────────────────────────

    def _resolve_upstream(self, wire_after):
        """Find the node to wire into."""
        if wire_after is not None:
            node = self.parent.node(wire_after)
            if node is None:
                raise ValueError(f"Node {wire_after!r} not found in {self.parent.path()}")
            return node

        for child in self.parent.children():
            if child.isDisplayFlagSet():
                return child
        return None

    # ── Rest Position SOP ────────────────────────────────────────

    def _create_rest_sop(self, container, upstream):
        """Create a Rest Position SOP to capture ``@rest``.

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input (can be ``None``).

        Returns:
            The created Rest Position SOP node.
        """
        rest = container.createNode("rest", "capture_rest")
        if upstream is not None:
            rest.setInput(0, upstream)
        return rest

    # ── Attribute Blur SOP ────────────────────────────────────────

    def _create_blur_sop(self, container, upstream, param_prefix=""):
        """Create an Attribute Blur SOP to smooth tension results.

        Blurs ``tension``, ``compression``, and ``Cd`` point attributes.
        Default iterations is 0 (no blur / pass-through).

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input.
            param_prefix (str): Channel reference prefix for linking
                to the subnet's ``blur_iterations`` parameter.

        Returns:
            The created Attribute Blur SOP node.
        """
        blur = container.createNode("attribblur", "tension_blur")
        blur.setInput(0, upstream)

        # Configure which attributes to blur
        _safe_parm_set(blur, "attribs", "tension compression tension_map_Cd")
        # Blur mode: 0 = by count (iterations)
        _safe_parm_set(blur, "mode", 0)
        # Default: 0 iterations (pass-through)
        _safe_parm_set(blur, "iterations", 0)

        # When inside a subnet, link iterations to the subnet parameter
        if param_prefix:
            parm = blur.parm("iterations")
            if parm is not None:
                parm.setExpression(
                    f'ch("{param_prefix}blur_iterations")',
                    hou.exprLanguage.Hscript,
                )

        return blur

    def _init_missing_attrs(self):
        """Set convenience attributes to ``None`` for unused modes."""
        for attr in (
            "wrangle_sop",
            "vop_sop",
            "switch_sop",
            "rest_sop",
            "attribcopy_sop",
            "blur_sop",
        ):
            if not hasattr(self, attr):
                setattr(self, attr, None)

    # ── Calculation SOP (mode dispatcher) ────────────────────────

    def _create_calc_sop(self, container, upstream, param_prefix=""):
        """Create the calculation node(s) based on the selected mode.

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input.
            param_prefix (str): Prefix for channel references when
                inside a subnet.

        Returns:
            The final output SOP node (Wrangle, VOP, or Switch).
        """
        if self._mode == "wrangle":
            self.wrangle_sop = self._create_wrangle_sop(
                container,
                upstream,
                param_prefix,
            )
            return self.wrangle_sop
        if self._mode == "vop":
            self.vop_sop = self._create_vop_sop(
                container,
                upstream,
                param_prefix,
            )
            return self.vop_sop
        # mode == "both"
        return self._create_both_sop(container, upstream, param_prefix)

    # ══════════════════════════════════════════════════════════════
    # MODE: both — Wrangle + VOP with Switch SOP
    # ══════════════════════════════════════════════════════════════

    def _create_both_sop(self, container, upstream, param_prefix=""):
        """Create both Wrangle and VOP branches with a Switch SOP.

        Network layout::

            capture_rest
            ├── tension_wrangle  (input 0 of switch)
            ├── tension_vop      (input 1 of switch)
            └── method_switch
                └── "Method" menu: Wrangle / VOP

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input.
            param_prefix (str): Prefix for channel references when
                inside a subnet.

        Returns:
            The Switch SOP node.
        """
        self.wrangle_sop = self._create_wrangle_sop(
            container,
            upstream,
            param_prefix,
        )
        self.wrangle_sop.setColor(hou.Color((0.4, 0.6, 0.8)))

        self.vop_sop = self._create_vop_sop(
            container,
            upstream,
            param_prefix,
        )
        self.vop_sop.setColor(hou.Color((0.8, 0.6, 0.4)))

        # Switch SOP: input 0 = wrangle, input 1 = vop
        self.switch_sop = container.createNode("switch", "method_switch")
        self.switch_sop.setInput(0, self.wrangle_sop)
        self.switch_sop.setInput(1, self.vop_sop)
        self.switch_sop.parm("input").set(0)  # default: wrangle

        # Add a labeled menu to the Switch node
        ptg = self.switch_sop.parmTemplateGroup()
        ptg.replace(
            "input",
            hou.MenuParmTemplate(
                "input",
                "Method",
                ("0", "1"),
                menu_labels=("Wrangle (VEX)", "VOP (Nodes)"),
                default_value=0,
            ),
        )
        self.switch_sop.setParmTemplateGroup(ptg)

        # When inside a subnet, expose the method selector
        if param_prefix:
            # Add menu parm to the subnet interface
            subnet = container
            sub_ptg = subnet.parmTemplateGroup()
            sub_ptg.append(
                hou.MenuParmTemplate(
                    "method",
                    "Method",
                    ("0", "1"),
                    menu_labels=("Wrangle (VEX)", "VOP (Nodes)"),
                    default_value=0,
                )
            )
            subnet.setParmTemplateGroup(sub_ptg)

            self.switch_sop.parm("input").setExpression(
                'ch("../method")',
                hou.exprLanguage.Hscript,
            )

        return self.switch_sop

    # ══════════════════════════════════════════════════════════════
    # MODE: wrangle — single Attribute Wrangle with VEX code
    # ══════════════════════════════════════════════════════════════

    def _create_wrangle_sop(self, container, upstream, param_prefix=""):
        """Create an Attribute Wrangle SOP with the tension VEX snippet.

        The entire algorithm lives in a single VEX snippet with ``chf()``
        channel references for the three user parameters.

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input.
            param_prefix (str): Channel reference prefix (unused for
                wrangle — ``chf()`` references are local).

        Returns:
            The created Attribute Wrangle SOP node.
        """
        wrangle = container.createNode("attribwrangle", "tension_calc")
        wrangle.setInput(0, upstream)
        # Run over points (attribwrangle "class" parm: 2=points)
        wrangle.parm("class").set(2)

        # Set VEX snippet
        wrangle.parm("snippet").set(_TENSION_VEX)

        # Create spare parameters for chf() references
        ptg = wrangle.parmTemplateGroup()

        ptg.append(
            hou.FloatParmTemplate(
                "sensitivity",
                "Sensitivity",
                1,
                default_value=(self._sensitivity,),
                min=0.0,
                max=10.0,
            )
        )
        ptg.append(
            hou.FloatParmTemplate(
                "offset",
                "Offset",
                1,
                default_value=(self._offset,),
                min=0.0,
                max=1.0,
            )
        )
        ptg.append(
            hou.FloatParmTemplate(
                "epsilon",
                "Epsilon",
                1,
                default_value=(self._epsilon,),
                min=0.0,
                max=0.01,
            )
        )

        wrangle.setParmTemplateGroup(ptg)

        # When inside a subnet, link spare parms to the subnet interface.
        # The wrangle is a direct child of the subnet, so the relative
        # path to the subnet's parms is always "../" (one level up),
        # regardless of the param_prefix passed for VOP nodes.
        if param_prefix:
            for name in ("sensitivity", "offset", "epsilon"):
                wrangle.parm(name).setExpression(
                    f'ch("../{name}")',
                    hou.exprLanguage.Hscript,
                )

        return wrangle

    # ══════════════════════════════════════════════════════════════
    # MODE: vop — Attribute VOP with visual node network
    # ══════════════════════════════════════════════════════════════

    def _create_vop_sop(self, container, upstream, param_prefix=""):
        """Create the Attribute VOP containing the tension calculation network.

        The entire tension formula is built with pure VOP nodes except for
        the neighbor edge accumulation, which requires a single Inline Code
        VOP (Houdini VOPs lack a topological neighbor iterator node).

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input.
            param_prefix (str): Prefix for channel references
                (e.g. ``"../../"`` when inside a subnet).

        Returns:
            The created Attribute VOP SOP node.
        """
        vop = container.createNode("attribvop", "tension_calc")
        vop.setInput(0, upstream)
        # Run over points — parameter name varies across Houdini versions
        _set_run_over_points(vop)

        vop_net = vop

        # ── Remove default nodes ─────────────────────────────────
        for child in list(vop_net.children()):
            child.destroy()

        # ── Import attributes via Bind VOPs ──────────────────────
        import_p = self._create_bind_import(vop_net, "P", _PARMTYPE_VECTOR)
        import_rest = self._create_bind_import(
            vop_net,
            "rest",
            _PARMTYPE_VECTOR,
        )
        import_ptnum = self._create_bind_import(
            vop_net,
            "ptnum",
            _PARMTYPE_INT,
        )

        # ── Parameters (sensitivity, offset, epsilon) ────────────
        sens_parm = self._create_parameter(
            vop_net,
            "sensitivity",
            self._sensitivity,
            param_prefix,
        )
        offset_parm = self._create_parameter(
            vop_net,
            "offset",
            self._offset,
            param_prefix,
        )
        eps_parm = self._create_parameter(
            vop_net,
            "epsilon",
            self._epsilon,
            param_prefix,
        )

        # ── Inline Code: neighbor edge accumulation ──────────────
        inline = self._create_edge_accumulation_vop(vop_net)
        inline.setInput(0, import_p, 0)
        inline.setInput(1, import_rest, 0)
        inline.setInput(2, import_ptnum, 0)

        # ── Math: tension formula (all VOP nodes) ────────────────

        safe_rest = vop_net.createNode("max", "safe_rest")
        safe_rest.setInput(0, inline, 0)  # rest_avg
        safe_rest.setInput(1, eps_parm, 0)

        edge_diff = vop_net.createNode("subtract", "edge_diff")
        edge_diff.setInput(0, inline, 0)  # rest_avg
        edge_diff.setInput(1, inline, 1)  # def_avg

        edge_ratio = vop_net.createNode("divide", "edge_ratio")
        edge_ratio.setInput(0, edge_diff, 0)
        edge_ratio.setInput(1, safe_rest, 0)

        scaled = vop_net.createNode("multiply", "scaled")
        scaled.setInput(0, edge_ratio, 0)
        scaled.setInput(1, sens_parm, 0)

        tension_raw = vop_net.createNode("add", "tension_raw")
        tension_raw.setInput(0, scaled, 0)
        tension_raw.setInput(1, offset_parm, 0)

        tension_clamp = vop_net.createNode("clamp", "tension_clamp")
        tension_clamp.setInput(0, tension_raw, 0)
        _safe_parm_set(tension_clamp, "min", 0.0)
        _safe_parm_set(tension_clamp, "max", 1.0)

        # ── Compression ──────────────────────────────────────────

        compress_fit = vop_net.createNode("fit", "compress_fit")
        compress_fit.setInput(0, tension_clamp, 0)
        _safe_parm_set(compress_fit, "srcmin", 0.5)
        _safe_parm_set(compress_fit, "srcmax", 1.0)
        _safe_parm_set(compress_fit, "destmin", 0.0)
        _safe_parm_set(compress_fit, "destmax", 1.0)

        compress_clamp = vop_net.createNode("clamp", "compress_clamp")
        compress_clamp.setInput(0, compress_fit, 0)
        _safe_parm_set(compress_clamp, "min", 0.0)
        _safe_parm_set(compress_clamp, "max", 1.0)

        # ── Stretch (local, for color only) ──────────────────────

        stretch_fit = vop_net.createNode("fit", "stretch_fit")
        stretch_fit.setInput(0, tension_clamp, 0)
        _safe_parm_set(stretch_fit, "srcmin", 0.0)
        _safe_parm_set(stretch_fit, "srcmax", 0.5)
        _safe_parm_set(stretch_fit, "destmin", 1.0)
        _safe_parm_set(stretch_fit, "destmax", 0.0)

        stretch_clamp = vop_net.createNode("clamp", "stretch_clamp")
        stretch_clamp.setInput(0, stretch_fit, 0)
        _safe_parm_set(stretch_clamp, "min", 0.0)
        _safe_parm_set(stretch_clamp, "max", 1.0)

        # ── Color composition ────────────────────────────────────
        zero_const = vop_net.createNode("constant", "zero_const")
        _safe_parm_set(zero_const, "consttype", 0)  # 0 = float
        _safe_parm_set(zero_const, "floatval", 0.0)

        color = vop_net.createNode("floattovec", "color_compose")
        color.setInput(0, compress_clamp, 0)  # R = compression
        color.setInput(1, stretch_clamp, 0)  # G = stretch
        color.setInput(2, zero_const, 0)  # B = 0

        # ── Bind exports ─────────────────────────────────────────
        output_node = vop_net.createNode("geometryvopoutput", "output")

        bind_tension = self._create_bind_export(
            vop_net,
            "tension",
            _PARMTYPE_FLOAT,
        )
        bind_tension.setInput(0, tension_clamp, 0)

        bind_compress = self._create_bind_export(
            vop_net,
            "compression",
            _PARMTYPE_FLOAT,
        )
        bind_compress.setInput(0, compress_clamp, 0)

        bind_cd = self._create_bind_export(
            vop_net,
            "tension_map_Cd",
            _PARMTYPE_VECTOR,
        )
        bind_cd.setInput(0, color, 0)

        output_node.setInput(0, bind_tension, 0)
        output_node.setInput(1, bind_compress, 0)
        output_node.setInput(2, bind_cd, 0)

        vop_net.layoutChildren()
        return vop

    # ── VOP node helpers ─────────────────────────────────────────

    @staticmethod
    def _create_edge_accumulation_vop(vop_net):
        """Create an Inline Code VOP for neighbor-based edge accumulation.

        This is the only node that requires VEX — Houdini VOPs do not
        provide a built-in topological neighbor iterator node.  All other
        math is done with pure VOP nodes.

        Args:
            vop_net: The VOP network node to create inside.

        Returns:
            The created Inline Code VOP node with outputs:
            ``rest_avg`` (float) and ``def_avg`` (float).
        """
        inline = vop_net.createNode("inline", "edge_accumulation")

        # Configure inputs (multiparm: inputNum → inputName#/inputType#)
        _safe_parm_set(inline, "inputNum", 3)

        _safe_parm_set(inline, "inputName1", "P")
        _safe_parm_set(inline, "inputType1", "vector")

        _safe_parm_set(inline, "inputName2", "rest")
        _safe_parm_set(inline, "inputType2", "vector")

        _safe_parm_set(inline, "inputName3", "ptnum")
        _safe_parm_set(inline, "inputType3", "int")

        # Configure outputs (multiparm: outputNum → outputName#/outputType#)
        _safe_parm_set(inline, "outputNum", 2)

        _safe_parm_set(inline, "outputName1", "rest_avg")
        _safe_parm_set(inline, "outputType1", "float")

        _safe_parm_set(inline, "outputName2", "def_avg")
        _safe_parm_set(inline, "outputType2", "float")

        _safe_parm_set(
            inline,
            "code",
            "int ncount = neighbourcount(0, ptnum);\n"
            "float rest_total = 0;\n"
            "float def_total = 0;\n"
            "\n"
            "for (int i = 0; i < ncount; i++) {\n"
            "    int nb = neighbour(0, ptnum, i);\n"
            '    vector nb_P = point(0, "P", nb);\n'
            '    vector nb_rest = point(0, "rest", nb);\n'
            "    def_total += distance(P, nb_P);\n"
            "    rest_total += distance(rest, nb_rest);\n"
            "}\n"
            "\n"
            "float safe_count = max(float(ncount), 1.0);\n"
            "$rest_avg = rest_total / safe_count;\n"
            "$def_avg = def_total / safe_count;\n",
        )

        return inline

    @staticmethod
    def _create_bind_import(vop_net, name, parmtype):
        """Create a Bind VOP to import a point attribute.

        Args:
            vop_net: The VOP network to create inside.
            name (str): Attribute name to import (e.g. ``"P"``, ``"rest"``).
            parmtype (int): Attribute type index (use module constants
                ``_PARMTYPE_FLOAT``, ``_PARMTYPE_INT``, ``_PARMTYPE_VECTOR``).

        Returns:
            The created Bind VOP node.
        """
        bind = vop_net.createNode("bind", f"import_{name}")
        _safe_parm_set(bind, "parmname", name)
        _safe_parm_set(bind, "parmtype", parmtype)
        return bind

    @staticmethod
    def _create_parameter(vop_net, name, default, prefix=""):
        """Create a Parameter VOP node (channel reference or constant).

        Args:
            vop_net: The VOP network to create inside.
            name (str): Parameter name.
            default (float): Default value.
            prefix (str): Channel reference prefix for subnet parameters.

        Returns:
            The created Parameter VOP node.
        """
        parm_node = vop_net.createNode("parameter", f"parm_{name}")
        _safe_parm_set(parm_node, "parmname", name)
        _safe_parm_set(parm_node, "parmlabel", name.replace("_", " ").title())
        _safe_parm_set(parm_node, "parmtype", _PARMTYPE_FLOAT)
        _safe_parm_set(parm_node, "floatdef", default)

        if prefix:
            _safe_parm_set(parm_node, "usealiasparm", True)
            _safe_parm_set(parm_node, "aliasparm", f"{prefix}{name}")

        return parm_node

    @staticmethod
    def _create_bind_export(vop_net, name, parmtype):
        """Create a Bind Export VOP node to write a point attribute.

        Args:
            vop_net: The VOP network to create inside.
            name (str): Attribute name to export (e.g. ``"tension"``).
            parmtype (int): Attribute type index (use module constants
                ``_PARMTYPE_FLOAT``, ``_PARMTYPE_VECTOR``).

        Returns:
            The created Bind Export VOP node.
        """
        bind = vop_net.createNode("bind", f"export_{name}")
        _safe_parm_set(bind, "parmname", name)
        _safe_parm_set(bind, "parmtype", parmtype)
        _safe_parm_set(bind, "exportparm", 1)  # Enable export
        return bind
