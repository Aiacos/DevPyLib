"""Build step Tongue (parita' asFaceTongue MEL:35712-35925 e
asFaceTongueFinish MEL:35927-35947).

Apre con asFaceSnarlFinish (MEL:35728). Con una geometria lingua e il fit
`FaceFitTongue` (locator Tongue0..TongueN) crea N controller FK
`Tongue<i>_M` con i joint `Tongue<i>Joint_M`, fa seguire la mascella al
primo e pesa la lingua copiando i pesi da un cubo di servizio
(`tempWeightCube`) deformato sulla sagoma della lingua. Durante lo step
resta visibile solo la lingua; il finish (chiamato da Regions, MEL:35956)
rimostra il resto.

Divergenze (docs/gap-analysis.md §5o):
- le fasce di vertici del cubo (`polySelectConstraint` MEL:35837) sono
  calcolate dalle posizioni;
- il tasto modificatore che conserva `tempWeightCube` (MEL:35921) non e'
  portato: il cubo e' sempre cancellato;
- un joint lingua gia' influenza dello skinCluster non viene riaggiunto
  (il MEL andrebbe in errore);
- prerequisiti mancanti = warning + False, mai eccezioni.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_get_opm, as_parent_constraint, as_show_layer
from .ctrl_box import create_face_controller
from .face_ctrl_pp import face_add_constrained
from .face_snarl import face_snarl_finish
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import FacialFitting

_CUBE = "tempWeightCube"
_REQUIRED = ("FaceJoint_M", "SideReverse_M", "JawFollow_M", "lowerFaceStatic_M", "ctrlBox")


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _count_controllers():
    """N controller per i locator Tongue0..TongueN (MEL:35742-35747)."""
    count = 4
    for i in range(99):
        if not cmds.objExists("Tongue{}".format(i)):
            break
        count = i
    return count


def _show_only_tongue(geometry, tongue):
    if "." in tongue:
        cmds.setAttr(geometry + ".v", 1)
        return
    for geo in (get_fit_option("AllHead") or "").split():
        if cmds.objExists(geo) and not cmds.getAttr(geo + ".v", lock=True):
            cmds.setAttr(geo + ".v", 0)
    for geo in tongue.split():
        if not cmds.getAttr(geo + ".v", lock=True):
            cmds.setAttr(geo + ".v", 1)


def _new_skin_cluster(joints, geometry, name):
    """newSkinCluster "-toSelectedBones -mi 1 -dr 4 -rui false"."""
    sc = cmds.skinCluster(
        joints,
        geometry,
        toSelectedBones=True,
        maximumInfluences=1,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(sc, name)


def _build_controllers(count):
    for i in range(count):
        name = "Tongue{}".format(i)
        ctrl, joint, offset = name + "_M", name + "Joint_M", name + "Offset_M"
        create_face_controller(name, "_M", 4)
        cmds.setAttr(joint + ".segmentScaleCompensate", 0)
        cmds.setAttr(ctrl + "Shape.overrideColor", 6)
        cmds.connectAttr("ctrlBox.TongueCtrlVis", ctrl + "Shape.overrideVisibility", force=True)
        pos = _ws(name)
        cmds.xform(offset, worldSpace=True, translation=pos)
        cmds.xform(joint, worldSpace=True, translation=pos)
        cmds.scale(3.4 * 2.0, 3.4, 1, ctrl + ".cv[0:7]", relative=True, pivot=pos)
        cmds.rotate(0, 90, 0, ctrl + ".cv[0:7]", relative=True, objectSpace=True)
        cmds.parent(offset, "SideReverse_M")
        cmds.setAttr(offset + ".s", 1, 1, 1, type="float3")

    for i in range(1, count + 1):
        for suffix in ("Offset_M", "Joint_M"):
            cmds.delete(
                cmds.aimConstraint(
                    "Tongue{}".format(i),
                    "Tongue{}{}".format(i - 1, suffix),
                    aimVector=(1, 0, 0),
                    upVector=(0, 1, 0),
                    worldUpType="vector",
                    worldUpVector=(0, 1, 0),
                )
            )
    for i in range(1, count):
        cmds.parent("Tongue{}Offset_M".format(i), "Tongue{}_M".format(i - 1))
        cmds.parent("Tongue{}Joint_M".format(i), "Tongue{}Joint_M".format(i - 1))
    cmds.parent("Tongue0Joint_M", "FaceJoint_M")

    opm = as_get_opm()
    for i in range(count):
        ctrl, joint = "Tongue{}_M".format(i), "Tongue{}Joint_M".format(i)
        if opm:
            as_parent_constraint(ctrl, joint, maintain_offset=True)
            continue
        cmds.parentConstraint(ctrl, joint, maintainOffset=True)
        # scala per connessione (controller * SDK) al posto dello
        # scaleConstraint, per la scala non uniforme. Il MEL crea il nodo a
        # ogni asse: i due in piu' restano scollegati, come li' (MEL:35814).
        mpd = joint + "ScaleMPD"
        for axis in "xyz":
            cmds.createNode("multiplyDivide", name=mpd)
            cmds.connectAttr(ctrl + ".s" + axis, mpd + ".input1" + axis.upper())
            cmds.connectAttr("SDK" + ctrl + ".s" + axis, mpd + ".input2" + axis.upper())
            cmds.connectAttr(mpd + ".output" + axis.upper(), joint + ".s" + axis)


def _build_weight_cube(count, tongue_items):
    """Cubo a `count` segmenti, ogni sezione portata con un lattice sul
    locator corrispondente e scalata sulla sagoma della lingua, skinnato ai
    joint (MEL:35828-35869). Ritorna i joint."""
    cmds.polyCube(
        name=_CUBE,
        width=1,
        height=1,
        depth=1,
        subdivisionsX=1,
        subdivisionsY=1,
        subdivisionsZ=count,
        axis=(0, 1, 0),
        createUVs=4,
        constructionHistory=True,
    )
    cmds.select(tongue_items)
    bb = cmds.xform(query=True, worldSpace=True, boundingBox=True)
    all_vtxs = cmds.ls(_CUBE + ".vtx[*]", flatten=True)
    sections = []
    for i in range(count + 1):
        z = -0.5 + (1.0 / count) * i
        vtxs = [v for v in all_vtxs if abs(_ws(v)[2] - z) <= 0.1]
        sections.append(vtxs)
        cmds.select(vtxs)
        cmds.lattice(
            name="TongueLattice{}".format(i),
            divisions=(2, 5, 2),
            objectCentered=True,
            ldivisions=(2, 2, 2),
        )
    for i in range(count + 1):
        lattice = "TongueLattice{}Lattice".format(i)
        cmds.xform(lattice, worldSpace=True, translation=_ws("Tongue{}".format(i)))
        cmds.xform(lattice, worldSpace=True, scale=(bb[3] - bb[0], bb[4] - bb[1], 0))
    cmds.delete(_CUBE, constructionHistory=True)

    joints = ["Tongue{}Joint_M".format(i) for i in range(count)]
    _new_skin_cluster(joints, _CUBE, "tongueBoxSC")
    for i in range(count):
        vtxs = list(sections[i])
        if i == count - 1:
            vtxs += sections[i + 1]
        cmds.skinPercent("tongueBoxSC", vtxs, transformValue=(joints[i], 1))
        if i > 0:
            cmds.skinPercent("tongueBoxSC", sections[i], transformValue=(joints[i - 1], 0.5))
    return joints


def _tongue_skin_cluster(tongue_items, joints):
    """Lo skinCluster della lingua (creato se manca) con i joint lingua fra
    le influenze (MEL:35872-35899)."""
    found = ""
    for node in cmds.listHistory(tongue_items[0]) or []:
        if cmds.objectType(node) != "skinCluster":
            continue
        if not node.startswith("prefix_") and node != "squashIKSC":
            found = node
            break
    if not found:
        found = _new_skin_cluster(joints, tongue_items, "tongueSC")
    else:
        present = cmds.skinCluster(found, query=True, influence=True) or []
        for joint in joints:
            if joint not in present:
                cmds.skinCluster(found, edit=True, lockWeights=True, weight=0, addInfluence=joint)
    for joint in joints:
        cmds.setAttr(joint + ".liw", 0)
    return found


def face_tongue() -> bool:
    """Controller, joint e pesi della lingua (asFaceTongue). Salta (True)
    senza `upperLipMainCurve`, senza `FaceFitTongue` o senza geometria."""
    if not cmds.objExists("upperLipMainCurve"):
        return True
    face_snarl_finish()
    if not cmds.objExists("FaceFitTongue"):
        return True
    geometry = get_fit_option("Face") or ""
    tongue = get_fit_option("Tongue") or ""
    count = _count_controllers()

    as_face_hide_controllers(True)
    as_show_layer("Normal")
    if not tongue:
        return True
    tongue_items = tongue.split()
    missing = [n for n in tongue_items + [geometry] + list(_REQUIRED) if not cmds.objExists(n)]
    if missing or not cmds.attributeQuery("faceScale", node=FIT_SKELETON, exists=True):
        cmds.warning("face_tongue: missing {}".format(", ".join(missing) or "faceScale"))
        return False

    _show_only_tongue(geometry, tongue)
    if not cmds.objExists("TongueCurve"):
        # geometria scelta ma lingua non fittata: fit di default
        print("// No Fit Tongue was found, Now creating Default Fit Tongue.")
        FacialFitting(geometry).create_face_fit("Tongue", shading_group="asBlueSG")
        count = _count_controllers()
    if not all(cmds.objExists("Tongue{}".format(i)) for i in range(count + 1)):
        cmds.warning("face_tongue: tongue fit locators not found")
        return False

    _build_controllers(count)
    face_add_constrained("Tongue0_M", "JawFollow_M", "lowerFaceStatic_M", 10)

    joints = _build_weight_cube(count, tongue_items)
    skin = _tongue_skin_cluster(tongue_items, joints)
    vtxs = cmds.polyListComponentConversion(tongue_items, toVertex=True)
    try:
        cmds.skinPercent(skin, vtxs, transformValue=("Tongue0Joint_M", 1))
    except RuntimeError:
        pass  # catchQuiet nel MEL
    cmds.select(_CUBE)
    cmds.select(vtxs if "." in tongue else tongue_items, add=True)
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )
    cmds.delete(_CUBE)
    cmds.select(clear=True)
    return True


def face_tongue_finish():
    """Rimostra le geometrie nascoste dallo step Tongue (asFaceTongueFinish)."""
    if not cmds.objExists("FaceFitTongue"):
        return
    if cmds.objExists(_CUBE):
        cmds.delete(_CUBE)
    if "." in (get_fit_option("Tongue") or ""):
        return
    for geo in (get_fit_option("AllHead") or "").split():
        if cmds.objExists(geo) and not cmds.getAttr(geo + ".v", lock=True):
            cmds.setAttr(geo + ".v", 1)
