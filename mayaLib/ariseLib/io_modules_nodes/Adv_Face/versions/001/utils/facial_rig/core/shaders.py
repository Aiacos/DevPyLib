"""Shader e shading group condivisi con AdvancedSkeleton.

Parita' con asFitModeEnsureShaders (AdvancedSkeleton.mel v6.661): i nomi
degli shader/SG sono contratto di interoperabilita' (le curve/cilindri del
fitting e i tool AS li referenziano per nome).
"""

from typing import Dict, Tuple

import maya.cmds as cmds

# nome shader -> (r, g, b). "asRedSS" e' un surfaceShader, gli altri lambert.
FIT_SHADER_COLORS: Dict[str, Tuple[float, float, float]] = {
    "asRed": (1.0, 0.0, 0.0),
    "asRed2": (1.0, 0.0, 1.0),
    "asGreen": (0.0, 1.0, 0.0),
    "asGreen2": (1.0, 1.0, 0.0),
    "asBlue": (0.0, 0.0, 1.0),
    "asBlue2": (0.0, 1.0, 1.0),
    "asWhite": (1.0, 1.0, 1.0),
    "asBlack": (0.0, 0.0, 0.0),
    "asBones": (0.78, 0.76, 0.72),
    "asRedSS": (1.0, 0.0, 0.0),
}


# Shader del build (asFaceEnsureShaders, righe MEL 43824-43843):
# nome -> (r, g, b), applicato a color, ambientColor e incandescence.
FACE_SHADER_COLORS: Dict[str, Tuple[float, float, float]] = {
    "asFaceBlue": (0.0, 0.0, 1.0),
    "asFaceBrown": (0.541, 0.282, 0.200),
    "asFaceGreen": (0.000, 0.275, 0.098),
    "asFaceCyan": (0.0, 0.5, 0.5),
    "asFaceRed": (0.4, 0.0, 0.0),
}


def ensure_face_shaders() -> bool:
    """Crea (se mancanti) i 5 lambert asFace* del build, identici ad AS
    (parita' asFaceEnsureShaders)."""
    for name, (r, g, b) in FACE_SHADER_COLORS.items():
        sg_name = name + "SG"
        if cmds.objExists(name) and cmds.objExists(sg_name):
            continue
        if cmds.objExists(name):
            cmds.delete(name)
        if cmds.objExists(sg_name):
            cmds.delete(sg_name)
        shader = cmds.shadingNode("lambert", asShader=True, name=name)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
        for attr in ("color", "ambientColor", "incandescence"):
            cmds.setAttr("{}.{}".format(shader, attr), r, g, b, type="float3")
    return True


def ensure_fit_shaders() -> bool:
    """Crea (se mancanti) gli shader/SG del fitting, identici ad AS."""
    for name, (r, g, b) in FIT_SHADER_COLORS.items():
        sg_name = name + "SG"
        if cmds.objExists(name) and cmds.objExists(sg_name):
            continue
        if cmds.objExists(name):
            cmds.delete(name)
        if cmds.objExists(sg_name):
            cmds.delete(sg_name)
        node_type = "surfaceShader" if name == "asRedSS" else "lambert"
        shader = cmds.shadingNode(node_type, asShader=True, name=name)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
        cmds.connectAttr(shader + ".outColor", sg + ".surfaceShader", force=True)
        color_attr = ".outColor" if name == "asRedSS" else ".color"
        cmds.setAttr(shader + color_attr, r, g, b, type="float3")
    return True
