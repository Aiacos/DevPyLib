"""Control board facciale (parita' asFaceCtrlBox MEL 28556-29061,
asFaceCreateCtrlBox 43539, asCreateFaceController 43117,
asFaceControlOrient 43201).

Il board e' la lavagna 2D dei controlli: `ctrlBox` (quadro con gli
attributi *CtrlVis che pilotano la visibilita' delle famiglie di ctrl
e `limits` che abilita i transform limits degli slider), 12 slider
`ctrlBox<Name>`/`ctrl<Name>` con tap blendWeighted su tx/ty (il bus
del driving system), i ctrl opzionali Phonemes/Emotions/ARKit/
RobloxHead/SnapChat e `ctrlBox2` con gli indicatori di regione
(Eye1*, EyeRegion1*, EyeBrowRegion1*, LipRegion1_M, NoseRegion1_M,
teeth, tongue, UpMidLo).

`create_face_controller` e' la factory dei controlli on-face
(Offset->SDK->ctrl, colore e visibilita' per famiglia);
`face_control_orient` orienta l'offset di un ctrl sulla superficie
del cilindro FaceControlOrient.

Divergenze sanzionate: i nomi shape vengono normalizzati con rename
espliciti (il MEL si affida allo smart-rename di Maya); il box
SnapChat ricade sul template se Emotions e' disattivo (il MEL
fallirebbe duplicando un nodo inesistente).
"""

import math
from typing import Sequence, Tuple

import maya.cmds as cmds

from .build_utils import as_get_opm, as_lock_attr, as_parent_constraint
from .driving_system import ensure_output_blend_weighted
from .fit_options import FIT_SKELETON, get_fit_option

# (nome, x, y, half) in unita' di scale/4 — MEL 28685-28696
SLIDERS = (
    ("Brow_R", -0.25, 0.75, 0),
    ("Brow_L", 0.25, 0.75, 0),
    ("Eye_R", -0.25, 0.38, 0),
    ("Eye_L", 0.25, 0.38, 0),
    ("Cheek_R", -0.25, 0.0, 1),
    ("Cheek_L", 0.25, 0.0, 1),
    ("Nose_R", -0.25, -0.22, 1),
    ("Nose_L", 0.25, -0.22, 1),
    ("Lips_M", 0.0, -0.42, 0),
    ("Mouth_M", 0.0, -0.64, 2),
    ("MouthCorner_R", -0.25, -1.0, 0),
    ("MouthCorner_L", 0.25, -1.0, 0),
)

CTRL_VIS_ATTRS = (
    "ACtrlVis",
    "BCtrlVis",
    "CCtrlVis",
    "EyeCtrlVis",
    "AimCtrlVis",
    "TeethCtrlVis",
    "TongueCtrlVis",
    "RegionsCtrlVis",
    "UpMidLoCtrlVis",
    "SquashCtrlVis",
    "CustomCtrlVis",
)

_SQUARE = ((-1, 1, 0), (1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0))
_BAR = ((1, -0.02, 0), (-1, -0.02, 0), (-1, 0.02, 0), (1, 0.02, 0), (1, -0.02, 0))

# shape dei ctrl opzionali: (degree, knots, points) — dati MEL letterali
_ROBLOX_SHAPES = (
    (
        1,
        (0, 1, 2, 3, 4),
        (
            (-0.46293206014647192, 0.80755095211147043, 0),
            (0.80967673357217584, 0.46493704977017825, 0),
            (0.46706283123088332, -0.80515252407831328, 0),
            (-0.80806518235792024, -0.46923548208151244, 0),
            (-0.46293206014647192, 0.80755095211147043, 0),
        ),
    ),
    (
        1,
        (0, 1, 2, 3, 4),
        (
            (-0.093420957950459849, 0.16141288444794716, 0),
            (0.15956795949331018, 0.089731233936296548, 0),
            (0.090727709937966347, -0.16625073783596675, 0),
            (-0.16132337720844686, -0.089217502220313286, 0),
            (-0.093420957950459849, 0.16141288444794716, 0),
        ),
    ),
)

_ARKIT_SHAPES = (
    (
        3,
        (0, 0, 0, 0.20948400980000001, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 15, 15),
        (
            (0.63846096134640429, 0.32252763421928005, 0),
            (0.5908738429722421, 0.38848194907001943, 0),
            (0.30837388102789964, 0.57310297306837465, 0),
            (-0.0015820896781627463, 0.31814299945101532, 0),
            (-0.24170475847354664, 0.58581709915072566, 0),
            (-0.73451460067053642, 0.30795786940643505, 0),
            (-0.70856300895458435, -0.31016186055532613, 0),
            (-0.47735791912155917, -0.69943573629460321, 0),
            (-0.2698062276640491, -0.86573132570269684, 0),
            (0.018081559092066258, -0.67584338018919243, 0),
            (0.29429525233568504, -0.86144015037234545, 0),
            (0.48890166907027149, -0.71951976011925445, 0),
            (0.62095782099046715, -0.51069688745131747, 0),
            (0.68102676565410813, -0.35164017665726316, 0),
            (0.68102673791348933, -0.35164018515497442, 0),
            (0.53121265408213914, -0.26082274878071138, 0),
            (0.40750679534784229, -0.023495892825406491, 0),
            (0.51116180169515046, 0.26313239280615475, 0),
            (0.63966206997360631, 0.32252762541845964, 0),
        ),
    ),
    (
        3,
        (0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 8),
        (
            (0.32320616941669478, 0.90970256535044669, 0),
            (0.33632375210066751, 0.79643922188956595, 0),
            (0.24389755522904263, 0.61384955188135881, 0),
            (0.09672038795688391, 0.52143484977590926, 0),
            (-0.013701450778161539, 0.51344955868791731, 0),
            (-0.013701450513186147, 0.51344956243314599, 0),
            (-0.013701450513186149, 0.51344956243314599, 0),
            (-0.016698808627702306, 0.61187047125862426, 0),
            (0.039354082111945757, 0.76744943632243734, 0),
            (0.20185915557499434, 0.90005632105055489, 0),
            (0.32320615690201521, 0.90970254812654594, 0),
        ),
    ),
)

