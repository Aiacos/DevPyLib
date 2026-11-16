"""Helper dei controller on-face "PP" usati da EyeLid e Lip.

Parita' di:
- asCreatePP (MEL:42905-43052): controller + joint + (opzionale) attacher e
  subtracter;
- asFaceAddConstrained (MEL:38038-38143): follow blendMatrix fra due
  controller sorgente;
- asFaceHalfMoonCurve (MEL:38001-38036): forma a mezzaluna della curva;
- asSetRGBOverrideColor (MEL:7827-7835);
- asWeightHammerVertsMS (MEL:37828-37844).

Divergenze (docs/gap-analysis.md §5h): il ramo `legacyFaceJointOrient` di
asCreatePP (checkbox MEL opzionale, MEL:42983-42992) non e' portato; il
ramo non-matrice commentato di asFaceAddConstrained non esiste nemmeno nel
MEL eseguito.
"""

import maya.cmds as cmds

from .build_utils import as_matrix_connect_attr, as_parent_constraint
from .ctrl_box import create_face_controller, face_control_orient, place_ctrl_by_projection
from .driving_system import ensure_output_blend_weighted, unit_convert_and_reverse
from .face_prep import get_max_influences
from .fit_options import get_fit_option

_IDENTITY = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)


def _local_matrix_under(parent, start_parent=None, zero_rotation=False):
    """Matrice object-space di un transform temporaneo ri-parentato sotto
    `parent` (idioma MEL `tempMatrixTransform`)."""
    if start_parent:
        temp = cmds.createNode("transform", name="tempMatrixTransform", parent=start_parent)
    else:
        temp = cmds.createNode("transform", name="tempMatrixTransform")
    temp = cmds.parent(temp, parent)[0]
    if zero_rotation:
        cmds.xform(temp, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0))
    matrix = cmds.xform(temp, query=True, objectSpace=True, matrix=True)
    cmds.delete(temp)
    return matrix


def create_pp(
    trn_pos, name, side, ctrl_type, create_joint=True, bind_skin=False, create_attacher=False
):
    """Crea un controller on-face posizionato su `trn_pos` (asCreatePP).

    Args:
        trn_pos: transform o componente da cui leggere la posizione world.
        name, side: il controller si chiama `<name><side>`.
        ctrl_type: tipo di create_face_controller.
        create_joint: crea `<name>Joint<side>` guidato dal controller.
        bind_skin: aggiunge il joint allo skinCluster della Face.
        create_attacher: crea `<name>Attach<side>` (per agganciare il
            controller alla superficie) e `<name>Subtract<side>` (che
            annulla il movimento del controller, portato invece dal joint
            via `<name>JointPMAt<side>`).

    Returns:
        Nome del controller.
    """
    pos = cmds.xform(trn_pos, query=True, worldSpace=True, translation=True)
    ctrl = create_face_controller(name, side, ctrl_type)
    offset = name + "Offset" + side
    joint = name + "Joint" + side
    joint_offset = name + "JointOffset" + side
    joint_mm = name + "JointMM" + side
    sdk = "SDK" + name + side
    cmds.xform(offset, worldSpace=True, translation=pos)

    if create_joint:
        cmds.select(clear=True)
        cmds.createNode("transform", name=joint_offset)
        cmds.joint(name=joint)  # figlio di joint_offset (selezionato)
        cmds.parent(joint_offset, "FaceJoint_M")
        cmds.setAttr(joint + ".segmentScaleCompensate", 0)
        cmds.xform(joint_offset, worldSpace=True, translation=pos)
        as_parent_constraint(ctrl, joint, maintain_offset=True, force_mult_matrix=True)

    if bind_skin:
        skin = get_fit_option("SkinCluster") or ""
        cmds.skinCluster(skin, edit=True, addInfluence=joint, lockWeights=False, weight=0)

    cmds.select(clear=True)
    cmds.refresh()
    cmds.parent(offset, "SideReverse" + side)
    cmds.xform(offset, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))
    if side != "_M":
        face_control_orient(ctrl)
    place_ctrl_by_projection(ctrl)

    if create_joint:
        cmds.parent(joint, "FaceJoint_M")
        cmds.connectAttr("FaceJoint_M.worldInverseMatrix", joint_mm + ".matrixIn[2]", force=True)
        cmds.xform(joint, objectSpace=True, translation=(0, 0, 0))
        cmds.delete(joint_offset)
        matrix = _local_matrix_under(ctrl, zero_rotation=True)
        cmds.setAttr(joint_mm + ".matrixIn[0]", matrix, type="matrix")

    if create_attacher:
        attach = cmds.createNode("transform", name=name + "Attach" + side)
        cmds.parent(attach, offset, relative=True)
        cmds.parent(sdk, attach)

        pma = cmds.createNode("plusMinusAverage", name=name + "PMA" + side)
        cmds.connectAttr(ctrl + ".t", pma + ".input3D[0]")
        cmds.connectAttr(sdk + ".t", pma + ".input3D[1]")

        subtract = cmds.createNode("transform", name=name + "Subtract" + side, parent=sdk)
        mpd = cmds.createNode("multiplyDivide", name=name + "SubtractMPD" + side)
        cmds.setAttr(mpd + ".input1", -1, -1, -1, type="float3")
        cmds.connectAttr(pma + ".output3D", mpd + ".input2")
        cmds.connectAttr(mpd + ".output", subtract + ".t")
        cmds.parent(ctrl, subtract)

    if create_attacher and create_joint:
        # il joint non segue piu' il controller via matrice: lo guida la
        # somma delle traslazioni (cancellare la MM porta via PM e DM)
        cmds.delete(joint_mm)
        cmds.setAttr(joint + ".offsetParentMatrix", _IDENTITY, type="matrix")
        cmds.createNode("transform", name=joint_offset, parent=offset)
        if side == "_R":
            cmds.setAttr(joint_offset + ".sx", -1)
        cmds.parent(joint_offset, world=True)
        if side == "_R":
            cmds.setAttr(joint_offset + ".sx", -1 * cmds.getAttr(joint_offset + ".sx"))
        cmds.parent(joint, joint_offset, relative=True)
        cmds.setAttr(joint + ".r", 0, 0, 0, type="float3")

        pma_t = cmds.createNode("plusMinusAverage", name=name + "JointPMAt" + side)
        cmds.connectAttr(ctrl + ".t", pma_t + ".input3D[0]")
        cmds.connectAttr(sdk + ".t", pma_t + ".input3D[1]")
        follow = name + "Follow" + side
        if cmds.objExists(follow):
            cmds.connectAttr(follow + ".t", pma_t + ".input3D[2]")
        cmds.connectAttr(pma_t + ".output3D", joint + ".t")
    return ctrl


