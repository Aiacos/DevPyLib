"""WrinkleMap: rughe del viso come bump map pilotata dai controlli (frame
" WrinkleMap" del pannello Face, MEL AdvancedSkeleton.mel 2043-2120).

Port di:
- asWrinkleCurves              (MEL 44758-45146) -> wrinkle_curves
- asWrinkleMap                 (MEL 45148-45390) -> wrinkle_map
- asWmBake                     (MEL 45392-45787) -> wm_bake
- asWmEdit                     (MEL 45789-45862) -> wm_edit
- asWmEditApply                (MEL 45864-45884) -> wm_edit_apply
- asWmEditCancel               (MEL 45886-45905) -> wm_edit_cancel
- asWmImagePath                (MEL 45907-45912) -> wm_image_path
- asWmLongestExistingImagePath (MEL 45914-45932) -> wm_longest_existing_image_path
- asWmSetFolder                (MEL 45934-45948) -> wm_set_folder
- asWmOpenFolder               (MEL 45950-45960) -> wm_open_folder
- asWmEnsureWrinkleMapNode     (MEL 45962-45992) -> wm_ensure_wrinkle_map_node
- asWmSettings                 (MEL 45994-46008) -> wm_settings
- asWmView                     (MEL 46010-46043) -> wm_view
- asWmUVUpdate                 (MEL 46045-46250) -> wm_uv_update
- asWmAddAttrs                 (MEL 46252-46256) -> wm_add_attrs
- helper: asGoToBuildPose (MEL 12172-12397, solo il ramo faceSetup),
  asVersionRequirementCheck (MEL 58560-58580), asGetCurveNumCvs (MEL
  51669-51680), asobjSetCast (MEL 38248-38269), asInvertSelection (MEL
  67304-67326, ramo vtx), asGetImConvertCmd (MEL 46813-46821),
  asNrToLetter (MEL 66934). asWmLayout (MEL 60463) e' UI: non portata.

I textField della UI (asFaceFaceTextField, asFaceHeadJointTextField) si
leggono dalle opzioni omonime di FaceFitSkeleton (fit_options). Le finestre
di conferma e di scelta diventano argomenti, il cui default e' il bottone
di default del MEL ("OK").

Divergenze intenzionali (da riportare in docs/gap-analysis.md):
- prerequisiti mancanti ed errori danno cmds.warning + False invece
  dell'errore MEL a meta' procedura; wrinkle_curves, wrinkle_map e wm_bake
  rimuovono i nodi creati se falliscono a meta';
- le stringhe di comandi salvate in scena non passano mai da eval:
  faceBuildPose.udAttr/udExtraAttr si interpretano solo come
  "setAttr <plug> <numero>" (gli altri comandi danno un warning, e il
  FaceFitSkeleton.run e il ramo MetaHuman/ruote di asGoToBuildPose non si
  eseguono); WrinkleMap.shaderRestoreCmd si interpreta solo come
  "sets -e -forceElement <SG> <oggetto>";
- le curve si creano con cmds.curve passando i float, non con eval di una
  stringa: niente arrotondamento a 6 cifre della conversione MEL;
- il nodo bump2dWrinkle si crea e collega a mano (file.outAlpha ->
  bumpValue, outNormal -> shader.normalCamera) invece che con
  defaultNavigation -ce, che in batch collega il file direttamente a
  normalCamera;
- in asWrinkleMap la variabile $existingBumpMapConnectedNode non viene mai
  valorizzata, quindi il "Layered BumpMap" annunciato dal dialogo non
  viene mai costruito: qui e' lo stesso (il bump esistente resta
  scollegato da normalCamera), senza il codice morto;
- wm_uv_update non usa texLatticeDeformContext (un tool della UI, assente
  in batch) per misurare gli UV fra mento e fronte: ne calcola il
  bounding box in V con polyEvaluate. Non verificato contro il valore di
  texLattice1.boundingBoxSup/Inf in Maya con interfaccia;
- wm_uv_update interroga e seleziona gli UV in blocco invece che uno per
  volta, e salta il polyEditUV quando non c'e' nulla da scalare (il MEL
  andrebbe in errore); doBakeNonDefHistory diventa bakePartialHistory;
- lo shader duplicato per gli oggetti che non sono il viso prende il nome
  che hyperShade -duplicate gli da' davvero (il MEL lo presume uguale a
  quello di un duplicate di prova);
- imconvert/magick si lancia con subprocess senza shell (percorsi con
  spazi funzionanti) e dal bin di Maya se presente; l'eseguibile "magick"
  si cerca li' come nel MEL;
- niente progressBar, niente waitCursor, niente abilitazione del
  rowLayout Apply/Cancel; l'HUD "Editing WrinkleMap" si salta in batch;
- wm_view: il ripiego via Node Editor per quando soloMaterial fallisce
  (in batch succede su bump2dWrinkle) si tenta solo con l'interfaccia, e
  senza stringhe MEL differite (callable Python);
- asWmLongestExistingImagePath perde la "/" iniziale dei percorsi posix:
  qui viene conservata;
- le variabili MEL calcolate e mai usate (posizione dell'HeadJoint in
  asWmBake, FitEyeBall e maxScale in asWrinkleCurves) non si calcolano.

Comportamenti del MEL conservati benche' sospetti (vedi report del port):
- wm_uv_update fuori dal build rinomina il nuovo nodo di proiezione
  "polyProjFaceWrinkles" quando quel nome e' gia' preso dal nodo del viso,
  e imposta projectionHorizontalSweep sul nome letterale (quindi sul nodo
  vecchio);
- wm_uv_update fuori dal build lascia uvFaceWrinkles come UV set corrente
  del viso;
- in asWrinkleMap il valore del driver destro ($driverRightValue) e' uno
  solo: a sinistra i due driver di ForeHead/SmileLine usano l'ultimo;
- nei rig solo BlendShapes (RigType 1) ForeHead e SmileLine hanno due
  sezioni e un solo driver: il MEL va in errore su connectAttr, qui
  wrinkle_map ritorna False;
- FaceWrinkleSet e FaceWrinkleRenderingSet si riempiono con select per
  nome, che espande i set nei loro membri: gli shading group creati dal
  bake (*WrinkleDepthShaderSG, *WrinkleMaskShaderSG) non entrano nei set
  e restano in scena, vuoti, a ogni bake e dopo la rimozione;
- l'UV set uvFaceWrinkles resta sul viso dopo la rimozione delle rughe;
- i vertici "sopra il mento" e "sopra la fronte" si scelgono con
  polySelectConstraint sulla distanza dal piano Y=0, che e' senza segno:
  il viso deve stare sopra l'origine.
"""

import os
import random
import re
import subprocess

import maya.cmds as cmds

from .build_utils import as_align, as_create_mult_dl, as_lock_attr
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import face_fit_reselect

WRINKLE_GROUPS = ("ForeHead", "Frown", "CrowsFeet", "BunnyLines", "SmileLine")
WM_ELEMENTS = ("Curves", "Mask", "Test")
WM_VIEW_LAYERS = ("Normal", "Bump", "BumpFile", "Masks")

_WRINKLE_MAP = "WrinkleMap"
_CURVES = "WrinkleCurves"
_DRIVERS = "WrinkleDrivers"
_RENDERING = "WrinkleRendering"
_WRINKLE_SET = "FaceWrinkleSet"
_RENDERING_SET = "FaceWrinkleRenderingSet"
_BUILDING = "asWrinkleMapBuilding"
_RECURSING = "WmEditRecursing"
_UV_SET = "uvFaceWrinkles"
_UV_CHOOSER = "uvChooserFaceWrinkles"
_BUMP_FILE = "fileFaceWrinkles"
_BUMP = "bump2dWrinkle"
_MASKS = "WrinkleMasksLayeredTexture"
_PROJECTION = "polyProjFaceWrinkles"
_TEMP_LOC = "tempLoc"
_HUD = "HUDEDSMode"
_MIN_FACE_VERSION = 5.75  # asVersionRequirementCheck face 5.750 (MEL 44768)
_CTRL = 4  # bit di getModifiers per Ctrl: tiene WrinkleRendering in scena

_OUT_UV_ATTRS = ("outUv", "outVertexUvOne", "outVertexUvTwo", "outVertexUvThree", "outVertexCameraOne")  # fmt: skip
_IN_UV_ATTRS = ("uvCoord", "vertexUvOne", "vertexUvTwo", "vertexUvThree", "vertexCameraOne")

# nodi che asWrinkleCurves legge senza controllarli
_CURVE_NODES = (
    "EyeBrowInner_R",
    "EyeBrowOuter_R",
    "EyeBrowCenter_M",
    "ForeHeadAreaMesh",
    "upperEyeLidMainCurve",
    "lowerEyeLidMainCurve",
    "innerLid_R",
    "innerLid_L",
    "Nose_M",
    "NoseCorner_R",
    "Lip_R",
    "Cheek_R",
)

_ERRORS = (RuntimeError, ValueError, TypeError)


# ---------------------------------------------------------------- helper


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _exists_attr(node, attr):
    return cmds.objExists(node) and cmds.attributeQuery(attr, node=node, exists=True)


def _children(node, transforms_only=False):
    if not cmds.objExists(node):
        return []
    if transforms_only:
        return cmds.listRelatives(node, children=True, type="transform") or []
    return cmds.listRelatives(node, children=True) or []


def _group_name(group_node):
    """ForeHeadWrinkles -> ForeHead (substitute "Wrinkles" "", MEL 45239)."""
    return group_node.replace("Wrinkles", "", 1)


def _wrinkle_groups():
    return [_group_name(node) for node in _children(_CURVES)]


def _wrinkle_curves_list():
    """Le curve di tutti i gruppi, nell'ordine dei gruppi (MEL 45105-45111)."""
    curves = []
    for group in _children(_CURVES):
        curves.extend(_children(group, transforms_only=True))
    return curves


def _curve_num_cvs(curve):
    """asGetCurveNumCvs (MEL 51669-51680)."""
    spans = cmds.getAttr(curve + ".spans")
    if cmds.getAttr(curve + ".form") == 2:
        return spans
    return spans + cmds.getAttr(curve + ".degree")


def _modifiers():
    try:
        return int(cmds.getModifiers() or 0)
    except _ERRORS:
        return 0


def _face_geometry():
    """(geometry, mesh): l'opzione Face e la sua shape non intermedia."""
    geometry = get_fit_option("Face") or ""
    if not geometry or not cmds.objExists(geometry):
        raise RuntimeError('Face geometry "{}" not found'.format(geometry))
    shapes = cmds.listRelatives(geometry, shapes=True, noIntermediate=True) or []
    if not shapes:
        raise RuntimeError('Face geometry "{}" has no shape'.format(geometry))
    return geometry, shapes[0]


def _new_nodes(uuids_before):
    new_uuids = [
        uuid for uuid in cmds.ls(cmds.ls(long=True), uuid=True) if uuid not in uuids_before
    ]
    return cmds.ls(new_uuids, long=True) if new_uuids else []


def _delete_new_nodes(uuids_before):
    for node in _new_nodes(uuids_before):
        if cmds.objExists(node):
            try:
                cmds.delete(node)
            except _ERRORS:
                pass


def _delete_existing(nodes):
    for node in nodes:
        if cmds.objExists(node):
            cmds.delete(node)


def _hud_remove():
    try:
        if cmds.headsUpDisplay(_HUD, query=True, exists=True):
            cmds.headsUpDisplay(_HUD, remove=True)
    except _ERRORS:
        pass


def _hud_show(wrinkle, element):
    """HUD "Editing WrinkleMap" (MEL 45805-45808); in batch non esiste."""
    _hud_remove()
    if cmds.about(batch=True):
        return
    try:
        cmds.headsUpDisplay(
            _HUD,
            section=2,
            block=0,
            blockSize="medium",
            label="Editing WrinkleMap:  {}  ({})".format(wrinkle, element),
            labelFontSize="large",
        )
        cmds.displayColor("headsUpDisplayLabels", 16)
    except _ERRORS:
        pass


