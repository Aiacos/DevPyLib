"""Utility di build condivise a parita' con AdvancedSkeleton.

Port delle proc MEL generiche usate da ogni step del build facciale:
asAlign (9992), asLockAttr (10057), asParentConstraint (23065),
asMatrixConnectAttr (68183), asGetOpm (23474). I nomi dei nodi di
plumbing generati (<name>MM<side>, <name>DM<side>, <name>PM<side>)
sono parte del grafo che i tool AS si aspettano: vengono replicati
inclusi i casi limite della tokenizzazione MEL (nomi senza "_").
"""

import maya.cmds as cmds

from .fit_options import get_fit_option


def as_get_opm() -> bool:
    """True se il body rig usa l'offsetParentMatrix (parita' asGetOpm):
    attributo useOffsetParentMatrix sul FitSkeleton del body."""
    if cmds.objExists("FitSkeleton") and cmds.attributeQuery(
        "useOffsetParentMatrix", node="FitSkeleton", exists=True
    ):
        return bool(cmds.getAttr("FitSkeleton.useOffsetParentMatrix"))
    return False


def as_create_mult_dl(name: str) -> str:
    """Nodo moltiplicatore double-linear (parita' asCreateMultDL,
    MEL 67295): multDL da Maya 2026 (math nodes unit-less), altrimenti
    multDoubleLinear. Prima di 2026 createNode("multDL") non fallisce
    ma genera un nodo "unknown": lo si rileva e si ricade sul tipo
    classico."""
    node = cmds.createNode("multDL", name=name)
    if cmds.nodeType(node) == "unknown":
        cmds.delete(node)
        node = cmds.createNode("multDoubleLinear", name=name)
    return node


def as_face_hide_controllers(hide: bool):
    """Nasconde/mostra i controlli on-face e gli slider del board
    (parita' asFaceHideControllers, MEL 37948): i gruppi *Offset_<L>
    sotto ControlsSetup e i figli diretti di ctrlBox/ctrlBox2."""
    if not cmds.objExists("ControlsSetup"):
        cmds.warning("as_face_hide_controllers: ControlsSetup not found")
        return
    visible = 0 if hide else 1
    for node in cmds.listRelatives("ControlsSetup", allDescendents=True, type="transform") or []:
        short = node.split("|")[-1]
        # gmatch "*Offset_[A-Z]": "...Offset_" + una maiuscola finale
        if (
            len(short) >= 8
            and short[-2] == "_"
            and short[-1].isalpha()
            and short[-1].isupper()
            and short[:-2].endswith("Offset")
        ):
            cmds.setAttr(node + ".v", visible)
    boards = [b for b in ("ctrlBox", "ctrlBox2") if cmds.objExists(b)]
    for child in cmds.listRelatives(boards, children=True, type="transform") or []:
        cmds.setAttr(child + ".v", visible)


def as_show_layer(layer: str):
    """Mostra un layer di deformazione al posto della geometria del viso
    (parita' asShowLayer, MEL:39528). Con "Normal" torna la geometria e
    `DeformationLayers` viene nascosto e bloccato; con un altro nome
    restano visibili (e selezionati) i figli `<layer>Layer*`."""
    if not cmds.objExists("DeformationLayers"):
        return
    geometry = get_fit_option("Face") or ""
    all_geo = (get_fit_option("AllHead") or "").split()
    if geometry and geometry not in all_geo:
        all_geo.append(geometry)
    normal = layer == "Normal"
    for geo in all_geo:
        if cmds.objExists(geo) and not cmds.getAttr(geo + ".v", lock=True):
            cmds.setAttr(geo + ".v", normal)

    layers = cmds.listRelatives("DeformationLayers", children=True) or []
    for node in layers:
        cmds.setAttr(node + ".v", lock=False)
        cmds.setAttr(node + ".v", 0)
    cmds.select(clear=True)
    cmds.setAttr("DeformationLayers.v", lock=False)
    cmds.setAttr("DeformationLayers.v", not normal)
    cmds.setAttr("DeformationLayers.v", lock=normal)
    if not normal:
        for node in layers:
            if node.startswith(layer + "Layer"):
                cmds.setAttr(node + ".v", 1)
                cmds.select(node, add=True)


