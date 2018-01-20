__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya.mel as mel

import mayaLib.fluidLib.base.baseEmitter
import mayaLib.fluidLib.base.baseContainer


class BaseFluid():
    """
    Create Fluid Container and Emitter
    """

    def __init__(self, fluidName='', baseRes=32, emitObj=None):
        """
        Create Fluid Container and Emitter
        :param fluidName: str
        :param baseRes: int
        :param emitObj: str
        """
        # Create Fluid Container and Emitter
        cont = mayaLib.fluidLib.base.baseContainer.FluidContainer()
        emit = mayaLib.fluidLib.base.baseEmitter.FlEmitter(obj=emitObj)

        self.fluidShape = cont.getContainer()[0]
        self.fluidEmit = emit.getEmitter()[0]
        self.fluidTransform = pm.listRelatives(self.fluidShape, parent=True)

        if fluidName != None:
            if fluidName != '':
                pm.rename(self.fluidTransform, fluidName)

        # Connect Emitter to Fluid Container
        pm.connectDynamic(self.fluidShape, em=self.fluidEmit)
        pm.parent(self.fluidEmit, self.fluidShape)

        # Setup
        self.setupFluidShape(baseRes)

    def getFluidShape(self):
        return self.fluidShape

    def getFluidEmitter(self):
        return self.fluidEmit

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

    def setupEmitter(self):
        pass

    def oldCreator(self, fluidName):
        if fluidName != '':
            self.fluidEmitString = 'fluidEmitter -pos 0 0 0 -type omni  -name \\"' + fluidName + '#\\" -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
        else:
            self.fluidEmitString = 'fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
        mel.eval(
            'dynExecFluidEmitterCommands 1 { "1", "' + self.fluidEmitString + '", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;')
        if fluidName != '':
            self.fluidEmit_list = pm.ls(fluidName + '?')
            self.fluidShape_list = pm.ls('fluidShape?')
        else:
            self.fluidEmit_list = pm.ls('fluidEmitter?')
            self.fluidShape_list = pm.ls('fluidShape?')
        self.fluidEmit = self.fluidEmit_list[-1]
        self.fluidShape = self.fluidShape_list[-1]


if __name__ == '__main__':
    f = BaseFluid()
