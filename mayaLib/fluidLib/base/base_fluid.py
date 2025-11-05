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
        fluid_shape (pymel.core.nodetypes.Fluid): The Fluid Shape Node.
        fluid_emit (pymel.core.nodetypes.FluidEmitter): The Fluid Emitter Node.
        fluid_transform (pymel.core.nodetypes.Transform): The Fluid Transform Node.
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

        self.fluid_shape = cont.get_container()[0]
        self.fluid_emit = emit.get_emitter()[0]
        self.fluid_transform = pm.listRelatives(self.fluid_shape, parent=True)

        if fluid_name != "":
            pm.rename(self.fluid_transform, fluid_name)

        # Connect Emitter to Fluid Container
        pm.connectDynamic(self.fluid_shape, em=self.fluid_emit)
        pm.parent(self.fluid_emit, self.fluid_shape)

        # Setup fluid shape
        self.setup_fluid_shape(base_res)

    def get_fluid_shape(self):
        """
        Returns the fluid shape node.

        Returns:
            pymel.core.nodetypes.Fluid: The fluid shape node.
        """
        return self.fluid_shape

    def get_fluid_emitter(self):
        """
        Returns the fluid emitter node.

        Returns:
            pymel.core.nodetypes.FluidEmitter: The fluid emitter node.
        """
        return self.fluid_emit

    def setup_fluid_shape(self, base_res=32):
        """
        Sets up the fluid shape node.

        Args:
            base_res (int): The base resolution of the fluid.
        """
        # Base Resolution
        self.fluid_shape.baseResolution.set(base_res)

        # Boundary settings
        self.fluid_shape.boundaryX.set(0)
        self.fluid_shape.boundaryY.set(2)
        self.fluid_shape.boundaryZ.set(0)

        # Solver settings
        self.fluid_shape.highDetailSolve.set(3)
        self.fluid_shape.substeps.set(2)
        self.fluid_shape.solverQuality.set(254)

        # Resize settings
        self.fluid_shape.autoResize.set(1)
        self.fluid_shape.maxResolution.set(base_res**2)
        self.fluid_shape.autoResizeMargin.set(4)

        # Lighting settings
        self.fluid_shape.selfShadowing.set(1)

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
            self.fluid_emit_string = (
                'fluidEmitter -pos 0 0 0 -type omni  -name \\"'
                + fluid_name
                + '#\\" -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
            )
        else:
            self.fluid_emit_string = "fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;"

        mel.eval(
            'dynExecFluidEmitterCommands 1 { "1", "'
            + self.fluid_emit_string
            + '", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;'
        )

        if fluid_name != "":
            self.fluid_emit_list = pm.ls(fluid_name + "?")
            self.fluid_shape_list = pm.ls("fluidShape?")
        else:
            self.fluid_emit_list = pm.ls("fluidEmitter?")
            self.fluid_shape_list = pm.ls("fluidShape?")

        self.fluid_emit = self.fluid_emit_list[-1]
        self.fluid_shape = self.fluid_shape_list[-1]


if __name__ == "__main__":
    f = BaseFluid()
