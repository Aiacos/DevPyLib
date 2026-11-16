"""Auto-fitting per mesh facciali note (parita'
asNameMatcherAutoFaceFitting, righe MEL 47300-47806).

Il MEL riconosce le mesh di CharacterCreator 4/5 e MetaHuman dal nome
oggetto + vertex count, compila gli input della tab Pre e esegue
l'intera sequenza canonica di asCreateFaceFit per entrambi i lati
(non-symmetrical). Qui la stessa logica e' data-driven: AutoFitSource
descrive una sorgente (metadati + tabelle componenti per regione/lato)
e auto_face_fitting esegue la sequenza.

Le tabelle componenti delle mesh reali (centinaia di ID edge/vertice
hardcoded nel MEL) non sono ancora trascritte: components=None.
Trascriverle senza poterle verificare sulle mesh proprietarie
produrrebbe errori silenziosi; vanno estratte meccanicamente dal MEL e
validate in Maya interattivo con un asset CC/MH reale (follow-up).
La sequenza canonica, l'ordine delle regioni e il contratto della
tabella sono pero' gia' a parita' e coperti dai test con una sorgente
sintetica.

Nota parita' SG: il MEL auto-fitting passa per Nose/Cheek shading
group diversi da quelli della tabella $sections della UI (asBlueSG/
asBlue2SG vs asGreenSG); qui si usa fit_region, che applica i SG della
tabella regioni (parita' con la UI, fonte di verita' del progetto).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import maya.cmds as cmds

from .fit_options import set_fit_option
from .fitting import FacialFitting

# oggetti extra cercati in scena e aggiunti all'input Extras (MEL 47491)
AUTO_FIT_EXTRAS = (
    "Sideburns_Stubble",
    "Circle_Sparse",
    "Mustache_Sparse",
    "Soul_Patch_Sparse",
    "Classic_short",
    "CC_Base_TearLine",
    "Kevin_Brow",
    "Camila_Brow",
    "Eyebrows",
)

# oggetti sopracciglia cercati per l'input Eyebrow (MEL 47475)
AUTO_FIT_EYEBROWS = ("Eyebrows", "Brows")

# sequenza canonica delle regioni per lato (ordine MEL 47504-47777).
# (region, right_only): le regioni di mezzeria e le Lip (che innescano
# l'auto-fit non-symmetrical del lato Left) girano solo nel passo destro.
AUTO_FIT_SEQUENCE = (
    ("EyeBall", False),
    ("EyeLidOuter", False),
    ("EyeLidMain", False),
    ("EyeLidInner", False),
    ("LipOuter", True),
    ("LipMain", True),
    ("LipInner", True),
    ("EyeBrowInner", False),
    ("EyeBrowOuter", False),
    ("EyeBrowCenter", True),
    ("EyeBrowMid1", False),
    ("EyeBrowMid2", False),
    ("ForeHead", False),
    ("JawPivot", False),
    ("JawCorner", False),
    ("JawLine", False),
    ("Jaw", True),
    ("Nose", True),
    ("ChinCrease", True),
    ("Throat", True),
    ("NoseUnder", True),
    ("NoseBridge", True),
    ("Cheek", False),
    ("CheekBone", False),
    ("SmileBulge", False),
    ("FrownBulge", False),
    ("NoseCorner", False),
    ("NoseSide", False),
    ("Nostril", False),
    ("Pupil", False),
    ("Iris", False),
)


@dataclass
class AutoFitSource:
    """Descrizione di una mesh facciale nota.

    components mappa il nome regione a {"_R": [...], "_L": [...]}
    (liste di componenti da selezionare prima del fit; solo "_R" per le
    regioni right-only), piu' le chiavi speciali "Mask" (facce della
    maschera), "UpperTeeth"/"LowerTeeth"/"Tongue" (componenti per gli
    input quando non sono oggetti interi) e "TonguePlacement" (5 coppie
    (componente, offset_y) per piazzare Tongue0-4 sulla mezzeria).
    None = tabelle non ancora trascritte dal MEL.
    """

    name: str
    full_name: str
    face_obj: str
    teeth_obj: str
    vtx_count: int
    head_joint: str
    all_head: Tuple[str, ...]
    right_eye: str
    left_eye: str
    tongue: str
    eyelash: Tuple[str, ...]
    components: Optional[Dict] = None


# Metadati delle sorgenti riconosciute dal MEL (47303-47310, 47382-47497).
AUTO_FIT_SOURCES: List[AutoFitSource] = [
    AutoFitSource(
        name="CC4",
        full_name="CharacterCreator4",
        face_obj="CC_Base_Body",
        teeth_obj="CC_Base_Teeth",
        vtx_count=14164,
        head_joint="CC_Base_Head",
        all_head=("CC_Base_Body", "CC_Base_Teeth", "CC_Base_Tongue"),
        right_eye="CC_Base_Eye.f[0:319]",
        left_eye="CC_Base_Eye.f[320:639]",
        tongue="CC_Base_Tongue",
        eyelash=("CC_Base_Body.f[13446:14045]",),
    ),
    AutoFitSource(
        name="MH",
        full_name="MetaHuman",
        face_obj="head_lod0_mesh",
        teeth_obj="teeth_lod0_mesh",
        vtx_count=24049,
        head_joint="head",
        all_head=("head_lod0_mesh", "teeth_lod0_mesh", "saliva_lod0_mesh"),
        right_eye="eyeRight_lod0_mesh",
        left_eye="eyeLeft_lod0_mesh",
        tongue="",  # facce dei denti (tabella componenti)
        eyelash=("eyelashes_lod0_mesh",),
    ),
    AutoFitSource(
        name="CC5",
        full_name="CharacterCreator5",
        face_obj="CC_Base_Body",
        teeth_obj="CC_Base_Teeth",
        vtx_count=56412,
        head_joint="CC_Base_Head",
        all_head=("CC_Base_Body", "CC_Base_Teeth", "CC_Base_Tongue"),
        right_eye="CC_Base_Eye.f[0:1279]",
        left_eye="CC_Base_Eye.f[1280:2559]",
        tongue="CC_Base_Tongue",
        eyelash=("Eyelash_Low", "Eyelash_Up"),
    ),
]


def detect_auto_fit_source(extra_sources=None) -> Optional[AutoFitSource]:
    """Riconosce una mesh nota in scena (parita' MEL 47312-47330):
    l'oggetto face deve esistere e avere il vertex count atteso."""
    for source in list(AUTO_FIT_SOURCES) + list(extra_sources or []):
        if not cmds.objExists(source.face_obj):
            continue
        if cmds.polyEvaluate(source.face_obj, vertex=True) == source.vtx_count:
            return source
    return None


def _set_existing(option, candidates):
    """Persiste un'opzione con i soli oggetti presenti in scena."""
    existing = [obj for obj in candidates if cmds.objExists(obj)]
    if existing:
        set_fit_option(option, " ".join(existing))
    return existing


def auto_face_fitting(source: Optional[AutoFitSource] = None) -> bool:
    """Esegue l'auto-fitting completo (parita' MEL 47300-47806, senza
    le confirmDialog e senza il Build finale, che resta una scelta
    esplicita dell'utente).

    Sequenza: input della tab Pre (mask, face, head joint, occhi,
    denti, lingua, sopracciglia, ciglia, extras), poi per ogni lato
    (destro quindi sinistro, non-symmetrical) i fit della sequenza
    canonica; le regioni Lip girano solo a destra e producono il lato
    sinistro via auto-ricorsione. Chiude su lato destro con tutti i
    fit visibili, Tongue piazzata dai riferimenti.
    """
    if source is None:
        source = detect_auto_fit_source()
    if source is None:
        print("// Found no matches for Known Face-Meshes such as CharacterCreator or MetaHuman.")
        return False
    if source.components is None:
        cmds.warning(
            "{}: component tables not transcribed yet, "
            "auto-fitting unavailable for this source".format(source.full_name)
        )
        return False
    comp = source.components

    fitting = FacialFitting(source.face_obj)
    # come asChooseInput: skeleton se manca, mask dalla selezione facce
    if not cmds.objExists("FaceFitSkeleton"):
        fitting.create_fit_skeleton()
    cmds.select(comp["Mask"])
    if not fitting.create_fit_mask():
        return False

    set_fit_option("Face", source.face_obj)
    set_fit_option("HeadJoint", source.head_joint)
    _set_existing("AllHead", source.all_head)
    set_fit_option("RightEye", source.right_eye)
    set_fit_option("LeftEye", source.left_eye)
    if "UpperTeeth" in comp:
        set_fit_option("UpperTeeth", " ".join(comp["UpperTeeth"]))
    if "LowerTeeth" in comp:
        set_fit_option("LowerTeeth", " ".join(comp["LowerTeeth"]))
    if source.tongue:
        set_fit_option("Tongue", source.tongue)
    elif "Tongue" in comp:
        set_fit_option("Tongue", " ".join(comp["Tongue"]))
    _set_existing("Eyebrow", AUTO_FIT_EYEBROWS)
    _set_existing("Eyelash", source.eyelash)
    _set_existing("Extras", AUTO_FIT_EXTRAS)

    for side, side_name in (("_R", "Right"), ("_L", "Left")):
        fitting.switch_side(side_name)
        for region, right_only in AUTO_FIT_SEQUENCE:
            if right_only and side != "_R":
                continue
            if region == "EyeBall":
                if not fitting.fit_region("EyeBall"):
                    cmds.warning("Auto-fitting aborted at EyeBall{}".format(side))
                    return False
                continue
            table = comp.get(region)
            if not table or side not in table:
                continue
            cmds.select(table[side])
            if not fitting.fit_region(region, left_side=(side == "_L")):
                cmds.warning("Auto-fitting aborted at {}{}".format(region, side))
                return False

    fitting.switch_side("Right")
    fitting.show_both_sides()

    # Tongue: fit di mezzeria + piazzamento dai riferimenti (MEL 47783)
    if not fitting.fit_region("Tongue"):
        cmds.warning("Auto-fitting aborted at Tongue")
        return False
    for i, (ref, offset_y) in enumerate(comp.get("TonguePlacement", [])):
        pos = cmds.xform(ref, query=True, worldSpace=True, translation=True)
        cmds.xform(
            "Tongue{}".format(i), worldSpace=True, translation=(0, pos[1] + offset_y, pos[2])
        )

    cmds.refresh()
    print("// Auto FaceFitting completed for {}".format(source.full_name))
    return True
