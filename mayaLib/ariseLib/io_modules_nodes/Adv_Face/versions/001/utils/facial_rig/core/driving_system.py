"""Driving system di AdvancedSkeleton (parita' asDsSdk e famiglia).

Il "bus" che collega slider, controlli on-face e deformazione: ogni
attributo guidato riceve un blendWeighted bw<obj>_<attrLungo>
(asEnsureBlendWeighted, MEL 61107) che somma i contributi delle
animCurve SDK<ctrl>_<attr> (asEnsureSDKcurvesNamed, MEL 61222) create
da asDsSdk (MEL 60346) via setDrivenKeyframe. I driver tipo gli slider
del ctrlBox espongono il loro valore con un bw in modalita' "output"
(asEnsureOutputBlendWeighted, MEL 61181): attr -> bw.input[0], cosi'
piu' sistemi possono leggerli senza occupare l'attributo.

Nomi di nodi e topologia del grafo sono il contratto letto da
Selector, FaceCap/ARKit e dal bake: non vanno cambiati.
"""

import maya.cmds as cmds


def _round_off(value: float, decimals: int) -> float:
    """Arrotondamento half-away-from-zero (parita' asRoundOff, MEL 10041)."""
    factor = 10**decimals
    if value >= 0:
        return int(value * factor + 0.5) / float(factor)
    return -(int(abs(value) * factor + 0.5) / float(factor))


def attr_to_attribute(attr: str) -> str:
    """Nome lungo di un canale trasformazione (parita' asAttrToAttribute)."""
    mapping = {
        "tx": "translateX",
        "ty": "translateY",
        "tz": "translateZ",
        "rx": "rotateX",
        "ry": "rotateY",
        "rz": "rotateZ",
        "sx": "scaleX",
        "sy": "scaleY",
        "sz": "scaleZ",
    }
    return mapping.get(attr, attr)


def ctrl_to_bw(obj_attr: str) -> str:
    """Nome del blendWeighted di un attributo (parita' asCtrlToBw):
    bw<obj>_<attrLungo>."""
    obj, attr = obj_attr.split(".", 1)
    return "bw{}_{}".format(obj, attr_to_attribute(attr))


def ensure_blend_weighted(sdk_driven: str, output_mode: bool = False) -> str:
    """Garantisce il blendWeighted di un attributo (parita'
    asEnsureBlendWeighted, MEL 61107).

    Input mode (default): bw.output -> attr, preservando l'eventuale
    connessione esistente come bw.input[0]. Output mode: l'attributo
    alimenta bw.input[0] e resta libero (il nodo e' un "tap" per i
    driver). Il MEL distingue i due casi con il nodo-flag temporaneo
    asEnsureOutputBlendWeighted; qui e' un parametro esplicito.
    """
    tokens = sdk_driven.split(".")
    obj = tokens[0]
    attr = ".".join(tokens[1:])

    # niente bw annidati
    if cmds.nodeType(obj) == "blendWeighted":
        return obj

    attr = attr_to_attribute(attr)

    is_face_control = False
    if cmds.objExists("FaceAllSet") and cmds.sets(obj, isMember="FaceAllSet"):
        is_face_control = True
    if cmds.objExists("FaceBuildingSets"):
        is_face_control = True

    blend_weighted = "bw" + "{}.{}".format(obj, attr).replace(".", "_").replace("[", "_").replace(
        "]", "_"
    )

    if not cmds.objExists(blend_weighted):
        cmds.createNode("blendWeighted", name=blend_weighted)
        if is_face_control and cmds.objExists("FaceAllSet"):
            if cmds.sets(obj, isMember="FaceAllSet"):
                cmds.sets(blend_weighted, add="FaceAllSet")
        if not is_face_control and cmds.objExists("AllSet"):
            if cmds.sets(obj, isMember="AllSet"):
                cmds.sets(blend_weighted, add="AllSet")

        plug = "{}.{}".format(obj, attr)
        if not output_mode:
            # preserva l'input esistente spostandolo sul bw
            existing = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
            if existing:
                cmds.connectAttr(existing[0], blend_weighted + ".input[0]", force=True)
            cmds.connectAttr(blend_weighted + ".output", plug, force=True)
        else:
            cmds.connectAttr(plug, blend_weighted + ".input[0]", force=True)

    # il bw output puo' esistere gia' (DS custom cancellati): riconnetti
    if output_mode and not cmds.isConnected(
        "{}.{}".format(obj, attr), blend_weighted + ".input[0]", ignoreUnitConversion=True
    ):
        cmds.connectAttr("{}.{}".format(obj, attr), blend_weighted + ".input[0]", force=True)
    return blend_weighted