def as_align(
    obj: str,
    align_to: str,
    translate: bool = True,
    rotate: bool = False,
    joint_orient: bool = False,
    rotate_order: bool = False,
):
    """Allinea un transform a un altro (parita' asAlign, MEL 9992):
    parent temporaneo sotto il target, azzeramento dei canali locali
    richiesti, reparent alla gerarchia originale."""
    parents = cmds.listRelatives(obj, parent=True) or []

    cmds.parent(obj, align_to)
    # il parent puo' aver generato un Xform intermedio
    generated_xform = None
    current_parent = (cmds.listRelatives(obj, parent=True) or [None])[0]
    if current_parent != align_to:
        generated_xform = current_parent
    if translate:
        cmds.xform(obj, objectSpace=True, translation=(0, 0, 0))
        if generated_xform:
            cmds.xform(generated_xform, objectSpace=True, translation=(0, 0, 0))
    if rotate_order:
        cmds.setAttr(obj + ".rotateOrder", cmds.getAttr(align_to + ".rotateOrder"))
    if rotate:
        cmds.xform(obj, objectSpace=True, rotation=(0, 0, 0))
        if generated_xform:
            cmds.xform(generated_xform, objectSpace=True, rotation=(0, 0, 0))
    if joint_orient and rotate:
        cmds.setAttr(obj + ".jointOrient", 0, 0, 0, type="float3")

    if parents and cmds.objExists(parents[0]):
        cmds.parent(obj, parents[0])
    else:
        cmds.parent(obj, world=True)
    if generated_xform:
        cmds.delete(generated_xform)

    if joint_orient and not rotate:
        if cmds.getAttr(align_to + ".rotateOrder") != 0:
            cmds.warning(
                "Aligning jointOrient for objects without "
                "aligning rotation, and non-default "
                "rotationOrder, may cause problems."
            )
        constraint = cmds.orientConstraint(align_to, obj)
        rotation = cmds.xform(obj, query=True, objectSpace=True, rotation=True)
        cmds.delete(constraint[0])
        cmds.setAttr(obj + ".jointOrient", rotation[0], rotation[1], rotation[2], type="float3")
        cmds.setAttr(obj + ".rotate", 0, 0, 0, type="float3")


def as_lock_attr(obj: str, trans: bool, rot: bool, scale: bool, vis: bool):
    """Lock/unlock e keyable dei canali trasformazione (parita'
    asLockAttr, MEL 10057): lock=flag, keyable=!flag per ogni asse."""
    for axis in "XYZ":
        cmds.setAttr("{}.translate{}".format(obj, axis), lock=trans, keyable=not trans)
        cmds.setAttr("{}.rotate{}".format(obj, axis), lock=rot, keyable=not rot)
        cmds.setAttr("{}.scale{}".format(obj, axis), lock=scale, keyable=not scale)
    cmds.setAttr(obj + ".v", lock=vis, keyable=not vis)
    # in caso di unlock, sblocca anche gli attr double3 compound
    if not trans:
        cmds.setAttr(obj + ".translate", lock=False, keyable=False)
    if not rot:
        cmds.setAttr(obj + ".rotate", lock=False, keyable=False)
    if not scale:
        cmds.setAttr(obj + ".scale", lock=False, keyable=False)


def _split_name_side(node: str):
    """Tokenizzazione MEL per i nodi di plumbing: name_side dall'ultimo
    "_"; per i nomi senza "_" il MEL produce side == nome intero
    (quirk preservato: il grafo deve combaciare)."""
    tokens = node.split("_")
    name = tokens[0]
    for part in tokens[1:-1]:
        name += "_" + part
    side = "_" + tokens[-1]
    return name, side


