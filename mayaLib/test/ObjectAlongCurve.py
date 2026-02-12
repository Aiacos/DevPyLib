import maya.cmds as cmds
import pymel.core as pm


class CurvesFromEdge(object):
    """Create NURBS curves from polygon mesh edge loops with optional rebuild."""

    def __init__(self, geo, edge, rebuild=True):
        """Initialise NURBS curve from polygon edge loop."""
        self.geo = pm.ls(geo)[-1]
        self.name = str(geo.name()).replace("_geo", "") + "_cv_0"

        if isinstance(edge, pm.MeshEdge):
            edge_list = self._poly_select_edge_loop(edge)
        elif isinstance(edge, list):
            print("List: ", edge)
            if isinstance(edge[-1], pm.MeshEdge):
                edge_list = pm.ls(edge)
            elif isinstance(edge[-1], int):
                min_idx, max_idx = self._get_min_max_edge(edge)
                edge_list = self._poly_select_edge_loop_path(min_idx, max_idx)
            else:
                print("Not Valid Edge")
        else:
            print("Not Valid Edge")
        """
        if edge_idx and not edge_loop:
            tmp_loop_idx = pm.polySelect(geo, edgeLoop=edge_idx)
            min_edge = min(tmp_loop_idx)
            max_edge = max(tmp_loop_idx)
            pm.polySelect(geo, edgeLoopPath=[min_edge, max_edge])
        """

        self.cv, self.deformer_node = self.poly_to_curve(edge_list)
        if rebuild:
            self._rebuild_curve(self.cv)

        pm.select(cl=True)

    def _poly_select_edge_loop(self, edge):
        pm.polySelect(self.geo, edgeLoop=edge.index())

        return pm.ls(sl=True)

    def _poly_select_edge_loop_path(self, min_edge, max_edge):
        pm.polySelect(self.geo, edgeLoopPath=[min_edge, max_edge])

        return pm.ls(sl=True)

    def _get_min_max_edge(self, edge):
        tmp_loop = pm.ls(self._poly_select_edge_loop(edge), fl=True)
        tmp_loop_idx_list = [e.index() for e in tmp_loop]
        min_edge = min(tmp_loop_idx_list)
        max_edge = max(tmp_loop_idx_list)

        return int(min_edge), int(max_edge)

    def _reverse_curve_direction(self, cv):
        deformer_node = pm.reverseCurve(cv, ch=True, rpo=True)
        pm.rename(deformer_node, self.name + "_reverseCurve")

        return deformer_node

    def _rebuild_curve(self, cv):
        deformer_node = pm.rebuildCurve(
            cv,
            ch=True,
            rpo=True,
            rt=0,
            end=1,
            kr=0,
            kcp=0,
            kep=1,
            kt=0,
            s=4,
            d=3,
            tol=0.0001,
        )[-1]
        pm.rename(deformer_node, self.name + "_rebuildCurve")

        return deformer_node

    def poly_to_curve(self, edge_list):
        """Convert polygon edges to a NURBS curve.

        Creates a degree 3 NURBS curve from the provided edge list using Maya's
        polyToCurve command with smooth mesh preview conformity.

        Args:
            edge_list: List of polygon edges to convert to curve.

        Returns:
            tuple: The created curve and polyEdgeToCurve deformer node.
        """
        edge_list = pm.ls(edge_list)
        pm.select(edge_list)
        cv, deformer = pm.ls(
            pm.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1, n=self.name)
        )
        self.name = str(cv.name())
        pm.rename(deformer, self.name + "_polyEdgeToCurve")

        return cv, deformer

    def get_cv(self):
        """Get the created NURBS curve.

        Returns:
            The NURBS curve created from polygon edges.
        """
        return self.cv

    def get_deformer_node(self):
        """Get the polyEdgeToCurve deformer node.

        Returns:
            The deformer node created during curve conversion.
        """
        return self.deformer_node


class JointChainCurve(object):
    """Calculate spacing for joint chains distributed along curves."""

    def __init__(self, pointsNumber=5):
        """Initialise joint chain spacing calculator."""
        # nameBuilder_locator = curve[0] + "_loc"  # in function, lacal variables
        # nameBuilder_joint = curve[0] + "_jnt"  # in function, local variables

        self.spacing = 1.0 / (pointsNumber - 1)


def extract_feather_curves(geo, edge_idx_list):
    """Extract and rebuild NURBS curves from polygon edge loops.

    Creates NURBS curves from multiple edge loops on a polygon mesh, with
    alternating curve directions. Each curve is rebuilt to degree 3 with
    4 spans for consistent topology.

    Args:
        geo: Polygon geometry mesh to extract curves from.
        edge_idx_list: List of edge indices defining edge loops.

    Returns:
        list: List of rebuilt NURBS curves extracted from edge loops.
    """
    cv_list = []
    for loop_idx, i in zip(edge_idx_list, range(0, len(edge_idx_list))):
        tmp_loop_idx = pm.polySelect(geo, edgeLoop=loop_idx)
        # min_edge = min(tmp_loop_idx)
        # max_edge = max(tmp_loop_idx)
        # pm.polySelect(geo, edgeLoopPath=[min_edge, max_edge])
        loop = pm.ls(sl=True)
        cv = pm.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1)[0]

        if i % 2:
            pm.reverseCurve(cv, ch=True, rpo=True)

        pm.rebuildCurve(
            cv,
            ch=True,
            rpo=True,
            rt=0,
            end=1,
            kr=0,
            kcp=0,
            kep=1,
            kt=0,
            s=4,
            d=3,
            tol=0.0001,
        )
        cv_list.append(cv)

    return cv_list