def ensure_output_blend_weighted(sdk_driven: str) -> str:
    """Blend weighted in modalita' output (parita'
    asEnsureOutputBlendWeighted, MEL 61181)."""
    return ensure_blend_weighted(sdk_driven, output_mode=True)


def ensure_sdk_curves_named():
    """Rinomina le animCurve SDK col nome del plug guidato (parita'
    asEnsureSDKcurvesNamed, MEL 61222): per ogni transform *SDK*_*
    sotto |FaceMotionSystem| (o |MotionSystem| del body), le animCurve
    che alimentano i suoi nodi sorgente diventano
    SDK<ctrl>_<attr> e entrano nel set del rig."""
    for sdk_node in cmds.ls("*SDK*_*", type="transform") or []:
        long_name = cmds.ls(sdk_node, long=True)[0]
        if "|FaceMotionSystem|" in long_name:
            is_face_control = True
        elif "|MotionSystem|" in long_name:
            is_face_control = False
        else:
            continue

        for source in (
            cmds.listConnections(sdk_node, source=True, destination=False, skipConversionNodes=True)
            or []
        ):
            for curve in (
                cmds.listConnections(
                    source, source=True, destination=False, skipConversionNodes=True
                )
                or []
            ):
                # il MEL filtra sul NOME (gmatch "animCurve*"): solo le curve
                # appena create da setDrivenKeyframe, ancora col nome di
                # default. Filtrare sul tipo le rinominerebbe a ogni chiamata,
                # facendo crescere il numero in coda al nome.
                if not curve.startswith("animCurve"):
                    continue
                dest_plugs = (
                    cmds.listConnections(
                        source + ".output",
                        source=False,
                        destination=True,
                        plugs=True,
                        skipConversionNodes=True,
                    )
                    or []
                )
                if not dest_plugs:
                    continue
                new_name = dest_plugs[0].replace(".", "_", 1)
                new_name = cmds.rename(curve, new_name)

                if is_face_control and cmds.objExists("FaceAllSet"):
                    if cmds.sets(sdk_node, isMember="FaceAllSet"):
                        cmds.sets(new_name, add="FaceAllSet")
                if not is_face_control and cmds.objExists("AllSet"):
                    if cmds.sets(sdk_node, isMember="AllSet"):
                        cmds.sets(new_name, add="AllSet")


def ds_sdk(driver: str, driven: str, driver_value: float, driven_value: float):
    """Crea un collegamento del driving system (parita' asDsSdk,
    MEL 60346): setDrivenKeyframe lineare (0 -> default,
    driver_value -> driven_value) accodata al blendWeighted del driven,
    con il bw del driver come sorgente se esiste.

    No-op se driven_value coincide col valore di riposo (0, o 1 per le
    scale); driven mancante = warning (consente build parziali).
    """
    start_value = 0.0
    attr_part = driven.split(".")[-1]
    is_scale = attr_part in ("sx", "sy", "sz", "scaleX", "scaleY", "scaleZ")
    if is_scale:
        start_value = 1.0

    driven_value = _round_off(driven_value, 3)
    if driven_value == start_value:
        return
    if not cmds.objExists(driven):
        cmds.warning('Driven object:"{}" not found, skipping.'.format(driven))
        return

    blend_weighted = ensure_blend_weighted(driven)

    # se il driver ha un bw (es. slider del ctrlBox), guida dal bw
    drive_source = driver
    driver_bw = ctrl_to_bw(driver)
    if cmds.objExists(driver_bw):
        drive_source = driver_bw + ".output"

    # se anche il driven ha un bw (e non e' un nodo SDK), guida il bw
    driven_bw = ctrl_to_bw(driven)
    if (
        cmds.objExists(driven_bw)
        and not driven.startswith("SDK")
        and not cmds.objExists("ARKitQuickConnecting")
    ):
        driven = driven_bw + ".input"

    # se il driven e' un bw.input senza indice, prendi il prossimo libero
    if (
        driven.startswith("bw")
        and driven.endswith(".input")
        and cmds.objectType(driven.split(".")[0]) == "blendWeighted"
    ):
        cmds.dgeval(driven)
        driven += "[{}]".format(cmds.getAttr(driven, size=True))

    # scale concatenate: dal secondo driver in poi il contributo a
    # riposo deve essere 0 (non 1), o le scale si sommerebbero
    if is_scale:
        bw_inputs = (
            cmds.listConnections(
                blend_weighted + ".input", source=True, destination=False, skipConversionNodes=True
            )
            or []
        )
        if bw_inputs:
            first_sources = cmds.listConnections(
                bw_inputs[0], source=True, destination=False, skipConversionNodes=True
            ) or [None]
            if first_sources[0] != driver_bw:
                start_value -= 1
                driven_value -= 1

    before_curves = set(
        cmds.listConnections(
            blend_weighted + ".input",
            source=True,
            destination=False,
            skipConversionNodes=True,
            type="animCurve",
        )
        or []
    )
    cmds.setDrivenKeyframe(
        driven,
        currentDriver=drive_source,
        inTangentType="linear",
        outTangentType="linear",
        driverValue=0,
        value=start_value,
    )
    cmds.setDrivenKeyframe(
        driven,
        currentDriver=drive_source,
        inTangentType="linear",
        outTangentType="linear",
        driverValue=driver_value,
        value=driven_value,
    )

    ensure_sdk_curves_named()
    after_curves = (
        cmds.listConnections(
            blend_weighted + ".input",
            source=True,
            destination=False,
            skipConversionNodes=True,
            type="animCurve",
        )
        or []
    )
    for curve in after_curves:
        if curve in before_curves:
            continue
        cmds.setAttr(curve + ".preInfinity", 4)
        cmds.setAttr(curve + ".postInfinity", 4)