def _go_to_build_pose():
    """asGoToBuildPose faceSetup (MEL 12172-12242): riporta i controlli del
    viso alla posa di build eseguendo i comandi di faceBuildPose.udAttr (e
    udExtraAttr). Solo "setAttr <plug> <numero>": il resto non si esegue
    (mai eval di stringhe di scena) e viene segnalato."""
    if not _exists_attr("faceBuildPose", "udAttr"):
        raise RuntimeError("faceBuildPose.udAttr not found, build the face first")
    commands = cmds.getAttr("faceBuildPose.udAttr") or ""
    if _exists_attr("faceBuildPose", "udExtraAttr"):
        commands += cmds.getAttr("faceBuildPose.udExtraAttr") or ""
    skip_main = (_modifiers() // _CTRL) % 2
    for command in commands.split(";"):
        tokens = command.split()
        if not tokens:
            continue
        if skip_main and "Main." in command:
            continue
        try:
            if len(tokens) != 3 or tokens[0] != "setAttr":
                raise ValueError("unsupported command")
            cmds.setAttr(tokens[1], float(tokens[2]))
        except _ERRORS:
            cmds.warning("Failed: " + command)


def _run_shader_restore(commands):
    """Esegue WrinkleMap.shaderRestoreCmd (MEL 44799-44800), che
    asWrinkleCurves compone come "sets -e -forceElement <SG> <oggetto>;"."""
    for command in (commands or "").split(";"):
        tokens = command.split()
        if not tokens:
            continue
        if len(tokens) == 5 and tokens[:3] == ["sets", "-e", "-forceElement"]:
            if cmds.objExists(tokens[3]) and cmds.objExists(tokens[4]):
                cmds.sets(tokens[4], edit=True, forceElement=tokens[3])
                continue
        cmds.warning("Failed: " + command)


def _select_as_uvs():
    """ConvertSelectionToUVs sulla selezione corrente. Ritorna gli UV."""
    selection = cmds.ls(selection=True)
    uvs = cmds.polyListComponentConversion(selection, toUV=True) if selection else []
    if uvs:
        cmds.select(uvs)
    else:
        cmds.select(clear=True)
    return uvs


def _cast_components(components, dest_obj):
    """asobjSetCast (MEL 38248-38269): gli stessi componenti su dest_obj."""
    return [dest_obj + component[component.index(".") :] for component in components]


# ------------------------------------------------------- nodo e cartelle


def wm_ensure_wrinkle_map_node():
    """Crea il nodo WrinkleMap sotto FaceGroup se manca (parita'
    asWmEnsureWrinkleMapNode, MEL 45962-45992): attributi imagePath
    (<workspace>/<images>/WrinkleMaps/<scena>), shader, shaderRestoreCmd,
    duplicatedSG, mapWidth/mapHeight (1024), maskWidth/maskHeight (512),
    format (png:tga), modifier. Ritorna bool."""
    if cmds.objExists(_WRINKLE_MAP):
        return True
    head_joint = get_fit_option("HeadJoint") or ""
    if not head_joint or not cmds.objExists(head_joint):
        cmds.warning('wm_ensure_wrinkle_map_node: head joint "{}" not found'.format(head_joint))
        return False
    if not cmds.objExists("FaceGroup"):
        cmds.warning("wm_ensure_wrinkle_map_node: FaceGroup not found, build the face first")
        return False
    selection = cmds.ls(selection=True) or []
    head_joint_pos = _ws(head_joint)
    images_path = "{}/{}".format(
        cmds.workspace(query=True, active=True),
        cmds.workspace(fileRuleEntry="images"),
    )
    scene_name = cmds.file(query=True, sceneName=True) or ""
    basename = os.path.splitext(os.path.basename(scene_name))[0] or "Untitled"

    cmds.createNode("transform", name=_WRINKLE_MAP, parent="FaceGroup")
    as_lock_attr(_WRINKLE_MAP, True, True, True, False)
    cmds.addAttr(_WRINKLE_MAP, longName="imagePath", dataType="string")
    cmds.setAttr(
        _WRINKLE_MAP + ".imagePath",
        "{}/WrinkleMaps/{}".format(images_path, basename),
        type="string",
    )
    for attr in ("shader", "shaderRestoreCmd", "duplicatedSG"):
        cmds.addAttr(_WRINKLE_MAP, longName=attr, dataType="string")
    # come nel MEL: i canali sono gia' bloccati ma xform passa lo stesso
    cmds.xform(_WRINKLE_MAP, worldSpace=True, translation=head_joint_pos)
    for attr, default in (
        ("mapWidth", 1024),
        ("mapHeight", 1024),
        ("maskWidth", 512),
        ("maskHeight", 512),
    ):
        cmds.addAttr(
            _WRINKLE_MAP, keyable=True, longName=attr, attributeType="long", defaultValue=default
        )
    cmds.addAttr(
        _WRINKLE_MAP, keyable=True, longName="format", attributeType="enum", enumName="png:tga"
    )
    cmds.addAttr(
        _WRINKLE_MAP, keyable=False, longName="modifier", attributeType="long", defaultValue=0
    )
    if selection:
        cmds.select(selection)
    else:
        cmds.select(clear=True)
    return True


def wm_add_attrs(wrinkle, depth, width):
    """Attributi depth e width di una curva-ruga (parita' asWmAddAttrs, MEL
    46252-46256). Ritorna bool."""
    if not wrinkle or not cmds.objExists(wrinkle):
        cmds.warning('wm_add_attrs: "{}" not found'.format(wrinkle))
        return False
    values = (("depth", depth), ("width", width))
    for attr, _value in values:
        if cmds.attributeQuery(attr, node=wrinkle, exists=True):
            cmds.warning("wm_add_attrs: {}.{} already exists".format(wrinkle, attr))
            return False
    for attr, value in values:
        cmds.addAttr(
            wrinkle, keyable=True, longName=attr, attributeType="double", defaultValue=value
        )
    return True


def wm_image_path():
    """La cartella delle mappe, WrinkleMap.imagePath (parita' asWmImagePath,
    MEL 45907-45912); crea il nodo WrinkleMap se manca. "" se non si puo'."""
    if not wm_ensure_wrinkle_map_node():
        return ""
    return cmds.getAttr(_WRINKLE_MAP + ".imagePath") or ""


def wm_longest_existing_image_path():
    """La parte piu' lunga di wm_image_path() che esiste su disco (parita'
    asWmLongestExistingImagePath, MEL 45914-45932). "" se nessuna."""
    image_path = wm_image_path()
    tokens = [token for token in image_path.split("/") if token]
    if not tokens:
        return ""
    test_path = ("/" if image_path.startswith("/") else "") + tokens[0]
    longest = ""
    for index in range(1, len(tokens) + 1):
        if not os.path.exists(test_path):
            break
        longest = test_path
        if index < len(tokens):
            test_path += "/" + tokens[index]
    return longest


def wm_set_folder(folder):
    """Cambia la cartella delle mappe (parita' asWmSetFolder, MEL
    45934-45948; `folder` e' il risultato del fileDialog2). Le mappe si
    rigenerano li' al prossimo wm_edit_apply. Ritorna bool."""
    if not folder:
        return False
    if not wm_ensure_wrinkle_map_node():
        return False
    cmds.setAttr(_WRINKLE_MAP + ".imagePath", folder, type="string")
    print('// run "Apply", to re-create the maps at this new folder.')
    print("// Changed Folder to : {} ".format(folder))
    return True


def wm_open_folder():
    """Apre la cartella delle mappe (o il suo antenato piu' vicino che
    esiste) nel file manager (parita' asWmOpenFolder, MEL 45950-45960).
    Come nel MEL, solo su Windows e macOS. Ritorna bool."""
    image_path = wm_image_path()
    longest = wm_longest_existing_image_path()
    if not image_path or not longest:
        cmds.warning('wm_open_folder: no existing folder in "{}"'.format(image_path))
        return False
    print("// Opening : " + image_path)
    if cmds.about(windows=True):
        command = ["explorer", longest.replace("/", "\\")]
    elif cmds.about(macOS=True):
        command = ["open", longest]
    else:
        cmds.warning("wm_open_folder: not supported on this platform")
        return False
    try:
        subprocess.Popen(command)
    except OSError as exc:
        cmds.warning("wm_open_folder: failed: {}".format(exc))
        return False
    return True


def wm_settings():
    """Seleziona il nodo WrinkleMap, i cui attributi sono le impostazioni
    delle mappe (parita' asWmSettings, MEL 45994-46008). Ritorna bool."""
    if not wm_ensure_wrinkle_map_node():
        return False
    cmds.select(_WRINKLE_MAP)
    if _children(_CURVES):
        print('// Change attributes to change settings and run "Apply", to re-create the maps.')
    else:
        print("// Change attributes to change settings.")
    return True


# ------------------------------------------------------------------ view


def wm_view(layer):
    """Isola nel viewport un nodo della rete delle rughe (parita' asWmView,
    MEL 46010-46043): "Bump" bump2dWrinkle, "BumpFile" fileFaceWrinkles,
    "Masks" WrinkleMasksLayeredTexture; "Normal" toglie l'isolamento.
    Ritorna bool."""
    if layer not in WM_VIEW_LAYERS:
        cmds.warning('wm_view: unknown layer "{}"'.format(layer))
        return False
    if layer == "Normal":
        try:
            cmds.soloMaterial(unsolo=True)
        except _ERRORS as exc:
            cmds.warning("wm_view: failed: {}".format(exc))
            return False
        return True
    if not cmds.objExists(_CURVES):
        cmds.warning('wm_view: WrinkleCurves not found, you must run "Create WrinkleMap" first.')
        return False
    solo_node = {"Bump": _BUMP, "Masks": _MASKS, "BumpFile": _BUMP_FILE}[layer]
    if not cmds.objExists(solo_node):
        cmds.warning('wm_view: {} not found, you must run "Wrinkle Map" first.'.format(solo_node))
        return False
    try:
        cmds.soloMaterial(node=solo_node)
        return True
    except _ERRORS as exc:
        if cmds.about(batch=True):
            cmds.warning("wm_view: failed: {}".format(exc))
            return False
    # ripiego del MEL (46032-46040): aprire il Node Editor sblocca
    # soloMaterial, che viene ripetuto a finestra chiusa
    try:
        cmds.NodeEditorWindow()
        for window in cmds.lsUI(type="window") or []:
            if re.fullmatch(r"nodeEditor.*Window", window):
                cmds.evalDeferred(lambda window=window: cmds.deleteUI(window))
                cmds.evalDeferred(lambda: cmds.soloMaterial(node=solo_node), lowestPriority=True)
                break
    except _ERRORS as exc:
        cmds.warning("wm_view: failed: {}".format(exc))
        return False
    return True


# ------------------------------------------------------------------ edit


def _wm_edit(wrinkle, element):
    groups = _wrinkle_groups()
    building = cmds.objExists(_BUILDING)
    if element == "Curves" and not building:
        _hud_show(wrinkle, element)
    if element != "Mask" and not cmds.objExists(_RECURSING):
        _go_to_build_pose()

    if wrinkle == "All":
        cmds.createNode("transform", name=_RECURSING)
        try:
            cmds.select(clear=True)
            for group in groups:
                _wm_edit(group, element)
        finally:
            if cmds.objExists(_RECURSING):
                cmds.delete(_RECURSING)
        return
    recursing = cmds.objExists(_RECURSING)
    if not recursing:
        cmds.select(clear=True)

    group_node = wrinkle + "Wrinkles"
    if element == "Curves":
        # scala che stacca le curve dalla pelle e le rende editabili
        cmds.setAttr(_CURVES + ".s", 1.015, 1, 1.015, type="float3")
        if not recursing:
            for group in groups:
                cmds.setAttr(group + "Wrinkles.v", 0)
        cmds.setAttr(group_node + ".v", 1)
        cmds.select(_children(group_node, transforms_only=True), add=True)
    elif element == "Mask":
        cmds.select(group_node, add=True)
    elif element == "Test":
        if not cmds.attributeQuery("driver", node=group_node, exists=True):
            raise RuntimeError(
                'WrinkleCurve-driver not found, you must run "Create WrinkleMap" first.'
            )
        driver = cmds.getAttr(group_node + ".driver") or ""
        value = 1 if re.search(r"\.t[xy]", driver) else 10
        if driver == "ctrlMouthCorner_R.txPos_tyPos":
            cmds.setAttr("ctrlMouthCorner_R.tx", 1)
            cmds.setAttr("ctrlMouthCorner_R.ty", 1)
        else:
            cmds.setAttr(driver, value)
    if not building:
        print('// Editing wrinkle: "{}"'.format(wrinkle))


def wm_edit(wrinkle, element):
    """Mette in modifica una ruga (parita' asWmEdit, MEL 45789-45862).

    Args:
        wrinkle: "ForeHead", "Frown", "CrowsFeet", "BunnyLines",
            "SmileLine" oppure "All".
        element: "Curves" mostra e seleziona le curve del gruppo (e scala
            WrinkleCurves a 1.015 per staccarle dalla pelle); "Mask"
            seleziona il gruppo, i cui attributi multiply/offset/start
            regolano la maschera; "Test" porta il driver della ruga al
            valore di prova (serve wrinkle_map).

    Dopo "Curves" si chiude con wm_edit_apply o wm_edit_cancel. Ritorna
    bool."""
    if not cmds.objExists(_CURVES):
        cmds.warning('wm_edit: WrinkleCurves not found, you must run "Create WrinkleMap" first.')
        return False
    if element not in WM_ELEMENTS:
        cmds.warning('wm_edit: unknown element "{}"'.format(element))
        return False
    if wrinkle != "All" and wrinkle not in _wrinkle_groups():
        cmds.warning('wm_edit: unknown wrinkle "{}"'.format(wrinkle))
        return False
    try:
        _wm_edit(wrinkle, element)
    except _ERRORS as exc:
        cmds.warning("wm_edit: failed: {}".format(exc))
        return False
    return True


def _hide_curves_and_reset_scale():
    for group in _children(_CURVES):
        cmds.setAttr(group + ".v", 0)
    if cmds.objExists(_CURVES):
        cmds.setAttr(_CURVES + ".s", 1, 1, 1, type="float3")


def wm_edit_apply(modifier=None):
    """Chiude la modifica rigenerando le mappe (parita' asWmEditApply, MEL
    45864-45884): posa di build, curve nascoste e riportate a scala 1,
    wm_bake. `modifier` e' il valore di getModifiers (None = lo legge): con
    Ctrl (4) i nodi di rendering restano in scena. Ritorna bool."""
    if not cmds.objExists(_CURVES) or not cmds.objExists(_WRINKLE_MAP):
        cmds.warning(
            'wm_edit_apply: WrinkleCurves not found, you must run "Create WrinkleMap" first.'
        )
        return False
    _hud_remove()
    try:
        _go_to_build_pose()
        _hide_curves_and_reset_scale()
        cmds.refresh()
        cmds.setAttr(
            _WRINKLE_MAP + ".modifier", _modifiers() if modifier is None else int(modifier)
        )
    except _ERRORS as exc:
        cmds.warning("wm_edit_apply: failed: {}".format(exc))
        return False
    if not wm_bake():
        return False
    cmds.select(clear=True)
    print("// Applied wrinkle edit.")
    return True


def wm_edit_cancel():
    """Chiude la modifica senza rigenerare le mappe (parita'
    asWmEditCancel, MEL 45886-45905): posa di build, curve nascoste e
    riportate a scala 1. Ritorna bool."""
    _hud_remove()
    try:
        _go_to_build_pose()
        _hide_curves_and_reset_scale()
    except _ERRORS as exc:
        cmds.warning("wm_edit_cancel: failed: {}".format(exc))
        return False
    if not cmds.objExists(_BUILDING):
        print("// Cancelled wrinkle edit.")
    return True


# -------------------------------------------------------- wrinkle curves


def _version_too_old():
    """asVersionRequirementCheck face 5.750 (MEL 58560-58580)."""
    return (
        _exists_attr("FaceGroup", "version")
        and cmds.getAttr("FaceGroup.version") < _MIN_FACE_VERSION
    )


def _remove_wrinkles():
    """Rimuove tutto il setup delle rughe (MEL 44782-44803)."""
    restore = ""
    if _exists_attr(_WRINKLE_MAP, "shaderRestoreCmd"):
        restore = cmds.getAttr(_WRINKLE_MAP + ".shaderRestoreCmd") or ""
    members = []
    for wrinkle_set in (_WRINKLE_SET, _RENDERING_SET):
        if cmds.objExists(wrinkle_set):
            members += cmds.sets(wrinkle_set, query=True) or []
    _delete_existing(members)
    for attr in cmds.listAttr("ctrlBox", userDefined=True) or []:
        if attr.startswith("wrinkle"):
            cmds.deleteAttr("ctrlBox." + attr)
    if cmds.objExists(_WRINKLE_MAP):
        cmds.delete(_WRINKLE_MAP)
    _go_to_build_pose()
    _run_shader_restore(restore)


def _face_shader(mesh, shader):
    """(shader, shadingEngine) del viso (MEL 44810-44841). Con piu' shader
    assegnati per faccia si usa `shader`, o il primo come il menu del MEL."""
    engines = cmds.listConnections(
        mesh + ".instObjGroups[0]", source=False, destination=True, type="shadingEngine"
    )
    if engines:
        engine = engines[0]
        shaders = cmds.listConnections(engine + ".surfaceShader", source=True, destination=False)
        return (shaders or [""])[0], engine
    engines = (
        cmds.listConnections(
            mesh + ".instObjGroups[0].objectGroups",
            source=True,
            destination=False,
            type="shadingEngine",
        )
        or []
    )
    if not engines:
        return "", ""
    if len(engines) == 1:
        shaders = cmds.listConnections(
            engines[0] + ".surfaceShader", source=True, destination=False
        )
        return (shaders or [""])[0], engines[0]
    if not shader:
        shaders = cmds.listConnections(
            engines[0] + ".surfaceShader", source=True, destination=False
        )
        shader = (shaders or [""])[0]
    if not shader or not cmds.objExists(shader + ".outColor"):
        return "", ""
    engines = cmds.listConnections(shader + ".outColor", source=False, destination=True) or [""]
    return shader, engines[0]


def _duplicate_shader_for_others(engine, members, geometry):
    """Gli altri oggetti che usano lo shader del viso passano a una copia
    (MEL 44863-44889), cosi' il bump delle rughe resta solo sul viso."""
    engines_before = set(cmds.ls(type="shadingEngine"))
    cmds.select(engine, noExpand=True)
    probe = cmds.duplicate()
    duplicated = probe[0]
    cmds.delete(probe)
    cmds.select(engine, noExpand=True)
    cmds.hyperShade(duplicate=True)
    created = [node for node in cmds.ls(type="shadingEngine") if node not in engines_before]
    if not created:
        raise RuntimeError("failed to duplicate the face shader")
    if duplicated not in created:
        duplicated = created[0]
    cmds.setAttr(_WRINKLE_MAP + ".duplicatedSG", duplicated, type="string")
    restore = ""
    for member in members:
        if member == geometry:
            continue
        shapes = cmds.listRelatives(member, noIntermediate=True, shapes=True) or []
        connections = (
            cmds.listConnections(
                shapes[0], connections=True, plugs=True, source=False, destination=True
            )
            if shapes
            else []
        ) or []
        for source, destination in zip(connections[0::2], connections[1::2]):
            if destination.startswith(engine):
                cmds.disconnectAttr(source, destination)
        cmds.sets(member, edit=True, forceElement=duplicated)
        restore += "sets -e -forceElement {} {};".format(engine, member)
    cmds.setAttr(_WRINKLE_MAP + ".shaderRestoreCmd", restore, type="string")


def _snap(mesh, node=_TEMP_LOC):
    cmds.delete(cmds.geometryConstraint(mesh, node))


def _named_curve(points, name, parent):
    curve = cmds.curve(degree=1, point=[tuple(point) for point in points])
    cmds.rename(curve, name)
    if parent:
        cmds.parent(name, parent)


def _forehead_bounds():
    """Bounding box di ForeHeadAreaMesh, che va reso visibile per leggerlo
    (MEL 44915-44919)."""
    visible = cmds.getAttr("ForeHeadAreaMesh.v")
    if not visible:
        cmds.setAttr("ForeHeadAreaMesh.v", 1)
    bb_min = cmds.getAttr("ForeHeadAreaMesh.boundingBoxMin")[0]
    bb_max = cmds.getAttr("ForeHeadAreaMesh.boundingBoxMax")[0]
    if not visible:
        cmds.setAttr("ForeHeadAreaMesh.v", 0)
    return bb_min, bb_max


def _forehead_curves(bb_max):
    """ForeHeadWrinkle1..4 (MEL 44921-44981). Ritorna offsetDist."""
    cmds.createNode("transform", name="ForeHeadWrinkles", parent=_CURVES)
    pos_a = _ws("EyeBrowInner_R")
    pos_b = _ws("EyeBrowOuter_R")
    pos_c = _ws("EyeBrowCenter_M")
    cmds.xform(
        _TEMP_LOC, worldSpace=True, translation=(pos_c[0], (pos_c[1] + bb_max[1]) / 2.0, pos_c[2])
    )
    _snap("ForeHeadAreaMesh")
    cmds.spaceLocator(name="tempLoc2")
    cmds.pointConstraint(_TEMP_LOC, "EyeBrowCenter_M", "tempLoc2")
    pos = _ws("tempLoc2")
    cmds.delete("tempLoc2")
    points = [pos]
    offset_dist = pos[1] - pos_c[1]
    points.append((pos_a[0], pos_a[1] + offset_dist, pos_a[2]))

    for i in (1, 2):
        mid = "EyeBrowMid{}_R".format(i)
        if not cmds.objExists(mid):
            continue
        cmds.xform(_TEMP_LOC, worldSpace=True, translation=_ws(mid))
        _snap("ForeHeadAreaMesh")
        cmds.move(0, offset_dist, 0, _TEMP_LOC, relative=True)
        _snap("ForeHeadAreaMesh")
        points.append(_ws(_TEMP_LOC))

    cmds.xform(_TEMP_LOC, worldSpace=True, translation=pos_b)
    cmds.move(offset_dist * -1, offset_dist * 0.5, offset_dist * -1, _TEMP_LOC, relative=True)
    _snap("ForeHeadAreaMesh")
    points.append(_ws(_TEMP_LOC))
    _named_curve(points, "ForeHeadWrinkle1", "ForeHeadWrinkles")
    wm_add_attrs("ForeHeadWrinkle1", 10, 10)

    for i, (width, depth) in enumerate(((20, 10), (15, 5), (10, 7), (5, 1)), 1):
        curve = "ForeHeadWrinkle{}".format(i)
        if i != 1:
            cmds.duplicate("ForeHeadWrinkle1", name=curve)
            cmds.move(0, offset_dist * 0.70 * (i - 1), 0, curve + ".cv[0:99]", relative=True)
        cmds.setAttr(curve + ".depth", depth)
        cmds.setAttr(curve + ".width", width)
    return offset_dist


def _frown_curves(offset_dist):
    """FrownWrinkle1 (MEL 44983-44995)."""
    cmds.createNode("transform", name="FrownWrinkles", parent=_CURVES)
    pos_a = _ws("EyeBrowInner_R")
    pos_b = _ws("ForeHeadWrinkle1.cv[0]")
    points = [
        (pos_a[0] / 2.8, pos_b[1] - (offset_dist * 0.70), pos_a[2]),
        (pos_a[0] / 2.5, pos_b[1] - (offset_dist * 1.7), pos_a[2]),
        (pos_a[0] / 1.0, pos_b[1] - (offset_dist * 2.2), pos_a[2]),
    ]
    _named_curve(points, "FrownWrinkle1", "FrownWrinkles")
    wm_add_attrs("FrownWrinkle1", 7, 12)


def _crows_feet_curves(mesh, scale, bb_min):
    """CrowsFeetWrinkle1..3 dall'angolo esterno dell'occhio (MEL
    44997-45030)."""
    cmds.createNode("transform", name="CrowsFeetWrinkles", parent=_CURVES)
    num_cv = _curve_num_cvs("upperEyeLidMainCurve")
    pos_a = _ws("upperEyeLidMainCurve.cv[{}]".format(num_cv - 1))
    pos_b = (bb_min[0], pos_a[1], bb_min[2])
    cmds.xform(
        _TEMP_LOC,
        worldSpace=True,
        translation=[(pos_a[axis] + pos_b[axis]) / 2.0 for axis in range(3)],
    )
    _snap(mesh)
    pos_b = _ws(_TEMP_LOC)
    _named_curve([pos_a, pos_b], "CrowsFeetWrinkle2", "CrowsFeetWrinkles")
    wm_add_attrs("CrowsFeetWrinkle2", 6, 6)

    pos_a = _ws("upperEyeLidMainCurve.cv[{}]".format(num_cv - 2))
    _named_curve(
        [pos_a, (pos_b[0], pos_b[1] + (scale / 20.0), pos_b[2])],
        "CrowsFeetWrinkle1",
        "CrowsFeetWrinkles",
    )
    wm_add_attrs("CrowsFeetWrinkle1", 4, 4)

    num_cv = _curve_num_cvs("lowerEyeLidMainCurve")
    pos_a = _ws("lowerEyeLidMainCurve.cv[{}]".format(num_cv - 2))
    _named_curve(
        [pos_a, (pos_b[0], pos_b[1] - (scale / 20.0), pos_b[2])],
        "CrowsFeetWrinkle3",
        "CrowsFeetWrinkles",
    )
    wm_add_attrs("CrowsFeetWrinkle3", 4, 4)


def _bunny_lines_curves(scale):
    """BunnyLinesWrinkle1..3 sul dorso del naso (MEL 45032-45072)."""
    cmds.createNode("transform", name="BunnyLinesWrinkles", parent=_CURVES)
    pos_a = _ws("innerLid_R")
    cmds.xform(_TEMP_LOC, worldSpace=True, translation=(0, pos_a[1], pos_a[2]))
    constraint = cmds.pointConstraint(
        "innerLid_R", "innerLid_L", "Nose_M", "NoseCorner_R", _TEMP_LOC
    )[0]
    cmds.setAttr(constraint + ".NoseCorner_RW3", 0)
    cmds.setAttr(constraint + ".Nose_MW2", 0.5)
    cmds.setAttr(constraint + ".innerLid_LW1", 0.5)
    _named_curve([pos_a, _ws(_TEMP_LOC)], "BunnyLinesWrinkle1", "")

    cmds.setAttr(constraint + ".NoseCorner_RW3", 1)
    cmds.setAttr(constraint + ".Nose_MW2", 1)
    cmds.setAttr(constraint + ".innerLid_LW1", 0)
    _named_curve(
        [(pos_a[0], pos_a[1] - (scale / 80.0), pos_a[2]), _ws(_TEMP_LOC)],
        "BunnyLinesWrinkle3",
        "",
    )
    cmds.delete(constraint)

    # la 2 e' a meta' fra la 1 e la 3
    cmds.duplicate("BunnyLinesWrinkle3", name="BunnyLinesWrinkle2")
    cmds.blendShape(
        "BunnyLinesWrinkle1",
        "BunnyLinesWrinkle2",
        name="tempBs",
        frontOfChain=True,
        weight=(0, 0.5),
    )
    cmds.delete("BunnyLinesWrinkle2", constructionHistory=True)
    cmds.reorder("BunnyLinesWrinkle2", relative=-1)

    for i in (1, 2, 3):
        curve = "BunnyLinesWrinkle{}".format(i)
        cmds.reverseCurve(curve, constructionHistory=False, replaceOriginal=True)
        cmds.parent(curve, "BunnyLinesWrinkles")
    wm_add_attrs("BunnyLinesWrinkle1", 1, 1)
    wm_add_attrs("BunnyLinesWrinkle2", 3, 3)
    wm_add_attrs("BunnyLinesWrinkle3", 3, 3)


def _smile_line_curves(mesh, scale):
    """SmileLineWrinkle1 dal naso all'angolo della bocca (MEL 45076-45096).
    Come nel MEL, il pointConstraint su Lip_R/Cheek_R resta su tempLoc
    fino alla sua cancellazione."""
    cmds.createNode("transform", name="SmileLineWrinkles", parent=_CURVES)
    constraint = cmds.pointConstraint("NoseCorner_R", _TEMP_LOC, weight=0.5)[0]
    cmds.pointConstraint("innerLid_R", _TEMP_LOC, weight=0.25)
    cmds.pointConstraint("Nose_M", _TEMP_LOC, weight=0.25)
    cmds.delete(constraint)
    _snap(mesh)
    points = [_ws(_TEMP_LOC)]
    cmds.pointConstraint("Lip_R", _TEMP_LOC, weight=0.7)
    cmds.pointConstraint("Cheek_R", _TEMP_LOC, weight=0.3)
    _snap(mesh)
    pos = _ws(_TEMP_LOC)
    points.append((pos[0], pos[1] + (scale / 20.0), pos[2]))
    points.append((pos[0], pos[1] - (scale / 20.0), pos[2]))
    pos = _ws("Lip_R")
    points.append((pos[0], pos[1] - (scale / 10.0), pos[2]))
    _named_curve(points, "SmileLineWrinkle1", "SmileLineWrinkles")
    wm_add_attrs("SmileLineWrinkle1", 10, 10)


def _stick_curves_to_face(mesh):
    """Ricostruisce le curve a 6 CV e le appoggia sul viso, tenendole sul
    lato destro (MEL 45103-45140)."""
    for curve in _wrinkle_curves_list():
        cmds.rebuildCurve(
            curve,
            constructionHistory=False,
            replaceOriginal=True,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=False,
            keepEndPoints=False,
            keepTangents=False,
            spans=3,
            degree=3,
            tolerance=0.00155,
        )
        crossing_x_axis = False
        for index in range(6):
            cv = "{}.cv[{}]".format(curve, index)
            cmds.xform(_TEMP_LOC, worldSpace=True, translation=_ws(cv))
            _snap(mesh)
            pos = _ws(_TEMP_LOC)
            if pos[0] > 0:  # non oltre l'asse X
                crossing_x_axis = True
                cmds.xform(_TEMP_LOC, worldSpace=True, translation=(0, pos[1], pos[2]))
                _snap(mesh)
                pos = _ws(_TEMP_LOC)
            if index == 1 and crossing_x_axis:  # niente spigolo fra destra e sinistra
                pos_a = _ws(curve + ".cv[0]")
                cmds.xform(_TEMP_LOC, worldSpace=True, translation=(pos[0], pos_a[1], pos[2]))
                _snap(mesh)
                pos = _ws(_TEMP_LOC)
            cmds.xform(cv, worldSpace=True, translation=pos)


def _create_wrinkle_curves(mesh, scale):
    cmds.spaceLocator(name=_TEMP_LOC)
    if not cmds.objExists(_CURVES):
        cmds.createNode("transform", name=_CURVES, parent=_WRINKLE_MAP)
    bb_min, bb_max = _forehead_bounds()
    offset_dist = _forehead_curves(bb_max)
    _frown_curves(offset_dist)
    _crows_feet_curves(mesh, scale, bb_min)
    _bunny_lines_curves(scale)
    _smile_line_curves(mesh, scale)
    for group in _children(_CURVES):
        cmds.setAttr(group + ".v", 0)
    _stick_curves_to_face(mesh)
    cmds.delete(_TEMP_LOC)
    _wm_edit("All", "Curves")
    _hud_remove()


def wrinkle_curves(
    remove_existing=True, shader=None, duplicate_shared_shader=True, layer_existing_bump=True
):
    """Crea le curve-ruga di partenza (parita' asWrinkleCurves, MEL
    44758-45146): il nodo WrinkleMap con WrinkleCurves e i gruppi
    ForeHead/Frown/CrowsFeet/BunnyLines/SmileLineWrinkles, le cui curve (6
    CV, attributi depth e width) sono appoggiate sul lato destro del viso
    e lasciate in modifica (wm_edit "All" "Curves"). Se le rughe esistono
    gia', le rimuove tutte (curve, mappe, attributi sul ctrlBox) e
    ripristina gli shader.

    Args:
        remove_existing: risposta al dialogo "Wrinkles already exists,
            this will delete the existing Wrinkle setup".
        shader: lo shader da usare quando il viso ne ha piu' d'uno
            assegnato per faccia (dialogo asWmLayout); None = il primo.
        duplicate_shared_shader: risposta al dialogo "Multiple objects are
            using the face-shader": gli altri oggetti passano a una copia.
        layer_existing_bump: risposta al dialogo "Existing BumpMap exists
            for the Shader".

    Ritorna bool; False anche quando una risposta e' "Cancel"."""
    if not _exists_attr(FIT_SKELETON, "faceScale"):
        cmds.warning("wrinkle_curves: FaceFitSkeleton.faceScale not found, build the face first")
        return False
    if _version_too_old():
        cmds.warning(
            "wrinkle_curves: AdvancedSkeleton face-rig version older then v5.750 detected, "
            'You must first run "ReBuild AdvancedFace", before you can use this function'
        )
        return False
    if not cmds.objExists("ctrlBox") or not _exists_attr("faceBuildPose", "udAttr"):
        cmds.warning("wrinkle_curves: ctrlBox or faceBuildPose not found, build the face first")
        return False
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    if not wm_ensure_wrinkle_map_node():
        return False

    if _children(_CURVES):
        if not remove_existing:
            return False
        try:
            _remove_wrinkles()
        except _ERRORS as exc:
            cmds.warning("wrinkle_curves: failed to remove the wrinkles: {}".format(exc))
            return False
        print("// Wrinkles removed")
        return True

    try:
        geometry, mesh = _face_geometry()
    except RuntimeError as exc:
        cmds.warning("wrinkle_curves: {}".format(exc))
        return False
    for node in _CURVE_NODES:
        if not cmds.objExists(node):
            cmds.warning("wrinkle_curves: {} not found, build the face first".format(node))
            return False
    if cmds.objExists(_TEMP_LOC) or cmds.objExists("tempLoc2"):
        cmds.warning("wrinkle_curves: delete the leftover tempLoc/tempLoc2 nodes first")
        return False

    face_shader, engine = _face_shader(mesh, shader)
    if not face_shader or not engine:
        cmds.warning('wrinkle_curves: no shader found on "{}"'.format(geometry))
        return False
    if not cmds.attributeQuery("normalCamera", node=face_shader, exists=True):
        cmds.warning(
            'wrinkle_curves: No "normalCamera" attribute found on shader:"{}", therefore '
            "unable to apply bumpMap to the shader".format(face_shader)
        )
        return False
    if engine == "initialShadingGroup":
        cmds.warning(
            "wrinkle_curves: initialShadingGroup used as shader, unable to proceed, "
            "please make a new shader for the face first"
        )
        return False
    members = []
    for member in (
        cmds.listConnections(engine + ".dagSetMembers", source=True, destination=False) or []
    ):
        if member not in members:
            members.append(member)
    if len(members) > 1 and not duplicate_shared_shader:
        return False
    existing_bump = [
        node
        for node in cmds.listConnections(
            face_shader + ".normalCamera", source=True, destination=False
        )
        or []
        if node != _BUMP
    ]
    if existing_bump and not layer_existing_bump:
        return False

    try:
        _go_to_build_pose()
        cmds.refresh()
        cmds.setAttr(_WRINKLE_MAP + ".shader", face_shader, type="string")
        if len(members) > 1:
            _duplicate_shader_for_others(engine, members, geometry)
        if cmds.objExists(_BUMP):
            cmds.delete(_BUMP)
    except _ERRORS as exc:
        cmds.warning("wrinkle_curves: failed: {}".format(exc))
        return False

    uuids_before = set(cmds.ls(cmds.ls(long=True), uuid=True))
    try:
        _create_wrinkle_curves(mesh, scale)
    except _ERRORS as exc:
        _delete_new_nodes(uuids_before)
        cmds.warning("wrinkle_curves: failed and rolled back: {}".format(exc))
        return False
    return True


# ---------------------------------------------------------- uv del viso


def _uv_values(mesh_transform, count):
    """Le coppie (u, v) di tutti gli UV dell'UV set corrente."""
    if not count:
        return []
    flat = cmds.polyEditUV("{}.map[0:{}]".format(mesh_transform, count - 1), query=True) or []
    return list(zip(flat[0::2], flat[1::2]))


def _scale_uvs(geo, indices, **flags):
    cmds.select(clear=True)
    if not indices:
        return
    cmds.select(["{}.map[{}]".format(geo, index) for index in indices])
    cmds.polyEditUV(**flags)


def _select_above(geo, height):
    """I vertici di geo dall'altezza `height` in su (MEL 46147-46150)."""
    cmds.select(geo)
    try:
        cmds.polySelectConstraint(
            mode=3,
            type=1,
            dist=3,
            distbound=(height, 999),
            distaxis=(0, 1, 0),
            distpoint=(0, 0, 0),
        )
    finally:
        cmds.polySelectConstraint(mode=0)
    return [item for item in cmds.ls(selection=True) or [] if ".vtx" in item]


def _fit_components(section, geo, building):
    """I componenti del fit `section`, riportati su geo fuori dal build."""
    cmds.select(clear=True)
    face_fit_reselect(section, "")
    components = cmds.ls(selection=True, flatten=True) or []
    if not components:
        raise RuntimeError("the fit selection of {} is empty".format(section))
    if not building:
        components = cmds.ls(_cast_components(components, geo), flatten=True)
    return components


def _project_face_uvs(geo, mesh, building):
    """Proiezione cilindrica nell'UV set uvFaceWrinkles (MEL 46106-46134)."""
    created = cmds.polyProjection(
        geo + ".f[0:99999]",
        constructionHistory=True,
        type="Cylindrical",
        insertBeforeDeformers=building,
        createNewMap=True,
        uvSetName=_UV_SET,
        smartFit=True,
    )
    cmds.rename(created[0], _PROJECTION)
    # nome letterale come nel MEL: fuori dal build e' il nodo del viso
    cmds.setAttr(_PROJECTION + ".projectionHorizontalSweep", 360)
    cmds.namespace(setNamespace=":")
    try:
        cmds.polyUVSet(mesh, currentUVSet=True, uvSet=_UV_SET)
    except _ERRORS:
        pass
    if (cmds.polyUVSet(mesh, query=True, currentUVSet=True) or [""])[0] == _UV_SET:
        return
    print("polyProjection failed to generate UVSet, now creating this with `polyUVSet`")
    if cmds.objExists(created[0]):
        cmds.delete(created[0])
    cmds.polyUVSet(geo, create=True, uvSet=_UV_SET)
    cmds.polyUVSet(mesh, currentUVSet=True, uvSet=_UV_SET)
    created = cmds.polyProjection(
        geo + ".f[0:99999]",
        constructionHistory=True,
        type="Cylindrical",
        insertBeforeDeformers=building,
        createNewMap=False,
        uvSetName=_UV_SET,
        smartFit=True,
    )
    cmds.setAttr(created[0] + ".projectionHorizontalSweep", 360)
    # niente UV che "nuotano" sui modelli dove polyProjection non crea il set
    cmds.bakePartialHistory(geo, prePostDeformers=True)
    if (cmds.polyUVSet(mesh, query=True, currentUVSet=True) or [""])[0] != _UV_SET:
        raise RuntimeError(
            "UV assignment failed. Attempted both via `polyProjection` and `polyUVSet`"
        )


def _squeeze_uvs_in_v(geo, building, forehead_top):
    """Schiaccia in basso gli UV sotto il mento e in alto quelli sopra la
    fronte, e allarga a tutta l'altezza quelli in mezzo (MEL 46138-46176)."""
    jaw = _fit_components("Jaw_R", geo, building)
    above_jaw = _select_above(geo, _ws(jaw[0])[1])
    # asInvertSelection, ramo vtx (MEL 67309-67313)
    cmds.select(geo + ".vtx[0:999999]")
    if above_jaw:
        cmds.select(above_jaw, deselect=True)
    if _select_as_uvs():
        cmds.polyEditUV(pivotU=0, pivotV=0, scaleU=1, scaleV=0.01)

    above_forehead = _select_above(geo, forehead_top)
    if _select_as_uvs():
        cmds.polyEditUV(pivotU=0, pivotV=1, scaleU=1, scaleV=0.01)

    cmds.select(clear=True)
    if above_jaw:
        cmds.select(above_jaw)
    if above_forehead:
        cmds.select(above_forehead, deselect=True)
    between = _select_as_uvs()
    if not between:
        raise RuntimeError("no vertex found between jaw and forehead")
    # al posto di texLatticeDeformContext (MEL 46167-46174): il bounding
    # box in V degli UV selezionati
    lo_bound, hi_bound = cmds.polyEvaluate(between, boundingBoxComponent2d=True)[1]
    bound_height = hi_bound - lo_bound
    if bound_height <= 0:
        raise RuntimeError("the UVs between jaw and forehead have no height")
    cmds.polyEditUV(uValue=0, vValue=0.5 - ((lo_bound + hi_bound) / 2.0))
    cmds.polyEditUV(pivotU=0.5, pivotV=0.5, scaleU=1, scaleV=1.0 / bound_height)


def _squeeze_uvs_in_u(geo, building):
    """Schiaccia ai lati gli UV dietro la fronte e allarga quelli del viso
    (MEL 46178-46223). Ritorna il numero di UV."""
    forehead = _fit_components("ForeHead_R", geo, building)
    minimum = 0.0
    outermost = forehead[0]
    for component in forehead:
        x = _ws(component)[0]
        if x < minimum:
            minimum = x
            outermost = component
    cmds.select(outermost)
    edge_uvs = cmds.ls(_select_as_uvs(), flatten=True)
    edge_u = cmds.polyEditUV(edge_uvs, query=True)[0]
    if edge_u == 0.5:
        raise RuntimeError("the forehead fit lies on the UV center")

    num_uvs = cmds.polyEvaluate(geo, uvcoord=True)
    edge_indices = [int(uv[uv.rindex("[") + 1 : -1]) for uv in edge_uvs]
    values = _uv_values(geo, num_uvs)
    # come nel MEL, gli UV del vertice di bordo sono ancora selezionati
    left = sorted(set(edge_indices) | {i for i, (u, _v) in enumerate(values) if u < edge_u})
    _scale_uvs(geo, left, pivotU=0, pivotV=0.5, scaleU=0.01, scaleV=1)
    values = _uv_values(geo, num_uvs)
    right = [i for i, (u, _v) in enumerate(values) if u > (1 - edge_u)]
    _scale_uvs(geo, right, pivotU=1, pivotV=0.5, scaleU=0.01, scaleV=1)
    values = _uv_values(geo, num_uvs)
    middle = [i for i, (u, _v) in enumerate(values) if 0.1 < u < 0.9]
    _scale_uvs(geo, middle, pivotU=0.5, pivotV=0.5, scaleU=0.5 / (0.5 - edge_u), scaleV=1)
    return num_uvs


def _copy_uvs_to_face(geo, geometry, num_uvs):
    """Riporta sul viso gli UV riproiettati sulla copia, solo nella zona
    utile della mappa (MEL 46228-46249)."""
    cmds.polyUVSet(geo, currentUVSet=True, uvSet=_UV_SET)
    cmds.polyUVSet(geometry, currentUVSet=True, uvSet=_UV_SET)
    new_values = _uv_values(geo, num_uvs)
    old_values = _uv_values(geometry, num_uvs)
    for index, (u, v) in enumerate(new_values):
        if u < 0.1 or u > 0.9 or v < 0.1 or v > 0.9:
            continue
        if index < len(old_values) and (u, v) == old_values[index]:
            continue
        cmds.polyEditUV("{}.map[{}]".format(geometry, index), relative=False, uValue=u, vValue=v)


def _wm_uv_update(geometry):
    building = cmds.objExists(_BUILDING)
    _bb_min, bb_max = _forehead_bounds()
    # il MEL pretende la shape intermedia originale (senza inMesh)
    originals = [
        shape
        for shape in cmds.listRelatives(geometry, shapes=True) or []
        if cmds.getAttr(shape + ".intermediateObject")
        and not cmds.listConnections(shape + ".inMesh", source=True, destination=False)
    ]
    if not originals:
        raise RuntimeError("Failed to find intermediateShape")

    geo = geometry
    if not building:
        if cmds.objExists("tempUVObject"):
            cmds.delete("tempUVObject")
        cmds.duplicate(geometry, name="tempUVObject")
        for shape in cmds.listRelatives("tempUVObject", shapes=True, fullPath=True) or []:
            if cmds.getAttr(shape + ".intermediateObject"):
                cmds.delete(shape)
        geo = "tempUVObject"
        cmds.select(geo)
        cmds.polyUVSet(rename=True, uvSet=_UV_SET, newUVSet=_UV_SET + "Old")

    mesh = cmds.listRelatives(geo, shapes=True, noIntermediate=True)[0]
    current_uv_set = cmds.polyUVSet(mesh, query=True, currentUVSet=True)[0]
    _project_face_uvs(geo, mesh, building)
    cmds.select(clear=True)
    _squeeze_uvs_in_v(geo, building, bb_max[1])
    num_uvs = _squeeze_uvs_in_u(geo, building)
    cmds.polyUVSet(mesh, currentUVSet=True, uvSet=current_uv_set)
    cmds.select(clear=True)

    if not building:
        _copy_uvs_to_face(geo, geometry, num_uvs)
        cmds.delete("tempUVObject")
        cmds.select(clear=True)
        print("// UV projections updated.")


def wm_uv_update(confirm=True):
    """Proietta gli UV delle rughe (UV set uvFaceWrinkles) sul viso nella
    posa corrente (parita' asWmUVUpdate, MEL 46045-46250): proiezione
    cilindrica, poi gli UV sotto il mento, sopra la fronte e dietro la
    fronte vengono schiacciati ai bordi per lasciare la mappa al viso.
    Dentro wrinkle_map lavora sul viso; chiamata da sola (bottone "Update
    UV Pose") riproietta su una copia e riporta gli UV cambiati.

    `confirm` e' la risposta al dialogo "Re-project UV at current
    Face-Pose ?". Ritorna bool."""
    building = cmds.objExists(_BUILDING)
    if not building and not cmds.objExists(_CURVES):
        cmds.warning(
            'wm_uv_update: WrinkleCurves not found, you must run "Create WrinkleMap" first.'
        )
        return False
    if not building and not confirm:
        return False
    for node in ("ForeHeadAreaMesh", "FaceFitJaw", "FaceFitForeHead"):
        if not cmds.objExists(node):
            cmds.warning("wm_uv_update: {} not found".format(node))
            return False
    try:
        geometry, _mesh = _face_geometry()
        _wm_uv_update(geometry)
    except _ERRORS as exc:
        if not building and cmds.objExists("tempUVObject"):
            cmds.delete("tempUVObject")
        cmds.warning("wm_uv_update: failed: {}".format(exc))
        return False
    return True


# ------------------------------------------------------------------ bake


def _im_convert_command():
    """asGetImConvertCmd (MEL 46813-46821): imconvert, magick da Maya 2022.
    Se l'eseguibile e' nel bin di Maya se ne usa il percorso completo."""
    maya_bin = os.path.join(os.environ.get("MAYA_LOCATION", ""), "bin")
    for name in ("magick.exe", "magick", "imconvert.exe", "imconvert"):
        candidate = os.path.join(maya_bin, name)
        if os.path.isfile(candidate):
            return candidate
    return "imconvert"


def _im_convert(*arguments):
    """Lancia imconvert/magick (il `system` del MEL), senza shell."""
    command = [_im_convert_command()] + list(arguments)
    try:
        result = subprocess.run(command, capture_output=True, check=False)
    except OSError as exc:
        cmds.warning("wm_bake: {} failed: {}".format(command[0], exc))
        return False
    if result.returncode:
        cmds.warning("wm_bake: {} failed: {}".format(command[0], result.stderr))
        return False
    return True


def _surface_sampler(filename, extension, target, source, output, width, height, materials):
    cmds.surfaceSampler(
        filename=filename,
        fileFormat=extension,
        target=target,
        uvSet="map1",
        searchOffset=0,
        maxSearchDistance=0,
        searchCage="",
        source=source,
        mapOutput=output,
        mapWidth=width,
        mapHeight=height,
        max=1,
        mapSpace="tangent",
        mapMaterials=materials,
        shadows=1,
        superSampling=1,
        filterType=0,
        filterSize=3,
        overscan=1,
        searchMethod=0,
        useGeometryNormals=1,
        ignoreMirroredFaces=0,
        flipU=0,
        flipV=0,
    )


def _offset_curve(curve, name, distance):
    return cmds.offsetCurve(
        curve,
        name=name,
        constructionHistory=True,
        range=False,
        cutLoop=True,
        connectBreaks=2,
        stitch=True,
        cutRadius=0,
        distance=distance,
        tolerance=0.01,
        subdivisionDensity=5,
        useGivenNormal=True,
        normal=(0, 90, 0),
    )


def _ramp(name):
    """Ramp con il suo place2dTexture (nome come nel MEL)."""
    cmds.shadingNode("ramp", asTexture=True, name=name)
    place = cmds.shadingNode("place2dTexture", asUtility=True, name=name + "Place2dTexture")
    cmds.connectAttr(place + ".outUV", name + ".uv")
    cmds.connectAttr(place + ".outUvFilterSize", name + ".uvFilterSize")
    return place


def _ramp_color(ramp, index, value):
    cmds.setAttr(
        "{}.colorEntryList[{}].color".format(ramp, index), value, value, value, type="double3"
    )


def _surface_shader(name):
    shader = cmds.shadingNode("surfaceShader", asShader=True, name=name)
    engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=name + "SG")
    cmds.connectAttr(shader + ".outColor", engine + ".surfaceShader", force=True)
    return shader, engine


