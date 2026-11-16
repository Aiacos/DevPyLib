"""Build step UpMidLo (parita' asFaceUpMidLo MEL:35997-36243, con
asSkinWeightSet MEL:67457).

Con il fit `FaceFitUpMidLo` (locator upperFace / middleFace / lowerFace)
divide il viso in tre fasce orizzontali, ognuna con un controller
`<fascia>Face_M` e un joint `<fascia>FaceJoint_M`. I controller on-face
passano sotto la fascia che li contiene, e il peso che il viso aveva sul
joint della testa viene ripartito sui tre joint secondo i pesi sfumati di
una mesh di servizio (`UpMidLoLayer`). Le altre geometrie della testa
ricevono gli stessi pesi per copia.

Divergenze (docs/gap-analysis.md §5p):
- asSmoothFlood e' numerico (`jaw_weighing._smooth_flood`, come negli
  altri step);
- le due selezioni a fascia (`polySelectConstraint`, MEL:36134-36137) sono
  calcolate dalle posizioni: la distanza dal piano y=0 e' assoluta;
- ramo multiSkinClusters non portato;
- nodi assenti saltati nei reparent; prerequisiti mancanti = warning +
  False, mai eccezioni.
"""

import maya.cmds as cmds

from .build_utils import (
    as_align,
    as_face_hide_controllers,
    as_parent_constraint,
    as_show_layer,
)
from .ctrl_box import add_ctrl_box2_shape
from .face_prep import include_above_eyes
from .fit_options import FIT_SKELETON, get_fit_option
from .jaw_weighing import _lock_weights, _Mesh, _smooth_flood

_BANDS = ("upper", "middle", "lower")
_LAYER = "UpMidLoLayer"
_SKIN = "UpMidLoSC"
_GEO_OPTIONS = ("RightEye", "LeftEye", "UpperTeeth", "LowerTeeth", "Tongue", "Eyebrow", "Eyelash")
_REQUIRED = (
    "templateLayer", "allHeadCombinedLayer", "DeformationLayers", "FaceJoint_M", "OnFacecontrols",
    "SideReverse_R", "SideReverse_L", "SideReverse_M", "ctrlBox", "ctrlBox2", "middleFace",
    "lowerFace",
)  # fmt: skip


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _parent_existing(nodes, parent):
    nodes = [n for n in nodes if cmds.objExists(n)]
    if nodes and cmds.objExists(parent):
        cmds.parent(nodes, parent)


def _skin_cluster_of(obj):
    """asGetSkinCluster: ultimo skinCluster nella history."""
    found = ""
    for node in cmds.listHistory(obj, pruneDagObjects=True, interestLevel=2) or []:
        if cmds.nodeType(node) == "skinCluster":
            found = node
    return found


def _add_influences(skin, joints):
    present = cmds.skinCluster(skin, query=True, influence=True) or []
    for joint in joints:
        if joint not in present:
            cmds.skinCluster(skin, edit=True, lockWeights=False, weight=0, addInfluence=joint)


def _build_band_controller(band, scale):
    """Joint e controller a semicerchio di una fascia (MEL:36064-36100)."""
    joint, ctrl, offset = band + "FaceJoint_M", band + "Face_M", band + "FaceOffset_M"
    cmds.select("FaceJoint_M")
    cmds.joint(name=joint)
    cmds.setAttr(joint + ".segmentScaleCompensate", 0)
    pos = _ws(band + "Face")
    cmds.xform(joint, worldSpace=True, translation=(0, pos[1], pos[2]))
    circle = cmds.circle(
        center=(0, 0, 0),
        normal=(0, 1, 0),
        sweep=180,
        radius=4,
        degree=3,
        useTolerance=False,
        tolerance=0.000393701,
        sections=8,
        constructionHistory=False,
    )[0]
    cmds.rename(circle, ctrl)
    cmds.connectAttr("ctrlBox.UpMidLoCtrlVis", ctrl + "Shape.overrideVisibility")
    factor = (-4.5 * _ws("JawPivot")[0]) / scale
    cmds.scale(factor, factor, factor, ctrl + ".cv[0:99]", relative=True, pivot=(0, 0, 0))
    cmds.rotate(0, -90, 0, ctrl + ".cv[0:99]", relative=True)
    cmds.sets(ctrl, add="FaceControlSet")
    cmds.setAttr(ctrl + "Shape.overrideEnabled", 1)
    cmds.setAttr(ctrl + "Shape.overrideColor", 17)
    cmds.createNode("transform", name=offset)
    cmds.parent(ctrl, offset)
    cmds.parent(offset, "OnFacecontrols")
    cmds.setAttr(offset + ".s", 1, 1, 1, type="float3")
    as_align(offset, joint, translate=True)
    as_parent_constraint(ctrl, joint, maintain_offset=True)

    reverses = []
    for side in ("_R", "_L", "_M"):
        reverses.append(
            cmds.createNode(
                "transform", name=band + "SideReverse" + side, parent="SideReverse" + side
            )
        )
    cmds.parent(reverses, ctrl)
    if cmds.objExists(band + "Face1_M"):
        add_ctrl_box2_shape(ctrl)


