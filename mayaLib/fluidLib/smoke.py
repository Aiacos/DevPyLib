__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.fluidLib.base.baseFluid import BaseFluid
from mayaLib.fluidLib.utility import densityColor
from mayaLib.fluidLib.utility import mathFunction


class WispySmoke(BaseFluid):
    """
    Wispy Smoke Preset
    """

    def __init__(self, fluidName='', baseRes=32, emitObj=None):
        """
        Wispy Smoke Preset
        :param fluidName: str
        :param baseRes: int
        :param emitObj: str
        """
        BaseFluid.__init__(self, fluidName=fluidName, baseRes=baseRes, emitObj=emitObj)
        self.fluidContainer = BaseFluid.getFluidShape(self)
        self.fluidEmitter = BaseFluid.getFluidEmitter(self)

        self.setEmitter()

        # Update Dynamic Simulation
        self.fluidContainer.viscosity.set(0.125)
        self.fluidContainer.simulationRateScale.set(2)
        self.fluidContainer.emitInSubsteps.set(1)

        # Parameter
        self.setDensity()
        self.setVelocity()
        self.setTurbolence()

        # Shading
        self.setShading()

        pm.select(self.fluidContainer)

    def setEmitter(self):
        self.fluidEmitter.rate.set(250)
        self.fluidEmitter.maxDistance.set(0.2)
        self.fluidEmitter.fluidDensityEmission.set(2.5)

    def setDensity(self):
        self.fluidContainer.densityScale.set(0.65)
        self.fluidContainer.densityBuoyancy.set(25)
        self.fluidContainer.densityDissipation.set(0.15)

        self.fluidContainer.densityTension.set(0.025)
        self.fluidContainer.tensionForce.set(0.1)
        self.fluidContainer.densityGradientForce.set(10)

    def setVelocity(self):
        self.fluidContainer.velocitySwirl.set(5)

    def setTurbolence(self):
        pm.setKeyframe(self.fluidContainer, attribute='turbulenceStrength', time=1, value=5)
        pm.setKeyframe(self.fluidContainer, attribute='turbulenceStrength', time=12, value=0.1)
        self.fluidContainer.turbulenceFrequency.set(0.5)
        self.fluidContainer.turbulenceSpeed.set(0.5)

    def setShading(self):
        self.fluidContainer.transparency.set(0.214037, 0.214037, 0.214037, type="double3")
        self.fluidContainer.edgeDropoff.set(0)

        # Density Color
        dr, dg, db = densityColor.wispySmokeColor()
        self.fluidContainer.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluidContainer.colorInput.set(0)  # Constant

        # Opacity
        self.fluidContainer.opacityInput.set(5)  # density
        self.opacityGraph()
        self.fluidContainer.opacityInputBias.set(0.4)

    def opacityGraph(self):
        self.fluidContainer.opacity[0].opacity_Position.set(0)
        self.fluidContainer.opacity[0].opacity_FloatValue.set(0)
        self.fluidContainer.opacity[0].opacity_Interp.set(3)

        self.fluidContainer.opacity[1].opacity_Position.set(0.25)
        self.fluidContainer.opacity[1].opacity_FloatValue.set(0.1)
        self.fluidContainer.opacity[1].opacity_Interp.set(3)

        self.fluidContainer.opacity[2].opacity_Position.set(0.5)
        self.fluidContainer.opacity[2].opacity_FloatValue.set(0.5)
        self.fluidContainer.opacity[2].opacity_Interp.set(3)

        self.fluidContainer.opacity[3].opacity_Position.set(0.75)
        self.fluidContainer.opacity[3].opacity_FloatValue.set(0.1)
        self.fluidContainer.opacity[3].opacity_Interp.set(3)

        self.fluidContainer.opacity[4].opacity_Position.set(1)
        self.fluidContainer.opacity[4].opacity_FloatValue.set(0)
        self.fluidContainer.opacity[4].opacity_Interp.set(3)


class ThickSmoke(BaseFluid):
    """
    Thick Smoke Preset
    """

    def __init__(self, fluidName='', baseRes=32, emitObj=None):
        """
        Thick Smoke Preset
        :param fluidName: str
        :param baseRes: int
        :param emitObj: str
        """
        BaseFluid.__init__(self, fluidName=fluidName, baseRes=baseRes, emitObj=emitObj)
        self.fluidContainer = BaseFluid.getFluidShape(self)
        self.fluidEmitter = BaseFluid.getFluidEmitter(self)

        self.setEmitter()

        # Update Dynamic Simulation
        self.fluidContainer.viscosity.set(0.005)
        self.fluidContainer.velocityDamp.set(0.025)
        self.fluidContainer.emitInSubsteps.set(1)

        # Parameter
        self.setDensity()
        self.setVelocity()
        self.setTurbolence()

        # Shading
        self.setShading()

        pm.select(self.fluidContainer)

    def setEmitter(self):
        self.fluidEmitter.fluidDensityEmission.set(6)
        self.fluidEmitter.turbulence.set(8)
        self.fluidEmitter.turbulenceSpeed.set(0.25)
        self.fluidEmitter.detailTurbulence.set(1)

    def setDensity(self):
        self.fluidContainer.densityScale.set(0.5)
        self.fluidContainer.densityBuoyancy.set(10)
        self.fluidContainer.densityDissipation.set(0.2)
        self.fluidContainer.densityPressure.set(1.25)
        self.fluidContainer.densityPressureThreshold.set(0.1)
        self.fluidContainer.densityNoise.set(0.1)

        self.fluidContainer.densityTension.set(0.010)
        self.fluidContainer.tensionForce.set(0.05)
        self.fluidContainer.densityGradientForce.set(35)

    def setVelocity(self):
        self.fluidContainer.velocitySwirl.set(6)
        self.fluidContainer.velocityNoise.set(1)

    def setTurbolence(self):
        self.fluidContainer.turbulenceStrength.set(0.35)
        self.fluidContainer.turbulenceFrequency.set(0.5)
        self.fluidContainer.turbulenceSpeed.set(0.5)

    def setShading(self):
        self.fluidContainer.transparency.set(0.380057, 0.380057, 0.380057, type="double3")
        self.fluidContainer.edgeDropoff.set(0)

        # Density Color
        dr, dg, db = densityColor.wispySmokeColor()
        self.fluidContainer.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluidContainer.colorInput.set(0)  # Constant

        # Opacity
        self.fluidContainer.opacityInput.set(5)  # density
        self.opacityGraph()
        self.fluidContainer.opacityInputBias.set(0.4)

    def opacityGraph(self, sampling=20):
        step = 100 / sampling
        for i in [round(x * 0.01, 4) for x in range(0, 100 + 1, step)]:
            y = mathFunction.repartFunction(i, l=15)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Position.set(i)
            self.fluidContainer.opacity[int(i * sampling)].opacity_FloatValue.set(y)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Interp.set(1)


if __name__ == '__main__':
    wsmoke = WispySmoke()
    tsmoke = ThickSmoke()