def _bake_planes():
    """I piani su cui si campionano bump e maschere (MEL 45456-45472)."""
    cmds.polyPlane(
        name="WrinkleFacePlane1",
        width=0.5,
        height=1,
        subdivisionsX=1,
        subdivisionsY=1,
        axis=(0, 1, 0),
        createUVs=2,
        constructionHistory=False,
    )
    cmds.polyProjection(
        "WrinkleFacePlane1.f[0:8]",
        constructionHistory=False,
        type="Planar",
        insertBeforeDeformers=True,
        mapDirection="y",
    )
    cmds.parent("WrinkleFacePlane1", "WrinkleRenderingPlanes")
    cmds.setAttr("WrinkleFacePlane1.t", 0.25, 0, 0.5, type="float3")
    cmds.setAttr("WrinkleFacePlane1.v", 0)
    cmds.duplicate("WrinkleFacePlane1", name="WrinkleFacePlane2")
    cmds.duplicate("WrinkleFacePlane2", name="WrinkleFacePlane3")
    cmds.setAttr("WrinkleFacePlane3.tx", 0.5)
    cmds.setAttr("WrinkleFacePlane3.sx", 2)

    cmds.polyPlane(
        name="WrinkleFacePlane4",
        width=1,
        height=1,
        subdivisionsX=1,
        subdivisionsY=1,
        axis=(0, 1, 0),
        createUVs=2,
        constructionHistory=False,
    )
    cmds.setAttr("WrinkleFacePlane4.t", 0, -0.0125, 0.5, type="float3")
    cmds.setAttr("WrinkleFacePlane4.rz", 90)
    cmds.setAttr("WrinkleFacePlane4.sx", 0.025)
    cmds.setAttr("WrinkleFacePlane4.v", 0)
    cmds.parent("WrinkleFacePlane4", "WrinkleRenderingPlanes")