_SNAPCHAT_SHAPE = (
    3,
    (
        0,
        0,
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        34,
        34,
    ),
    (
        (0.0030724584016100847, -0.72415333316094221, 0),
        (-0.070068244057445855, -0.72415333316094221, 0),
        (-0.19384481744969426, -0.67633056616848275, 0),
        (-0.33731311842707318, -0.55536709671696727, 0),
        (-0.4554634839378558, -0.56380640853916619, 0),
        (-0.56798764156717252, -0.62006848735382436, 0),
        (-0.5342303942783776, -0.45972156273204795, 0),
        (-0.67769869525575632, -0.46253466667278093, 0),
        (-0.84929803564046447, -0.37814154845079329, 0),
        (-0.63550213614476259, -0.35282361298419695, 0),
        (-0.48359452334518488, -0.2009160001846193, 0),
        (-0.35700484601220361, 0.0072536914296166622, 0),
        (-0.63550213614476259, 0.05226335448134338, 0),
        (-0.61299730461889934, 0.17885303181432483, 0),
        (-0.48359452334518488, 0.13946957664406393, 0),
        (-0.39357519724173157, 0.13103026482186514, 0),
        (-0.40764071694539622, 0.19573165545872218, 0),
        (-0.45177785159041656, 0.56867395284608491, 0),
        (0, 0.86143228140292361, 0),
        (0.45177785159041656, 0.56867395284608491, 0),
        (0.40764071694539622, 0.19573165545872218, 0),
        (0.39357519724173157, 0.13103026482186514, 0),
        (0.48359452334518488, 0.13946957664406393, 0),
        (0.61299730461889934, 0.17885303181432483, 0),
        (0.63550213614476259, 0.05226335448134338, 0),
        (0.35700484601220361, 0.0072536914296166622, 0),
        (0.48359452334518488, -0.2009160001846193, 0),
        (0.63550213614476259, -0.35282361298419695, 0),
        (0.84929803564046447, -0.37814154845079329, 0),
        (0.67769869525575632, -0.46253466667278093, 0),
        (0.5342303942783776, -0.45972156273204795, 0),
        (0.56798764156717252, -0.62006848735382436, 0),
        (0.4554634839378558, -0.56380640853916619, 0),
        (0.33731311842707318, -0.55536709671696727, 0),
        (0.19384481744969426, -0.67633056616848275, 0),
        (0.070068244057445855, -0.72415333316094221, 0),
        (-0.0030724584016100847, -0.72415333316094221, 0),
    ),
)


def _named_curve(name: str, points: Sequence, degree: int = 1, knots: Sequence = None) -> str:
    """Curva con transform e shape dai nomi deterministici."""
    if knots is None:
        knots = list(range(len(points)))
    curve = cmds.curve(degree=degree, point=points, knot=knots)
    curve = cmds.rename(curve, name)
    shape = cmds.listRelatives(curve, shapes=True)[0]
    if shape != name + "Shape":
        cmds.rename(shape, name + "Shape")
    return curve


def _merge_shape(source: str, target: str, shape_name: str):
    """Sposta la shape di `source` sotto `target` col nome dato e
    cancella il transform vuoto (il giro parent -add -s del MEL)."""
    shape = cmds.listRelatives(source, shapes=True)[0]
    if shape != shape_name:
        shape = cmds.rename(shape, shape_name)
    cmds.parent(shape, target, addObject=True, shape=True)
    cmds.delete(source)


def _connect_limit_enables(ctrl: str):
    """ctrlBox.limits pilota i transform limits del ctrl (catchQuiet
    nel MEL: Maya<=2012 non ha questi attributi)."""
    for attr in (
        "minTransXLimitEnable",
        "minTransYLimitEnable",
        "maxTransXLimitEnable",
        "maxTransYLimitEnable",
    ):
        try:
            cmds.connectAttr("ctrlBox.limits", "{}.{}".format(ctrl, attr), force=True)
        except RuntimeError:
            pass


