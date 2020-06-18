__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.fluidLib.base.baseFluid import BaseFluid
from mayaLib.fluidLib.utility import mathFunction

class FireSmoke(BaseFluid):
    """
    Fire Preset
    """

    def __init__(self, fluidName='', baseRes=32, emitObj=None):
        """
        Fire with Smoke Preset
        :param fluidName: str
        :param baseRes: int
        :param emitObj: str
        """
        BaseFluid.__init__(self, fluidName=fluidName, baseRes=baseRes, emitObj=emitObj)
        self.fluidContainer = BaseFluid.getFluidShape(self)

        self.fluidContainer.temperatureMethod.set(2)
        self.fluidContainer.fuelMethod.set(2)

        # Parameter
        self.setDensity()
        self.setVelocity()
        self.setTurbolence()
        self.setTemperature()
        self.setFuel()

        # Shading
        self.setShading()

        pm.select(self.fluidContainer)

    def setDensity(self):
        self.fluidContainer.densityDissipation.set(1)
        self.fluidContainer.densityTension.set(0.01)
        self.fluidContainer.tensionForce.set(0.05)
        self.fluidContainer.densityGradientForce.set(15)

    def setVelocity(self):
        self.fluidContainer.velocitySwirl.set(6)

    def setTurbolence(self):
        self.fluidContainer.turbulenceStrength.set(0.025)
        self.fluidContainer.turbulenceFrequency.set(0.5)
        self.fluidContainer.turbulenceSpeed.set(0.65)

    def setTemperature(self):
        self.fluidContainer.temperatureScale.set(2.5)
        self.fluidContainer.buoyancy.set(100)
        self.fluidContainer.temperatureDissipation.set(4)
        self.fluidContainer.temperatureDiffusion.set(0)
        self.fluidContainer.temperatureTurbulence.set(1)

    def setFuel(self):
        self.fluidContainer.reactionSpeed.set(1)
        self.fluidContainer.maxReactionTemp.set(0.01)
        self.fluidContainer.lightReleased.set(1)

    def setShading(self):
        self.fluidContainer.transparency.set(0.5, 0.5, 0.5, type="double3")
        self.fluidContainer.glowIntensity.set(0.075)

        # Density Color
        self.fluidContainer.color[0].color_Position.set(0)
        self.fluidContainer.color[0].color_Color.set(0.005, 0.005, 0.005, type="double3")

        self.fluidContainer.color[1].color_Position.set(1)
        self.fluidContainer.color[1].color_Color.set(0.5, 0.5, 0.5, type="double3")
        self.fluidContainer.colorInputBias.set(1)
        self.fluidContainer.colorInput.set(5)

        # Temperature Color
        self.fluidContainer.incandescence[0].incandescence_Position.set(0.8)
        self.fluidContainer.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")

        self.fluidContainer.incandescence[1].incandescence_Position.set(0.815)
        self.fluidContainer.incandescence[1].incandescence_Color.set(0.896, 0.201495, 0, type="double3")

        self.fluidContainer.incandescence[2].incandescence_Position.set(1)
        self.fluidContainer.incandescence[2].incandescence_Color.set(2.5, 1.666667, 0.5, type="double3")

        self.fluidContainer.incandescenceInputBias.set(0.9)

        # Opacity
        self.fluidContainer.opacityInput.set(6) # 5 Density / 6 Temperature
        self.opacityGraph()
        self.fluidContainer.opacityInputBias.set(0.35)

    def opacityGraph(self, sampling=20):
        step = 100/sampling
        for i in [round(x * 0.01, 4) for x in range(0, 100+1, step)]:
            y = mathFunction.repartFunction(i, l=15)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Position.set(i)
            self.fluidContainer.opacity[int(i * sampling)].opacity_FloatValue.set(y)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Interp.set(1)


if __name__ == '__main__':
    fire = FireSmoke()