def _curves_on_plane(geometry, curves):
    """Copia ogni curva nello spazio UV del viso, sul piano XZ (MEL
    45474-45500)."""
    default_uv_set = "map1"
    uv_sets = cmds.polyUVSet(geometry, query=True, allUVSets=True) or []
    if "map1" not in uv_sets:
        default_uv_set = uv_sets[0]
    cmds.duplicate(geometry, name="tempMainGeometry")
    # l'UV set corrente (uvFaceWrinkles) diventa quello letto dal sampler
    cmds.polyCopyUV(
        "tempMainGeometry", uvSetNameInput="", uvSetName=default_uv_set, constructionHistory=True
    )
    if cmds.objExists("closestSampler"):
        cmds.delete("closestSampler")
    cmds.createNode("closestPointOnMesh", name="closestSampler")
    cmds.connectAttr("tempMainGeometry.outMesh", "closestSampler.inMesh", force=True)
    for curve in curves:
        on_plane = curve + "OnPlane"
        cmds.duplicate(curve, name=on_plane)
        cmds.parent(on_plane, "WrinkleRenderingCurves")
        cmds.xform(on_plane, worldSpace=True, pivots=(0, 0, 0))
        for index in range(_curve_num_cvs(curve)):
            pos = _ws("{}.cv[{}]".format(curve, index))
            cmds.setAttr("closestSampler.inPosition", pos[0], pos[1], pos[2])
            u = cmds.getAttr("closestSampler.parameterU")
            v = cmds.getAttr("closestSampler.parameterV")
            cmds.xform(
                "{}.cv[{}]".format(on_plane, index), worldSpace=True, translation=(u, 0, 1 - v)
            )
    cmds.delete("tempMainGeometry")


