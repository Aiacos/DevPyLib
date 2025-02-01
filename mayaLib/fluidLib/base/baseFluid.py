__author__ = "Lorenzo Argentieri"

import maya.mel as mel
import pymel.core as pm

import mayaLib.fluidLib.base.baseContainer
import mayaLib.fluidLib.base.baseEmitter


class BaseFluid(object):
    """
    Class for creating and managing a fluid container and emitter.

    Attributes:
        fluidShape (pymel.core.nodetypes.Fluid): The Fluid Shape Node.
        fluidEmit (pymel.core.nodetypes.FluidEmitter): The Fluid Emitter Node.
        fluidTransform (pymel.core.nodetypes.Transform): The Fluid Transform Node.
    """

    def __init__(self, fluidName="", baseRes=32, emitObj=None):
        """
        Initializes the fluid container and emitter.

        Args:
            fluidName (str): The name of the fluid.
            baseRes (int): The base resolution of the fluid.
            emitObj (str): The object to attach the emitter to.
        """
        # Create Fluid Container and Emitter
        cont = mayaLib.fluidLib.base.baseContainer.FluidContainer()
        emit = mayaLib.fluidLib.base.baseEmitter.FlEmitter(obj=emitObj)

        self.fluidShape = cont.getContainer()[0]
        self.fluidEmit = emit.getEmitter()[0]
        self.fluidTransform = pm.listRelatives(self.fluidShape, parent=True)

        if fluidName != "":
            pm.rename(self.fluidTransform, fluidName)

        # Connect Emitter to Fluid Container
        pm.connectDynamic(self.fluidShape, em=self.fluidEmit)
        pm.parent(self.fluidEmit, self.fluidShape)

        # Setup fluid shape
        self.setupFluidShape(baseRes)

    def getFluidShape(self):
        """
        Returns the fluid shape node.

        Returns:
            pymel.core.nodetypes.Fluid: The fluid shape node.
        """
        return self.fluidShape

    def getFluidEmitter(self):
        """
        Returns the fluid emitter node.

        Returns:
            pymel.core.nodetypes.FluidEmitter: The fluid emitter node.
        """
        return self.fluidEmit

    def setupFluidShape(self, baseRes=32):
        """
        Sets up the fluid shape node.

        Args:
            baseRes (int): The base resolution of the fluid.
        """
        # Base Resolution
        self.fluidShape.baseResolution.set(baseRes)

        # Boundary settings
        self.fluidShape.boundaryX.set(0)
        self.fluidShape.boundaryY.set(2)
        self.fluidShape.boundaryZ.set(0)

        # Solver settings
        self.fluidShape.highDetailSolve.set(3)
        self.fluidShape.substeps.set(2)
        self.fluidShape.solverQuality.set(254)

        # Resize settings
        self.fluidShape.autoResize.set(1)
        self.fluidShape.maxResolution.set(baseRes**2)
        self.fluidShape.autoResizeMargin.set(4)

        # Lighting settings
        self.fluidShape.selfShadowing.set(1)

    def setupEmitter(self):
        """
        Sets up the fluid emitter node.
        """
        pass

    def oldCreator(self, fluidName):
        """
        Legacy method for creating a fluid emitter.

        Args:
            fluidName (str): The name of the fluid.
        """
        if fluidName != "":
            self.fluidEmitString = (
                'fluidEmitter -pos 0 0 0 -type omni  -name \\"'
                + fluidName
                + '#\\" -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
            )
        else:
            self.fluidEmitString = "fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;"

        mel.eval(
            'dynExecFluidEmitterCommands 1 { "1", "'
            + self.fluidEmitString
            + '", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;'
        )

        if fluidName != "":
            self.fluidEmit_list = pm.ls(fluidName + "?")
            self.fluidShape_list = pm.ls("fluidShape?")
        else:
            self.fluidEmit_list = pm.ls("fluidEmitter?")
            self.fluidShape_list = pm.ls("fluidShape?")

        self.fluidEmit = self.fluidEmit_list[-1]
        self.fluidShape = self.fluidShape_list[-1]


if __name__ == "__main__":
    f = BaseFluid()