def unit_convert_and_reverse(name, driver):
    """Catena unitConversion(0.1) + reverse (parita' asUnitConvertAndReverse,
    MEL AdvancedSkeleton.mel:67335).

    Crea `<name>UnitConversion` (conversionFactor 0.1, driver -> .input) e
    `<name>Reverse` (<name>UnitConversion.output -> .inputX).
    """
    uc = cmds.createNode("unitConversion", name=name + "UnitConversion")
    cmds.setAttr(uc + ".conversionFactor", 0.1)
    cmds.connectAttr(driver, uc + ".input")
    rev = cmds.createNode("reverse", name=name + "Reverse")
    cmds.connectAttr(uc + ".output", rev + ".inputX")


def mirror_connect_ctrls(connect: bool):
    """Collega (o scollega) gli attributi keyable dei ctrl on-face _R
    ai gemelli _L (parita' asFaceMirrorConnectCtrls, MEL 37538): usato
    durante l'animate-fit per lavorare in simmetria."""
    if not cmds.objExists("OnFacecontrols"):
        cmds.warning("OnFacecontrols not found (face rig not built)")
        return
    for node in cmds.listRelatives("OnFacecontrols", allDescendents=True, type="transform") or []:
        if not node.endswith("Offset_R"):
            continue
        ctrl = node.replace("Offset", "", 1)
        left_ctrl = ctrl.replace("_R", "_L", 1)
        for attr in cmds.listAttr(ctrl, keyable=True) or []:
            if not cmds.attributeQuery(attr, node=left_ctrl, exists=True):
                continue
            source = "{}.{}".format(ctrl, attr)
            destination = "{}.{}".format(left_ctrl, attr)
            if connect:
                if not cmds.isConnected(source, destination):
                    cmds.connectAttr(source, destination)
            elif cmds.isConnected(source, destination):
                cmds.disconnectAttr(source, destination)