def _wrinkle_mesh(curve):
    """La striscia di una ruga con lo shader a rampa che ne da' il profilo
    (MEL 45502-45593)."""
    depth = cmds.getAttr(curve + ".depth") if _exists_attr(curve, "depth") else 10
    width = cmds.getAttr(curve + ".width") if _exists_attr(curve, "width") else 10
    center_pos = 0.5
    offset_a = width * 0.001
    offset_b = width * -0.001
    smile_line = curve == "SmileLineWrinkle1"
    if smile_line:  # rampa su misura: rilievo da un lato solo
        offset_b = width * -0.025
        center_pos = 0.1
    on_plane = curve + "OnPlane"
    curve_a = on_plane + "OffsetA"
    curve_b = on_plane + "OffsetB"
    cmds.rename(_offset_curve(on_plane, curve_a, offset_a)[1], curve + "OffsetCurveA")
    cmds.rename(_offset_curve(on_plane, curve_b, offset_b)[1], curve + "OffsetCurveB")
    if smile_line:  # l'offset non deve uscire dai bordi
        if cmds.getAttr(curve_b + ".boundingBoxMin")[0][0] < 0.03:
            for step in range(1, 20):
                cmds.setAttr(curve + "OffsetCurveB.distance", offset_b + (0.01 * step))
                if cmds.getAttr(curve_b + ".boundingBoxMin")[0][0] > 0.03:
                    break
        offset_b = cmds.getAttr(curve + "OffsetCurveB.distance")
    cmds.addAttr(
        on_plane, keyable=False, longName="offsetA", attributeType="double", defaultValue=offset_a
    )
    cmds.addAttr(
        on_plane, keyable=False, longName="offsetB", attributeType="double", defaultValue=offset_b
    )
    profiles = [curve_a, on_plane, curve_b]
    if cmds.getAttr(curve_a + ".boundingBoxMin")[0][0] > 0.5:  # oltre il centro
        profiles.remove(curve_a)
    cmds.loft(
        profiles,
        name=curve + "Loft",
        constructionHistory=False,
        uniform=True,
        close=False,
        autoReverse=False,
        degree=1,
        sectionSpans=1,
        range=False,
        polygon=0,
        reverseSurfaceNormals=True,
    )
    cmds.parent(curve_a, curve_b, "WrinkleRenderingCurves")
    mesh = curve + "Mesh"
    cmds.nurbsToPoly(
        curve + "Loft",
        name=mesh,
        matchNormalDir=True,
        constructionHistory=False,
        format=2,
        polygonType=1,
        polygonCount=200,
        chordHeightRatio=0.9,
        fractionalTolerance=0.01,
        minEdgeLength=0.001,
        delta=0.1,
        uType=1,
        uNumber=20,
        vType=1,
        vNumber=21,
        useChordHeight=False,
        useChordHeightRatio=False,
        chordHeight=0.01,
        edgeSwap=False,
        normalizeTrimmedUVRange=False,
        matchRenderTessellation=False,
        useSurfaceShader=True,
    )
    cmds.parent(mesh, "WrinkleRenderingMeshes")
    if cmds.polyNormalPerVertex(mesh + ".vtx[0]", query=True, normalY=True)[0] < 0:
        cmds.polyNormal(mesh, constructionHistory=False, normalMode=0, userNormalMode=0)
    cmds.delete(curve_a, curve_b, curve + "Loft")
    cmds.delete(mesh, constructionHistory=True)

    shader, engine = _surface_shader(curve + "WrinkleDepthShader")
    ramp1 = curve + "WrinkleDepthRamp1"  # sfuma ai lati della ruga
    cmds.shadingNode("ramp", asTexture=True, name=ramp1)
    place = cmds.shadingNode(
        "place2dTexture", asUtility=True, name=curve + "WrinkleDepthRampPlace2dTexture"
    )
    cmds.connectAttr(place + ".outUV", ramp1 + ".uv")
    cmds.connectAttr(place + ".outUvFilterSize", ramp1 + ".uvFilterSize")
    cmds.connectAttr(ramp1 + ".outColor", shader + ".outColor")
    cmds.setAttr(ramp1 + ".type", 0)
    cmds.setAttr(ramp1 + ".interpolation", 4)
    _ramp_color(ramp1, 0, 0)
    cmds.setAttr(ramp1 + ".colorEntryList[1].position", center_pos)
    _ramp_color(ramp1, 1, 1)
    cmds.setAttr(ramp1 + ".colorEntryList[2].position", 1)
    _ramp_color(ramp1, 2, 0)

    ramp2 = curve + "WrinkleDepthRamp2"  # sfuma alle estremita'
    cmds.shadingNode("ramp", asTexture=True, name=ramp2)
    place = cmds.shadingNode(
        "place2dTexture", asUtility=True, name=curve + "WrinkleDepthRampPlace2dTexture"
    )
    cmds.connectAttr(place + ".outUV", ramp2 + ".uv")
    cmds.connectAttr(place + ".outUvFilterSize", ramp2 + ".uvFilterSize")
    cmds.setAttr(ramp2 + ".type", 1)
    cmds.setAttr(ramp2 + ".interpolation", 4)
    _ramp_color(ramp2, 0, 0)
    cmds.setAttr(ramp2 + ".colorEntryList[1].position", 0.25)
    _ramp_color(ramp2, 1, depth * 0.1)
    cmds.setAttr(ramp2 + ".colorEntryList[2].position", 0.75)
    _ramp_color(ramp2, 2, depth * (0.05 if curve.startswith("CrowsFeetWrinkle") else 0.1))
    cmds.setAttr(ramp2 + ".colorEntryList[3].position", 1)
    _ramp_color(ramp2, 3, 0)
    cmds.connectAttr(ramp2 + ".outColor", ramp1 + ".colorEntryList[1].color")
    if curve.startswith("ForeHeadWrinkle"):  # non sfuma verso il centro
        _ramp_color(ramp2, 0, depth * 0.1)
    cmds.sets(mesh, edit=True, forceElement=engine)