def as_matrix_connect_attr(source_attr: str, dest_attr: str):
    """Connette una matrice a un transform (parita' asMatrixConnectAttr,
    MEL 68183): diretta sull'offsetParentMatrix se il body rig usa
    l'OPM, altrimenti via decomposeMatrix <name>DM<side> sui canali
    t/r/s/shear (naming con substring degli ultimi 2 caratteri, quirk
    MEL preservato)."""
    if as_get_opm():
        cmds.connectAttr(source_attr, dest_attr)
        return
    dest_obj = dest_attr.split(".")[0]
    name, side = dest_obj[:-2], dest_obj[-2:]
    dm = "{}DM{}".format(name, side)
    if cmds.objExists(dm):
        cmds.warning("DM:{} already exists".format(dm))
        return
    cmds.createNode("decomposeMatrix", name=dm)
    cmds.setAttr(dm + ".inputRotateOrder", cmds.getAttr(dest_obj + ".rotateOrder"))
    cmds.connectAttr(source_attr, dm + ".inputMatrix")
    for z, (lower, upper) in enumerate((("x", "X"), ("y", "Y"), ("z", "Z"))):
        cmds.connectAttr("{}.outputTranslate{}".format(dm, upper), "{}.t{}".format(dest_obj, lower))
        cmds.connectAttr("{}.outputRotate{}".format(dm, upper), "{}.r{}".format(dest_obj, lower))
        cmds.connectAttr("{}.outputScale{}".format(dm, upper), "{}.s{}".format(dest_obj, lower))
        shear = ("xy", "xz", "yz")[z]
        cmds.connectAttr("{}.outputShear{}".format(dm, upper), "{}.sh{}".format(dest_obj, shear))


def as_parent_constraint(
    parent: str,
    child: str,
    maintain_offset: bool = False,
    force_mult_matrix: bool = False,
    skip_scale: bool = False,
    include_pick_matrix: bool = False,
):
    """Vincola un nodo a un parent (parita' asParentConstraint,
    MEL 23065).

    Con l'OPM del body (o force_mult_matrix, il flag MEL -FMM) crea la
    catena multMatrix <name>MM<side> (offset opzionale, worldMatrix
    del parent, worldInverseMatrix del padre del child) collegata via
    as_matrix_connect_attr; altrimenti parentConstraint+scaleConstraint
    classici.

    Nota parita': l'azzeramento del transform del child avviene PRIMA
    della connessione (il MEL lo fa dopo, che in modalita' decompose
    fallirebbe sui canali ormai connessi); lo stato finale di scena e'
    lo stesso.
    """
    opm = as_get_opm() or force_mult_matrix
    sel = cmds.ls(selection=True) or []

    if opm:
        name, side = _split_name_side(child)
        mm = "{}MM{}".format(name, side)
        if not cmds.objExists(mm):
            cmds.createNode("multMatrix", name=mm)
        plug_nr = 0

        if maintain_offset:
            temp = cmds.createNode("transform", name="tempMatrixTransform", parent=child)
            temp = cmds.parent(temp, parent)[0]
            matrix = cmds.xform(temp, query=True, objectSpace=True, matrix=True)
            cmds.delete(temp)
            cmds.setAttr("{}.matrixIn[{}]".format(mm, plug_nr), matrix, type="matrix")
            plug_nr += 1

        src = parent + ".worldMatrix[0]"
        dst = "{}.matrixIn[{}]".format(mm, plug_nr)
        if not cmds.isConnected(src, dst):
            cmds.connectAttr(src, dst, force=True)
        plug_nr += 1

        child_parent = (cmds.listRelatives(child, parent=True) or [None])[0]
        if child_parent:
            src = child_parent + ".worldInverseMatrix[0]"
            dst = "{}.matrixIn[{}]".format(mm, plug_nr)
            if not cmds.isConnected(src, dst):
                cmds.connectAttr(src, dst)
            plug_nr += 1

        cmds.xform(
            child, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)
        )
        if cmds.objectType(child) == "joint":
            cmds.setAttr(child + ".jo", 0, 0, 0, type="float3")

        if include_pick_matrix or skip_scale:
            pm = "{}PM{}".format(name, side)
            cmds.createNode("pickMatrix", name=pm)
            cmds.connectAttr(mm + ".matrixSum", pm + ".inputMatrix")
            as_matrix_connect_attr(pm + ".outputMatrix", child + ".offsetParentMatrix")
            if skip_scale:
                cmds.setAttr(pm + ".useScale", 0)
        else:
            as_matrix_connect_attr(mm + ".matrixSum", child + ".offsetParentMatrix")
    else:
        if maintain_offset:
            cmds.parentConstraint(parent, child, maintainOffset=True)
            if not skip_scale:
                cmds.scaleConstraint(parent, child, maintainOffset=True)
        else:
            cmds.parentConstraint(parent, child)
            if not skip_scale:
                cmds.scaleConstraint(parent, child)

    if sel:
        cmds.select(sel)
    else:
        cmds.select(clear=True)


