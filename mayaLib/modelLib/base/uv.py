import math
import pymel.core as pm
import maya.mel as mel
from mayaLib.rigLib.utils.util import getAllObjectUnderGroup


def checkUVInBoundaries(shell):
    uvs = pm.polyListComponentConversion(shell, tuv=True)

    uMax = 1
    uMin = 0
    vMax = 1
    vMin = 0
    for i, uv in zip(range(len(pm.ls(uvs, fl=True))), pm.ls(uvs, fl=True)):
        u, v = pm.polyEditUV(uv, q=True, u=True, v=True)

        if i > 0:
            if (u > uMin) and (u < uMax) and (v > vMin) and (v < vMax):
                pass
                # return True
            else:
                return False

        uMax = int(u) + 1
        uMin = int(u)

        vMax = int(v) + 1
        vMin = int(v)

    return True


def checkUVBoundaries(shell):
    uvs = pm.polyListComponentConversion(shell, tuv=True)
    uvTileRange = []

    for i, uv in zip(range(len(pm.ls(uvs, fl=True))), pm.ls(uvs, fl=True)):
        u, v = pm.polyEditUV(uv, q=True, u=True, v=True)

        uMax = int(u) + 1
        uMin = int(u)

        vMax = int(v) + 1
        vMin = int(v)

        tile = [uMin, uMax, vMin, vMax]
        if tile not in uvTileRange:
            uvTileRange.append([uMin, uMax, vMin, vMax])

    return uvTileRange


def cutUVTile(shell):
    for tile in checkUVBoundaries(shell):
        tmpBuffer = []
        uvs = pm.polyListComponentConversion(shell, tuv=True)

        for uv in pm.ls(uvs, fl=True):
            u, v = pm.polyEditUV(uv, q=True, u=True, v=True)
            if u > tile[0] and u < tile[1] and v > tile[2] and v < tile[3]:
                tmpBuffer.append(uv)

        faces = pm.polyListComponentConversion(pm.ls(tmpBuffer), tuv=True)
        pm.select(faces)
        mel.eval('CreateUVShellAlongBorder;')
        # pm.polyMapCut(faces, ch=True)


def recursiveCutUV(geo):
    shellList = getUVShell(geo)
    for shell in shellList:
        if not checkUVInBoundaries(shell):
            cutUVTile(shell)


def getUVShell(geo):
    shellNumber = pm.polyEvaluate(geo, uvShell=True)
    shellList = []
    for i in range(shellNumber):
        shellFaces = pm.polyListComponentConversion(pm.polyEvaluate(geo, uvsInShell=i), toFace=True)
        shellList.append(shellFaces)

    return shellList


def setTexelDensity(geo, texelDensity=10.24, mapRes=1024):
    texSetTexelDensity = 'texSetTexelDensity ' + str(texelDensity) + ' ' + str(mapRes) + ';'
    pm.select(geo.f[:])
    mel.eval(texSetTexelDensity)


def uvLayoutNoScale(geoList, uCount, vCount, mapRes=1024, iteration=2):
    pm.u3dLayout(geoList, res=mapRes, mutations=iteration, rot=2, box=[0, 1, 0, 1], shellSpacing=0.0009765625,
                 tileMargin=0.001953125, layoutScaleMode=1, u=uCount, v=vCount, rst=90, rmn=0, rmx=360)


def finalLayoutUV(geoList, area=1):
    tileNumber = math.ceil(area)
    tileValue = tileNumber / 2
    uCount = tileValue if tileValue % 2 else tileValue + 1
    vCount = tileValue + 1

    print 'UV: ', math.ceil(uCount), math.ceil(vCount)
    uvLayoutNoScale(geoList, math.ceil(uCount), math.ceil(vCount))

    badShellList = []
    for geo in geoList:
        for shell in getUVShell(geo):
            if not checkUVInBoundaries(shell):
                badShellList.append(shell)
    if len(badShellList) > 0:
        print 'Bad Shells'
        uvLayoutNoScale(badShellList, 1, 1)
        pm.polyEditUV(badShellList, u=0, v=vCount)

    print 'Auto UV Complete!'


def autoSeamUV(geo, angle=0):
    try:
        pm.u3dAutoSeam(geo, s=angle, p=1)  # s=0
    except:
        pm.unfold(geo)


def unfoldOptimizeUV(geo, normalizeShell=False):
    pm.u3dUnfold(geo, mapsize=1024, iterations=2, pack=0, borderintersection=True, triangleflip=True, roomspace=0)
    if normalizeShell:
        shellList = getUVShell(geo)
        for shell in shellList:
            pm.polyNormalizeUV(shell, normalizeType=1, preserveAspectRatio=False, centerOnTile=True,
                               normalizeDirection=0)


def fixNonManifoldUV(geo):
    pm.select(geo)
    mel.eval(
        'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')


def autoUV(geoList=pm.ls(sl=True), mapRes=1024, texelDensity=32, autoSeam=0):
    # Default TexelDensity
    # texelDensity = mapRes/100;
    area = 0

    for geo in geoList:
        print geo
        # Automatic Projection UV
        pm.polyAutoProjection(geo.f[:], lm=0, pb=0, ibd=1, cm=0, l=0, sc=0, o=0, p=6, ps=0.2, ws=0)

        # fi non Manifold UV
        fixNonManifoldUV(geo)

        # Auto Seam 1
        autoSeamUV(geo, autoSeam)

        # Unfold3D Optimize
        unfoldOptimizeUV(geo)

        # Layout
        pm.u3dLayout(geo, res=256, mutations=1, rot=2, scl=1, box=[0, 1, 0, 1])

        # set Texel Density
        setTexelDensity(geo, texelDensity, mapRes)

        # check UV boundaries
        recursiveCutUV(geo)

        # delete history
        pm.delete(geo, ch=1)

        area = area + pm.polyEvaluate(geo, uvArea=True)

    print 'Total Area: ', area, ' -- RoundUp: ', math.ceil(area)

    # Layout with TexelDensity
    finalLayoutUV(geoList, area)
    pm.select(geoList)


if __name__ == "__main__":
    geos = getAllObjectUnderGroup(pm.ls(sl=True)[0])
    autoUV(geos, texelDensity=32)