def create_ctrl_box_slider(name: str, x: float, y: float, half: int):
    """Slot slider del board (parita' asFaceCreateCtrlBox).

    Args:
        name: suffisso (es. "Brow_R") -> ctrlBox<name> + ctrl<name>.
        x, y: posizione del box nel board.
        half: 0 quadro intero; 1 solo meta' superiore (ty 0..1);
              2 solo meta' inferiore (ty -1..0).
    """
    duplicate = cmds.duplicate("ctrlBoxTemplate", renameChildren=True)
    box = cmds.rename(duplicate[0], "ctrlBox" + name)
    child = cmds.listRelatives(box, children=True, type="transform")[0]
    ctrl = cmds.rename(child, "ctrl" + name)
    cmds.setAttr(box + ".t", x, y, 0, type="float3")
    _connect_limit_enables(ctrl)

    ensure_output_blend_weighted(ctrl + ".tx")
    ensure_output_blend_weighted(ctrl + ".ty")

    if half:
        pos0 = cmds.xform(box + ".cv[0]", query=True, worldSpace=True, translation=True)
        pos2 = cmds.xform(box + ".cv[2]", query=True, worldSpace=True, translation=True)
        pos3 = cmds.xform(box + ".cv[3]", query=True, worldSpace=True, translation=True)
        if half == 1:
            cmds.xform(
                box + ".cv[2]",
                worldSpace=True,
                translation=(pos2[0], (pos0[1] + pos2[1]) / 2.0, pos2[2]),
            )
            cmds.xform(
                box + ".cv[3]",
                worldSpace=True,
                translation=(pos3[0], (pos0[1] + pos3[1]) / 2.0, pos3[2]),
            )
            cmds.transformLimits(
                ctrl,
                translationX=(-1, 1),
                translationY=(0, 1),
                translationZ=(0, 0),
                enableTranslationZ=(True, True),
            )
        if half == 2:
            cmds.xform(
                box + ".cv[1]",
                worldSpace=True,
                translation=(pos2[0], (pos0[1] + pos2[1]) / 2.0, pos2[2]),
            )
            for cv in (".cv[0]", ".cv[4]"):
                cmds.xform(
                    box + cv,
                    worldSpace=True,
                    translation=(pos3[0], (pos0[1] + pos2[1]) / 2.0, pos3[2]),
                )
            cmds.transformLimits(
                ctrl,
                translationX=(-1, 1),
                translationY=(-1, 0),
                translationZ=(0, 0),
                enableTranslationZ=(True, True),
            )


def create_face_controller(name: str, side: str, ctrl_type: int) -> str:
    """Factory dei controlli on-face (parita' asCreateFaceController).

    Args:
        name: nome base (es. "Cheek").
        side: suffisso lato ("_R", "_L", "_M").
        ctrl_type: 1=rosso/B, 2|12=verde/A, 3|13=blu/C, 4=Regions
            (+joint), 5=Custom.

    Returns:
        Nome del controller creato.
    """
    radius = 0.2
    letter, color = "", 0
    if ctrl_type == 1:
        radius, letter, color = 0.15, "B", 13  # rosso
    if ctrl_type in (2, 12):
        radius, letter, color = 0.3, "A", 14  # verde
    if ctrl_type in (3, 13):
        radius, letter, color = 0.15, "C", 6  # blu
    if ctrl_type == 4:
        letter, color = "Regions", 14
    if ctrl_type == 5:
        letter, color = "Custom", 28

    ctrl = cmds.circle(
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=radius,
        degree=3,
        useTolerance=False,
        sections=8,
        constructionHistory=False,
    )[0]
    ctrl = cmds.rename(ctrl, name + side)
    cmds.sets(ctrl, add="FaceControlSet")
    shape = cmds.listRelatives(ctrl, shapes=True)[0]
    cmds.setAttr(shape + ".overrideEnabled", 1)
    cmds.setAttr(shape + ".overrideColor", color)
    cmds.createNode("transform", name=name + "Offset" + side)
    cmds.createNode("transform", name="SDK" + name + side, parent=name + "Offset" + side)
    cmds.parent(ctrl, "SDK" + name + side)

    if ctrl_type == 4:
        cmds.select(clear=True)
        cmds.joint(name=name + "Joint" + side)

    cmds.connectAttr("ctrlBox." + letter + "CtrlVis", shape + ".overrideVisibility")
    return ctrl


def add_ctrl_box2_shape(ctrl: str):
    """Aggancia al controller la sua sagoma di ctrlBox2 (parita'
    asAddCtrlBox2Shape, MEL:37900-37946).

    La curva indicatrice `<Name>1_<S>` diventa una seconda shape del
    controller, tenuta ferma nel quadro da un transformGeometry che annulla
    il movimento del controller (`<ctrl>TG` guidato da `<ctrl>TGXform`
    sotto `ctrlBox2Constrained`).
    """
    name, side = ctrl.split("_")[0], ctrl.split("_")[1]
    ctrl1 = "{}1_{}".format(name, side)

    # copia della shape indicatrice sotto il controller, con i CV alla
    # stessa posizione world
    copy = cmds.duplicate(ctrl1, name=ctrl1 + "2")[0]
    shape = cmds.listRelatives(copy, shapes=True, fullPath=True)[0]
    cmds.parent(shape, ctrl, add=True, shape=True)
    cmds.delete(copy)
    shape = "{}|{}2Shape".format(ctrl, ctrl1)
    form = cmds.getAttr(ctrl1 + ".form")
    num_cv = cmds.getAttr(ctrl1 + ".spans") + (0 if form == 2 else cmds.getAttr(ctrl1 + ".degree"))
    for i in range(num_cv):
        pos = cmds.xform(
            "{}|{}Shape.cv[{}]".format(ctrl1, ctrl1, i),
            query=True,
            worldSpace=True,
            translation=True,
        )
        cmds.xform("{}.cv[{}]".format(shape, i), worldSpace=True, translation=pos)
    cmds.delete(ctrl1)
    shape = cmds.rename(shape, ctrl1 + "Shape")
    cmds.setAttr(shape + ".overrideEnabled", 1)
    cmds.setAttr(shape + ".overrideColor", cmds.getAttr(ctrl + "Shape.overrideColor"))

    # una seconda copia fa da shape "Orig" (intermediate)
    copy = cmds.duplicate(ctrl, name=ctrl + "2")[0]
    cmds.parent("{}|{}Shape".format(copy, ctrl1), ctrl, add=True, shape=True)
    cmds.delete(copy)
    orig = cmds.rename("{}|{}Shape1".format(ctrl, ctrl1), ctrl1 + "OrigShape")
    cmds.setAttr(orig + ".intermediateObject", 1)

    tg = cmds.createNode("transformGeometry", name=ctrl + "TG")
    cmds.connectAttr(orig + ".worldSpace[0]", tg + ".inputGeometry", force=True)
    cmds.connectAttr(tg + ".outputGeometry", shape + ".create", force=True)

    offset = cmds.createNode("transform", name=ctrl + "TGXformOffset", parent=ctrl)
    offset = cmds.parent(offset, "ctrlBox2Constrained")[0]
    xform = cmds.createNode("transform", name=ctrl + "TGXform", parent=offset)
    as_parent_constraint(ctrl, xform, force_mult_matrix=True)
    source = ".offsetParentMatrix" if as_get_opm() else ".matrix"
    cmds.connectAttr(xform + source, tg + ".transform", force=True)
    cmds.setAttr(tg + ".invertTransform", 1)