def _insert_mm_plug(mm: str, plug_nr: int):
    """Libera matrixIn[plug_nr] facendo scorrere di uno le connessioni
    successive (parita' asInsertMMPlug con sourcePlug vuoto, MEL:67307)."""
    num_plugs = len(cmds.listConnections(mm, source=True, destination=False) or [])
    source = cmds.listConnections(
        "{}.matrixIn[{}]".format(mm, plug_nr), source=True, destination=False, plugs=True
    )
    if source and "HJO" in source[0]:  # HoldJointOrientMatrix resta dov'e'
        plug_nr += 1
    existing = {}
    for i in range(plug_nr, num_plugs):
        plugs = cmds.listConnections(
            "{}.matrixIn[{}]".format(mm, i), source=True, destination=False, plugs=True
        )
        if plugs:
            existing[i] = plugs[0]
    for i, plug in existing.items():
        cmds.connectAttr(plug, "{}.matrixIn[{}]".format(mm, i + 1), force=True)
    if plug_nr in existing:
        cmds.disconnectAttr(existing[plug_nr], "{}.matrixIn[{}]".format(mm, plug_nr))


def as_opm_scale_reset(joint: str):
    """Annulla la scala che un joint eredita dal multMatrix del suo
    as_parent_constraint (parita' asOPMScaleReset, MEL:37447).

    I controller on-face vivono sotto OnFacecontrols/SideReverse, che sono
    scalati (e specchiati a destra): senza questa correzione il joint
    guidato eredita quella scala. La diagonale di matrixIn[0] diventa la
    scala inversa di SideReverse<side>.
    """
    tokens = joint.split("_")  # tokenize MEL: primi due token
    name, side = tokens[0], "_" + tokens[1]
    if as_get_opm():
        source_plug = joint + ".offsetParentMatrix"
    else:
        source_plug = "{}DM{}.inputMatrix".format(name, side)
    if not cmds.objExists(source_plug):
        cmds.warning('Failed to asOPMScaleReset "{}": {} not found.'.format(joint, source_plug))
        return
    matrix = cmds.getAttr(source_plug)
    if 0.999 < matrix[10] < 1.001:
        return
    mms = cmds.listConnections(source_plug, source=True, destination=False, type="multMatrix")
    if not mms:
        cmds.warning(
            'Failed to asOPMScaleReset "{}" as it is not connected to multMatrix.'.format(joint)
        )
        return
    mm = mms[0]
    inverse = cmds.getAttr("SideReverse{}.worldInverseMatrix".format(side))
    offset = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]
    if cmds.listConnections(mm + ".matrixIn[0]", source=True, destination=False):
        _insert_mm_plug(mm, 0)
    else:
        offset = list(cmds.getAttr(mm + ".matrixIn[0]"))
    offset[0], offset[5], offset[10] = inverse[0], inverse[5], inverse[10]
    cmds.setAttr(mm + ".matrixIn[0]", offset, type="matrix")


def _split_blend_name_side(node: str):
    """Tokenizzazione di asParentConstraintBlend (MEL 67927): name dal
    primo token, side dal SECONDO (non l'ultimo). Per i nomi facciali a
    underscore singolo coincide con _split_name_side."""
    tokens = node.split("_")
    name = tokens[0]
    side = ("_" + tokens[1]) if len(tokens) > 1 else ""
    return name, side


