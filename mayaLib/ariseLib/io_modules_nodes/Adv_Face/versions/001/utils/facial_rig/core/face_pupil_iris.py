"""Controller Pupil/Iris dell'occhio (parita' asFacePupilIris, MEL:29470-29842).

Chiamata in coda a asFaceEyeBall (MEL:29455) quando esiste `FaceFitPupil` o
`FaceFitIris`. Per lato: campiona i loop `PupilCurve`/`IrisCurve` sulla geo
dell'occhio, crea i controller `Pupil`/`Iris` (Pupil figlio di Iris, Iris
figlio di `Eye`) con i joint `PupilJoint`/`IrisJoint` sotto `EyeJoint`, pesa
i vertici (pupilla + interno alla pupilla, iride + anello fra i due loop,
sfumatura verso l'EyeJoint) e collega gli attributi `ctrlEye<side>.pupil` e
`.iris` alle scale/tz dei gruppi SDK.

Divergenze (vedi docs/gap-analysis.md §5g):
- asSmoothFlood (MEL:39228) usa il Paint Skin Weights Tool (artisan), che
  in mayapy non esiste: `_smooth_flood` fa lo stesso lavoro numericamente
  (media dei vicini sull'influenza A, resto su B, altre influenze ferme).
  I pesi risultanti sono equivalenti ma non identici al bit.
- le geo occhio definite come selezione di facce (`eye.f[..]`, ramo
  TempDuplicatedEye MEL:29505-29518) non sono portate: warning e skip.
- `$eyeRadius` e `$backHalfVtxs` (MEL:29569-29591) sono calcolati dal MEL ma
  mai usati: omessi.
- oggetti assenti = warning e skip del lato, mai eccezioni.
"""

import maya.cmds as cmds

from .build_utils import as_parent_constraint
from .ctrl_box import create_face_controller
from .driving_system import ds_sdk, ensure_output_blend_weighted
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import get_face_fit_selection_other_object

_XYZ = ("x", "y", "z")


def _selected():
    return cmds.ls(selection=True, flatten=True) or []


def _to_vertices():
    """ConvertSelectionToVertices (il runTimeCommand non gira in batch)."""
    cmds.select(cmds.polyListComponentConversion(toVertex=True))


def _grow():
    cmds.polySelectConstraint(propagate=1, type=0x0001)