def _mask_surface(wrinkle_group, eye_brow_inner_uv):
    """La mesh della maschera di un gruppo, attorno alle sue curve (MEL
    45613-45644). False se il gruppo non ha curve."""
    on_planes = cmds.ls(wrinkle_group + "Wrinkle*OnPlane") or []
    if not on_planes:
        return False
    surface = wrinkle_group + "WrinkleMaskSurface"
    loft_flags = {
        "name": surface,
        "constructionHistory": False,
        "uniform": True,
        "close": False,
        "autoReverse": False,
        "sectionSpans": 1,
        "range": False,
        "polygon": 0,
        "reverseSurfaceNormals": True,
    }
    if len(on_planes) == 1:
        offset_a, offset_b = 0.01, -0.01
        if _exists_attr(on_planes[0], "offsetA"):
            offset_a = cmds.getAttr(on_planes[0] + ".offsetA")
            offset_b = cmds.getAttr(on_planes[0] + ".offsetB")
        _offset_curve(on_planes[0], "WrinkleOffsetCurve1", offset_a)
        _offset_curve(on_planes[0], "WrinkleOffsetCurve2", offset_b)
        cmds.loft("WrinkleOffsetCurve1", "WrinkleOffsetCurve2", degree=1, **loft_flags)
        cmds.delete("WrinkleOffsetCurve1", "WrinkleOffsetCurve2")
    else:
        cmds.loft(on_planes, degree=3, **loft_flags)
    cmds.extendSurface(
        surface,
        constructionHistory=False,
        extendMethod=0,
        extensionType=0,
        distance=0.02,
        join=True,
        replaceOriginal=True,
        extendSide=2,
        extendDirection=2,
    )
    if wrinkle_group == "ForeHead":  # la fronte sfuma oltre l'asse X
        pos = _ws("ForeHeadWrinkleMaskSurface.cv[0][0]")
        cmds.move(
            (1 - eye_brow_inner_uv[0]) - pos[0],
            0,
            0,
            "ForeHeadWrinkleMaskSurface.cv[0][0:99]",
            relative=True,
        )
    mask = wrinkle_group + "WrinkleMask"
    cmds.nurbsToPoly(
        surface,
        name=mask,
        matchNormalDir=True,
        constructionHistory=False,
        format=1,
        polygonType=1,
        polygonCount=200,
        chordHeightRatio=0.9,
        fractionalTolerance=0.01,
        minEdgeLength=0.001,
        delta=0.1,
        uType=1,
        uNumber=3,
        vType=1,
        vNumber=3,
        useChordHeight=False,
        useChordHeightRatio=False,
        chordHeight=0.2,
        edgeSwap=False,
        normalizeTrimmedUVRange=False,
        matchRenderTessellation=False,
        useSurfaceShader=True,
    )
    cmds.delete(surface)
    cmds.parent(mask, "WrinkleRenderingMasks")
    return True


def _mask_shader(prefix, wrinkle_group, sections, index, eye_brow_inner_uv):
    """Shader della maschera di una sezione (MEL 45657-45720): trasparenza
    a rampa che sfuma ai bordi, per la rampa di sezione."""
    section = sections[index]
    name = prefix + wrinkle_group + section + "WrinkleMask"
    shader, engine = _surface_shader(name + "Shader")
    mask_ramp = name + "Ramp"
    _ramp(mask_ramp)
    cmds.connectAttr(mask_ramp + ".outColor", shader + ".outTransparency")

    sections_ramp = wrinkle_group + section + "WrinkleSectionsMaskRamp"
    _ramp(sections_ramp)
    cmds.setAttr(sections_ramp + ".interpolation", 4)
    _ramp_color(sections_ramp, 0, 0)
    _ramp_color(sections_ramp, 1, 0)
    cmds.setAttr(sections_ramp + ".colorEntryList[1].position", 1.0)
    cmds.connectAttr(sections_ramp + ".outColor", mask_ramp + ".colorEntryList[0].color")

    cmds.setAttr(mask_ramp + ".type", 5)
    _ramp_color(mask_ramp, 1, 1)
    cmds.setAttr(mask_ramp + ".colorEntryList[0].position", 0.9)
    cmds.setAttr(mask_ramp + ".colorEntryList[1].position", 1.0)

    cmds.sets(wrinkle_group + section + "WrinkleMask", edit=True, forceElement=engine)

    cmds.setAttr(sections_ramp + ".invert", 1 if wrinkle_group == "SmileLine" else 0)
    if len(sections) > 1:  # sfumatura fra le sezioni
        if sections[0] == "U1":
            cmds.setAttr(sections_ramp + ".type", 1)
        if sections[0] == "V1":
            cmds.setAttr(sections_ramp + ".type", 0)
        if index == 0:
            _ramp_color(sections_ramp, 0, 1)
        if index == 1:
            _ramp_color(sections_ramp, 1, 1)

    if wrinkle_group == "ForeHead" and section == "U2":  # sfuma verso il centro
        _ramp_color(sections_ramp, 0, 1)
        _ramp_color(sections_ramp, 1, 1)
        cmds.setAttr(sections_ramp + ".colorEntryList[2].position", 0.25)
        _ramp_color(sections_ramp, 2, 0)
        if cmds.objExists("closestSampler"):
            cmds.delete("closestSampler")
        cmds.createNode("closestPointOnMesh", name="closestSampler")
        cmds.connectAttr("ForeHeadU1WrinkleMask.outMesh", "closestSampler.inMesh", force=True)
        cmds.setAttr("closestSampler.inPosition", eye_brow_inner_uv[0], 0, 1 - eye_brow_inner_uv[1])
        cmds.setAttr(
            sections_ramp + ".colorEntryList[2].position",
            cmds.getAttr("closestSampler.parameterU"),
        )
        cmds.setAttr(sections_ramp + ".interpolation", 1)
        cmds.setAttr("closestSampler.inPositionX", 0.5)
        u = cmds.getAttr("closestSampler.parameterU")
        cmds.delete("closestSampler")
        cmds.setAttr(sections_ramp + ".colorEntryList[3].position", u)
        _ramp_color(sections_ramp, 3, 0.5)


