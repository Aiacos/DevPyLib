"""Base strutturale del build facciale (parita' asFaceEnsureAdvancedBase,
righe MEL 43845-43994).

Crea i ~25 nodi che ogni componente del build presuppone: la gerarchia
FaceMotionSystem/ControlsSetup/ConstrainedSetup, il FaceDeformationSystem
con JawSetup e i gruppi JawFollow*/JawStatic, i SideReverse* (specchi a
sx=-1 per il lato destro), i layer di deformazione (templateLayer e
allHeadCombinedLayer, copie nascoste della testa), la scala globale
MainAndHeadScaleMultiplyDivide, il follow del head joint (multMatrix
FMM), il nodo faceBuildPose e i set FaceAllSet/FaceControlSet/FaceAreas/
FaceBuildingSets.

Idempotente: se FaceMotionSystem esiste si limita a renderlo visibile.
"""

import maya.cmds as cmds

from .build_utils import as_align, as_lock_attr, as_parent_constraint
from .fit_options import get_fit_option
from .shaders import ensure_face_shaders


def _delete_intermediate_shapes(node: str):
    for shape in cmds.listRelatives(node, shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)


def ensure_advanced_base() -> bool:
    """Crea la base strutturale del build (parita'
    asFaceEnsureAdvancedBase). Ritorna False con warning se mancano
    FaceGroup o l'HeadJoint."""
    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    all_head_string = get_fit_option("AllHead") or ""

    ensure_face_shaders()
    sel = cmds.ls(selection=True) or []

    if not cmds.objExists("FaceGroup"):
        cmds.warning("FaceGroup does not exists, must build a Fit-system first")
        return False
    if not cmds.objExists(head_joint):
        cmds.warning('HeadJoint: "{}" Does not exists'.format(head_joint))
        return False
    if not cmds.objExists(geometry):
        cmds.warning('Face geometry "{}" does not exist'.format(geometry))
        return False
    if cmds.objExists("FaceMotionSystem"):
        cmds.setAttr("FaceMotionSystem.v", 1)
        return True

    # nodi top-level
    cmds.createNode("transform", name="FaceMotionSystem", parent="FaceGroup")
    as_align("FaceMotionSystem", head_joint, translate=True)
    cmds.createNode("transform", name="ControlsSetup", parent="FaceMotionSystem")
    cmds.createNode("transform", name="ConstrainedSetup", parent="FaceMotionSystem")
    cmds.createNode("transform", name="DeformJointConstraints", parent="ConstrainedSetup")
    cmds.createNode("transform", name="FaceDeformationSystem", parent="FaceGroup")
    cmds.setAttr("FaceDeformationSystem.v", 0)
    cmds.setAttr("FaceDeformationSystem.v", lock=True)
    cmds.createNode("transform", name="FaceDeformationFollowHead", parent="FaceDeformationSystem")
    as_align("FaceDeformationFollowHead", head_joint, translate=True)
    cmds.createNode("transform", name="JawSetup", parent="FaceDeformationFollowHead")
    pos = [0.0, 0.0, 0.0]
    if cmds.objExists("JawPivot"):  # potrebbe essere "skip below eyes"
        pos = cmds.xform("JawPivot", query=True, worldSpace=True, translation=True)
    cmds.xform("JawSetup", worldSpace=True, translation=(0, pos[1], pos[2]))

    for side in ("_R", "_L", "_M"):
        cmds.createNode("transform", name="JawFollowSideReverse" + side, parent="JawSetup")
        cmds.createNode("transform", name="JawFollow" + side, parent="JawFollowSideReverse" + side)
    cmds.createNode("transform", name="JawStatic_M", parent="JawFollowSideReverse_M")
    cmds.setAttr("JawFollowSideReverse_R.sx", -1)

    cmds.createNode("transform", name="SideReverseSetup", parent="ConstrainedSetup")
    for side in ("_M", "_R", "_L"):
        cmds.createNode("transform", name="SideReverseSetup" + side, parent="SideReverseSetup")
        for prefix in ("FaceStatic", "middleFaceStatic", "lowerFaceStatic"):
            cmds.createNode("transform", name=prefix + side, parent="SideReverseSetup" + side)
    cmds.setAttr("SideReverseSetup_R.sx", -1)

    cmds.createNode("transform", name="Aimcontrols", parent="ControlsSetup")
    cmds.createNode("transform", name="OnFacecontrols", parent="ControlsSetup")
    for side in ("_R", "_L", "_M"):
        cmds.createNode("transform", name="SideReverse" + side, parent="OnFacecontrols")
    cmds.setAttr("SideReverse_R.sx", -1)
    cmds.createNode("transform", name="Regionscontrols", parent="ControlsSetup")
    cmds.createNode("transform", name="Customcontrols", parent="ControlsSetup")

    cmds.createNode("transform", name="FaceBuildInProgress")
    cmds.createNode("transform", name="FaceBuildInProgressHidden", parent="FaceBuildInProgress")
    cmds.setAttr("FaceBuildInProgressHidden.v", 0)
    cmds.createNode("transform", name="DeformationLayers", parent="FaceDeformationSystem")

    # templateLayer: copia nascosta della Face
    cmds.duplicate(geometry, name="templateLayer")
    as_lock_attr("templateLayer", False, False, False, False)
    cmds.parent("templateLayer", "DeformationLayers")
    cmds.sets("templateLayer", edit=True, forceElement="initialShadingGroup")
    _delete_intermediate_shapes("templateLayer")
    cmds.setAttr("templateLayer.v", 0)

    # allHeadCombinedLayer: unione di tutte le geometrie della testa
    all_head = [obj for obj in all_head_string.split() if cmds.objExists(obj)]
    if not all_head:
        all_head = [geometry]
    cmds.select(all_head)
    duplicates = cmds.duplicate(returnRootsOnly=True)
    if len(duplicates) > 1:
        cmds.polyUnite(
            duplicates, constructionHistory=0, mergeUVSets=1, name="allHeadCombinedLayer"
        )
        cmds.delete(duplicates)
    else:
        cmds.rename(duplicates[0], "allHeadCombinedLayer")
    cmds.parent("allHeadCombinedLayer", "DeformationLayers")
    cmds.sets("allHeadCombinedLayer", edit=True, forceElement="initialShadingGroup")
    _delete_intermediate_shapes("allHeadCombinedLayer")
    cmds.setAttr("allHeadCombinedLayer.v", 0)

    # scala globale: segue il Main del body rig se presente
    cmds.createNode("multiplyDivide", name="MainAndHeadScaleMultiplyDivide")
    cmds.setAttr("MainAndHeadScaleMultiplyDivide.input1", 1, 1, 1, type="float3")
    if cmds.objExists("MainScaleMultiplyDivide"):
        cmds.connectAttr("MainScaleMultiplyDivide.output", "MainAndHeadScaleMultiplyDivide.input1")
    elif cmds.objExists("Main"):  # body rig piu' vecchio di 5.732
        cmds.connectAttr("Main.s", "MainAndHeadScaleMultiplyDivide.input1")
    # caso speciale: MainScaleMultiplyDivide orfano del body rig
    if cmds.objExists("MainScaleMultiplyDivide"):
        if cmds.getAttr("MainScaleMultiplyDivide.input1X", settable=True):
            cmds.setAttr("MainScaleMultiplyDivide.input1", 1, 1, 1, type="float3")

    as_parent_constraint(
        head_joint, "FaceMotionSystem", maintain_offset=True, force_mult_matrix=True
    )
    as_parent_constraint(
        head_joint, "FaceDeformationFollowHead", maintain_offset=True, force_mult_matrix=True
    )

    # faceBuildPose
    if not cmds.objExists("faceBuildPose"):
        cmds.createNode("transform", name="faceBuildPose", parent="FaceMotionSystem")
        cmds.addAttr("faceBuildPose", longName="udAttr", dataType="string")

    # Sets
    cmds.select(clear=True)
    cmds.sets(name="FaceAllSet", empty=True)
    cmds.sets(name="FaceControlSet", empty=True)
    cmds.sets(name="FaceAreas", empty=True)
    if cmds.objExists("Sets"):
        cmds.sets("FaceAllSet", add="Sets")
        cmds.sets("FaceControlSet", add="Sets")
        cmds.sets("FaceAreas", add="Sets")
    cmds.sets(name="FaceBuildingSets", empty=True)
    cmds.sets("FaceBuildingSets", add="FaceAllSet")
    # allBeforeFaceBuild viene creato da asFacePrep; se il prep non e'
    # ancora portato lo si crea vuoto per mantenere la struttura dei set
    if not cmds.objExists("allBeforeFaceBuild"):
        cmds.sets(name="allBeforeFaceBuild", empty=True)
    cmds.sets("allBeforeFaceBuild", add="FaceBuildingSets")

    if sel:
        cmds.select(sel)
    else:
        cmds.select(clear=True)
    return True
