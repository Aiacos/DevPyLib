__author__ = 'Lorenzo Argentieri'

import os
import pymel.core as pm
from mayaLib.rigLib.utils import deform


class MuscleConnect():
    def __init__(self, mainSkinGeo, muscleGeo, muscleList=pm.ls('*_MUS'), rigModelGrp=None):
        if mainSkinGeo and muscleGeo:
            self.mainSkinGeo = pm.ls(mainSkinGeo)[0]
            self.mainMuscleGeo = pm.ls(muscleGeo)[0]
        else:
            print 'No valid Geo!'

        # apply Muscle Deformer
        self.cMuscleDeformer = deform.cMuscleSystemDeformer(self.mainMuscleGeo)

        # connect muscle
        deform.cMuscleConnectMuscle(self.mainMuscleGeo, muscleList)

        # duplicate Main Body
        muscleSkinBSGeo = pm.duplicate(self.mainSkinGeo, n='body_wrapped_GEO')
        # group and parent muscle mesh
        self.muscleDeformGrp = pm.group(self.mainMuscleGeo, muscleSkinBSGeo, n='muscleDeform_GRP', p=rigModelGrp)
        # Wrap main body with Muscle Body
        deform.wrapDeformer(muscleSkinBSGeo, self.mainMuscleGeo)

        # apply BlendShape
        deform.blendShapeDeformer(self.mainSkinGeo, muscleSkinBSGeo, 'muscleBS', frontOfChain=False)

        # set Attr for Muscle Deformer
        self.cMuscleDeformer.enableSmooth.set(1)
        self.cMuscleDeformer.smoothStrength.set(0)
        self.cMuscleDeformer.smoothExpand.set(10)
        self.cMuscleDeformer.smoothCompress.set(10)
        self.cMuscleDeformer.smoothHold.set(1)

        # ToDO:
        # generate wheights