def face_add_constrained(target, source_a, source_b, value):
    """Fa seguire `target` a una miscela di due controller sorgente
    (asFaceAddConstrained): attributo `follow<source_a>` (0-10) sul target,
    gruppo `<name>Follow<side>` sopra l'SDK guidato da un blendMatrix.
    """
    name, side = target.split("_")[0], "_" + target.split("_")[1]
    attr = "follow" + source_a
    blend = "{}{}Blend{}".format(name, side, source_a)

    cmds.addAttr(
        target,
        keyable=True,
        longName=attr,
        attributeType="double",
        minValue=0,
        maxValue=10,
        defaultValue=value,
    )
    unit_convert_and_reverse(blend, "{}.{}".format(target, attr))
    # override via bw, cosi' altri driver possono guidare lo stesso attr
    ensure_output_blend_weighted("{}.{}".format(target, attr))
    cmds.connectAttr(
        "bw{}{}_{}.output".format(name, side, attr), blend + "UnitConversion.input", force=True
    )
    cmds.connectAttr(blend + "UnitConversion.output", blend + "Reverse.inputX", force=True)

    follow = cmds.createNode(
        "transform", name=name + "Follow" + side, parent=name + "Offset" + side
    )
    cmds.parent("SDK" + name + side, follow)
    bm = cmds.createNode("blendMatrix", name=name + "BM" + side)
    follow_parent = cmds.listRelatives(follow, parent=True)[0]
    for letter, source in (("A", source_a), ("B", source_b)):
        mm = cmds.createNode("multMatrix", name="{}MM{}{}".format(name, letter, side))
        matrix = _local_matrix_under(source, start_parent=target)
        cmds.setAttr(mm + ".matrixIn[0]", matrix, type="matrix")
        cmds.connectAttr(source + ".worldMatrix", mm + ".matrixIn[1]")
        cmds.connectAttr(follow_parent + ".worldInverseMatrix", mm + ".matrixIn[2]")
    cmds.connectAttr("{}MMA{}.matrixSum".format(name, side), bm + ".inputMatrix")
    cmds.connectAttr("{}MMB{}.matrixSum".format(name, side), bm + ".target[0].targetMatrix")
    cmds.connectAttr(blend + "Reverse.outputX", bm + ".target[0].weight")
    as_matrix_connect_attr(bm + ".outputMatrix", follow + ".offsetParentMatrix")


def face_half_moon_curve(ctrl, rotation):
    """Deforma la curva del controller a mezzaluna e la ruota di
    `rotation` gradi attorno a Z (asFaceHalfMoonCurve)."""

    def cv(index):
        return "{}.cv[{}]".format(ctrl, index)

    def pos(index):
        return cmds.xform(cv(index), query=True, worldSpace=True, translation=True)

    factor = 8.0
    for i, (cv1, cv2) in enumerate(((7, 3), (0, 2), (6, 4))):
        if i > 0:
            factor = 4.0
        a, b = pos(cv1), pos(cv2)
        cmds.xform(
            cv(cv2),
            worldSpace=True,
            translation=(
                (a[0] * factor + b[0]) / (factor + 1),
                (a[1] * 3 + b[1]) / 4.0,
                (a[2] * 3 + b[2]) / 4.0,
            ),
        )
    for index in (1, 5):
        a, b = pos(index), pos(3)
        cmds.xform(
            cv(index),
            worldSpace=True,
            translation=((a[0] * factor + b[0]) / (factor + 1), a[1], a[2]),
        )

    pivot = cmds.xform(ctrl, query=True, worldSpace=True, translation=True)
    cvs = ctrl + ".cv[0:99]"
    cmds.scale(0.8, 1.0, 1.0, cvs, relative=True, pivot=pivot)
    if "LidOuter" in ctrl:
        cmds.scale(0.75, 1.5, 1, cvs, relative=True, pivot=pivot)
    cmds.rotate(0, 0, rotation, cvs, relative=True, pivot=pivot, objectSpace=True)


def set_rgb_override_color(obj, rgb):
    """Colore di override RGB (asSetRGBOverrideColor)."""
    cmds.setAttr(obj + ".overrideRGBColors", 1)
    for channel, value in zip("RGB", rgb):
        cmds.setAttr(obj + ".overrideColor" + channel, value)


def weight_hammer_verts_ms(iterations, skin_cluster):
    """Weight hammer sui vertici selezionati (asWeightHammerVertsMS):
    `skinCluster -smoothWeights` rispettando il limite di influenze del
    game engine quando attivo."""
    if not cmds.ls(selection=True):
        return
    cmds.skinCluster(
        skin_cluster,
        edit=True,
        smoothWeights=0,
        smoothWeightsMaxIterations=iterations,
        obeyMaxInfluences=get_max_influences() > 0,
    )
