"""Ponte fra il nodo di Arise Rigging System e il build facciale.

Il nodo Arise (`Adv_Face`, in DevPyLib) resta sottile:
raccoglie gli attributi impostati dall'utente e chiama queste funzioni, che
non dipendono da Arise e sono quindi provabili con mayapy.

Flusso di `rig_creation()` nel nodo:

    build_face(options)          # rig con i nomi ADV, come il port del MEL
    nodes = face_rig_nodes()     # da passare a tagging_utils.tag_nodes
    kept = geometry_nodes()      # da passare a tagging_utils.tag_as_dont_tag
    rename_to_arise(prefix)      # nomi secondo Arise (core/arise_naming)

e di `on_delete_operation()`, che Arise chiama prima della propria pulizia:

    delete_face()                # pesi al joint della testa, poi via il rig

Vedi docs/arise-node.md per il disegno e i limiti.
"""

import maya.cmds as cmds

from .fit_options import FIT_OPTIONS, FIT_SKELETON, get_fit_option, set_fit_option

FACE_ROOT = "FaceGroup"


# I campi del nodo Arise: (sezione, titolo nell'editor, opzione di
# FaceFitSkeleton). Sono le opzioni del pannello Face di AdvancedSkeleton
# (sezioni "Pre" e "Build"), nello stesso ordine. Tipo, default e voci dei
# menu vengono da FIT_OPTIONS. Restano fuori SkinCluster (lo trova il
# build), NonSymSide (stato del fitting) e postRebuildScript.
NODE_FIELDS = (
    ("Geometry", "Face Mesh", "Face"),
    ("Geometry", "Head Joint", "HeadJoint"),
    ("Geometry", "Mask", "Mask"),
    ("Geometry", "All Head Meshes", "AllHead"),
    ("Geometry", "Right Eye", "RightEye"),
    ("Geometry", "Left Eye", "LeftEye"),
    ("Geometry", "Upper Teeth", "UpperTeeth"),
    ("Geometry", "Lower Teeth", "LowerTeeth"),
    ("Geometry", "Tongue", "Tongue"),
    ("Geometry", "Eyebrow", "Eyebrow"),
    ("Geometry", "Eyelash", "Eyelash"),
    ("Geometry", "Extras", "Extras"),
    ("Rig", "Rig Type", "RigType"),
    ("Rig", "Include", "Include"),
    ("Rig", "Lip Ctrls", "LipCtrls"),
    ("Rig", "Non Symmetrical", "NonSym"),
    ("Rig", "Simpler Eye Lid", "SimplerEyeLid"),
    ("Rig", "Eye Base", "EyeBase"),
    ("Rig", "Eye Socket", "EyeSocket"),
    ("Rig", "Cyclops", "Cyclops"),
    ("Rig", "Long Snout", "LongSnout"),
    ("Rig", "Lip To Nose Vertices", "vtxsFromLipToNose"),
    ("Shapes", "Phonemes", "Phonemes"),
    ("Shapes", "Emotions", "Emotions"),
    ("Shapes", "ARKit", "ARKit"),
    ("Shapes", "SnapChat", "SnapChat"),
    ("Skinning", "Game Engine", "GameEngine"),
    ("Skinning", "Multi Skin Clusters", "MultiSkinClusters"),
    ("Skinning", "Use Max Influences", "UseMaxInf"),
    ("Skinning", "Max Influences", "MaxInf"),
    ("Skinning", "Roblox Head", "RobloxHead"),
    ("Skinning", "Legacy Joint Orient", "LegacyFaceJointOrient"),
    ("Scripts", "Pre Rebuild Script", "preRebuildScript"),
)
# opzioni che il port non realizza ancora (docs/gap-analysis.md)
NOT_PORTED = ("MultiSkinClusters", "RobloxHead")


def node_fields():
    """I campi da creare sul nodo Arise, come lista di dict con chiavi
    section, title, option, type ("string" | "bool" | "enum" | "long"),
    default, items (voci del menu, per gli enum) e ported.

    Il default e' il valore salvato dal fitting quando FaceFitSkeleton e' in
    scena, cosi' il nodo appena creato mostra lo stato reale del viso e non
    lo sovrascrive; altrimenti e' il default di AdvancedSkeleton."""
    fitted = cmds.objExists(FIT_SKELETON)
    fields = []
    for section, title, name in NODE_FIELDS:
        option = FIT_OPTIONS[name]
        if fitted:
            default = get_fit_option(name)
        elif option.attr_type == "enum":
            default = option.enum_values[option.default]
        else:
            default = option.default
        fields.append(
            {
                "section": section,
                "title": title,
                "option": name,
                "type": option.attr_type,
                "default": default,
                "items": list(option.enum_values),
                "ported": name not in NOT_PORTED,
            }
        )
    return fields


def apply_options(options):
    """Scrive su FaceFitSkeleton le opzioni date ({nome opzione: valore},
    es. {"Face": "head_geo", "ARKit": True}). I valori None sono ignorati.
    Ritorna False con un warning se FaceFitSkeleton manca."""
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("apply_options: FaceFitSkeleton not found (fit the face first)")
        return False
    ok = True
    for name, value in (options or {}).items():
        if value is None:
            continue
        ok = set_fit_option(name, value) and ok
    return ok


def build_face(options=None) -> bool:
    """Costruisce il rig facciale (i 30 step) leggendo il fitting dalla
    scena. `options` passa da `apply_options` prima del build."""
    from ..builder import FacialRigBuilder
    from .ui.build_frame import config_from_scene

    if options and not apply_options(options):
        return False
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("build_face: FaceFitSkeleton not found (fit the face first)")
        return False
    return bool(FacialRigBuilder(config_from_scene()).build())