def place_ctrl_by_projection(ctrl: str):
    """Spinge i CV del ctrl fin sulla superficie della mesh (parita'
    asFacePlaceCtrlByProjection, MEL 43153).

    Proietta la curva del ctrl su allHeadCombinedLayer lungo la
    direzione locale derivata da <name>Offset<side>.ry (X negata sul
    lato destro), trova il CV proiettato piu' esterno nel frame del
    ctrl (maxZ) e sposta i CV del ctrl di quel tanto lungo la propria Z.
    No-op con warning se manca allHeadCombinedLayer.
    """
    if not cmds.objExists("allHeadCombinedLayer"):
        cmds.warning("allHeadCombinedLayer not found: skipping ctrl projection for {}".format(ctrl))
        return
    tokens = ctrl.split("_")
    name = tokens[0]
    side = "_" + tokens[1]
    ry = cmds.getAttr("{}Offset{}.ry".format(name, side))

    rad = math.radians(ry)
    dir_x = math.sin(rad)
    dir_z = math.cos(rad)
    if ctrl.endswith("_R"):
        dir_x *= -1

    projection = cmds.polyProjectCurve(
        ctrl,
        "allHeadCombinedLayer",
        constructionHistory=True,
        direction=(dir_x, 0.0, dir_z),
        pointsOnEdges=0,
        tolerance=0.01,
    )
    cv_pos = cmds.createNode("transform", name="cvPos", parent=ctrl)
    max_z = -999.0
    for curve in cmds.listRelatives(projection[0], children=True, type="transform") or []:
        cvs = cmds.ls(curve + ".cv[*]", flatten=True) or []
        for cv in cvs:
            pos = cmds.xform(cv, query=True, worldSpace=True, translation=True)
            cmds.xform(cv_pos, worldSpace=True, translation=pos)
            pos_z = cmds.getAttr(cv_pos + ".tz")
            if pos_z > max_z:
                max_z = pos_z
    cmds.delete(cv_pos)
    cmds.delete(projection[0])

    w_scale = cmds.xform(ctrl, query=True, worldSpace=True, scale=True)
    cmds.move(
        0,
        0,
        max_z * w_scale[0],
        ctrl + ".cv[0:99]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )


def face_control_orient(ctrl: str):
    """Orienta l'Offset del ctrl sulla superficie di FaceControlOrient
    (parita' asFaceControlOrient)."""
    if not cmds.objExists("FaceControlOrient"):
        return
    tokens = ctrl.split("_")
    offset = tokens[0] + "Offset_" + tokens[1]
    cmds.delete(
        cmds.normalConstraint(
            "FaceControlOrient",
            offset,
            weight=1,
            aimVector=(0, 0, 1),
            upVector=(0, 1, 0),
            worldUpType="vector",
            worldUpVector=(0, 1, 0),
        )
    )


def _position_board(scale: float):
    """Posiziona ctrlBoxOffset accanto alla testa (bbox mask o
    FitEyeBall)."""
    mask = get_fit_option("Mask") or ""
    pos = [0.0, 0.0, 0.0]
    if mask:
        cmds.select(mask.split())
        bb = cmds.xform(query=True, worldSpace=True, boundingBox=True)
        pos = [bb[3] * 1.5, (bb[1] + bb[4]) / 2.0, (bb[2] + bb[5]) / 2.0]
    if cmds.objExists("FitEyeBall"):
        eye = cmds.xform("FitEyeBall", query=True, worldSpace=True, translation=True)
        pos[1] = eye[1] - ((scale / 4.0) * 0.38)
        pos[2] = eye[2]
    cmds.xform("ctrlBoxOffset", worldSpace=True, translation=pos)


def _create_templates(scale: float):
    """ctrlBoxTemplate (cornice reference) + ctrlTemplate (rombo)."""
    _named_curve("ctrlBoxTemplate", _SQUARE)
    cmds.parent("ctrlBoxTemplate", "ctrlBox")
    cmds.setAttr("ctrlBoxTemplate.t", 0, 0, 0, type="float3")
    cmds.setAttr("ctrlBoxTemplate.s", scale / 24.0, scale / 24.0, scale / 24.0, type="float3")
    cmds.setAttr("ctrlBoxTemplateShape.overrideEnabled", 1)
    cmds.setAttr("ctrlBoxTemplateShape.overrideDisplayType", 2)

    cmds.duplicate("ctrlBoxTemplate", name="ctrlTemplate")
    cmds.parent("ctrlTemplate", "ctrlBoxTemplate")
    cmds.transformLimits(
        "ctrlTemplate",
        translationX=(-1, 1),
        translationY=(-1, 1),
        translationZ=(0, 0),
        enableTranslationX=(True, True),
        enableTranslationY=(True, True),
        enableTranslationZ=(True, True),
    )
    _connect_limit_enables("ctrlTemplate")
    cmds.setAttr("ctrlTemplateShape.overrideDisplayType", 0)
    cmds.setAttr("ctrlTemplate.rz", 45)
    cmds.setAttr("ctrlTemplate.s", 0.2, 0.2, 0.2, type="float3")
    cmds.setAttr("ctrlTemplateShape.overrideEnabled", 0)
    cmds.makeIdentity("ctrlTemplate", apply=True, translate=False, rotate=True, scale=True)
    for attr in ("tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"):
        cmds.setAttr("ctrlTemplate." + attr, lock=True, keyable=False)
    cmds.sets("ctrlTemplate", add="FaceControlSet")


def _optional_ctrl_box(name: str) -> str:
    """ctrlBox<name> vuoto dal template per i ctrl opzionali."""
    box = "ctrlBox" + name
    cmds.duplicate("ctrlBoxTemplate", name=box)
    children = cmds.listRelatives(box, children=True, type="transform", fullPath=True) or []
    if children:
        cmds.delete(children)
    return box


def _place_optional_box(box: str, scale: float, tx: float):
    """Posiziona il box opzionale DOPO il parent del ctrl (i ctrl hanno
    i transform lockati: il MEL muove solo il box)."""
    cmds.setAttr(box + ".t", 0, 0, 0, type="float3")
    cmds.setAttr(box + ".s", scale / 66.0, scale / 66.0, scale / 66.0, type="float3")
    cmds.setAttr(box + ".translateX", tx)
    cmds.setAttr(box + ".ty", (scale / 4.0) * -1.3)


def _curve_shape_ctrl(name: str, box: str, shapes: Sequence[Tuple]) -> str:
    """Ctrl da shape nurbs letterali (ARKit/Roblox/SnapChat)."""
    cmds.createNode("transform", name=name, parent=box)
    cmds.sets(name, add="FaceControlSet")
    for index, (degree, knots, points) in enumerate(shapes):
        suffix = "Shape" if index == 0 else "Shape{}".format(index)
        source = cmds.curve(degree=degree, point=points, knot=knots)
        _merge_shape(source, name, name + suffix)
        cmds.setAttr("{}{}.isHistoricallyInteresting".format(name, suffix), 0)
    as_lock_attr(name, True, True, True, True)
    return name


def _create_phonemes(scale: float):
    _named_curve(
        "ctrlPhonemes_M",
        (
            (-0.922009, 0, 1),
            (-0.176985, 0, -0.989507),
            (0.194834, 0, -0.989507),
            (0.934309, 0, 1),
            (0.572202, 0, 1),
            (0.39323, 0, 0.493605),
            (-0.389254, 0, 0.493605),
            (-0.56129, 0, 1),
            (-0.922009, 0, 1),
        ),
    )
    cmds.sets("ctrlPhonemes_M", add="FaceControlSet")
    _named_curve(
        "ctrlPhonemes_M1",
        (
            (-0.303236, 0, 0.224453),
            (-0.00217431, 0, -0.693995),
            (0.305825, 0, 0.224453),
            (-0.303236, 0, 0.224453),
        ),
    )
    _merge_shape("ctrlPhonemes_M1", "ctrlPhonemes_M", "ctrlPhonemes_MShape1")
    cmds.rotate(
        90, 0, 0, "ctrlPhonemes_M.cv[0:99]", relative=True, pivot=(0, 0, 0), objectSpace=True
    )
    cmds.scale(0.6, 0.6, 0.6, "ctrlPhonemes_M.cv[0:99]", relative=True, pivot=(0, 0, 0))
    as_lock_attr("ctrlPhonemes_M", True, True, True, True)
    box = _optional_ctrl_box("Phonemes_M")
    cmds.parent("ctrlPhonemes_M", box, relative=True)
    _place_optional_box(box, scale, scale / -25.0)


def _create_emotions(scale: float):
    cmds.circle(
        name="ctrlEmotions_M",
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=0.025,
        degree=3,
        useTolerance=False,
        tolerance=0.000610236,
        sections=4,
        constructionHistory=False,
    )
    cmds.sets("ctrlEmotions_M", add="FaceControlSet")
    cmds.move(-0.04, 0.075, 0, "ctrlEmotions_M.cv[0:99]", relative=True)
    cmds.circle(
        name="ctrlEmotions_M1",
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=0.025,
        degree=3,
        useTolerance=False,
        tolerance=0.000610236,
        sections=4,
        constructionHistory=False,
    )
    cmds.move(0.04, 0.075, 0, "ctrlEmotions_M1.cv[0:99]", relative=True)
    _merge_shape("ctrlEmotions_M1", "ctrlEmotions_M", "ctrlEmotions_MShape1")
    cmds.move(
        0,
        -0.02,
        0,
        "ctrlEmotions_MShape.cv[1]",
        "ctrlEmotions_MShape1.cv[1]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.move(
        0,
        0.02,
        0,
        "ctrlEmotions_MShape.cv[3]",
        "ctrlEmotions_MShape1.cv[3]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.circle(
        name="ctrlEmotions_M2",
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=0.07,
        degree=3,
        useTolerance=False,
        tolerance=0.000610236,
        sections=8,
        constructionHistory=False,
    )
    cmds.move(
        0,
        -0.12,
        0,
        "ctrlEmotions_M2.cv[1]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.move(
        0,
        -0.07,
        0,
        "ctrlEmotions_M2.cv[0]",
        "ctrlEmotions_M2.cv[2]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.move(0, 0.04, 0, "ctrlEmotions_M2.cv[0:99]", relative=True)
    _merge_shape("ctrlEmotions_M2", "ctrlEmotions_M", "ctrlEmotions_MShape2")
    cmds.select(
        "ctrlEmotions_MShape.cv[0:99]",
        "ctrlEmotions_MShape1.cv[0:99]",
        "ctrlEmotions_MShape2.cv[0:99]",
    )
    cmds.scale(10, 10, 10, relative=True, pivot=(0, 0, 0))
    cmds.move(0, -0.3, 0, relative=True)
    as_lock_attr("ctrlEmotions_M", True, True, True, True)
    box = _optional_ctrl_box("Emotions_M")
    cmds.parent("ctrlEmotions_M", box, relative=True)
    _place_optional_box(box, scale, 0.0)


def _create_ctrl_box2(scale: float):
    """ctrlBox2: il quadro degli indicatori di regione."""
    cmds.duplicate("ctrlBoxOffset", name="ctrlBox2Offset")
    cmds.rename("ctrlBox2Offset|ctrlBox", "ctrlBox2")
    shape = cmds.listRelatives("ctrlBox2", shapes=True)[0]
    if shape != "ctrlBox2Shape":
        cmds.rename(shape, "ctrlBox2Shape")
    cmds.setAttr("ctrlBox2Offset.tx", cmds.getAttr("ctrlBox2Offset.tx") + scale / 3.5)
    children = cmds.listRelatives("ctrlBox2", children=True, type="transform", fullPath=True) or []
    if children:
        cmds.delete(children)
    for attr in cmds.listAttr("ctrlBox2", userDefined=True) or []:
        cmds.deleteAttr("ctrlBox2", attribute=attr)
    cmds.createNode("transform", name="ctrlBox2Constrained", parent="ConstrainedSetup")
    as_parent_constraint("ctrlBox2", "ctrlBox2Constrained")


def _create_region_indicators(scale: float):
    """Le sagome di regione dentro ctrlBox2 (MEL 28945-29047)."""
    eye_base = bool(get_fit_option("EyeBase"))
    for b in (1, -1):
        if not cmds.objExists("FitEyeBall"):
            continue
        side = "_R" if b == 1 else "_L"

        if eye_base:
            _named_curve(
                "EyeBase1" + side, ((0, 1, 0), (0, -1, 0), (0, 0, 0), (1, 0, 0), (-1, 0, 0))
            )
            cmds.scale(
                scale / 80,
                scale / 80,
                scale / 80,
                "EyeBase1{}.cv[0:99]".format(side),
                relative=True,
                pivot=(0, 0, 0),
            )
            cmds.setAttr("EyeBase1" + side + ".tx", -0.05 * scale * b)
            cmds.setAttr("EyeBase1" + side + ".ty", 0.095 * scale)
            cmds.parent("EyeBase1" + side, "ctrlBox2", relative=True)

        cmds.circle(
            name="Eye1" + side,
            center=(0, 0, 0),
            normal=(0, 0, 1),
            sweep=360,
            radius=0.3,
            degree=3,
            useTolerance=False,
            tolerance=0.000610236,
            sections=8,
            constructionHistory=False,
        )
        cmds.scale(
            scale / 10,
            scale / 10,
            scale / 10,
            "Eye1{}.cv[0:99]".format(side),
            relative=True,
            pivot=(0, 0, 0),
        )
        cmds.setAttr("Eye1" + side + ".tx", -0.05 * scale * b)
        cmds.setAttr("Eye1" + side + ".ty", 0.095 * scale)
        cmds.parent("Eye1" + side, "ctrlBox2", relative=True)

        cmds.duplicate("Eye1" + side, name="EyeRegion1" + side)
        pos = cmds.xform("EyeRegion1" + side, query=True, worldSpace=True, translation=True)
        cmds.scale(1.5, 1.5, 1.5, "EyeRegion1{}.cv[0:99]".format(side), relative=True, pivot=pos)

        cmds.circle(
            name="EyeBrowRegion1" + side,
            center=(0, 0, 0),
            normal=(0, 0, 1),
            sweep=360,
            radius=0.3,
            degree=3,
            useTolerance=False,
            tolerance=0.000610236,
            sections=8,
            constructionHistory=False,
        )
        cmds.scale(
            scale / 7,
            scale / 10,
            scale / 8,
            "EyeBrowRegion1{}.cv[0:99]".format(side),
            relative=True,
            pivot=(0, 0, 0),
        )
        cmds.setAttr("EyeBrowRegion1" + side + ".tx", -0.05 * scale * b)
        cmds.setAttr("EyeBrowRegion1" + side + ".ty", 0.188 * scale)
        cmds.move(
            0,
            0.06 * scale,
            0,
            "EyeBrowRegion1{}.cv[5]".format(side),
            relative=True,
            objectSpace=True,
            worldSpaceDistance=True,
        )
        cmds.move(
            0,
            0.03 * scale,
            0,
            "EyeBrowRegion1{}.cv[4]".format(side),
            "EyeBrowRegion1{}.cv[6]".format(side),
            relative=True,
            objectSpace=True,
            worldSpaceDistance=True,
        )
        cmds.parent("EyeBrowRegion1" + side, "ctrlBox2", relative=True)

        cmds.setAttr("Eye1" + side + "Shape.overrideEnabled", 1)
        cmds.setAttr("Eye1" + side + "Shape.overrideColor", 18)

    cmds.circle(
        name="LipRegion1_M",
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=0.3,
        degree=3,
        useTolerance=False,
        tolerance=0.000610236,
        sections=8,
        constructionHistory=False,
    )
    cmds.move(
        0, -0.3, 0, "LipRegion1_M.cv[1]", relative=True, objectSpace=True, worldSpaceDistance=True
    )
    cmds.move(
        0,
        -0.15,
        0,
        "LipRegion1_M.cv[2]",
        "LipRegion1_M.cv[0]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.move(
        0,
        0.15,
        0,
        "LipRegion1_M.cv[3]",
        "LipRegion1_M.cv[7]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.move(
        0,
        0.25,
        0,
        "LipRegion1_M.cv[4]",
        "LipRegion1_M.cv[6]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.move(
        0, 0.25, 0, "LipRegion1_M.cv[5]", relative=True, objectSpace=True, worldSpaceDistance=True
    )
    cmds.scale(
        scale / 3.5,
        scale / 3.5,
        scale / 3.5,
        "LipRegion1_M.cv[0:99]",
        relative=True,
        pivot=(0, 0, 0),
    )
    cmds.parent("LipRegion1_M", "ctrlBox2", relative=True)
    cmds.setAttr("LipRegion1_M.ty", -0.25 * scale)

    if cmds.objExists("FaceFitUpMidLo"):
        _named_curve("lowerFace1_M", _BAR)
        cmds.scale(
            scale / 50.0,
            scale / 10.0,
            scale / 10.0,
            "lowerFace1_M.cv[0:99]",
            relative=True,
            pivot=(0, 0, 0),
        )
        cmds.parent("lowerFace1_M", "ctrlBox2", relative=True)
        cmds.setAttr("lowerFace1_M.tx", 0.09 * scale)
        cmds.setAttr("lowerFace1_M.ty", -0.16 * scale)
        cmds.duplicate("lowerFace1_M", name="middleFace1_M")
        cmds.setAttr("middleFace1_M.ty", -0.0875 * scale)
        cmds.duplicate("lowerFace1_M", name="upperFace1_M")
        cmds.setAttr("upperFace1_M.ty", -0.015 * scale)

    cmds.circle(
        name="NoseRegion1_M",
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=0.3,
        degree=3,
        useTolerance=False,
        tolerance=0.000610236,
        sections=8,
        constructionHistory=False,
    )
    cmds.move(
        0, 0.1, 0, "NoseRegion1_M.cv[1]", relative=True, objectSpace=True, worldSpaceDistance=True
    )
    cmds.move(
        0, 0.3, 0, "NoseRegion1_M.cv[5]", relative=True, objectSpace=True, worldSpaceDistance=True
    )
    cmds.scale(
        scale / 5, scale / 5, scale / 5, "NoseRegion1_M.cv[0:99]", relative=True, pivot=(0, 0, 0)
    )
    cmds.scale(
        0.5, 1, 1, "NoseRegion1_M.cv[0]", "NoseRegion1_M.cv[2]", relative=True, pivot=(0, 0, 0)
    )
    cmds.move(
        0,
        -0.1,
        0,
        "NoseRegion1_M.cv[0]",
        "NoseRegion1_M.cv[2]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.parent("NoseRegion1_M", "ctrlBox2", relative=True)
    cmds.setAttr("NoseRegion1_M.ty", -0.1 * scale)

    if (get_fit_option("UpperTeeth") or "") != "":
        _named_curve("upperTeeth1_M", _BAR)
        cmds.scale(
            scale / 50.0,
            scale / 10.0,
            scale / 10.0,
            "upperTeeth1_M.cv[0:99]",
            relative=True,
            pivot=(0, 0, 0),
        )
        cmds.parent("upperTeeth1_M", "ctrlBox2", relative=True)
        cmds.setAttr("upperTeeth1_M.tx", -0.1 * scale)
        cmds.setAttr("upperTeeth1_M.ty", -0.20 * scale)
        cmds.setAttr("upperTeeth1_MShape.overrideEnabled", 1)
        cmds.setAttr("upperTeeth1_MShape.overrideColor", 14)
        cmds.duplicate("upperTeeth1_M", name="lowerTeeth1_M")
        cmds.setAttr("lowerTeeth1_M.ty", -0.25 * scale)

    if cmds.objExists("FaceFitTongue"):
        _named_curve("Tongue11_M", _BAR)
        cmds.scale(
            scale / 50.0,
            scale / 10.0,
            scale / 10.0,
            "Tongue11_M.cv[0:99]",
            relative=True,
            pivot=(0, 0, 0),
        )
        cmds.parent("Tongue11_M", "ctrlBox2", relative=True)
        cmds.setAttr("Tongue11_M.tx", 0.09 * scale)
        cmds.setAttr("Tongue11_M.ty", -0.26 * scale)
        cmds.setAttr("Tongue11_MShape.overrideColor", 6)
        cmds.duplicate("Tongue11_M", name="Tongue21_M")
        cmds.setAttr("Tongue21_M.ty", -0.28 * scale)
        cmds.duplicate("Tongue11_M", name="Tongue31_M")
        cmds.setAttr("Tongue31_M.ty", -0.30 * scale)


def face_ctrl_box() -> bool:
    """Crea il control board (parita' asFaceCtrlBox).

    Presuppone il prep eseguito (base strutturale, FaceControlSet,
    FaceJoint_M). Ritorna False con warning se la base manca.
    """
    for node in (
        FIT_SKELETON,
        "ControlsSetup",
        "ConstrainedSetup",
        "FaceMotionSystem",
        "FaceControlSet",
    ):
        if not cmds.objExists(node):
            cmds.warning("{} not found: run the build prep first".format(node))
            return False

    phonemes = bool(get_fit_option("Phonemes"))
    emotions = bool(get_fit_option("Emotions"))
    arkit = bool(get_fit_option("ARKit"))
    roblox_head = bool(get_fit_option("RobloxHead"))
    snap_chat = bool(get_fit_option("SnapChat"))
    cyclops = bool(get_fit_option("Cyclops"))
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")

    if cmds.objExists("ctrlBoxOffset"):
        cmds.delete("ctrlBoxOffset")

    cmds.setAttr(FIT_SKELETON + ".v", lock=False)
    cmds.setAttr(FIT_SKELETON + ".v", 0)
    cmds.setAttr(FIT_SKELETON + ".v", lock=True)

    _named_curve("ctrlBox", _SQUARE)
    cmds.createNode("transform", name="ctrlBoxOffset")
    cmds.parent("ctrlBox", "ctrlBoxOffset")
    cmds.parent("ctrlBoxOffset", "ControlsSetup")

    cmds.addAttr(
        "ctrlBox", keyable=True, longName="limits", attributeType="bool", defaultValue=True
    )
    for attr in CTRL_VIS_ATTRS:
        cmds.addAttr(
            "ctrlBox", keyable=True, longName=attr, attributeType="bool", defaultValue=True
        )
    # senza body rig Main.jointVis non esiste: attributo locale
    if not (cmds.objExists("Main") and cmds.attributeQuery("jointVis", node="Main", exists=True)):
        cmds.addAttr(
            "ctrlBox", keyable=True, longName="jointsVis", attributeType="bool", defaultValue=False
        )
        if cmds.objExists("FaceJoint_M"):
            cmds.connectAttr("ctrlBox.jointsVis", "FaceJoint_M.v")

    cmds.setAttr("ctrlBox.AimCtrlVis", 0)
    cmds.setAttr("ctrlBox.RegionsCtrlVis", 0)
    cmds.setAttr("ctrlBox.overrideEnabled", 1)
    cmds.setAttr("ctrlBox.overrideColor", 17)

    # allunga il quadro verso il basso e congela la scala
    cmds.move(0, -0.4, 0, "ctrlBoxShape.cv[2:3]", relative=True)
    cmds.xform("ctrlBox", scale=(scale / 8.0, scale / 4.0, scale / 8.0))
    cmds.makeIdentity("ctrlBox", apply=True, translate=False, rotate=False, scale=True)

    _position_board(scale)

    # rebuild: ripristina la posizione scelta dall'utente
    if cmds.objExists("prefix_ctrlBox"):
        t = cmds.getAttr("prefix_ctrlBox.t")[0]
        cmds.setAttr("ctrlBox.t", t[0], t[1], t[2], type="float3")
        s = cmds.getAttr("prefix_ctrlBox.s")[0]
        cmds.setAttr("ctrlBox.s", s[0], s[1], s[2], type="float3")

    _create_templates(scale)

    for name, x, y, half in SLIDERS:
        create_ctrl_box_slider(name, (scale / 4.0) * x, (scale / 4.0) * y, half)

    # gli attributi del board vivono solo nel channelBox
    for attr in cmds.listAttr("ctrlBox", keyable=True) or []:
        try:
            cmds.setAttr("ctrlBox." + attr, keyable=False, channelBox=True)
        except RuntimeError:
            pass

    if phonemes:
        _create_phonemes(scale)
    if emotions:
        _create_emotions(scale)
    if roblox_head:
        box = _optional_ctrl_box("RobloxHead_M")
        _place_optional_box(box, scale, (scale / 25.0) * 2)
        _curve_shape_ctrl("ctrlRobloxHead_M", box, _ROBLOX_SHAPES)
    if arkit:
        box = _optional_ctrl_box("ARKit_M")
        _place_optional_box(box, scale, scale / 25.0)
        _curve_shape_ctrl("ctrlARKit_M", box, _ARKIT_SHAPES)
    if snap_chat:
        if cmds.objExists("ctrlBoxEmotions_M"):
            cmds.duplicate("ctrlBoxEmotions_M", name="ctrlBoxSnapChat_M")
            cmds.setAttr("ctrlBoxSnapChat_M.translateX", scale / 25.0)
            child = "ctrlBoxSnapChat_M|ctrlEmotions_M"
            if cmds.objExists(child):
                cmds.delete(child)
            box = "ctrlBoxSnapChat_M"
        else:  # il MEL presuppone Emotions attivo
            box = _optional_ctrl_box("SnapChat_M")
            _place_optional_box(box, scale, scale / 25.0)
        _curve_shape_ctrl("ctrlSnapChat_M", box, (_SNAPCHAT_SHAPE,))

    cmds.delete("ctrlBoxTemplate")

    _create_ctrl_box2(scale)
    _create_region_indicators(scale)

    cmds.spaceLocator(name="tempLoc")
    cmds.setAttr("tempLoc.v", 0)
    cmds.createNode("transform", name="tempLocFlip", parent="FaceMotionSystem")
    cmds.parent("tempLoc", "tempLocFlip")

    if cyclops:
        cmds.setAttr("ctrlBoxEye_R.overrideEnabled", 1)
        cmds.setAttr("ctrlBoxEye_R.overrideVisibility", 0)
        cmds.setAttr("ctrlBoxEye_L.tx", 0)

    cmds.select(clear=True)
    return True
