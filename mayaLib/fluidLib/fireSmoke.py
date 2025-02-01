"""
Fire with Smoke Preset

This class is a preset for creating fire with smoke simulations
"""

__author__ = "Lorenzo Argentieri"

from mayaLib.fluidLib.base.baseFluid import BaseFluid
from mayaLib.fluidLib.utility import mathFunction


class FireSmoke(BaseFluid):
    """
    Fire with Smoke Preset

    This class is a preset for creating fire with smoke simulations
    """

    def __init__(self, fluidName="", baseRes=32, emitObj=None):
        """
        Fire with Smoke Preset

        Args:
            fluidName (str): The name of the fluid.
            baseRes (int): The base resolution of the fluid.
            emitObj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluidName=fluidName, baseRes=baseRes, emitObj=emitObj)
        self.fluidContainer = BaseFluid.getFluidShape(self)

        # Set the temperature method to 2, which is the heat method.
        self.fluidContainer.temperatureMethod.set(2)
        # Set the fuel method to 2, which is the standard fuel method.
        self.fluidContainer.fuelMethod.set(2)

        # Set the density parameters.
        self.setDensity()
        # Set the velocity parameters.
        self.setVelocity()
        # Set the turbolence parameters.
        self.setTurbolence()
        # Set the temperature parameters.
        self.setTemperature()
        # Set the fuel parameters.
        self.setFuel()

        # Set the shading parameters.
        self.setShading()

    def setDensity(self):
        """
        Set the density parameters.
        """
        # Set the density dissipation to 1.
        self.fluidContainer.densityDissipation.set(1)
        # Set the density tension to 0.01.
        self.fluidContainer.densityTension.set(0.01)
        # Set the tension force to 0.05.
        self.fluidContainer.tensionForce.set(0.05)
        # Set the density gradient force to 15.
        self.fluidContainer.densityGradientForce.set(15)

    def setVelocity(self):
        """
        Set the velocity parameters.
        """
        # Set the velocity swirl to 6.
        self.fluidContainer.velocitySwirl.set(6)

    def setTurbolence(self):
        """
        Set the turbolence parameters.
        """
        # Set the turbolence strength to 0.025.
        self.fluidContainer.turbulenceStrength.set(0.025)
        # Set the turbolence frequency to 0.5.
        self.fluidContainer.turbulenceFrequency.set(0.5)
        # Set the turbolence speed to 0.65.
        self.fluidContainer.turbulenceSpeed.set(0.65)

    def setTemperature(self):
        """
        Set the temperature parameters.
        """
        # Set the temperature scale to 2.5.
        self.fluidContainer.temperatureScale.set(2.5)
        # Set the buoyancy to 100.
        self.fluidContainer.buoyancy.set(100)
        # Set the temperature dissipation to 4.
        self.fluidContainer.temperatureDissipation.set(4)
        # Set the temperature diffusion to 0.
        self.fluidContainer.temperatureDiffusion.set(0)
        # Set the temperature turbolence to 1.
        self.fluidContainer.temperatureTurbulence.set(1)

    def setFuel(self):
        """
        Set the fuel parameters.
        """
        # Set the reaction speed to 1.
        self.fluidContainer.reactionSpeed.set(1)
        # Set the max reaction temperature to 0.01.
        self.fluidContainer.maxReactionTemp.set(0.01)
        # Set the light released to 1.
        self.fluidContainer.lightReleased.set(1)

    def setShading(self):
        """
        Set the shading parameters.
        """
        # Set the transparency to 0.5.
        self.fluidContainer.transparency.set(0.5, 0.5, 0.5, type="double3")
        # Set the glow intensity to 0.075.
        self.fluidContainer.glowIntensity.set(0.075)

        # Set the density color.
        self.fluidContainer.color[0].color_Position.set(0)
        self.fluidContainer.color[0].color_Color.set(0.005, 0.005, 0.005, type="double3")

        self.fluidContainer.color[1].color_Position.set(1)
        self.fluidContainer.color[1].color_Color.set(0.5, 0.5, 0.5, type="double3")
        self.fluidContainer.colorInputBias.set(1)
        self.fluidContainer.colorInput.set(5)

        # Set the temperature color.
        self.fluidContainer.incandescence[0].incandescence_Position.set(0.8)
        self.fluidContainer.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")

        self.fluidContainer.incandescence[1].incandescence_Position.set(0.815)
        self.fluidContainer.incandescence[1].incandescence_Color.set(0.896, 0.201495, 0, type="double3")

        self.fluidContainer.incandescence[2].incandescence_Position.set(1)
        self.fluidContainer.incandescence[2].incandescence_Color.set(2.5, 1.666667, 0.5, type="double3")

        self.fluidContainer.incandescenceInputBias.set(0.9)

        # Set the opacity.
        self.fluidContainer.opacityInput.set(6)  # 5 Density / 6 Temperature
        self.opacityGraph()
        self.fluidContainer.opacityInputBias.set(0.35)

    def opacityGraph(self, sampling=20):
        """
        Set the opacity graph.

        Args:
            sampling (int): The number of samples for the graph.
        """
        step = int(100 / sampling)
        for i in [round(x * 0.01, 4) for x in range(0, 100 + 1, step)]:
            y = mathFunction.repart_function(i, l=15)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Position.set(i)
            self.fluidContainer.opacity[int(i * sampling)].opacity_FloatValue.set(y)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Interp.set(1)


if __name__ == "__main__":
    fire = FireSmoke()
