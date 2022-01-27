import math

import maya.mel as mel
import pymel.core as pm


class AutoUV():

    def __init__(self, geoList=pm.ls(sl=True), mapRes=1024, texelDensity=16, autoSeamAngle=0,
                 autoProject=True, autoSeam=True, autoCutUV=True):
        """

        :param geoList:
        :param mapRes:
        :param texelDensity:
        :param autoSeamAngle:
        :param autoProject:
        :param autoSeam:
        :param autoCutUV:
        """

        area = 0

        for geo in geoList:
            print(('Current Geo: ', geo.name()))

            # fi non Manifold UV
            self.fixNonManifoldUV(geo)

            # Automatic Projection UV
            if autoProject:
                pm.polyAutoProjection(geo.f[:], lm=0, pb=0, ibd=1, cm=0, l=0, sc=0, o=0, p=6, ps=0.2, ws=0)

            # Auto Seam 1
            if autoSeam:
                self.autoSeamUV(geo, autoSeamAngle)

            # Unfold3D Optimize
            self.unfoldOptimizeUV(geo)

            # set Texel Density
            self.setTexelDensity(geo, texelDensity, mapRes)

            # Layout
            self.uvLayoutFast(geo)

            # check UV boundaries
            if autoCutUV:
                self.recursiveCutUV(geo)

            # delete history
            pm.delete(geo, ch=1)

            area = area + pm.polyEvaluate(geo, uvArea=True)

        print(('Total Area: ', area, ' -- RoundUp: ', math.ceil(area)))
        # Layout with TexelDensity
        self.finalLayoutUV(geoList, area)
        # pm.select(geoList)

        print('Auto UV Complete!')

    def checkUVInBoundaries(self, shell):
        uvs = pm.polyListComponentConversion(shell, tuv=True)

        uMax = 1
        uMin = 0
        vMax = 1
        vMin = 0
        for i, uv in zip(list(range(len(pm.ls(uvs, fl=True)))), pm.ls(uvs, fl=True)):
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

    def checkUVBoundaries(self, shell):
        uvs = pm.polyListComponentConversion(shell, tuv=True)
        uvTileRange = []

        for i, uv in zip(list(range(len(pm.ls(uvs, fl=True)))), pm.ls(uvs, fl=True)):
            u, v = pm.polyEditUV(uv, q=True, u=True, v=True)

            uMax = int(u) + 1
            uMin = int(u)

            vMax = int(v) + 1
            vMin = int(v)

            tile = [uMin, uMax, vMin, vMax]
            if tile not in uvTileRange:
                uvTileRange.append([uMin, uMax, vMin, vMax])

        return uvTileRange

    def cutUVTile(self, shell):
        for tile in self.checkUVBoundaries(shell):
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

    def recursiveCutUV(self, geo):
        shellList = self.getUVShell(geo)
        for shell in shellList:
            if not self.checkUVInBoundaries(shell):
                self.cutUVTile(shell)
                # self.recursiveCutUV(geo)

    def getUVShell(self, geo):
        shellNumber = pm.polyEvaluate(geo, uvShell=True)
        shellList = []
        for i in range(shellNumber):
            shellFaces = pm.polyListComponentConversion(pm.polyEvaluate(geo, uvsInShell=i), toFace=True)
            shellList.append(shellFaces)

        return shellList

    def setTexelDensity(self, geo, texelDensity=10.24, mapRes=1024):
        texSetTexelDensity = 'texSetTexelDensity ' + str(texelDensity) + ' ' + str(mapRes) + ';'
        pm.select(geo.f[:])
        mel.eval(texSetTexelDensity)

    def uvLayoutNoScale(self, geoList, uCount, vCount, mapRes=1024, iteration=1):
        pm.u3dLayout(geoList, res=mapRes, mutations=iteration, rot=2, box=[0, 1, 0, 1], shellSpacing=0.0009765625,
                     tileMargin=0.001953125, layoutScaleMode=1, u=uCount, v=vCount, rst=90, rmn=0, rmx=360)

    def uvLayoutFast(self, geo):
        pm.u3dLayout(geo, res=256, mutations=1, rot=2, scl=0, box=[0, 1, 0, 1], shellSpacing=0.0009765625,
                     tileMargin=0.0009765625, layoutScaleMode=1)

        shellList = self.getUVShell(geo)
        pm.select(shellList)
        mel.eval('texStackShells {};')
        mel.eval('texSnapShells bottomLeft;')
        mel.eval('texAlignShells minV {} "";')
        mel.eval('texAlignShells minU {} "";')

        pm.polyEditUV(shellList, u=0.001, v=0.001)

    def finalLayoutUV(self, geoList, area=1):
        tileNumber = math.ceil(area)
        tileValue = tileNumber / 2
        uCount = tileValue if tileValue % 2 else tileValue + 1
        vCount = tileValue + 1

        print(('UV: ', math.ceil(uCount), math.ceil(vCount)))
        self.uvLayoutNoScale(geoList, math.ceil(uCount), math.ceil(vCount))

        badShellList = []
        for geo in geoList:
            for shell in self.getUVShell(geo):
                if not self.checkUVInBoundaries(shell):
                    badShellList.append(shell)
        if len(badShellList) > 0:
            print('Bad Shells')
            self.uvLayoutNoScale(badShellList, 1, 1)
            pm.polyEditUV(badShellList, u=0, v=vCount)

    def autoSeamUV(self, geo, angle=0):
        try:
            pm.u3dAutoSeam(geo, s=angle, p=1)  # s=0
        except:
            pm.unfold(geo)

    def unfoldOptimizeUV(self, geo, normalizeShell=False):
        pm.u3dUnfold(geo, mapsize=1024, iterations=2, pack=0, borderintersection=True, triangleflip=True, roomspace=0)
        if normalizeShell:
            shellList = self.getUVShell(geo)
            for shell in shellList:
                pm.polyNormalizeUV(shell, normalizeType=1, preserveAspectRatio=False, centerOnTile=True,
                                   normalizeDirection=0)

    def fixNonManifoldUV(self, geo):
        pm.select(geo)
        mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')


def transferUV(source, destination):
    source = pm.ls(source)[-1]
    destination = pm.ls(destination)[-1]

    pm.select(source)
    pm.select(destination, add=True)

    pm.transferAttributes(transferPositions=0, transferNormals=0, transferUVs=2, transferColors=2, sampleSpace=0,
                          searchMethod=3, flipUVs=0, colorBorders=1, sourceUvSpace="map1", targetUvSpace="map1")


def unwrella_unwrap_all(geo_list, keep_seam=True):
    for geo in geo_list:
        pm.select(geo)

        if keep_seam:
            mel.eval('unwrella -mc "map1" -t 0 -st 0.150000 -pad 2.000000 -w 1024 -h 1024 -ug 0 -ga 90.000000 -ur 0 -ra 90.000000 -ks 1 -tx 1 -ty 1 -p 1 -pr 1 -ro 1 -fr 0 -re 1 -c "" -ca 45.000000 -ce 0.000000 -co 0;')
        else:
            mel.eval('unwrella -mc "map1" -t 0 -st 0.150000 -pad 2.000000 -w 1024 -h 1024 -ug 0 -ga 90.000000 -ur 0 -ra 90.000000 -ks 0 -tx 1 -ty 1 -p 1 -pr 1 -ro 1 -fr 0 -re 1 -c "" -ca 45.000000 -ce 0.000000 -co 0;')



if __name__ == "__main__":
    geos = pm.ls(sl=True)
    a = AutoUV(geos)
