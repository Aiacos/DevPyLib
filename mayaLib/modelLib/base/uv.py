import math

import maya.mel as mel
import pymel.core as pm


class AutoUV():

    def __init__(self, geoList=pm.ls(sl=True), mapRes=1024, texelDensity=16, autoSeamAngle=0,
                 autoProject=True, autoSeam=True, autoCutUV=True):
        """
        Initializes the AutoUV process for the given list of geometries.

        This method performs several UV operations on each geometry in the provided list.
        It can automatically fix non-manifold UVs, project UVs, create seams, unfold and optimize UVs,
        set texel density, layout UVs, and cut UV boundaries based on the specified parameters.

        Args:
            geoList (list): A list of geometries to process. Defaults to the current selection in Maya.
            mapRes (int): The resolution for the texture map. Defaults to 1024.
            texelDensity (float): The desired texel density for the UVs. Defaults to 16.
            autoSeamAngle (float): The angle threshold for automatic seam creation. Defaults to 0.
            autoProject (bool): If True, performs automatic UV projection. Defaults to True.
            autoSeam (bool): If True, creates seams automatically based on the angle. Defaults to True.
            autoCutUV (bool): If True, performs recursive cutting of UVs at boundaries. Defaults to True.
        """
        area = 0
        geoList = pm.ls(geoList)
        for geo in geoList:
            print(('Current Geo: ', geo.name()))

            # fix no-Manifold UV
            self.fixNonManifoldUV(geo)

            # Automatic Projection UV
            if autoProject:
                pm.select(geo)
                mel.eval('texNormalProjection 1 1 "" ;')
                #pm.polyAutoProjection(geo.f[:], lm=0, pb=0, ibd=1, cm=0, l=0, sc=0, o=0, p=6, ps=0.2, ws=0)

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
        """
        Checks whether all UVs in the given shell are within the boundaries of the UV tile.

        Args:
            shell (str): The name of the shell to check.

        Returns:
            bool: True if all UVs are within the boundaries, False otherwise.
        """
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
        """
        Determines the UV tile boundaries for the given UV shell.

        This function calculates the UV tile boundaries by converting the shell
        into its corresponding UV vertices and then determining the minimum and
        maximum U and V values for each tile. It collects all unique UV tiles
        that the shell occupies.

        Args:
            shell (str): The name of the UV shell to check.

        Returns:
            list: A list of UV tile boundaries, where each boundary is represented
                  as a list of four integers [uMin, uMax, vMin, vMax].
        """
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
        """
        Cuts the UV shell at the tile boundaries by selecting the UVs that fall within each tile and then
        calling the Maya command 'CreateUVShellAlongBorder' to create a new UV shell at the selected UVs.

        Args:
            shell (str): The name of the UV shell to cut at the tile boundaries.
        """
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
        """
        Recursively cuts the UV shells of the given geometry at the tile boundaries
        until all UV shells are within the tile boundaries.

        Args:
            geo (str): The name of the geometry to cut the UV shells of.
        """
        shellList = self.getUVShell(geo)
        for shell in shellList:
            if not self.checkUVInBoundaries(shell):
                self.cutUVTile(shell)
                # self.recursiveCutUV(geo)

    def getUVShell(self, geo):
        """
        Get a list of UV shells for the given geometry. This function returns a list of strings, where each string is a list of faces that make up a UV shell.

        Args:
            geo (str): The name of the geometry to get the UV shells of.

        Returns:
            list: A list of strings, where each string is a list of faces that make up a UV shell.
        """
        shellNumber = pm.polyEvaluate(geo, uvShell=True)
        shellList = []
        for i in range(shellNumber):
            shellFaces = pm.polyListComponentConversion(pm.polyEvaluate(geo, uvsInShell=i), toFace=True)
            shellList.append(shellFaces)

        return shellList

    def setTexelDensity(self, geo, texelDensity=10.24, mapRes=1024):
        """
        Set the texel density of the given geometry.

        Args:
            geo (str): The name of the geometry to set the texel density of.
            texelDensity (float): The desired texel density. Defaults to 10.24.
            mapRes (int): The resolution of the texture map. Defaults to 1024.
        """
        texSetTexelDensity = 'texSetTexelDensity ' + str(texelDensity) + ' ' + str(mapRes) + ';'
        pm.select(geo.f[:])
        mel.eval(texSetTexelDensity)

    def uvLayoutNoScale(self, geoList, uCount, vCount, mapRes=1024, iteration=1):
        """
        Arranges the UV shells of the given geometries without scaling.

        This function uses Maya's u3dLayout command to layout the UV shells of the provided
        list of geometries. The layout is performed without scaling the shells, while allowing
        for rotations and mutations to optimize the packing. The function also sets the box
        boundaries, shell spacing, tile margin, and layout scale mode.

        Args:
            geoList (list): A list of geometries to layout UVs for.
            uCount (int): The number of tiles in the U direction.
            vCount (int): The number of tiles in the V direction.
            mapRes (int, optional): The resolution for the texture map. Defaults to 1024.
            iteration (int, optional): The number of mutations to apply. Defaults to 1.
        """
        pm.u3dLayout(geoList, res=mapRes, mutations=iteration, rot=2, box=[0, 1, 0, 1], shellSpacing=0.0009765625,
                     tileMargin=0.001953125, layoutScaleMode=1, u=uCount, v=vCount, rst=90, rmn=0, rmx=360)
        pm.u3dLayout(geoList, res=mapRes, mutations=iteration, rot=2, box=[0, 1, 0, 1], shellSpacing=0.0009765625,
                     tileMargin=0.001953125, layoutScaleMode=1, u=uCount, v=vCount, rst=90, rmn=0, rmx=360)

    def uvLayoutFast(self, geo):
        """
        Perform a fast UV layout on the given geometry.

        This function uses Maya's u3dLayout command to quickly layout the UV shells of the
        provided geometry. The layout is performed without scaling the shells, while allowing
        for rotations and mutations to optimize the packing. The UV shells are then stacked
        and snapped to the bottom left corner of the UV space, and aligned to the minimum
        U and V values.

        Args:
            geo (str): The name of the geometry to layout UVs for.
        """
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
        """
        Perform a final layout of the UVs for the given geometry list.

        This method first calculates the number of tiles needed to fit all the UV shells
        in the given geometry list, and then calls the `uvLayoutNoScale` method to layout
        the UV shells. After the layout, it checks which shells are still outside of the
        UV boundaries and layouts them again with a smaller tile size.

        Args:
            geoList (list): A list of geometries to layout UVs for.
            area (float): The total area of the UV space. Defaults to 1.
        """
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
        """
        Automatically create seams for the given geometry based on the given angle.

        This method will call Maya's u3dAutoSeam command to create seams for the given geometry
        based on the given angle. If the command fails (for example, if the geometry has no UVs),
        it will do nothing.

        Args:
            geo (str): The name of the geometry to create seams for.
            angle (float): The angle threshold for creating seams. Defaults to 0.
        """
        try:
            pm.u3dAutoSeam(geo, s=angle, p=1)
        except:
            pass
            #pm.unfold(geo)

    def unfoldOptimizeUV(self, geo, normalizeShell=False):
        """
        Unfold and optimize the UVs of the given geometry.

        This method will call Maya's u3dUnfold command to unfold the UVs of the given geometry.
        The UVs are then optimized to reduce the number of UV islands and improve
        the packing of the UVs.

        Args:
            geo (str): The name of the geometry to unfold and optimize the UVs of.
            normalizeShell (bool, optional): If True, the UV shells are normalized after unfolding. Defaults to False.
        """
        pm.u3dUnfold(geo, mapsize=1024, iterations=2, pack=0, borderintersection=True, triangleflip=True, roomspace=0)
        if normalizeShell:
            shellList = self.getUVShell(geo)
            for shell in shellList:
                pm.polyNormalizeUV(shell, normalizeType=1, preserveAspectRatio=False, centerOnTile=True,
                                   normalizeDirection=0)

    def fixNonManifoldUV(self, geo):
        """
        Fix non-manifold UVs for the given geometry.

        This method will call Maya's polyCleanup command to fix non-manifold UVs
        for the given geometry. Non-manifold UVs are UVs that are not connected
        to any other UVs or have multiple connections to other UVs.

        Args:
            geo (str): The name of the geometry to fix non-manifold UVs for.
        """
        pm.select(geo)
        mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')
        pm.select(geo)
        mel.eval(
            'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };')


