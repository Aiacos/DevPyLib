"""Build step RebuildRestore (parita' asFaceRebuildRestore
MEL:37060-37366).

Ultimo step, attivo solo su un rebuild: il Prep ha rinominato il rig
precedente in `prefix_*` (sotto `prefix_FaceGroup`) e qui se ne recupera cio'
che l'utente aveva personalizzato, prima di cancellarlo:

- attributi aggiunti a mano sui controller;
- pesi dello skinCluster del viso (da `prefix_asFaceSkinWeightsHolder`);
- driving system modificati (quelli segnati `<ctrl>_<attr>_tweaked` su
  `FaceSetupEditHistory`);
- collegamenti delle corrective shape;
- forma e colore delle curve dei controller;
- orientamenti personalizzati dei controller (`<Name>CustomOrient<side>`).

Le checkbox "Keep ..." della UI MEL sono parametri della funzione, con gli
stessi default (tutto attivo).

Divergenze (docs/gap-analysis.md §5r):
- "keep HeadSquash" richiama asAdvancedSquash / asOptimizeSquash, che
  appartengono al rig del corpo e non sono portate: warning;
- dopo aver ripristinato un CustomOrient il MEL chiama
  asFaceAttachControllers (MEL:38911), non portata: warning;
- "keep BlendShapes" nel MEL e' un ciclo vuoto ("to be connected.."):
  omesso;
- un controller del vecchio rig senza corrispondente nel nuovo viene
  saltato (il MEL andrebbe in errore su addAttr).
"""

import re

import maya.cmds as cmds

from .driving_system import ensure_blend_weighted, ensure_output_blend_weighted
from .fit_options import get_fit_option

_PREFIX = "prefix_"
_HISTORY = "FaceSetupEditHistory"
_SKIP_TYPES = ("string", "message")


def _unprefixed(name):
    return name.replace(_PREFIX, "", 1)


def _restore_user_attributes():
    """Attributi utente dei controller del vecchio rig che il nuovo non ha
    (MEL:37089-37140). Ognuno e' segnato come "tweaked" sullo storico."""
    for old in cmds.sets(_PREFIX + "FaceControlSet", query=True) or []:
        new = _unprefixed(old)
        if not cmds.objExists(new):
            continue
        for attr in cmds.listAttr(old, userDefined=True) or []:
            plug = "{}.{}".format(old, attr)
            attr_type = cmds.getAttr(plug, type=True)
            if attr_type == "float":
                attr_type = "double"
            if attr_type.endswith("Array") or attr_type in _SKIP_TYPES:
                continue
            if re.search(r"W[0-9]$", attr):  # pesi dei constraint
                continue
            if cmds.attributeQuery(attr, node=new, exists=True):
                continue
            short = cmds.listAttr(plug, shortNames=True)[0]
            flags = {
                "keyable": cmds.getAttr(plug, keyable=True),
                "shortName": short,
                "longName": attr,
                "attributeType": attr_type,
                "defaultValue": cmds.getAttr(plug),
            }
            if cmds.attributeQuery(attr, node=old, rangeExists=True):
                low, high = cmds.attributeQuery(attr, node=old, range=True)
                flags.update(hasMinValue=True, minValue=low, hasMaxValue=True, maxValue=high)
            if cmds.attributeQuery(attr, node=old, softRangeExists=True):
                low, high = cmds.attributeQuery(attr, node=old, softRange=True)
                flags.update(
                    softMinValue=low, hasSoftMinValue=True, softMaxValue=high, hasSoftMaxValue=True
                )
            if attr_type == "enum":
                flags["enumName"] = cmds.addAttr(plug, query=True, enumName=True)
            try:
                cmds.addAttr(new, **flags)
            except RuntimeError as exc:
                cmds.warning("face_rebuild_restore: {}.{} not restored ({})".format(new, attr, exc))
                continue
            history = _PREFIX + _HISTORY
            if not cmds.objExists(history):
                cmds.createNode("transform", name=history, parent=_PREFIX + "ControlsSetup")
            tweaked = "{}_{}_tweaked".format(new, short)
            if not cmds.attributeQuery(tweaked, node=history, exists=True):
                cmds.addAttr(
                    history, keyable=False, defaultValue=1, longName=tweaked, attributeType="bool"
                )

    history = _PREFIX + _HISTORY
    if cmds.objExists(history):
        cmds.parent(history, "ControlsSetup")
        cmds.rename(history, _HISTORY)
        if cmds.objExists(_PREFIX + "FaceAllSet"):
            cmds.sets(_HISTORY, remove=_PREFIX + "FaceAllSet")
        cmds.sets(_HISTORY, add="FaceAllSet")