def _reparent_controllers():
    """Ogni gruppo di controller on-face passa sotto la sua fascia
    (MEL:36103-36124)."""
    above = include_above_eyes()
    eye_region = "EyeBaseOffset" if get_fit_option("EyeBase") else "EyeRegionOffset"
    for side in ("_R", "_L"):
        if above:
            _parent_existing(
                [eye_region + side, "EyeOffset" + side, "EyeBrowRegionOffset" + side],
                "upperSideReverse" + side,
            )
        _parent_existing(["middleFaceStatic" + side], "middleSideReverse" + side)
        _parent_existing(
            ["lowerFaceStatic" + side, "SmilePullOffset" + side], "lowerSideReverse" + side
        )
    if above:
        _parent_existing(["EyeBrowCenterOffset_M", "NoseCreaseOffset_M"], "upperSideReverse_M")
    _parent_existing(["NoseRegionOffset_M", "middleFaceStatic_M"], "middleSideReverse_M")
    _parent_existing(["JawOffset_M", "lowerFaceStatic_M"], "lowerSideReverse_M")
    _parent_existing(["upperTeethOffset_M"], "lowerSideReverse_M")


def _weight_layer():
    """Pesi delle tre fasce su UpMidLoLayer: netti sopra `upperFace` e sotto
    `lowerFace`, poi sfumati (MEL:36126-36143). Ritorna la mesh letta."""
    joints = [band + "FaceJoint_M" for band in _BANDS]
    sc = cmds.skinCluster(
        ["FaceJoint_M"] + joints,
        _LAYER,
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    cmds.rename(sc, _SKIN)
    cmds.skinPercent(_SKIN, _LAYER, transformValue=("middleFaceJoint_M", 1))

    mesh = _Mesh(_LAYER)
    upper_y, lower_y = _ws("upperFace")[1], _ws("lowerFace")[1]
    upper = [i for i, p in enumerate(mesh.points) if upper_y <= abs(p.y) <= 9999]
    if upper:
        cmds.skinPercent(_SKIN, mesh.vtxs(upper), transformValue=("upperFaceJoint_M", 1))
    lower = [i for i, p in enumerate(mesh.points) if abs(p.y) <= lower_y]
    if lower:
        cmds.skinPercent(_SKIN, mesh.vtxs(lower), transformValue=("lowerFaceJoint_M", 1))

    every = set(range(len(mesh.points)))
    for inf_a, inf_b in (
        ("upperFaceJoint_M", "middleFaceJoint_M"),
        ("lowerFaceJoint_M", "middleFaceJoint_M"),
        ("lowerFaceJoint_M", "FaceJoint_M"),
    ):
        _smooth_flood(_SKIN, mesh, every, inf_a, inf_b, 10)
    return mesh


def _skin_weight_set(joint, geometry, skin, vtx_ids, weights):
    """asSkinWeightSet: scrive i pesi grezzi di un joint, poi normalizza
    prima col joint bloccato e poi sbloccato."""
    index = None
    conns = cmds.listConnections(skin + ".matrix", connections=True) or []
    for plug, node in zip(conns[0::2], conns[1::2]):
        if node == joint:
            index = int(plug.rsplit("[", 1)[1][:-1])
    if index is None:
        return
    for vtx, weight in zip(vtx_ids, weights):
        cmds.setAttr("{}.wl[{}].w[{}]".format(skin, vtx, index), weight)
    for lock in (1, 0):
        cmds.setAttr(joint + ".lockInfluenceWeights", lock)
        try:
            cmds.skinPercent(skin, geometry, normalize=True)
        except RuntimeError:
            pass  # catchQuiet nel MEL


def _split_head_weight(geometry, skin, head_joint, mesh, non_symmetrical, tolerance):
    """Il peso che ogni vertice del viso ha sul joint della testa passa ai
    tre joint di fascia, in proporzione ai pesi di UpMidLoLayer
    (MEL:36152-36182)."""

    def layer_weight(vtx, joint):
        return cmds.skinPercent(
            _SKIN, "{}.vtx[{}]".format(_LAYER, vtx), query=True, transform=joint
        )

    vtx_ids = []
    split = {band: [] for band in _BANDS}
    for vtx in range(cmds.polyEvaluate(geometry, vertex=True)):
        if not non_symmetrical and mesh.points[vtx].x > tolerance:
            continue
        face_vtx = "{}.vtx[{}]".format(geometry, vtx)
        infs = cmds.skinPercent(skin, face_vtx, query=True, ignoreBelow=0.01, transform=None)
        if head_joint not in (infs or []):
            continue
        head_weight = cmds.skinPercent(skin, face_vtx, query=True, transform=head_joint)
        vtx_ids.append(vtx)
        for band in _BANDS:
            split[band].append(head_weight * layer_weight(vtx, band + "FaceJoint_M"))

    _skin_weight_set(head_joint, geometry, skin, vtx_ids, [0.0] * len(vtx_ids))
    for band in _BANDS:
        _skin_weight_set(band + "FaceJoint_M", geometry, skin, vtx_ids, split[band])
    if not non_symmetrical:
        cmds.copySkinWeights(
            sourceSkin=skin,
            destinationSkin=skin,
            mirrorMode="YZ",
            mirrorInverse=True,
            surfaceAssociation="closestPoint",
            influenceAssociation="closestJoint",
        )


def _copy_to_other_geometries(geometry):
    """Le geometrie di AllHead che non hanno un ruolo dichiarato ricevono
    i pesi di fascia per copia da UpMidLoLayer (MEL:36184-36238)."""
    defined = [geometry]
    for option in _GEO_OPTIONS:
        defined += (get_fit_option(option) or "").split()
    defined_objects = [item.split(".")[0] for item in defined]
    joints = [band + "FaceJoint_M" for band in _BANDS]
    for geo in (get_fit_option("AllHead") or "").split():
        if geo in defined or geo in defined_objects or not cmds.objExists(geo):
            continue
        skin = _skin_cluster_of(geo)
        if not skin:
            cmds.warning("face_up_mid_lo: {} has no skinCluster, skipped".format(geo))
            continue
        _add_influences(skin, joints)
        cmds.select(_LAYER, geo)
        cmds.copySkinWeights(
            noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
        )


def face_up_mid_lo() -> bool:
    """Fasce upper / middle / lower del viso (asFaceUpMidLo). Salta (True)
    senza il fit `upperFace` o senza `JawPivot`."""
    if cmds.objExists("ctrlBox") and cmds.attributeQuery("AimCtrlVis", node="ctrlBox", exists=True):
        cmds.setAttr("ctrlBox.AimCtrlVis", 0)
    if not cmds.objExists("upperFace") or not cmds.objExists("JawPivot"):
        return True
    geometry = get_fit_option("Face") or ""
    skin = get_fit_option("SkinCluster") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    missing = [
        n for n in (geometry, skin, head_joint) + _REQUIRED if not n or not cmds.objExists(n)
    ]
    if missing:
        cmds.warning("face_up_mid_lo: missing {}".format(", ".join(missing) or "Face options"))
        return False
    if get_fit_option("MultiSkinClusters"):
        cmds.warning("face_up_mid_lo: multiSkinClusters is not ported, using the face skinCluster")
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    non_symmetrical = bool(get_fit_option("NonSym"))

    # mesh di servizio (weight-by-softmod ignora i pesi bloccati)
    cmds.duplicate("templateLayer", name=_LAYER)
    cmds.duplicate("allHeadCombinedLayer", name="UpMidLoAllHeadCombinedLayer")
    as_show_layer("UpMidLo")
    cmds.parent(_LAYER, world=True)

    as_face_hide_controllers(True)
    cmds.setAttr("ctrlBox2.v", 1)
    cmds.setAttr("ctrlBox.UpMidLoCtrlVis", 1)
    _lock_weights(1)
    cmds.setAttr(head_joint + ".lockInfluenceWeights", 0)

    for band in _BANDS:
        _build_band_controller(band, scale)
    _reparent_controllers()

    mesh = _weight_layer()
    joints = [band + "FaceJoint_M" for band in _BANDS]
    _add_influences(skin, joints)
    if cmds.objExists("lipSlideSurfaceSC"):
        _add_influences("lipSlideSurfaceSC", ["lowerFaceJoint_M"])
        cmds.skinPercent(
            "lipSlideSurfaceSC", "lipSlideSurface", transformValue=("lowerFaceJoint_M", 1)
        )

    _split_head_weight(geometry, skin, head_joint, mesh, non_symmetrical, 0.01 * scale)
    _copy_to_other_geometries(geometry)

    cmds.parent(_LAYER, "DeformationLayers")
    as_show_layer("Normal")
    return True