def face_rig_nodes():
    """I nodi creati dal build (membri di FaceAllSet), per registrarli
    presso Arise con `tagging_utils.tag_nodes` e per cancellarli. Lista
    vuota se il rig non c'e'.

    Restano fuori gli antenati di FaceFitSkeleton (FaceGroup): esistono da
    prima del build, li crea il fitting, e cancellarli porterebbe via il
    fitting. Gli skinCluster delle geometrie dell'utente non sono in
    FaceAllSet (esistevano prima del build, MEL 36854-36868)."""
    if not cmds.objExists("FaceAllSet"):
        return []
    fit_path = (cmds.ls(FIT_SKELETON, long=True) or [""])[0]
    nodes = []
    for node in cmds.sets("FaceAllSet", query=True) or []:
        long_name = (cmds.ls(node, long=True) or [""])[0]
        if not long_name or fit_path.startswith(long_name + "|"):
            continue
        nodes.append(node)
    return nodes


# opzioni di FaceFitSkeleton che nominano geometrie dell'utente
GEOMETRY_OPTIONS = (
    "Face", "AllHead", "RightEye", "LeftEye", "UpperTeeth", "LowerTeeth",
    "Tongue", "Eyebrow", "Eyelash", "Extras",
)  # fmt: skip


def geometry_nodes():
    """I nodi che appartengono alle geometrie dell'utente e non al rig:
    le shape (comprese le Orig), i deformer con i loro set, groupId,
    groupParts e bindPose, esclusi i membri di FaceAllSet.

    Il Prep ricrea lo skinCluster del viso (rebind): il nodo ha lo stesso
    nome ma e' nuovo, e Arise, che considera suo tutto cio' che nasce
    durante `rig_creation()`, lo cancellerebbe uscendo da Build. Il nodo
    Arise passa questa lista a `tagging_utils.tag_as_dont_tag`."""
    built = set(face_rig_nodes())
    found = []
    for option in GEOMETRY_OPTIONS:
        for geometry in (get_fit_option(option) or "").split():
            if not cmds.objExists(geometry):
                continue
            found += cmds.listRelatives(geometry, shapes=True, fullPath=True) or []
            # dalla history e non da findDeformers, che su una mesh
            # referenziata con shape "Deformed" separata non trova nulla
            history = cmds.listHistory(geometry, pruneDagObjects=True) or []
            deformers = cmds.ls(history, type="geometryFilter") or []
            found += deformers
            for deformer in deformers:
                # cancellare il set di un deformer cancella il deformer
                for kind in ("dagPose", "objectSet", "groupId", "groupParts"):
                    found += cmds.listConnections(deformer, type=kind) or []
    nodes = []
    for node in found:
        if node not in built and node not in nodes:
            nodes.append(node)
    return nodes


def _skinned_geometry(skin):
    """La geometria deformata da uno skinCluster ("" se non c'e')."""
    return (cmds.skinCluster(skin, query=True, geometry=True) or [""])[0]


def _release_skin_influences(nodes):
    """Toglie i joint del rig dagli skinCluster che li usano, restituendo
    il loro peso al joint della testa (asDeleteAdvancedFace, MEL
    27686-27721): blocca tutte le influenze tranne HeadJoint, rimuove quelle
    del rig con un solo comando, normalizza e sblocca. Cancellare un joint
    ancora influenza lascerebbe la mesh senza quei pesi.

    Divergenza dal MEL: il MEL lo fa sul solo skinCluster del viso, qui su
    ogni skinCluster non creato dal build che usa joint del rig (le
    geometrie di occhi, denti e lingua hanno il proprio)."""
    head_joint = get_fit_option("HeadJoint") or ""
    rig_joints = set(cmds.ls(nodes, type="joint"))
    built = set(nodes)
    for skin in cmds.ls(type="skinCluster"):
        if skin in built:  # skinCluster creato dal build: se ne va col rig
            continue
        influences = cmds.skinCluster(skin, query=True, influence=True) or []
        ours = [j for j in influences if j in rig_joints]
        if not ours:
            continue
        if len(ours) == len(influences):  # MEL 27686-27703: serve un joint che resti
            if not cmds.objExists(head_joint):
                continue
            cmds.skinCluster(skin, edit=True, addInfluence=head_joint, lockWeights=False, weight=1)
            influences.append(head_joint)
        for joint in influences:
            if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
                cmds.setAttr(joint + ".lockInfluenceWeights", joint != head_joint)
        cmds.skinCluster(skin, edit=True, removeInfluence=ours)
        geometry = _skinned_geometry(skin)
        if geometry:
            cmds.skinPercent(skin, geometry, normalize=True)
        for joint in influences:
            if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
                cmds.setAttr(joint + ".lockInfluenceWeights", 0)


def _normalize_skin_clusters():
    """Normalizza tutti gli skinCluster della scena (MEL 27726-27733)."""
    for skin in cmds.ls(type="skinCluster"):
        geometry = _skinned_geometry(skin)
        if not geometry:
            continue
        try:
            cmds.skinPercent(skin, geometry, normalize=True)
        except RuntimeError:  # catchQuiet nel MEL
            pass


def delete_face() -> bool:
    """Cancella il rig facciale lasciando il fitting e i pesi sul joint
    della testa. Il nodo Arise la chiama da `on_delete_operation()`, prima
    della pulizia di Arise: i joint del build non sono dichiarati ad Arise,
    che li cancellerebbe mentre sono ancora influenze. Ritorna True se
    c'era qualcosa da cancellare."""
    nodes = face_rig_nodes()
    if not nodes:
        return False
    _release_skin_influences(nodes)
    for node in nodes:
        if cmds.objExists(node):  # un padre cancellato porta via i figli
            try:
                cmds.delete(node)
            except RuntimeError:
                pass
    _normalize_skin_clusters()
    return True