def _restore_driving_curve(old_curve, in_bw):
    """Riporta nel nuovo rig una animCurve SDK del vecchio (MEL:37176-37212)."""
    if not old_curve.startswith(_PREFIX):  # aggiunta dopo il build: non era in FaceAllSet
        old_curve = cmds.rename(old_curve, _PREFIX + old_curve)
    curve = _unprefixed(old_curve)
    if cmds.objExists(curve):
        cmds.nodeCast(old_curve, curve, swapNames=True)
        return
    targets = cmds.listConnections(
        old_curve + ".output", source=False, destination=True, type="blendWeighted"
    )
    out_bw = _unprefixed(targets[0]) if targets else ""
    cmds.duplicate(old_curve, name=curve)
    if cmds.objExists(_PREFIX + "FaceAllSet"):
        cmds.sets(curve, remove=_PREFIX + "FaceAllSet")
    cmds.connectAttr(in_bw + ".output", curve + ".input")
    if not out_bw or not cmds.objExists(out_bw):
        # anche quando fra curva e blendWeighted c'e' un unitConversion (le
        # rotazioni): la ricerca diretta qui sopra non lo attraversa
        tokens = curve.split("_")
        ensure_blend_weighted(
            "{}_{}.{}".format(
                tokens[0].replace("bw", "", 1), tokens[1], tokens[2].rstrip("0123456789")
            )
        )
    dest = cmds.listConnections(
        old_curve + ".output", source=False, destination=True, skipConversionNodes=True
    )
    dest_bw = _unprefixed(dest[0]) if dest else ""
    if not dest_bw or not cmds.objExists(dest_bw):
        cmds.warning("face_rebuild_restore: no target found, {} not restored".format(curve))
        return
    index = cmds.getAttr(dest_bw + ".input", size=True)
    cmds.connectAttr(curve + ".output", "{}.input[{}]".format(dest_bw, index), force=True)


def _restore_driving_systems():
    """Driving system modificati dall'utente (segnati sullo storico): le
    loro animCurve tornano quelle del vecchio rig (MEL:37150-37215)."""
    if not cmds.objExists(_HISTORY):
        return
    for tweaked in cmds.listAttr(_HISTORY, userDefined=True, string="*_tweaked") or []:
        tokens = tweaked.split("_")
        driver, attr = tokens[0] + "_" + tokens[1], tokens[2]
        old_driver = _PREFIX + driver
        if not cmds.objExists(old_driver) or not cmds.attributeQuery(
            attr, node=old_driver, exists=True
        ):
            continue
        count = 0
        old_bws = cmds.listConnections(
            "{}.{}".format(old_driver, attr), source=False, destination=True, type="blendWeighted"
        )
        for old_bw in old_bws or []:
            in_bw = _unprefixed(old_bw)
            if not cmds.objExists(in_bw):
                if not cmds.objExists("{}.{}".format(driver, attr)):
                    continue
                ensure_output_blend_weighted("{}.{}".format(driver, attr))
            curves = cmds.listConnections(old_bw, source=False, destination=True, type="animCurve")
            for old_curve in curves or []:
                _restore_driving_curve(old_curve, in_bw)
                count += 1
        print("// Restoring edited DrivingSystem:{}, ({} sdk-animCurves.)".format(tweaked, count))


def _restore_corrective_shapes(geometry):
    """Ricollega le corrective shape al nuovo rig (MEL:37249-37280)."""
    nodes = cmds.ls("*Corrective*", recursive=True, type="blendShape") or []
    if nodes:
        print("// Restoring Corrective Shapes.")
    for node in nodes:
        if cmds.objExists("asFaceBS") and cmds.objExists("FaceCorrective"):
            index = len(cmds.listAttr("asFaceBS.w", multi=True) or [])
            cmds.blendShape("asFaceBS", edit=True, target=(geometry, index, "FaceCorrective", 1))
            cmds.setAttr("asFaceBS.FaceCorrective", 1)
        # gli SDK guidati dai controller prefix_ passano a quelli nuovi
        for sdk in (
            cmds.listConnections(node, source=True, destination=False, type="animCurve") or []
        ):
            flags = {"source": True, "destination": False, "connections": True, "type": "transform"}
            pairs = cmds.listConnections(sdk, plugs=True, **flags) or []
            for dest_plug, driver_plug in zip(pairs[0::2], pairs[1::2]):
                if not driver_plug.startswith(_PREFIX):
                    continue
                new_plug = _unprefixed(driver_plug)
                if cmds.objExists(new_plug):
                    cmds.connectAttr(new_plug, dest_plug, force=True)