def store_as_ds_sdk(
    ctrls, ctrls_side: str, drive_obj: str, drive_side: str, drive_attr: str, drive_value: float
):
    """Converte i fit-anim di una lista di ctrl in reti SDK (parita'
    asFaceStoreAsDsSdk, MEL 37685).

    Per ogni ctrl crea (al frame 30) il transform <base>Values_R/M che
    fotografa la posa target, poi per ogni attributo con fit-anim
    collega il driver all'SDK group (o al bw dell'attributo custom)
    via ds_sdk.

    Args:
        ctrls: nomi base dei ctrl (senza suffisso lato).
        ctrls_side: "_RL" per le coppie laterali, "_M" per i middle.
        drive_obj: nome base del driver (es. "ctrlCheek").
        drive_side: "_RL" (driver per lato) o "_M" (driver centrale).
        drive_attr: attributo del driver (es. "ty").
        drive_value: valore del driver alla posa target.
    """
    auto_key = cmds.autoKeyframe(query=True, state=True)
    if auto_key:
        cmds.autoKeyframe(state=False)
    skip_ctrl = set()
    for base in ctrls:
        cmds.currentTime(30)
        # i transform Values fotografano la posa del frame 30
        for b in (1, -1):
            side = "_R" if b == 1 else "_L"
            if ctrls_side == "_M":
                side = "_M"
            if ctrls_side == "_M" and drive_side == "_M" and b == -1:
                continue
            valu_obj = base + ("Values_M" if side == "_M" else "Values_R")
            ctrl = base + side
            if not cmds.objExists(ctrl):
                print('// control:"{}" not found. skipping.'.format(ctrl))
                skip_ctrl.add(base)
            if not cmds.objExists(valu_obj) and base not in skip_ctrl:
                cmds.createNode("transform", name=valu_obj, parent=ctrl)
                cmds.parent(valu_obj, cmds.listRelatives(ctrl, parent=True)[0])

        cmds.currentTime(0)
        if base in skip_ctrl:
            continue

        driven_values = {}
        attr_have_fit_anim = {}
        for b in (1, -1):
            side = "_R" if b == 1 else "_L"
            if ctrls_side == "_M" and drive_side == "_M" and b == -1:
                continue
            if ctrls_side == "_M":
                ctrl = base + "_M"
                valu_obj = base + "Values_M"
            else:
                ctrl = base + side
                valu_obj = base + "Values_R"
            cmds.delete(ctrl, staticChannels=True)
            if drive_side == "_RL":
                drive_obj_side = drive_obj + side
            else:
                drive_obj_side = drive_obj + "_M"
            in_loop_drive_value = drive_value

            for attr in cmds.listAttr(ctrl, keyable=True) or []:
                if b == 1:
                    if cmds.attributeQuery(attr, node=valu_obj, exists=True):
                        driven_values[attr] = cmds.getAttr("{}.{}".format(valu_obj, attr))
                    else:  # attributo custom: niente nodo SDK
                        driven_values[attr] = cmds.getAttr("{}.{}".format(ctrl, attr), time=30)
                    attr_have_fit_anim[attr] = bool(
                        cmds.listConnections(
                            "{}.{}".format(ctrl, attr),
                            source=True,
                            destination=False,
                            type="animCurve",
                        )
                    )
                if not attr_have_fit_anim.get(attr):
                    continue

                driven_value = driven_values[attr]
                # un driver laterale che guida un ctrl di mezzeria
                # specchia i canali laterali (es. cornerLip -> LipRegion)
                if ctrls_side == "_M" and side == "_L":
                    if attr in ("translateX", "rotateY", "rotateZ"):
                        driven_value *= -1

                # caso speciale ctrlLips_M.tx
                if (
                    drive_obj == "ctrlLips"
                    and drive_side == "_M"
                    and drive_attr == "tx"
                    and side == "_L"
                ):
                    in_loop_drive_value = 1

                if attr.startswith("scale"):
                    cmds.setAttr("{}.{}".format(ctrl, attr), 1)
                else:
                    cmds.setAttr("{}.{}".format(ctrl, attr), 0)

                # ctrlMouthCorner separa la guida X dalla Y per un
                # joystick piu' intuitivo (tranne ctrlMouth_M.ty)
                if (
                    drive_obj.startswith("ctrlMouth")
                    and "{}_M.{}".format(drive_obj, drive_attr) != "ctrlMouth_M.ty"
                ):
                    if drive_attr == "tx" and attr in ("translateY", "rotateZ"):
                        continue
                    if drive_attr == "ty" and attr not in ("translateY", "rotateZ"):
                        continue

                driver_plug = "{}.{}".format(drive_obj_side, drive_attr)
                if not cmds.attributeQuery(attr, node=valu_obj, exists=True):
                    # attributo custom: si accoda al suo bw, se esiste
                    bw = "bw{}_{}".format(ctrl, attr)
                    if cmds.objExists(bw):
                        ds_sdk(driver_plug, bw + ".input", in_loop_drive_value, driven_value)
                else:
                    ds_sdk(
                        driver_plug,
                        "SDK{}.{}".format(ctrl, attr),
                        in_loop_drive_value,
                        driven_value,
                    )
    if auto_key:
        cmds.autoKeyframe(state=True)


def face_ds_finish(drive_obj: str, drive_side: str, drive_attr: str, drive_value: float):
    """Converte tutti i fit-anim dei ctrl on-face in reti SDK e rimuove
    le anim di preview (parita' asFaceDsFinish, MEL 37654). E' la
    chiusura standard di ogni step di build basato su animate-fit."""
    if not cmds.objExists("OnFacecontrols"):
        cmds.warning("OnFacecontrols not found (face rig not built)")
        return
    driven_side = []
    driven_middle = []
    for shape in cmds.listRelatives("OnFacecontrols", allDescendents=True, type="nurbsCurve") or []:
        ctrl = (cmds.listRelatives(shape, parent=True) or [""])[0]
        if not cmds.listConnections(ctrl, source=True, destination=False, type="animCurve"):
            continue
        if ctrl.endswith("_L"):
            continue
        if ctrl.endswith("_R"):
            driven_side.append(ctrl[:-2])
        else:
            driven_middle.append(ctrl[:-2])

    if driven_side:
        store_as_ds_sdk(driven_side, "_RL", drive_obj, drive_side, drive_attr, drive_value)
    if driven_middle:
        store_as_ds_sdk(driven_middle, "_M", drive_obj, drive_side, drive_attr, drive_value)

    from .fitting import remove_fit_animations_from_on_face_ctrls

    remove_fit_animations_from_on_face_ctrls()