def transferUV(source, destination):
    """
    Transfer UVs from the source geometry to the destination geometry.

    This function uses Maya's transferAttributes command to copy UVs from the
    source geometry to the destination geometry. The UVs are transferred in the
    UV space specified by "map1" for both the source and destination.

    Args:
        source (str or list): The name or list of names of the source geometry
                              from which UVs are transferred.
        destination (str or list): The name or list of names of the destination
                                   geometry to which UVs are transferred.
    """
    source = pm.ls(source)[-1]
    destination = pm.ls(destination)[-1]

    pm.select(source)
    pm.select(destination, add=True)

    pm.transferAttributes(transferPositions=0, transferNormals=0, transferUVs=2, transferColors=2, sampleSpace=0,
                          searchMethod=3, flipUVs=0, colorBorders=1, sourceUvSpace="map1", targetUvSpace="map1")


def unwrella_unwrap_all(geo_list, keep_seam=True):
    """
    Unwrap UVs using the Unwrella plugin for a list of geometries.

    This function iterates over each geometry in the provided list and applies
    the Unwrella UV unwrapping technique. The unwrapping can either keep existing
    seams or not, based on the `keep_seam` parameter.

    Args:
        geo_list (list): A list of geometries to unwrap UVs for.
        keep_seam (bool): If True, existing seams are preserved during unwrapping.
                          If False, all seams are removed. Defaults to True.
    """
    for geo in geo_list:
        pm.select(geo)

        if keep_seam:
            mel.eval('unwrella -mc "map1" -t 0 -st 0.150000 -pad 2.000000 -w 1024 -h 1024 -ug 0 -ga 90.000000 -ur 0 -ra 90.000000 -ks 1 -tx 1 -ty 1 -p 1 -pr 1 -ro 1 -fr 0 -re 1 -c "" -ca 45.000000 -ce 0.000000 -co 0;')
        else:
            mel.eval('unwrella -mc "map1" -t 0 -st 0.150000 -pad 2.000000 -w 1024 -h 1024 -ug 0 -ga 90.000000 -ur 0 -ra 90.000000 -ks 0 -tx 1 -ty 1 -p 1 -pr 1 -ro 1 -fr 0 -re 1 -c "" -ca 45.000000 -ce 0.000000 -co 0;')



if __name__ == "__main__":
    geos = pm.ls(sl=True)
    a = AutoUV(geos)