def _restore_curve_shapes(controls):
    """Forma (CV) e colore delle curve dei controller (MEL:37283-37316)."""
    print("// Restoring control shapes and colors.")
    old_version = cmds.getAttr(_PREFIX + "FaceGroup.version")
    for ctrl in controls:
        if not cmds.objExists(ctrl):
            continue
        for shape in cmds.listRelatives(ctrl, shapes=True) or []:
            old_shape = _PREFIX + shape
            if not cmds.objExists(old_shape) or len(cmds.ls(shape)) != 1:
                continue
            if cmds.objectType(shape) != "nurbsCurve" or cmds.objectType(old_shape) != "nurbsCurve":
                continue
            # prima della 5.764 iride e pupilla erano orientate diversamente
            if old_version < 5.764 and re.match(r"(Iris|Pupil)_.*Shape$", shape):
                continue
            count = cmds.getAttr(old_shape + ".spans") + cmds.getAttr(old_shape + ".degree")
            try:
                for i in range(count):
                    pos = cmds.getAttr("{}.controlPoints[{}]".format(old_shape, i))[0]
                    cmds.setAttr("{}.controlPoints[{}]".format(shape, i), *pos)
                cmds.setAttr(shape + ".overrideColor", cmds.getAttr(old_shape + ".overrideColor"))
            except RuntimeError as exc:
                cmds.warning("face_rebuild_restore: {} shape not restored ({})".format(shape, exc))


def _restore_custom_orients(controls):
    """Gruppi `<Name>CustomOrient<side>` inseriti dall'utente sopra un
    controller (MEL:37319-37346)."""
    restored = False
    for ctrl in controls:
        if not cmds.objExists(ctrl) or not cmds.objExists(_PREFIX + ctrl):
            continue
        if not cmds.listRelatives(ctrl, shapes=True) or "_" not in ctrl:
            continue
        name, side = ctrl.split("_")[0], "_" + ctrl.split("_")[1]
        orient = name + "CustomOrient" + side
        old_orient = _PREFIX + orient
        if not cmds.objExists(old_orient):
            continue
        cmds.createNode("transform", name=orient, parent=old_orient)
        parent = _unprefixed(cmds.listRelatives(old_orient, parent=True)[0])
        children = cmds.listRelatives(parent, children=True, type="transform") or []
        cmds.parent(orient, parent)
        if children:
            cmds.parent(children, orient, relative=True)
        restored = True
    if restored:
        print("// Restoring custom control orientations.")
        cmds.warning(
            "face_rebuild_restore: custom orientations restored, but asFaceAttachControllers "
            "is not ported: re-attach the controllers from the AdvancedSkeleton UI"
        )


def face_rebuild_restore(
    keep_all=True,
    keep_skin_weights=True,
    keep_head_squash=True,
    keep_corrective_shapes=True,
    keep_driving_systems=True,
    keep_curve_shapes=True,
    keep_custom_orient=True,
) -> bool:
    """Recupera dal rig precedente (`prefix_*`) le personalizzazioni
    dell'utente e poi lo cancella (asFaceRebuildRestore). Senza
    `prefix_FaceGroup` (primo build) non fa nulla.

    Gli argomenti sono le checkbox "Keep ..." della UI MEL; come li',
    `keep_all` attiva tutto tranne i pesi, che seguono `keep_skin_weights`.
    """
    if not cmds.objExists(_PREFIX + "FaceGroup"):
        return True
    if not cmds.objExists("FaceControlSet") or not cmds.objExists("FaceAllSet"):
        cmds.warning("face_rebuild_restore: FaceControlSet / FaceAllSet not found")
        return False
    geometry = get_fit_option("Face") or ""
    controls = cmds.sets("FaceControlSet", query=True) or []

    if cmds.objExists(_PREFIX + "FaceControlSet"):
        _restore_user_attributes()

    if keep_skin_weights and cmds.objExists(_PREFIX + "asFaceSkinWeightsHolder"):
        print("// Restoring SkinWeights.")
        cmds.select(_PREFIX + "asFaceSkinWeightsHolder", geometry)
        cmds.copySkinWeights(
            noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
        )
    if keep_all or keep_driving_systems:
        _restore_driving_systems()
    if (keep_all or keep_head_squash) and cmds.objExists(_PREFIX + "SquashSetup"):
        cmds.warning(
            "face_rebuild_restore: the head squash is not restored (asAdvancedSquash is not "
            "ported): rebuild it from the AdvancedSkeleton UI"
        )
    if keep_all or keep_corrective_shapes:
        _restore_corrective_shapes(geometry)
    if keep_all or keep_curve_shapes:
        _restore_curve_shapes(controls)
    if keep_all or keep_custom_orient:
        _restore_custom_orients(controls)

    # il vecchio rig non serve piu'
    if cmds.objExists(_PREFIX + "FaceAllSet"):
        members = [
            m for m in cmds.sets(_PREFIX + "FaceAllSet", query=True) or [] if cmds.objExists(m)
        ]
        if members:
            cmds.delete(members)
    if cmds.objExists(_PREFIX + "FaceGroup"):
        cmds.delete(_PREFIX + "FaceGroup")
    cmds.select(clear=True)
    print("// Advanced Face Rebuild complete.")
    return True
