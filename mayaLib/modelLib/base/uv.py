import math
import pymel.core as pm
import maya.mel as mel


def checkUVInBoundaries(shell):
    uvs = pm.polyListComponentConversion(shell, tuv=True)
    uList = []
    vList = []

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

        # print 'uMax: ', uMax, 'uMin: ', uMin, 'vMax: ', vMax, 'vMin: ', vMin
        # print 'UV: ', u, v

    return True


def checkUVBoundaries(shell):
    uvs = pm.polyListComponentConversion(shell, tuv=True)
    uvTileRange = []

    uMax = 1
    uMin = 0
    vMax = 1
    vMin = 0
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
    uvs = pm.polyListComponentConversion(shell, tuv=True)

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


def recursiveCutUV(geo, stop=5):
    # pm.polyMapCut(faces, ch=False)
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


def setTexelDensity(geo, texelDensity=32, mapRes=1024):
    texSetTexelDensity = 'texSetTexelDensity ' + str(texelDensity) + ' ' + str(mapRes) + ';'
    pm.select(geo.f[:])
    mel.eval(texSetTexelDensity)


def uvLayoutNoScale(geoList, uCount, vCount, mapRes=1024):
    pm.u3dLayout(geoList, res=1024, mutations=2, rot=2, box=[0, 1, 0, 1], shellSpacing=0.0009765625,
                 tileMargin=0.001953125, layoutScaleMode=1, u=uCount, v=vCount)


def finalLayoutUV(geoList, area=1):
    tileValue = round(math.sqrt(area))
    uCount = tileValue if tileValue >= 1 else tileValue + 1
    vCount = tileValue if tileValue >= 1 else tileValue + 1
    i = 0

    uvLayoutNoScale(geoList, uCount, vCount)

    shellList = getUVShell(geoList)
    for shell in shellList:
        if not checkUVInBoundaries(shell):
            'Test!!!!!'
            uvLayoutNoScale(geoList, uCount, vCount)
            print 'UV count: ', uCount, vCount
            if i % 2:
                vCount += 1
            else:
                uCount += 1
            i += 1


def autoSeamUV(geo, angle=0):
    try:
        pm.u3dAutoSeam(geo, s=angle, p=1)  # s=0
    except:
        pm.unfold(geo)


def unfoldOptimizeUV(geo):
    # fixNonManifoldUV(geo)
    pm.u3dUnfold(geo, mapsize=1024, iterations=2, pack=0, borderintersection=True, triangleflip=True, roomspace=0)


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
        pm.polyAutoProjection(geo.f[:])

        # fi non Manifold UV
        fixNonManifoldUV(geo)

        # Auto Seam 1
        autoSeamUV(geo, autoSeam)

        # Unfold3D Optimize
        unfoldOptimizeUV(geo)

        # Layout
        pm.u3dLayout(geo, res=1024, mutations=1, rot=2, scl=1, box=[0, 1, 0, 1])

        # set Texel Density
        setTexelDensity(geo)

        # check UV boundaries
        recursiveCutUV(geo)

        pm.delete(geo, ch=1)

        area = area + pm.polyEvaluate(geo, uvArea=True)

    print 'Total Area: ', area, ' -- RoundUp: ', round(area)

    # Layout with TexelDensity
    finalLayoutUV(geoList, area)
    pm.select(geoList)


if __name__ == "__main__":
    geos = pm.ls(sl=True)
    autoUV(geos)
