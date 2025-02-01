__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.fluidLib.base.baseFluid import BaseFluid
from mayaLib.fluidLib.utility import densityColor
from mayaLib.fluidLib.utility import mathFunction


class Fire(BaseFluid):
    """
    Fire Preset
    """

    def __init__(self, fluidName='', baseRes=32, emitObj=None):
        """Constructor for the Fire class.

        Args:
            fluidName (str): The name of the fluid.
            baseRes (int): The base resolution of the fluid.
            emitObj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluidName=fluidName, baseRes=baseRes, emitObj=emitObj)
        self.fluidContainer = BaseFluid.getFluidShape(self)

        self.fluidContainer.temperatureMethod.set(2)
        self.fluidContainer.fuelMethod.set(2)

        # Update Dynamic Simulation
        self.fluidContainer.viscosity.set(0.005)
        self.fluidContainer.velocityDamp.set(0.01)
        self.fluidContainer.simulationRateScale.set(2)
        self.fluidContainer.emitInSubsteps.set(1)

        # Parameter
        self.setDensity()
        self.setVelocity()
        self.setTurbolence()
        self.setTemperature()

        # Shading
        self.setShading()

        pm.select(self.fluidContainer)

    def setDensity(self):
        """Set the density parameters."""
        self.fluidContainer.densityBuoyancy.set(2.5)
        self.fluidContainer.densityDissipation.set(2.5)

        self.fluidContainer.densityTension.set(0.01)
        self.fluidContainer.tensionForce.set(0.05)
        self.fluidContainer.densityGradientForce.set(15)

    def setVelocity(self):
        """Set the velocity parameters."""
        self.fluidContainer.velocitySwirl.set(2.5)

    def setTurbolence(self):
        """Set the turbolence parameters."""
        self.fluidContainer.turbulenceStrength.set(0.25)
        self.fluidContainer.turbulenceFrequency.set(0.5)
        self.fluidContainer.turbulenceSpeed.set(0.65)

    def setTemperature(self):
        """Set the temperature parameters."""
        self.fluidContainer.temperatureScale.set(2)
        self.fluidContainer.buoyancy.set(15)
        self.fluidContainer.temperatureDissipation.set(2.5)
        self.fluidContainer.temperatureDiffusion.set(0.01)
        self.fluidContainer.temperatureTurbulence.set(2.5)
        self.fluidContainer.temperatureNoise.set(0.25)

    def setShading(self):
        """Set the shading parameters."""
        self.fluidContainer.transparency.set(0.5, 0.5, 0.5, type="double3")
        self.fluidContainer.glowIntensity.set(0.075)

        # Density Color
        dr, dg, db = densityColor.smokeColor()
        self.fluidContainer.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluidContainer.colorInput.set(5)

        # Temperature Color
        self.fluidContainer.incandescence[0].incandescence_Position.set(0.5)
        self.fluidContainer.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")
        self.fluidContainer.incandescence[0].incandescence_Interp.set(3)

        self.fluidContainer.incandescence[1].incandescence_Position.set(0.75)
        self.fluidContainer.incandescence[1].incandescence_Color.set(0.896, 0.201495, 0, type="double3")
        self.fluidContainer.incandescence[1].incandescence_Interp.set(3)

        self.fluidContainer.incandescence[2].incandescence_Position.set(1)
        self.fluidContainer.incandescence[2].incandescence_Color.set(2.5, 1.666667, 0.5, type="double3")
        self.fluidContainer.incandescence[2].incandescence_Interp.set(3)

        self.fluidContainer.incandescenceInputBias.set(0.8)

        # Opacity
        self.fluidContainer.opacityInput.set(5)  # density
        self.opacityGraph()
        self.fluidContainer.opacityInputBias.set(0.35)

    def opacityGraph(self, sampling=20):
        """
        Create an opacity graph for the fire.

        The opacity graph is a simple curve that goes from 0 to 1 and then
        comes back to 0. It is used to fade out the fire at the end of its
        lifespan.

        Args:
            sampling (int): The number of points to sample in the opacity
                graph. Defaults to 20.
        """
        step = int(100 / sampling)
        for i in [round(x * 0.01, 4) for x in range(0, 100 + 1, step)]:
            y = mathFunction.laplace_distribution2(i)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Position.set(i)
            self.fluidContainer.opacity[int(i * sampling)].opacity_FloatValue.set(y)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Interp.set(1)


if __name__ == '__main__':
    fire = Fire()