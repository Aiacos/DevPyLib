import maya.cmds as cmds
import pymel.core as pm


class CurvesFromEdge(object):
    def __init__(self, geo, edge, rebuild=True):
        self.geo = pm.ls(geo)[-1]
        self.name = str(geo.name()).replace('_geo', '') + '_cv_0'

        if isinstance(edge, pm.MeshEdge):
            edge_list = self._poly_select_edge_loop(edge)
        elif isinstance(edge, list):
            print('List: ', edge)
            if isinstance(edge[-1], pm.MeshEdge):
                edge_list = pm.ls(edge)
            elif isinstance(edge[-1], int):
                min_idx, max_idx = self._get_min_max_edge(edge)
                edge_list = self._poly_select_edge_loop_path(min_idx, max_idx)
            else:
                print('Not Valid Edge')
        else:
            print('Not Valid Edge')
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
        pm.rename(deformer_node, self.name + '_reverseCurve')

        return deformer_node

    def _rebuild_curve(self, cv):
        deformer_node = \
        pm.rebuildCurve(cv, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.0001)[-1]
        pm.rename(deformer_node, self.name + '_rebuildCurve')

        return deformer_node

    def poly_to_curve(self, edge_list):
        edge_list = pm.ls(edge_list)
        pm.select(edge_list)
        cv, deformer = pm.ls(pm.polyToCurve(form=2, degree=3, conformToSmoothMeshPreview=1, n=self.name))
        self.name = str(cv.name())
        pm.rename(deformer, self.name + '_polyEdgeToCurve')

        return cv, deformer

    def get_cv(self):
        return self.cv

    def get_deformer_node(self):
        return self.deformer_node


class JointChainCurve(object):
    def __init__(self, pointsNumber=5):
        #nameBuilder_locator = curve[0] + "_loc"  # in function, lacal variables
        #nameBuilder_joint = curve[0] + "_jnt"  # in function, local variables

        self.spacing = 1.0 / (pointsNumber - 1)




def extract_feather_curves(geo, edge_idx_list):
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

        pm.rebuildCurve(cv, ch=True, rpo=True, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.0001)
        cv_list.append(cv)

    return cv_list

## Var ##


curve = cmds.ls(sl=True)



## Main --wip

def deleteConnection(plug):
    # """ Equivalent of MEL: CBdeleteConnection """

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
    for p in range(1, pointsNumber):
        if p == 1:
            cmds.spaceLocator(p=cmds.pointOnCurve(curve, pr=0.0, p=True), n=nameBuilder_locator + str(p))
            # joint
        cmds.spaceLocator(p=cmds.pointOnCurve(curve, pr=spacing * p, p=True), n=nameBuilder_locator + str(p))
        # joint


def pathMode(path):
    nameBuilder_locator = path + "_loc"
    nameBuilder_joint = path + "_jnt"
    locatorList = []
    for p in range(1, pointsNumber):
        if p == 1:
            locator = cmds.spaceLocator(n=nameBuilder_locator + str(p))
            motionPath = cmds.pathAnimation(locator[0], c=path, f=True)
            deleteConnection(motionPath + '.u')
            cmds.setAttr(motionPath + '.uValue', 0)
            locatorList.append(locator[0])
            # joint
        locator = cmds.spaceLocator(n=nameBuilder_locator + str(p))
        motionPath = cmds.pathAnimation(locator[0], c=path, f=True)
        deleteConnection(motionPath + '.u')
        cmds.setAttr(motionPath + '.uValue', spacing * p)
        locatorList.append(locator[0])
        # joint
        # -gruppa i locator
    return locatorList


locList = []
for cv in curve:
    print(cv)
    locList.extend(pathMode(cv))
cmds.group(locList, n='locator_grp')
## --ToDo

# gui
# object oriented
# multithreading

# docstring not working. why?
