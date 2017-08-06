__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya.mel as mel

class BaseFluid():
    def __init__(self, fluidName='', baseRes=32):
        if fluidName != '':
            self.fluidEmitString = 'fluidEmitter -pos 0 0 0 -type omni  -name \\"' + fluidName + '#\\" -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
        else:
            self.fluidEmitString = 'fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'

        mel.eval('dynExecFluidEmitterCommands 1 { "1", "' + self.fluidEmitString + '", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;')

        if fluidName != '':
            self.fluidEmit_list = pm.ls(fluidName + '?')
            self.fluidShape_list = pm.ls('fluidShape?')
        else:
            self.fluidEmit_list = pm.ls('fluidEmitter?')
            self.fluidShape_list = pm.ls('fluidShape?')

        print self.fluidEmit_list
        self.fluidEmit = self.fluidEmit_list[-1]
        self.fluidShape = self.fluidShape_list[-1]

        print '/////////////////'
        print self.fluidEmit
        print self.fluidShape

        self.setupFluidShape(baseRes)

    def setupFluidShape(self, baseRes=32):
        # Base Resolution
        self.fluidShape.baseResolution.set(baseRes)

        # Boundary
        self.fluidShape.boundaryX.set(0)
        self.fluidShape.boundaryY.set(2)
        self.fluidShape.boundaryZ.set(0)

        # Solver
        self.fluidShape.highDetailSolve.set(3)
        self.fluidShape.substeps.set(2)
        self.fluidShape.solverQuality.set(254)

        # Resize
        self.fluidShape.autoResize.set(1)
        self.fluidShape.maxResolution.set(baseRes**2)
        self.fluidShape.autoResizeMargin.set(4)

        # Lighting
        self.fluidShape.selfShadowing.set(1)

    def setupEmitter():
        pass


if __name__ == '__main__':
    f = BaseFluid()
