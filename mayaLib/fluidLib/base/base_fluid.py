__author__ = "Lorenzo Argentieri"

"""Base fluid system combining containers and emitters.

Provides the BaseFluid class that composes FluidContainer and FlEmitter
to create complete fluid simulation setups.
"""

import maya.mel as mel
import pymel.core as pm

import mayaLib.fluidLib.base.base_container
import mayaLib.fluidLib.base.base_emitter


class BaseFluid(object):
    """
    Class for creating and managing a fluid container and emitter.

    Attributes:
        fluidShape (pymel.core.nodetypes.Fluid): The Fluid Shape Node.
        fluidEmit (pymel.core.nodetypes.FluidEmitter): The Fluid Emitter Node.
        fluidTransform (pymel.core.nodetypes.Transform): The Fluid Transform Node.
    """

    def __init__(self, fluid_name="", base_res=32, emit_obj=None):
        """
        Initializes the fluid container and emitter.

        Args:
            fluid_name (str): The name of the fluid.
            base_res (int): The base resolution of the fluid.
            emit_obj (str): The object to attach the emitter to.
        """
        # Create Fluid Container and Emitter
        cont = mayaLib.fluidLib.base.base_container.FluidContainer()
        emit = mayaLib.fluidLib.base.base_emitter.FlEmitter(obj=emit_obj)

        self.fluidShape = cont.get_container()[0]
        self.fluidEmit = emit.get_emitter()[0]
        self.fluidTransform = pm.listRelatives(self.fluidShape, parent=True)

        if fluid_name != "":
            pm.rename(self.fluidTransform, fluid_name)

        # Connect Emitter to Fluid Container
        pm.connectDynamic(self.fluidShape, em=self.fluidEmit)
        pm.parent(self.fluidEmit, self.fluidShape)

        # Setup fluid shape
        self.setup_fluid_shape(base_res)

    def get_fluid_shape(self):
        """
        Returns the fluid shape node.

        Returns:
            pymel.core.nodetypes.Fluid: The fluid shape node.
        """
        return self.fluidShape

    def get_fluid_emitter(self):
        """
        Returns the fluid emitter node.

        Returns:
            pymel.core.nodetypes.FluidEmitter: The fluid emitter node.
        """
        return self.fluidEmit

    def setup_fluid_shape(self, base_res=32):
        """
        Sets up the fluid shape node.

        Args:
            base_res (int): The base resolution of the fluid.
        """
        # Base Resolution
        self.fluidShape.baseResolution.set(base_res)

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
        self.fluidShape.maxResolution.set(base_res**2)
        self.fluidShape.autoResizeMargin.set(4)

        # Lighting settings
        self.fluidShape.selfShadowing.set(1)

    def setup_emitter(self):
        """
        Sets up the fluid emitter node.
        """
        pass

    def old_creator(self, fluid_name):
        """
        Legacy method for creating a fluid emitter.

        Args:
            fluid_name (str): The name of the fluid.
        """
        if fluid_name != "":
            self.fluidEmitString = (
                'fluidEmitter -pos 0 0 0 -type omni  -name \\"'
                + fluid_name
                + '#\\" -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
            )
        else:
            self.fluidEmitString = "fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;"

        mel.eval(
            'dynExecFluidEmitterCommands 1 { "1", "'
            + self.fluidEmitString
            + '", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;'
        )

        if fluid_name != "":
            self.fluidEmit_list = pm.ls(fluid_name + "?")
            self.fluidShape_list = pm.ls("fluidShape?")
        else:
            self.fluidEmit_list = pm.ls("fluidEmitter?")
            self.fluidShape_list = pm.ls("fluidShape?")

        self.fluidEmit = self.fluidEmit_list[-1]
        self.fluidShape = self.fluidShape_list[-1]


if __name__ == "__main__":
    f = BaseFluid()
