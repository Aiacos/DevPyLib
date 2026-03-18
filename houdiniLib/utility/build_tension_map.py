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

# ── VOP parmtype menu tokens ─────────────────────────────────────
# The Bind/Parameter VOP ``parmtype`` menu accepts token strings.
# Verified in Houdini 21.5 via parm.menuItems().
_PARMTYPE_INT = "int"  # index 1
_PARMTYPE_FLOAT = "float"  # index 0
_PARMTYPE_VECTOR = "vector"  # index 7

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
    v@Cd = v@tension_map_Cd;
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
        _safe_parm_set(blur, "attributes", "tension compression tension_map_Cd Cd")
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
    # MODE: vop — Wrangle (neighbors) + Attribute VOP (math nodes)
    # ══════════════════════════════════════════════════════════════

    def _create_vop_sop(self, container, upstream, param_prefix=""):
        """Create a Wrangle + Attribute VOP chain.

        A Wrangle computes ``rest_avg`` and ``def_avg`` (neighbor iteration
        requires VEX).  An Attribute VOP does the tension formula, compression,
        and color mapping with pure visual VOP nodes.

        Default VOP nodes are preserved for geometry pass-through.
        Bind Exports are NOT wired into geometryvopoutput (that would
        overwrite P and destroy the geometry).

        Args:
            container: Parent node to create inside.
            upstream: Node to wire as input.
            param_prefix (str): Channel reference prefix.

        Returns:
            The Attribute VOP SOP node.
        """
        # ── Wrangle: neighbor edge accumulation ──────────────────
        avg_wrangle = container.createNode("attribwrangle", "edge_avg_calc")
        avg_wrangle.setInput(0, upstream)
        avg_wrangle.parm("class").set(2)
        avg_wrangle.parm("snippet").set(
            textwrap.dedent("""\
            int ncount = neighbourcount(0, @ptnum);
            float rest_total = 0, def_total = 0;
            for (int i = 0; i < ncount; i++) {
                int nb = neighbour(0, @ptnum, i);
                def_total  += distance(@P,    point(0, "P",    nb));
                rest_total += distance(@rest,  point(0, "rest", nb));
            }
            float safe_count = max(float(ncount), 1.0);
            f@rest_avg = rest_total / safe_count;
            f@def_avg  = def_total  / safe_count;
        """)
        )

        # ── Attribute VOP: pure math nodes ───────────────────────
        vop = container.createNode("attribvop", "tension_vop_math")
        vop.setInput(0, avg_wrangle)
        _set_run_over_points(vop)

        # KEEP default nodes (geometryvopglobal, geometryvopoutput)
        vop_net = vop

        # Import rest_avg and def_avg (float attribs from wrangle)
        import_rest_avg = vop_net.createNode("bind", "import_rest_avg")
        _safe_parm_set(import_rest_avg, "parmname", "rest_avg")
        _safe_parm_set(import_rest_avg, "parmtype", "float")

        import_def_avg = vop_net.createNode("bind", "import_def_avg")
        _safe_parm_set(import_def_avg, "parmname", "def_avg")
        _safe_parm_set(import_def_avg, "parmtype", "float")

        # Constants (floatdef is the correct H21.5 parameter name)
        sens = vop_net.createNode("constant", "sensitivity")
        _safe_parm_set(sens, "consttype", 0)
        _safe_parm_set(sens, "floatdef", self._sensitivity)

        off = vop_net.createNode("constant", "offset")
        _safe_parm_set(off, "consttype", 0)
        _safe_parm_set(off, "floatdef", self._offset)

        eps = vop_net.createNode("constant", "epsilon")
        _safe_parm_set(eps, "consttype", 0)
        _safe_parm_set(eps, "floatdef", self._epsilon)

        zero = vop_net.createNode("constant", "zero")
        _safe_parm_set(zero, "consttype", 0)
        _safe_parm_set(zero, "floatdef", 0.0)

        # ── Tension formula ──────────────────────────────────────
        safe_rest = vop_net.createNode("max", "safe_rest")
        safe_rest.setInput(0, import_rest_avg, 0)
        safe_rest.setInput(1, eps, 0)

        edge_diff = vop_net.createNode("subtract", "edge_diff")
        edge_diff.setInput(0, import_rest_avg, 0)
        edge_diff.setInput(1, import_def_avg, 0)

        edge_ratio = vop_net.createNode("divide", "edge_ratio")
        edge_ratio.setInput(0, edge_diff, 0)
        edge_ratio.setInput(1, safe_rest, 0)

        scaled = vop_net.createNode("multiply", "scaled")
        scaled.setInput(0, edge_ratio, 0)
        scaled.setInput(1, sens, 0)

        tension_raw = vop_net.createNode("add", "tension_raw")
        tension_raw.setInput(0, scaled, 0)
        tension_raw.setInput(1, off, 0)

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

        # ── Stretch (for color green channel) ────────────────────
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

        # ── Color: (R=compress, G=stretch, B=0) ──────────────────
        color = vop_net.createNode("floattovec", "color_compose")
        color.setInput(0, compress_clamp, 0)
        color.setInput(1, stretch_clamp, 0)
        color.setInput(2, zero, 0)

        # ── Bind Exports (exportparm=1 = Always) ────────────────
        # NOT wired into geometryvopoutput — that overwrites P!
        for attr_name, attr_type, source in [
            ("tension", "float", tension_clamp),
            ("compression", "float", compress_clamp),
            ("tension_map_Cd", "vector", color),
            ("Cd", "vector", color),
        ]:
            ex = vop_net.createNode("bind", f"export_{attr_name}")
            _safe_parm_set(ex, "parmname", attr_name)
            _safe_parm_set(ex, "parmtype", attr_type)
            _safe_parm_set(ex, "exportparm", 1)
            ex.setInput(0, source, 0)

        vop_net.layoutChildren()
        return vop