## Var ##


curve = cmds.ls(sl=True)


## Main --wip
class ObjectAlongCurve(object):
    """Create joint chains along a curve path using motion path animation."""

    def __init__(self, path_crv, n_jnt=12, offset_driver=None):
        """Initialise joint chain along curve path."""
        self.path_crv = path_crv
        self.n_jnts = n_jnt

        self.path_crv_name = str(path_crv).replace("_crv", "")
        # self.name_builder_locator = self.path_crv_name + "_loc"
        # self.name_builder_joint = self.path_crv_name + "_jnt"

        self.spacing = 1.0 / (n_jnt - 1)
        self.joint_list, self.motionpath_list = self._build_jnts()
        self.joint_list_grp = cmds.group(
            self.joint_list[0], n=self.path_crv_name + "_jnts_grp", w=True
        )

        if offset_driver:
            self._add_offset(offset_driver)

    def _build_jnts(self):
        joint_list = []
        motionpath_list = []
        for p in range(0, self.n_jnts):
            jnt_name = f"{self.path_crv_name}_{str(p)}_jnt"
            if p == 0:
                joint = cmds.joint(n=jnt_name)
                cmds.setAttr(jnt_name + ".inheritsTransform", 0)
                motionPath = cmds.pathAnimation(joint, c=self.path_crv, f=True)
                deleteConnection(motionPath + ".u")
                cmds.setAttr(motionPath + ".uValue", 0)
                joint_list.append(joint)
                motionpath_list.append(motionPath)
            else:
                joint = cmds.joint(n=jnt_name)
                cmds.setAttr(jnt_name + ".inheritsTransform", 0)
                motionPath = cmds.pathAnimation(joint, c=self.path_crv, f=True)
                deleteConnection(motionPath + ".u")
                cmds.setAttr(motionPath + ".uValue", self.spacing * p)
                joint_list.append(joint)
                motionpath_list.append(motionPath)

        return joint_list, motionpath_list

    def _add_offset(self, offset_driver):
        for m in self.motionpath_list:
            u_value = cmds.getAttr(m + ".uValue")

            add_node = cmds.shadingNode("addDoubleLinear", asUtility=True)
            cmds.setAttr(add_node + ".input1", u_value)
            cmds.connectAttr(offset_driver, add_node + ".input2", f=True)
            cmds.connectAttr(add_node + ".output", m + ".uValue")


def deleteConnection(plug):
    """Delete Maya attribute connections safely.

    Equivalent to MEL's CBdeleteConnection command. Handles both read-only
    and writable destination attributes by using appropriate disconnection
    methods.

    Args:
        plug: Maya attribute plug to disconnect (e.g., "node.attribute").
    """
    if cmds.connectionInfo(plug, isDestination=True):
        plug = cmds.connectionInfo(plug, getExactDestination=True)
        readOnly = cmds.ls(plug, ro=True)
        # delete -icn doesn't work if destination attr is readOnly
        if readOnly:
            source = cmds.connectionInfo(plug, sourceFromDestination=True)
            cmds.disconnectAttr(source, plug)
        else:
            cmds.delete(plug, icn=True)


def pointMode():
    """Create locators at evenly-spaced points along a curve.

    Generates locator transforms positioned at parametric points along the
    selected curve using pointOnCurve evaluation. Spacing is determined by
    the global spacing variable.
    """
    for p in range(1, pointsNumber):
        if p == 1:
            cmds.spaceLocator(
                p=cmds.pointOnCurve(curve, pr=0.0, p=True),
                n=nameBuilder_locator + str(p),
            )
            # joint
        cmds.spaceLocator(
            p=cmds.pointOnCurve(curve, pr=spacing * p, p=True),
            n=nameBuilder_locator + str(p),
        )
        # joint


def pathMode(path):
    """Create locators along a curve path using motion path animation.

    Generates locator transforms distributed along the specified curve using
    Maya's pathAnimation system. Each locator's position is controlled by
    a motionPath node with disconnected time input for static placement.

    Args:
        path: Name of the NURBS curve to distribute locators along.

    Returns:
        list: List of created locator transform names.
    """
    nameBuilder_locator = path + "_loc"
    nameBuilder_joint = path + "_jnt"
    locatorList = []
    for p in range(1, pointsNumber):
        if p == 1:
            locator = cmds.spaceLocator(n=nameBuilder_locator + str(p))
            motionPath = cmds.pathAnimation(locator[0], c=path, f=True)
            deleteConnection(motionPath + ".u")
            cmds.setAttr(motionPath + ".uValue", 0)
            locatorList.append(locator[0])
            # joint
        locator = cmds.spaceLocator(n=nameBuilder_locator + str(p))
        motionPath = cmds.pathAnimation(locator[0], c=path, f=True)
        deleteConnection(motionPath + ".u")
        cmds.setAttr(motionPath + ".uValue", spacing * p)
        locatorList.append(locator[0])
        # joint
        # -gruppa i locator
    return locatorList


locList = []
for cv in curve:
    print(cv)
    locList.extend(pathMode(cv))
cmds.group(locList, n="locator_grp")
## --ToDo

# gui
# object oriented
# multithreading

# docstring not working. why?