def _bake_masks(image_path, extension, mask_size, eye_brow_inner_uv):
    """Una maschera per sezione di ogni gruppo, campionata a destra e
    specchiata a sinistra (MEL 45600-45734)."""
    cmds.duplicate("WrinkleFacePlane2", name="WrinkleFacePlane3")
    cmds.setAttr("WrinkleFacePlane3.tx", 0.5)
    cmds.setAttr("WrinkleFacePlane3.sx", 2)
    prefix = ""
    for group_node in _children(_CURVES):
        wrinkle_group = _group_name(group_node)
        sections = []
        for index in range(2):
            if _exists_attr(group_node, "sections{}".format(index)):
                sections.append(cmds.getAttr("{}.sections{}".format(group_node, index)) or "")
        if not _mask_surface(wrinkle_group, eye_brow_inner_uv):
            continue
        mask = wrinkle_group + "WrinkleMask"
        for index, section in enumerate(sections):
            if len(sections) > 1:
                cmds.duplicate(mask, name=wrinkle_group + section + "WrinkleMask")
            for _ in range(6):  # nome casuale: evita la cache degli shader
                number = random.randrange(26)
                prefix += chr(64 + number) if number else ""
            _mask_shader(prefix, wrinkle_group, sections, index, eye_brow_inner_uv)
            base = "{}/{}{}Mask".format(image_path, wrinkle_group, section)
            if not cmds.objExists("SkipBaker"):
                _surface_sampler(
                    base + "_R",
                    extension,
                    "WrinkleFacePlane3",
                    wrinkle_group + section + "WrinkleMask",
                    "alpha",
                    mask_size[0],
                    mask_size[1],
                    1,
                )
                _im_convert(
                    "{}_R.{}".format(base, extension), "-flop", "{}_L.{}".format(base, extension)
                )
            for side in ("_R", "_L"):
                cmds.setAttr(
                    "fileWrinkle{}{}{}.fileTextureName".format(wrinkle_group, section, side),
                    "{}{}.{}".format(base, side, extension),
                    type="string",
                )
        if len(sections) > 1:
            cmds.delete(mask)


def _bake_bump(mesh, image_path, extension, map_size):
    """Campiona WrinklesMesh sulla meta' destra, la specchia e affianca le
    due meta' in bump.<ext>; aggiunge un uvSnapshot (MEL 45736-45749)."""
    sampled = "{}/sampleddiffuseRGB.{}".format(image_path, extension)
    flipped = "{}/sampleddiffuseRGBFlipped.{}".format(image_path, extension)
    _surface_sampler(
        image_path + "/sampleddiffuseRGB",
        extension,
        "WrinkleFacePlane2",
        "WrinklesMesh",
        "diffuseRGB",
        map_size[0] // 2,
        map_size[1],
        0,
    )
    _im_convert(sampled, "-flop", flipped)
    _im_convert(sampled, flipped, "+append", "{}/bump.{}".format(image_path, extension))
    for leftover in (sampled, flipped):
        if os.path.isfile(leftover):
            os.remove(leftover)
    snapshot = "{}/uvSnapshot.{}".format(image_path, extension)
    if not os.path.exists(snapshot):
        cmds.select(mesh)
        cmds.uvSnapshot(
            overwrite=True,
            fileFormat=extension,
            xResolution=map_size[0],
            yResolution=map_size[1],
            antiAliased=True,
            redColor=255,
            greenColor=255,
            blueColor=255,
            name=snapshot,
            uMin=0,
            uMax=1,
            vMin=0,
            vMax=1,
        )


def _rendering_set(nodes_before):
    """FaceWrinkleRenderingSet con i nodi nati nel bake (MEL 45758-45770).
    select/deselect per nome come nel MEL: i set vengono espansi nei loro
    membri. Ritorna il nome del set."""
    nodes_after = cmds.ls()
    before = set(nodes_before)
    cmds.select(nodes_after)
    cmds.select([node for node in nodes_after if node in before], deselect=True)
    cmds.select(cmds.ls(selection=True, objectsOnly=True))
    rendering_set = cmds.sets(name=_RENDERING_SET)
    if cmds.objExists("Sets"):
        cmds.sets(rendering_set, add="Sets")
    cmds.select(clear=True)
    return rendering_set


def _wm_bake(geometry, mesh):
    map_size = (cmds.getAttr(_WRINKLE_MAP + ".mapWidth"), cmds.getAttr(_WRINKLE_MAP + ".mapHeight"))
    mask_size = (
        cmds.getAttr(_WRINKLE_MAP + ".maskWidth"),
        cmds.getAttr(_WRINKLE_MAP + ".maskHeight"),
    )
    modifier = cmds.getAttr(_WRINKLE_MAP + ".modifier")
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    image_path = cmds.getAttr(_WRINKLE_MAP + ".imagePath") or ""
    extension = cmds.getAttr(_WRINKLE_MAP + ".format", asString=True)

    if cmds.objExists(_RENDERING):
        if cmds.objExists(_RENDERING_SET):
            _delete_existing(cmds.sets(_RENDERING_SET, query=True) or [])
    nodes_before = cmds.ls()
    curves = _wrinkle_curves_list()
    if cmds.objExists(_RENDERING):
        cmds.delete(_RENDERING)

    current_uv_set = cmds.polyUVSet(mesh, query=True, currentUVSet=True)[0]
    cmds.polyUVSet(mesh, currentUVSet=True, uvSet=_UV_SET)
    try:
        face_fit_reselect("EyeBrowInner_R", "")
        uvs = _select_as_uvs()
        eye_brow_inner_uv = (cmds.polyEditUV(uvs, query=True) if uvs else None) or [0.0, 0.0]

        cmds.createNode("transform", name=_RENDERING)
        for child in ("Planes", "Curves", "Masks", "Meshes"):
            cmds.createNode("transform", name=_RENDERING + child, parent=_RENDERING)
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        _bake_planes()
        _curves_on_plane(geometry, curves)
        for curve in curves:
            _wrinkle_mesh(curve)
        meshes = cmds.parent(_children("WrinkleRenderingMeshes"), world=True)
        cmds.polyUnite(meshes, constructionHistory=False, mergeUVSets=True, name="WrinklesMesh")
        cmds.parent("WrinklesMesh", "WrinkleRenderingMeshes")

        _bake_masks(image_path, extension, mask_size, eye_brow_inner_uv)
        if not cmds.objExists("SkipBaker"):
            _bake_bump(mesh, image_path, extension, map_size)
        cmds.setAttr(
            _BUMP_FILE + ".fileTextureName",
            "{}/bump.{}".format(image_path, extension),
            type="string",
        )

        cmds.setAttr("WrinkleFacePlane2.v", 0)
        cmds.setAttr("WrinkleFacePlane3.v", 0)
        cmds.setAttr("WrinkleRenderingMasks.v", 0)
        cmds.setAttr(_WRINKLE_MAP + ".modifier", 0)
    finally:
        cmds.polyUVSet(mesh, currentUVSet=True, uvSet=current_uv_set)

    rendering_set = _rendering_set(nodes_before)

    # WrinkleRendering accanto al viso, per chi lo tiene in scena con Ctrl
    cmds.setAttr(_RENDERING + ".rx", 90)
    cmds.setAttr(_RENDERING + ".s", scale * 0.75, scale * 0.75, scale * 0.75, type="float3")
    pos = _ws("ctrlBox")
    cmds.setAttr(_RENDERING + ".t", pos[0] * -1.5, pos[1] + (scale * 0.35), pos[2], type="float3")
    cmds.setAttr("WrinkleRenderingPlanes.ty", scale * -0.005)

    if modifier != _CTRL:
        cmds.delete(_RENDERING)
        if cmds.objExists(rendering_set):
            _delete_existing(cmds.sets(rendering_set, query=True) or [])


def wm_bake():
    """Genera le immagini delle rughe nella cartella WrinkleMap.imagePath
    (parita' asWmBake, MEL 45392-45787): le curve vengono portate nello
    spazio UV del viso, trasformate in strisce con shader a rampa e
    campionate con surfaceSampler in bump.<ext>; per ogni sezione di ogni
    gruppo si campiona una maschera <Gruppo><Sezione>Mask_R.<ext>, poi
    specchiata in _L con imconvert/magick. Aggiorna i nodi file. I nodi di
    rendering (WrinkleRendering) vengono cancellati alla fine, a meno che
    WrinkleMap.modifier valga 4 (Ctrl). Un nodo "SkipBaker" in scena salta
    il campionamento. Serve wrinkle_map. Ritorna bool."""
    for node in (_WRINKLE_MAP, _CURVES, _BUMP_FILE, "ctrlBox"):
        if not cmds.objExists(node):
            cmds.warning('wm_bake: {} not found, you must run "Wrinkle Map" first.'.format(node))
            return False
    if not _exists_attr(FIT_SKELETON, "faceScale"):
        cmds.warning("wm_bake: FaceFitSkeleton.faceScale not found")
        return False
    try:
        geometry, mesh = _face_geometry()
    except RuntimeError as exc:
        cmds.warning("wm_bake: {}".format(exc))
        return False
    if _UV_SET not in (cmds.polyUVSet(geometry, query=True, allUVSets=True) or []):
        cmds.warning("wm_bake: UV set {} not found on {}".format(_UV_SET, geometry))
        return False
    uuids_before = set(cmds.ls(cmds.ls(long=True), uuid=True))
    try:
        _wm_bake(geometry, mesh)
    except (OSError,) + _ERRORS as exc:
        _delete_new_nodes(uuids_before)
        cmds.warning("wm_bake: failed and rolled back: {}".format(exc))
        return False
    return True


# ----------------------------------------------------------- wrinkle map


def _group_drivers(wrinkle_group, side):
    """(drivers, driverValues, secDrivers, sections) di un gruppo (MEL
    45243-45252)."""
    table = {
        "ForeHead": (
            ["ctrlBrow{}.ty"],
            [1, 1],
            ["EyeBrowOuter{}.ty", "EyeBrowInner{}.ty"],
            ["U1", "U2"],
        ),
        "Frown": (["ctrlBrow{}.squeeze"], [10], ["EyeBrowInner{}.tx"], [""]),
        "CrowsFeet": (["ctrlEye{}.squint"], [10], [], [""]),
        "BunnyLines": (["ctrlNose{}.ty"], [1], ["NoseCorner{}.ty"], [""]),
        "SmileLine": (
            ["ctrlMouthCorner{}.txPos_tyPos"],
            [1],
            ["Lip{}.tx", "Lip{}.ty"],
            ["U1", "U2"],
        ),
    }
    if wrinkle_group not in table:
        raise RuntimeError('unknown wrinkle group "{}"'.format(wrinkle_group))
    drivers, values, sec_drivers, sections = table[wrinkle_group]
    return (
        [driver.format(side) for driver in drivers],
        list(values),
        [driver.format(side) for driver in sec_drivers],
        list(sections),
    )


def _add_slider(node, attr, default, minimum=None, maximum=None):
    """addAttr -k 1 seguito da setAttr -k 0 -cb 1, come nel MEL."""
    flags = {"keyable": True, "longName": attr, "defaultValue": default}
    if minimum is not None:
        flags["minValue"] = minimum
    if maximum is not None:
        flags["maxValue"] = maximum
    cmds.addAttr(node, **flags)
    cmds.setAttr("{}.{}".format(node, attr), keyable=False, channelBox=True)


def _connect_uv_chooser(file_node):
    for out_attr, in_attr in zip(_OUT_UV_ATTRS, _IN_UV_ATTRS):
        cmds.connectAttr("{}.{}".format(_UV_CHOOSER, out_attr), "{}.{}".format(file_node, in_attr))


def _set_values(values, index, value):
    while len(values) <= index:
        values.append(0)
    values[index] = value