def _dist(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5


def _skin_cluster_of(node, skip_prefix=False):
    """Ultimo skinCluster nella history (escluso squashIKSC), come il MEL."""
    found = ""
    for hist in cmds.listHistory(node) or []:
        if cmds.nodeType(hist) != "skinCluster" or hist == "squashIKSC":
            continue
        if skip_prefix and hist.startswith("prefix_"):
            continue
        found = hist
    return found


def _neighbours(vtx):
    edges = cmds.polyListComponentConversion(vtx, toEdge=True)
    around = cmds.ls(cmds.polyListComponentConversion(edges, toVertex=True), flatten=True)
    return [v for v in around if v != vtx]


def _smooth_flood(inf_a, inf_b, iterations):
    """Sfuma il peso di inf_a sui vertici selezionati (asSmoothFlood).

    Equivalente numerico del flood "smooth" di artisan con solo inf_a e
    inf_b sbloccate: a ogni passata il peso di inf_a diventa la media fra
    il vertice e i suoi adiacenti e inf_b riceve il resto (la stessa regola
    verificata contro il MEL in jaw_weighing).
    """
    vtxs = _selected()
    if not vtxs:
        return
    skin = _skin_cluster_of(vtxs[0].split(".", 1)[0])
    if not skin:
        return
    around = {v: _neighbours(v) for v in vtxs}

    def weight(vtx, influence):
        return cmds.skinPercent(skin, vtx, query=True, transform=influence)

    for _ in range(iterations):
        new = {}
        for vtx in vtxs:
            near = around[vtx]
            if not near:
                continue
            budget = weight(vtx, inf_a) + weight(vtx, inf_b)
            average = (weight(vtx, inf_a) + sum(weight(n, inf_a) for n in near)) / (len(near) + 1)
            new[vtx] = (min(average, budget), budget)
        for vtx, (w_a, budget) in new.items():
            cmds.skinPercent(
                skin, vtx, normalize=False, transformValue=[(inf_a, w_a), (inf_b, budget - w_a)]
            )


def _nearest_eye_geo_first(eye_geos, left_suffix):
    """Riordina le geo occhio mettendo per prima quella piu' vicina al
    loop della pupilla (MEL:29521-29543)."""
    if len(eye_geos) < 2:
        return eye_geos
    pos_a = cmds.xform(
        "PupilCurve" + left_suffix + ".cv[0]", query=True, worldSpace=True, translation=True
    )
    sampler = cmds.createNode("closestPointOnMesh", name="closestSampler")
    nearest, min_dist = eye_geos[0], 999.0
    for geo in eye_geos:
        cmds.connectAttr(geo + ".outMesh", sampler + ".inMesh", force=True)
        cmds.setAttr(sampler + ".inPosition", pos_a[0], pos_a[1], pos_a[2], type="float3")
        index = cmds.getAttr(sampler + ".result.closestVertexIndex")
        pos_b = cmds.xform(
            "{}.vtx[{}]".format(geo, index), query=True, worldSpace=True, translation=True
        )
        if _dist(pos_a, pos_b) < min_dist:
            min_dist, nearest = _dist(pos_a, pos_b), geo
    cmds.delete(sampler)
    return [nearest] + [g for g in eye_geos if g != nearest]


def _loop_vertices(selection_text):
    """Vertici, centro e raggio (meta' altezza) di un loop campionato."""
    cmds.select(selection_text.split())
    _to_vertices()
    vtxs = _selected()
    bb = cmds.xform(query=True, boundingBox=True)
    center = [(bb[3] + bb[0]) / 2.0, (bb[4] + bb[1]) / 2.0, (bb[5] + bb[2]) / 2.0]
    return vtxs, center, (bb[4] - bb[1]) / 2.0


def _grow_side(start, pupil_vtxs, iris_vtxs, state):
    """Allarga la selezione da `start` finche' resta confinata dai loop di
    pupilla e iride (MEL:29664-29676). Ritorna (vertici, loop_adiacenti)."""
    cmds.select(start)
    adjacent = False
    for _ in range(99):
        if start in iris_vtxs:  # il loop dell'iride e' accanto a quello della pupilla
            adjacent = True
            cmds.select(iris_vtxs)
            break
        _grow()
        cmds.select(pupil_vtxs, iris_vtxs, deselect=True)
        count = len(_selected())
        if count == state["previous"]:
            break
        state["previous"] = count
    return _selected(), adjacent


def _extent(vtxs):
    bb = cmds.xform(vtxs, query=True, boundingBox=True)
    return (bb[3] - bb[0]) + (bb[4] - bb[1]) + (bb[5] - bb[2])


def _create_ctrl_and_joint(name, ctrl_type, side, pos, radius, face_scale, skin, eye_geo, vtxs):
    """Controller + joint di pupilla o iride (MEL:29606-29636)."""
    ctrl = create_face_controller(name, side, ctrl_type)
    cmds.connectAttr("ctrlBox.EyeCtrlVis", ctrl + "Shape.overrideVisibility", force=True)
    cmds.select("EyeJoint" + side)
    joint = cmds.joint(name=name + "Joint" + side)
    cmds.setAttr(joint + ".segmentScaleCompensate", 0)

    cvs = ctrl + ".cv[0:7]"
    cmds.scale(radius * 4.0, radius * 4.0, radius * 4.0, cvs, pivot=(0, 0, 0))
    cmds.move(
        0, 0, face_scale / 100.0, cvs, relative=True, objectSpace=True, worldSpaceDistance=True
    )
    offset = name + "Offset" + side
    cmds.xform(offset, worldSpace=True, translation=pos)
    cmds.xform(joint, worldSpace=True, translation=pos)
    cmds.parent(offset, "Eye" + side)
    cmds.setAttr(offset + ".r", 0, 0, 0)  # orienta come l'occhio

    cmds.skinCluster(skin, edit=True, addInfluence=joint, lockWeights=False, weight=0)
    # normalizzazione "insolita" del MEL: tutta la geo torna sull'EyeJoint
    cmds.skinPercent(skin, eye_geo, transformValue=("EyeJoint" + side, 1))
    cmds.skinPercent(skin, vtxs, transformValue=(joint, 1))
    return ctrl, joint


def _connect_attrs(side, iris_radius, eye_ball_scale):
    """SDK pupil/iris -> scale e tz dei gruppi SDK (MEL:29775-29800)."""
    eye_ctrl = "ctrlEye" + side
    pos_a = cmds.xform("FitEyeBall", query=True, worldSpace=True, translation=True)
    # il MEL misura sempre da Iris_R, anche per il lato sinistro
    iris_ref = "Iris_R" if cmds.objExists("Iris_R") else "Iris" + side
    pos_b = cmds.xform(iris_ref, query=True, worldSpace=True, translation=True)
    dist = _dist(pos_a, pos_b)
    temp = cmds.createNode("transform", name="tempXform", parent="FitEyeBall")
    cmds.setAttr(temp + ".tz", 0.5)
    pos_a = cmds.xform(temp, query=True, worldSpace=True, translation=True)
    cmds.delete(temp)
    dist2 = _dist(pos_a, pos_b)

    for axis in _XYZ:
        ensure_output_blend_weighted(eye_ctrl + ".pupil")
        ds_sdk(eye_ctrl + ".pupil", "SDKPupil{}.s{}".format(side, axis), 0, 1)
        ds_sdk(eye_ctrl + ".pupil", "SDKPupil{}.s{}".format(side, axis), 10, 2)
        ensure_output_blend_weighted(eye_ctrl + ".iris")
        ds_sdk(eye_ctrl + ".iris", "SDKIris{}.s{}".format(side, axis), 0, 1)
        ds_sdk(
            eye_ctrl + ".iris",
            "SDKIris{}.s{}".format(side, axis),
            10,
            eye_ball_scale[0] / (iris_radius * 2),
        )
        ds_sdk(eye_ctrl + ".iris", "SDKIris{}.s{}".format(side, axis), -10, 0)
        curve = "SDKIris{}_scale{}".format(side, axis.upper())
        if cmds.objExists(curve):
            cmds.keyTangent(curve, index=(1, 1), inTangentType="spline", outTangentType="spline")
            cmds.keyTangent(curve, index=(2, 2), inTangentType="flat", outTangentType="flat")
    ds_sdk(eye_ctrl + ".iris", "SDKIris" + side + ".tz", 0, 0)
    ds_sdk(eye_ctrl + ".iris", "SDKIris" + side + ".tz", 10, dist * -1)
    ds_sdk(eye_ctrl + ".iris", "SDKIris" + side + ".tz", -10, dist2)
    curve = "SDKIris" + side + "_translateZ"
    if cmds.objExists(curve):
        cmds.keyTangent(curve, index=(0, 0), outTangentType="flat")
        cmds.keyTangent(curve, index=(1, 1), inTangentType="spline", outTangentType="spline")


def _build_side(side, left_suffix, eye_geos, face_scale, eye_ball_scale, temp_pos, state):
    eye_ctrl = "ctrlEye" + side
    eye_geos = _nearest_eye_geo_first(eye_geos, left_suffix)
    eye_geo = eye_geos[0]

    pupil_text = get_face_fit_selection_other_object("PupilCurve" + left_suffix, eye_geo, side)
    iris_text = get_face_fit_selection_other_object("IrisCurve" + left_suffix, eye_geo, side)
    if not pupil_text.strip():
        cmds.warning("Pupil{} EdgeLoop not defined".format(side))
        return
    if not iris_text.strip():
        cmds.warning("Iris{} EdgeLoop not defined".format(side))
        return

    pupil_vtxs, pupil_pos, pupil_radius = _loop_vertices(pupil_text)
    iris_vtxs, iris_pos, iris_radius = _loop_vertices(iris_text)
    skin = _skin_cluster_of(pupil_vtxs[0], skip_prefix=True)
    if not skin:
        cmds.warning("face_pupil_iris: no skinCluster on {}".format(eye_geo))
        return

    for name, ctrl_type, pos, radius, vtxs in (
        ("Pupil", 2, pupil_pos, pupil_radius, pupil_vtxs),
        ("Iris", 1, iris_pos, iris_radius, iris_vtxs),
    ):
        _create_ctrl_and_joint(name, ctrl_type, side, pos, radius, face_scale, skin, eye_geo, vtxs)
        if name == "Pupil":  # iris prima, cosi' pupil appare per ultimo
            for attr in ("iris", "pupil"):
                cmds.addAttr(
                    eye_ctrl,
                    longName=attr,
                    attributeType="double",
                    keyable=True,
                    softMinValue=-10,
                    hasSoftMinValue=True,
                    softMaxValue=10,
                    hasSoftMaxValue=True,
                    defaultValue=0,
                )

    cmds.parent("PupilOffset" + side, "Iris" + side)
    cmds.parent("PupilJoint" + side, "IrisJoint" + side)

    multi_skin = bool(get_fit_option("MultiSkinClusters"))
    head_joint = get_fit_option("HeadJoint") or ""
    for name in ("Pupil", "Iris"):
        joint = name + "Joint" + side
        as_parent_constraint(name + side, joint)
        mm = "{}JointMM{}".format(name, side)
        if multi_skin and cmds.objExists(mm) and cmds.objExists(head_joint):
            # inverseMatrix fuori dall'HeadJoint
            cmds.connectAttr(head_joint + ".worldInverseMatrix", mm + ".matrixIn[1]", force=True)
            cmds.setAttr(
                mm + ".matrixIn[2]", *cmds.getAttr(head_joint + ".worldMatrix"), type="matrix"
            )
            parent = cmds.listRelatives(joint, parent=True)[0]
            cmds.connectAttr(parent + ".worldInverseMatrix", mm + ".matrixIn[3]")

    # vertici adiacenti al primo vertice della pupilla, ai due lati del loop
    cmds.select(pupil_vtxs[0])
    cmds.select(cmds.polyListComponentConversion(toEdge=True))
    _to_vertices()
    cmds.select(pupil_vtxs, deselect=True)
    starts = _selected()
    if not starts:
        cmds.warning("face_pupil_iris: Pupil{} loop has no neighbours".format(side))
        return

    side_a, adjacent = _grow_side(starts[0], pupil_vtxs, iris_vtxs, state)
    if len(starts) < 2:  # la pupilla e' un buco nella geometria
        outer_vtxs, inner_vtxs = side_a, pupil_vtxs
    else:
        side_b, adjacent_b = _grow_side(starts[1], pupil_vtxs, iris_vtxs, state)
        adjacent = adjacent or adjacent_b
        # il lato con l'ingombro minore e' l'interno della pupilla
        if _extent(side_a) < _extent(side_b):
            inner_vtxs, outer_vtxs = side_a, side_b
        else:
            inner_vtxs, outer_vtxs = side_b, side_a

    loops_pupil_to_iris = 0
    cmds.select(pupil_vtxs[0])
    for i in range(10):
        _grow()
        if set(_selected()) & set(iris_vtxs):
            loops_pupil_to_iris = i
            break

    pupil_joint, iris_joint, eye_joint = "PupilJoint" + side, "IrisJoint" + side, "EyeJoint" + side
    for joint, vtxs in (
        (pupil_joint, pupil_vtxs),
        (pupil_joint, inner_vtxs),
        (iris_joint, iris_vtxs),
        (iris_joint, outer_vtxs),
    ):
        if vtxs:
            cmds.skinPercent(skin, vtxs, transformValue=(joint, 1))

    if not adjacent and outer_vtxs:
        cmds.select(outer_vtxs)
        _smooth_flood(pupil_joint, iris_joint, loops_pupil_to_iris)

    cmds.skinCluster(skin, edit=True, selectInfluenceVerts=pupil_joint)
    pupil_weighted = _selected()
    cmds.skinCluster(skin, edit=True, selectInfluenceVerts=iris_joint)
    iris_weighted = _selected()

    # quanti loop servono dall'iride per arrivare a meta' sfera
    cmds.parent(temp_pos, "FitEyeBall" + left_suffix)
    loops_iris_to_half = 0
    if outer_vtxs:
        cmds.select(outer_vtxs)
        for i in range(20):
            loops_iris_to_half = i
            _grow()
            reached = False
            for vtx in _selected():
                pos = cmds.xform(vtx, query=True, worldSpace=True, translation=True)
                cmds.xform(temp_pos, worldSpace=True, translation=pos)
                if cmds.getAttr(temp_pos + ".tz") < 0:
                    reached = True
            if reached:
                break

    cmds.select(iris_vtxs)
    for _ in range(1, loops_iris_to_half):
        _grow()
        cmds.select(pupil_weighted + iris_weighted, deselect=True)
    if _selected():
        _smooth_flood(iris_joint, eye_joint, loops_iris_to_half)

    _connect_attrs(side, iris_radius, eye_ball_scale)

    # le altre geo dell'occhio copiano i pesi dalla prima
    cyclops = bool(get_fit_option("Cyclops"))
    for other in eye_geos[1:]:
        other_skin = _skin_cluster_of(other)
        if not other_skin:
            continue
        cmds.skinCluster(
            other_skin, edit=True, addInfluence=pupil_joint, lockWeights=False, weight=0
        )
        cmds.skinCluster(
            other_skin, edit=True, addInfluence=iris_joint, lockWeights=False, weight=0
        )
        if cyclops and side == "_R":
            cmds.skinCluster(other_skin, edit=True, removeInfluence=("PupilJoint_R", "IrisJoint_R"))
        # i pesi scritti da _smooth_flood entrano nella copia solo dopo che
        # lo skinCluster sorgente e' stato rivalutato (in Maya interattivo
        # ci pensa il viewport): senza, la copia legge i pesi di prima
        # In mayapy la prima copia fatta subito dopo aver aggiunto le
        # influenze trasferisce solo in parte (quasi tutto resta a EyeJoint);
        # ripetendola il risultato coincide con quello del MEL in Maya
        # interattivo. Verificato sulla demo clairee (lenti degli occhi).
        for _ in range(2):
            cmds.select(eye_geo, other)
            cmds.copySkinWeights(
                noMirror=True,
                surfaceAssociation="closestPoint",
                influenceAssociation="closestJoint",
            )

    build_pose = "faceBuildPose" if cmds.objExists("faceBuildPose") else "buildPose"
    if cmds.objExists(build_pose + ".udAttr"):
        for attr in ("pupil", "iris"):
            current = cmds.getAttr(build_pose + ".udAttr") or ""
            cmds.setAttr(
                build_pose + ".udAttr",
                current + "setAttr {}.{} 0;".format(eye_ctrl, attr),
                type="string",
            )


def face_pupil_iris() -> bool:
    """Costruisce i controller di pupilla e iride (asFacePupilIris).

    Returns:
        True se la procedura e' arrivata in fondo (i lati senza loop
        definiti vengono saltati con warning); False con warning se manca
        la base costruita da face_eye_ball.
    """
    for node in (FIT_SKELETON, "FitEyeBall", "ctrlBox", "OnFacecontrols"):
        if not cmds.objExists(node):
            cmds.warning("face_pupil_iris: {} not found".format(node))
            return False

    face_scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    eye_ball_scale = cmds.xform("FitEyeBall", query=True, worldSpace=True, scale=True)
    temp_pos = cmds.createNode("transform", name="TempPos")
    state = {"previous": 0}  # $tempString2 del MEL: sopravvive fra lati e crescite

    for side, option, left_suffix in (("_R", "RightEye", ""), ("_L", "LeftEye", "Left")):
        eye_geos = (get_fit_option(option) or "").split()
        if not eye_geos:
            cmds.warning("face_pupil_iris: no eye geometry for {}".format(side))
            continue
        if ".f" in eye_geos[0]:
            cmds.warning(
                "face_pupil_iris: face-selection eye geometry is not supported yet, "
                "skipping Pupil/Iris{}".format(side)
            )
            continue
        required = ["PupilCurve" + left_suffix, "IrisCurve" + left_suffix, "Eye" + side]
        required += ["EyeJoint" + side, "ctrlEye" + side, "FitEyeBall" + left_suffix]
        missing = [n for n in required + eye_geos if not cmds.objExists(n)]
        if missing:
            cmds.warning("face_pupil_iris: missing {} for {}".format(", ".join(missing), side))
            continue
        _build_side(side, left_suffix, eye_geos, face_scale, eye_ball_scale, temp_pos, state)

    cmds.delete(temp_pos)
    cmds.select(clear=True)
    return True