class MuscleUtil():
    def __init__(self, muscleScriptPath='/Applications/Autodesk/maya2018/Maya.app/Contents/scripts/muscle/'):
        self.homePath = os.getenv("HOME")
        self.muscleScriptPath = muscleScriptPath

        skipSourceFileList = ['fixDeletedMuscle.mel']

        for file in os.listdir(self.muscleScriptPath):
            if file.endswith('.mel'):
                if not file in skipSourceFileList:
                    pm.mel.eval('source "' + os.path.join(self.muscleScriptPath, file) + '";')

    def mirrorMuscle(self, muscleSurface, usePymel=True):
        mus = pm.ls(muscleSurface)

        pm.select(mus)
        if usePymel:
            self.cMCUI_createMirrorPm(search='_L_', replace='_R_')
        else:
            pm.mel.eval('cMCUI_createMirror();')
            
        if (pm.objExists(pm.ls('*TEMPPASTE*'))):
            pm.delete(pm.ls('*TEMPPASTE*'))

    def mirrorAllMuscle(self, musclePattern='cMuscleSurface_*'):
        muscleList = pm.ls(musclePattern)
        for mus in muscleList:
            self.mirrorMuscle(mus)

    def cMCUI_createMirrorPm(self, search='l_', replace='r_', nAxis=0, musIdentifier='Mus'):
        if search == '' or replace == '':
            print 'no side specified!'
            return

        creators = pm.ls(pm.mel.eval('cMuscle_getSelectedDeformers("cMuscleCreator") ;'))
        for creator in creators:
            nMidControls = creator.nMidControls.get()
            nAround = creator.nAround.get()

            # We start by just mirroring the attach start/end points...then we "create" the muscle normally...
            # This way we get the same results as a normal build...but attached to what we want...then we do hand mirroring
            # of all the shapes/poses/attributes after...
            startLocs = pm.ls(pm.mel.eval('cMCUI_getMuscleItems({"' + creator.name() + '"}, "startLocs") ;'))
            endLocs = pm.ls(pm.mel.eval('cMCUI_getMuscleItems({"' + creator.name() + '"}, "endLocs") ;'))

            if len(startLocs) == 3 and len(endLocs) == 3:
                startLocA = pm.ls(pm.mel.eval('cMuscle_duplicateObject("' + startLocs[
                    1].name() + '", "' + search + '", "' + replace + '" , 1) ;'))[0]
                startLocB = pm.ls(pm.mel.eval('cMuscle_duplicateObject("' + startLocs[
                    2].name() + '", "' + search + '", "' + replace + '" , 1) ;'))[0]
                endLocA = pm.ls(pm.mel.eval(
                    'cMuscle_duplicateObject("' + endLocs[1].name() + '", "' + search + '", "' + replace + '" , 1) ;'))[
                    0]
                endLocB = pm.ls(pm.mel.eval(
                    'cMuscle_duplicateObject("' + endLocs[2].name() + '", "' + search + '", "' + replace + '" , 1) ;'))[
                    0]

                pm.mel.eval('cMuscle_mirrorObject("' + startLocA.name() + '", ' + str(nAxis) + ' ) ;')
                pm.mel.eval('cMuscle_mirrorObject("' + startLocB.name() + '", ' + str(nAxis) + ' ) ;')
                pm.mel.eval('cMuscle_mirrorObject("' + endLocA.name() + '", ' + str(nAxis) + ' ) ;')
                pm.mel.eval('cMuscle_mirrorObject("' + endLocB.name() + '", ' + str(nAxis) + ' ) ;')

                # Figure out proper basename by searching/replacing the main name of the creator they all have, as well as the # at the end...
                # And then finally searching/replacing for side...
                baseName = str(
                    pm.mel.eval('cMuscle_strSearchReplace("' + creator.name() + '", "cMuscleCreator", "") ;'))
                baseName = baseName[:baseName.rfind(musIdentifier) + len(musIdentifier)]
                endNumber = baseName[baseName.rfind(musIdentifier) + len(musIdentifier):]
                # print baseName, ' ', endNumber
                baseName = str(baseName).replace(search, replace, 1)
                ## endNumber = match("[0-9]+$", $creator) ;
                ## $baseName = cMuscle_strSearchReplace($baseName, $endNumber, "") ;
                ## $baseName = cMuscle_strSearchReplace($baseName, $search, $replace) ;
                pm.mel.eval('string $msg = (uiRes("m_cMuscleCreatorUI.kMirroringCreator"));')
                # $msg = `format -stringArg $creator -stringArg $baseName $msg`;
                # print ($msg) ;

                # Guess the attach parents..which should now be correct since we mirrored...
                ## string $parents[] ;
                parents = startLocA.getParent()
                attachStart = pm.ls(str(parents).replace('_L_', '_R_', 1))[0]
                parents = endLocA.getParent()
                attachEnd = pm.ls(str(parents).replace('_L_', '_R_', 1))[0]
                # $parents = `listRelatives -ni -parent $startLocA` ;
                # string $attachStart = $parents[0] ;
                # $parents = `listRelatives -ni -parent $endLocA` ;
                # string $attachEnd = $parents[0] ;

                # See if this muscle has a cMuscleObject on it....
                surfData = pm.mel.eval('cMCUI_getMuscleItems({"' + creator.name() + '"}, "surf") ;')
                mO = pm.ls(surfData)[2]
                if mO != '':
                    bHasMO = True
                else:
                    bHasMO = False

                # Now do the regular build....
                #
                # select -r $startLocA $startLocA $endLocA $endLocB ;
                pm.select(startLocA, startLocB, endLocA, endLocB, r=True)
                creatorData = pm.ls(pm.mel.eval(
                    'cMuscle_createCreatorMuscleFromSel("' + baseName + '", ' + str(nMidControls) + ', ' + str(
                        nAround) + ', "' + attachStart.name() + '", "' + attachEnd.name() + '", ' + str(
                        bHasMO).lower() + ' ) ;'))
                creatorNew = creatorData[0]

                # Whee..ok now the muscle is made...etc.. .but we need to do the copy/pasting of all the stuff...
                pm.mel.eval(
                    'cMCUI_copyPasteMuscle("' + creator.name() + '", "' + creatorNew.name() + '", true, "' + str(
                        nAxis) + '", "' + search + '", "' + replace + '") ;')

            else:
                print 'invalid startLoc or endLoc: ', startLocA, startLocB, endLocA, endLocB