def as_parent_constraint_blend(driver: str, driven: str, target: str):
    """Follow blend pilotato da driver.follow (parita'
    asParentConstraintBlend, MEL 67918).

    Il driven segue il target con un peso 0..1 derivato da
    driver.follow (0..10, *0.1), restando ancorato alla posa statica
    (Main, o l'HeadJoint se non c'e' body rig) quando follow=0. Crea la
    rete blendMatrix <name>BM<side> + multMatrix MMFollow/MMStatic/
    MMRelToParent + il moltiplicatore <driver>FollowMDL<side>; sul ramo
    non-OPM aggiunge il decompose <name>DM<side> verso t/r/s del driven.
    """
    opm = as_get_opm()
    ud_max = 10.0
    name, side = _split_blend_name_side(driven)

    m1 = cmds.xform(driven, query=True, worldSpace=True, matrix=True)
    # m2 = matrice del driven relativa al target (offset al build)
    temp = cmds.createNode("transform", name="tempTransformMatrix", parent=driven)
    temp = cmds.parent(temp, target)[0]
    m2 = cmds.xform(temp, query=True, objectSpace=True, matrix=True)
    cmds.delete(temp)

    bm = "{}BM{}".format(name, side)
    cmds.createNode("blendMatrix", name=bm)
    cmds.setAttr(bm + ".inputMatrix", m1, type="matrix")

    cmds.addAttr(
        driver,
        keyable=True,
        longName="follow",
        attributeType="double",
        minValue=0,
        maxValue=ud_max,
        defaultValue=ud_max,
    )
    mdl = as_create_mult_dl("{}FollowMDL{}".format(driver, side))
    cmds.connectAttr(driver + ".follow", mdl + ".input1")
    cmds.setAttr(mdl + ".input2", 0.1)

    mm_follow = "{}MMFollow{}".format(name, side)
    cmds.createNode("multMatrix", name=mm_follow)
    cmds.setAttr(mm_follow + ".matrixIn[0]", m2, type="matrix")
    cmds.connectAttr(target + ".worldMatrix[0]", mm_follow + ".matrixIn[1]")
    cmds.connectAttr(mm_follow + ".matrixSum", bm + ".target[0].targetMatrix")
    cmds.connectAttr(mdl + ".output", bm + ".target[0].weight")

    # posa statica: offset + scala del Main (o HeadJoint senza body)
    mm_static = "{}MMStatic{}".format(name, side)
    cmds.createNode("multMatrix", name=mm_static)
    if cmds.objExists("Main"):
        cmds.setAttr(mm_static + ".matrixIn[0]", m1, type="matrix")
        cmds.connectAttr("Main.worldMatrix[0]", mm_static + ".matrixIn[1]")
    else:
        cmds.setAttr(
            mm_static + ".matrixIn[0]",
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            type="matrix",
        )
        head_joint = get_fit_option("HeadJoint")
        cmds.connectAttr(head_joint + ".worldMatrix[0]", mm_static + ".matrixIn[1]")
    cmds.connectAttr(mm_static + ".matrixSum", bm + ".inputMatrix")

    mm_rel = "{}MMRelToParent{}".format(name, side)
    cmds.createNode("multMatrix", name=mm_rel)
    cmds.connectAttr(bm + ".outputMatrix", mm_rel + ".matrixIn[0]")
    parent = (cmds.listRelatives(driven, parent=True) or [None])[0]
    cmds.connectAttr(parent + ".worldInverseMatrix", mm_rel + ".matrixIn[1]")

    if opm:
        cmds.connectAttr(mm_rel + ".matrixSum", driven + ".offsetParentMatrix")
        cmds.xform(driven, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0))
    else:
        dm = "{}DM{}".format(name, side)
        cmds.createNode("decomposeMatrix", name=dm)
        cmds.setAttr(dm + ".inputRotateOrder", cmds.getAttr(driven + ".rotateOrder"))
        cmds.connectAttr(mm_rel + ".matrixSum", dm + ".inputMatrix")
        cmds.connectAttr(dm + ".outputTranslate", driven + ".t")
        cmds.connectAttr(dm + ".outputRotate", driven + ".r")
        cmds.connectAttr(dm + ".outputScale", driven + ".s")