def _secondary_drivers(wrinkle_group, side, sec_drivers, drivers, values, state):
    """Nei rig a joint il driver della maschera e' lo spostamento del joint
    (MEL 45265-45310): <Gruppo>Driver<n><side> segue il joint sotto
    WrinkleDrivers, e il valore a fine corsa si misura a destra portando il
    controllo al valore di prova."""
    if not cmds.objExists(_DRIVERS):
        cmds.createNode("transform", name=_DRIVERS, parent=_WRINKLE_MAP)
        cmds.parentConstraint("FaceMotionSystem", _DRIVERS, maintainOffset=True)
        for axis in "XYZ":
            cmds.connectAttr("FaceMotionSystem.scale" + axis, _DRIVERS + ".scale" + axis)
    for index, sec_driver in enumerate(sec_drivers):
        sec_obj, sec_attr = sec_driver.split(".")[:2]
        driver_node = "{}Driver{}{}".format(wrinkle_group, index + 1, side)
        offset = "{}Driver{}Offset{}".format(wrinkle_group, index + 1, side)
        cmds.createNode("transform", name=offset, parent=_DRIVERS)
        cmds.createNode("transform", name=driver_node, parent=offset)
        as_align(offset, sec_obj, True, True, False, False)
        driver_plug = "{}.{}".format(driver_node, sec_attr)
        while len(drivers) <= index:
            drivers.append("")
        drivers[index] = driver_plug
        if wrinkle_group == "SmileLine":
            # 45 gradi per separare sorriso e broncio, poi scambio x/y
            cmds.rotate(0, 0, 45, offset, relative=True, objectSpace=True)
            cmds.rotate(-180, 0, 0, offset, relative=True, objectSpace=True)
        if side == "_R":
            _wm_edit(wrinkle_group, "Test")
            pos = _ws(sec_obj)
            _go_to_build_pose()
            _hide_curves_and_reset_scale()
            cmds.xform(driver_node, worldSpace=True, translation=pos)
            _set_values(values, index, cmds.getAttr(driver_plug))
            if wrinkle_group == "SmileLine" and index == 1:
                values[index] = values[index - 1]
            cmds.setAttr(driver_plug, 0)
            state["right_value"] = values[index]
        else:
            _set_values(values, index, state["right_value"])
        if values[index] == 0:
            values[index] = 0.1  # niente divisione per zero
        cmds.pointConstraint(sec_obj, driver_node)


def _mask_layer(group_node, wrinkle_group, section, side, layer, driver, driver_value):
    """Un livello di WrinkleMasksLayeredTexture: file della maschera, il
    cui alpha segue il driver attraverso un setRange (MEL 45321-45354)."""
    name = wrinkle_group + section + side
    inputs = "{}.inputs[{}]".format(_MASKS, layer)
    cmds.setAttr(inputs + ".color", 0, 0, 0, type="double3")
    cmds.setAttr(inputs + ".blendMode", 4)  # Add
    file_node = cmds.shadingNode("file", asTexture=True, name="fileWrinkle" + name)
    _connect_uv_chooser(file_node)
    cmds.connectAttr(file_node + ".outColor", inputs + ".color", force=True)

    set_range = cmds.createNode("setRange", name="srWrinkle" + name)
    cmds.setAttr(set_range + ".maxX", 1)
    cmds.setAttr(set_range + ".oldMaxX", 1)
    multiply = cmds.createNode("unitConversion", name="srWrinkleMultiplyUC" + name)
    cmds.setAttr(multiply + ".conversionFactor", 0.5)
    cmds.connectAttr(group_node + ".multiply", multiply + ".input")
    cmds.connectAttr(multiply + ".output", set_range + ".maxX")
    cmds.connectAttr(group_node + ".start", set_range + ".oldMinX")
    cmds.connectAttr(group_node + ".offset", set_range + ".minX")

    if driver_value == 1:
        cmds.connectAttr(driver, set_range + ".valueX")
    else:
        conversion = driver.replace(".", "_", 1)
        if cmds.objExists(conversion):
            cmds.delete(conversion)
        cmds.createNode("unitConversion", name=conversion)
        cmds.setAttr(conversion + ".conversionFactor", 1.0 / driver_value)
        cmds.connectAttr(driver, conversion + ".input")
        cmds.connectAttr(conversion + ".output", set_range + ".valueX")

    # sdk: la connessione diretta non si aggiorna in continuo in Maya 2022
    for tangent, value in (("spline", 0), ("flat", 1)):
        cmds.setDrivenKeyframe(
            inputs + ".alpha",
            inTangentType=tangent,
            outTangentType=tangent,
            driverValue=value,
            value=value,
            currentDriver=set_range + ".outValueX",
        )


def _wrinkle_set(nodes_before):
    """FaceWrinkleSet con i nodi nati in wrinkle_map (MEL 45364-45386);
    select/deselect per nome come nel MEL."""
    nodes_after = cmds.ls()
    before = set(nodes_before)
    cmds.select(nodes_after)
    cmds.select([node for node in nodes_after if node in before], deselect=True)
    cmds.sets(name=_WRINKLE_SET)
    if cmds.objExists("Sets"):
        cmds.sets(_WRINKLE_SET, add="Sets")
    cmds.select(clear=True)
    duplicated = cmds.getAttr(_WRINKLE_MAP + ".duplicatedSG") or ""
    if duplicated and cmds.objExists(duplicated):
        cmds.sets(duplicated, add=_WRINKLE_SET)
    for member in cmds.sets(_WRINKLE_SET, query=True) or []:
        if "." not in member:
            cmds.setAttr(member + ".isHistoricallyInteresting", 0)


def _wrinkle_map(mesh, shader, blend_shapes_only):
    cmds.createNode("transform", name=_BUILDING)
    _add_slider("ctrlBox", "wrinkleMapMultiply", 1)
    _add_slider("ctrlBox", "wrinkleMapOffset", 0)

    if not wm_uv_update():
        raise RuntimeError("the UV projection failed")

    if not cmds.objExists(_UV_CHOOSER):
        cmds.createNode("uvChooser", name=_UV_CHOOSER)
    uv_set_nr = 0
    for index in range(cmds.getAttr(mesh + ".uvSet", size=True)):
        if cmds.getAttr("{}.uvSet[{}].uvSetName".format(mesh, index)) == _UV_SET:
            uv_set_nr = index
    cmds.connectAttr(
        "{}.uvSet[{}].uvSetName".format(mesh, uv_set_nr), _UV_CHOOSER + ".uvSets[0]", force=True
    )

    cmds.shadingNode("file", asTexture=True, name=_BUMP_FILE)
    # al posto di defaultNavigation -ce (MEL 45206-45208)
    cmds.shadingNode("bump2d", asUtility=True, name=_BUMP)
    cmds.connectAttr(_BUMP_FILE + ".outAlpha", _BUMP + ".bumpValue")
    cmds.connectAttr(_BUMP + ".outNormal", shader + ".normalCamera", force=True)
    _connect_uv_chooser(_BUMP_FILE)

    # maschere: bumpDepth = outAlpha * (wrinkleMapMultiply * 0.5) + offset
    multiply1 = as_create_mult_dl("multDoubleLinearFaceWrinkles1")
    cmds.connectAttr("ctrlBox.wrinkleMapMultiply", multiply1 + ".input1")
    cmds.setAttr(multiply1 + ".input2", 0.5)
    multiply2 = as_create_mult_dl("multDoubleLinearFaceWrinkles2")
    cmds.connectAttr(multiply1 + ".output", multiply2 + ".input2")
    plus = cmds.shadingNode("plusMinusAverage", asUtility=True, name="plusMinusAverageFaceWrinkles")
    cmds.connectAttr(multiply2 + ".output", plus + ".input1D[0]")
    cmds.connectAttr("ctrlBox.wrinkleMapOffset", plus + ".input1D[1]")
    cmds.connectAttr(plus + ".output1D", _BUMP + ".bumpDepth")

    cmds.shadingNode("layeredTexture", asTexture=True, name=_MASKS)
    cmds.setAttr(_MASKS + ".alphaIsLuminance", 1)
    cmds.connectAttr(_MASKS + ".outAlpha", multiply2 + ".input1")

    layer = 0
    state = {"right_value": 0.0}
    for group_node in _children(_CURVES):
        wrinkle_group = _group_name(group_node)
        for side in ("_R", "_L"):
            drivers, values, sec_drivers, sections = _group_drivers(wrinkle_group, side)
            if not cmds.attributeQuery("driver", node=group_node, exists=True):
                cmds.addAttr(group_node, keyable=True, longName="driver", dataType="string")
                cmds.setAttr(group_node + ".driver", drivers[0], type="string")
                _add_slider(group_node, "multiply", 1, 0, 2)
                _add_slider(group_node, "offset", 0)
                _add_slider(group_node, "start", 0.25, 0, 1)
            if not blend_shapes_only:
                _secondary_drivers(wrinkle_group, side, sec_drivers, drivers, values, state)
            as_lock_attr(group_node, True, True, True, False)

            for index, section in enumerate(sections):
                if index >= len(drivers) or index >= len(values):
                    raise RuntimeError(
                        "{}: no driver for section {}".format(group_node, section or index)
                    )
                attr = "sections{}".format(index)
                if side == "_R":
                    if not cmds.attributeQuery(attr, node=group_node, exists=True):
                        cmds.addAttr(group_node, longName=attr, dataType="string")
                    cmds.setAttr("{}.{}".format(group_node, attr), section, type="string")
                _mask_layer(
                    group_node, wrinkle_group, section, side, layer, drivers[index], values[index]
                )
                layer += 1

    if not wm_bake():
        raise RuntimeError("the bake failed")
    cmds.delete(_BUILDING)


def _rollback_wrinkle_map(uuids_before):
    """Toglie cio' che wrinkle_map ha creato. L'UV set uvFaceWrinkles resta
    sulla shape (come dopo la rimozione delle rughe): cancellarlo
    aggiungerebbe un nodo deleteUVSet alla history del viso."""
    _delete_new_nodes(uuids_before)
    for attr in ("wrinkleMapMultiply", "wrinkleMapOffset"):
        if _exists_attr("ctrlBox", attr):
            cmds.deleteAttr("ctrlBox." + attr)
    for group_node in _children(_CURVES):
        for attr in ("driver", "multiply", "offset", "start", "sections0", "sections1"):
            if cmds.attributeQuery(attr, node=group_node, exists=True):
                cmds.deleteAttr("{}.{}".format(group_node, attr))
    try:
        _go_to_build_pose()
    except _ERRORS:
        pass


def wrinkle_map(modifier=None, remove_existing=True):
    """Costruisce la bump map delle rughe dalle curve (parita'
    asWrinkleMap, MEL 45148-45390): UV set uvFaceWrinkles sul viso,
    fileFaceWrinkles -> bump2dWrinkle -> normalCamera dello shader, la cui
    bumpDepth e' la somma delle maschere (WrinkleMasksLayeredTexture, un
    livello per sezione e lato) pilotate dai controlli attraverso i
    setRange srWrinkle*; attributi wrinkleMapMultiply/wrinkleMapOffset sul
    ctrlBox e driver/multiply/offset/start sui gruppi; infine wm_bake e il
    set FaceWrinkleSet con i nodi creati. Se la mappa esiste gia', rimuove
    tutte le rughe (come il MEL, passando da wrinkle_curves).

    Args:
        modifier: valore di getModifiers (None = lo legge): con Ctrl (4)
            i nodi di rendering del bake restano in scena.
        remove_existing: risposta al dialogo di rimozione di
            wrinkle_curves quando la mappa esiste gia'.

    Ritorna bool."""
    if not cmds.objExists(_CURVES) or not cmds.objExists(_WRINKLE_MAP):
        cmds.warning(
            'wrinkle_map: WrinkleCurves not found, you must run "Create Wrinkle Curves" first.'
        )
        return False
    nodes_before = cmds.ls()
    try:
        cmds.softSelect(edit=True, softSelectEnabled=False)
    except _ERRORS:
        pass
    cmds.setAttr(_WRINKLE_MAP + ".modifier", _modifiers() if modifier is None else int(modifier))
    if cmds.objExists(_WRINKLE_SET):
        return wrinkle_curves(remove_existing=remove_existing)  # e' lui a rimuovere

    blend_shapes_only = (
        _exists_attr(FIT_SKELETON, "RigType") and cmds.getAttr(FIT_SKELETON + ".RigType") == 1
    )
    shader = cmds.getAttr(_WRINKLE_MAP + ".shader") or ""
    if not shader or not cmds.objExists(shader + ".normalCamera"):
        cmds.warning('wrinkle_map: shader "{}" not found'.format(shader))
        return False
    for node in ("ctrlBox", "FaceMotionSystem"):
        if not cmds.objExists(node):
            cmds.warning("wrinkle_map: {} not found, build the face first".format(node))
            return False
    try:
        _geometry, mesh = _face_geometry()
    except RuntimeError as exc:
        cmds.warning("wrinkle_map: {}".format(exc))
        return False
    if not wm_edit_cancel():  # WrinkleCurves a scala 1
        return False

    uuids_before = set(cmds.ls(cmds.ls(long=True), uuid=True))
    try:
        _wrinkle_map(mesh, shader, blend_shapes_only)
        _wrinkle_set(nodes_before)
    except _ERRORS as exc:
        _rollback_wrinkle_map(uuids_before)
        cmds.warning("wrinkle_map: failed and rolled back: {}".format(exc))
        return False
    cmds.select("ctrlBox")
    print("// WrinkleMap created")
    return True
