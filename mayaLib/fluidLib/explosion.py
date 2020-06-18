__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.fluidLib.base.baseFluid import BaseFluid
from mayaLib.fluidLib.utility import mathFunction
from mayaLib.fluidLib.utility import densityColor

class Explosion(BaseFluid):
    """
    Explosion Preset
    """

    def __init__(self, fluidName='', baseRes=32, emitObj=None):
        """
        Explosion Preset
        :param fluidName: str
        :param baseRes: int
        :param emitObj: str
        """
        BaseFluid.__init__(self, fluidName=fluidName, baseRes=baseRes, emitObj=emitObj)
        self.fluidContainer = BaseFluid.getFluidShape(self)
        self.fluidEmitter = BaseFluid.getFluidEmitter(self)

        # Update Emitter Type
        if emitObj == None:
            self.fluidEmitter.emitterType.set(4)
            self.fluidEmitter.volumeShape.set(1)

        self.setEmitter()

        # Update Dynamic Simulation
        self.fluidContainer.velocityDamp.set(0.025)
        self.fluidContainer.simulationRateScale.set(2.5)

        # Add Temperature and Fuel
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

    def setEmitter(self, startFrame=1):
        pm.setKeyframe(self.fluidEmitter, attribute='fluidDensityEmission', time=1, value=8)
        pm.setKeyframe(self.fluidEmitter, attribute='fluidDensityEmission', time=6, value=0)

        pm.setKeyframe(self.fluidEmitter, attribute='fluidHeatEmission', time=1, value=5)
        pm.setKeyframe(self.fluidEmitter, attribute='fluidHeatEmission', time=6, value=0)

        pm.setKeyframe(self.fluidEmitter, attribute='fluidFuelEmission', time=1, value=5)
        pm.setKeyframe(self.fluidEmitter, attribute='fluidFuelEmission', time=6, value=0)

        self.fluidEmitter.turbulence.set(6)
        self.fluidEmitter.turbulenceSpeed.set(0.25)
        self.fluidEmitter.detailTurbulence.set(1)


    def setDensity(self):
        self.fluidContainer.densityScale.set(0.75)
        self.fluidContainer.densityBuoyancy.set(2.5)
        self.fluidContainer.densityDissipation.set(1.5)

        self.fluidContainer.densityNoise.set(0.1)
        self.fluidContainer.densityGradientForce.set(35)


    def setVelocity(self):
        # self.fluidContainer.velocitySwirl.set(6) # al frame 1
        pm.setKeyframe(self.fluidContainer, attribute='velocitySwirl', time=1, value=6)
        #self.fluidContainer.velocitySwirl.set(2.5) # al frame 50
        pm.setKeyframe(self.fluidContainer, attribute='velocitySwirl', time=50, value=2.5)
        self.fluidContainer.velocityNoise.set(1)

    def setTurbolence(self):
        #self.fluidContainer.turbulenceStrength.set(3.5) # al frame 1
        pm.setKeyframe(self.fluidContainer, attribute='turbulenceStrength', time=1, value=3.5)
        #self.fluidContainer.turbulenceStrength.set(0.1) # al frame 6
        pm.setKeyframe(self.fluidContainer, attribute='turbulenceStrength', time=6, value=0.1)
        self.fluidContainer.turbulenceFrequency.set(0.5)
        self.fluidContainer.turbulenceSpeed.set(0.5)

    def setTemperature(self):
        self.fluidContainer.temperatureScale.set(2.5)

        #self.fluidContainer.buoyancy.set(1) # frame 1
        pm.setKeyframe(self.fluidContainer, attribute='buoyancy', time=1, value=1)
        #self.fluidContainer.buoyancy.set(125) #frame 10
        pm.setKeyframe(self.fluidContainer, attribute='buoyancy', time=10, value=125)

        #self.fluidContainer.temperaturePressure.set(0)# frame 1
        pm.setKeyframe(self.fluidContainer, attribute='temperaturePressure', time=1, value=0)
        #self.fluidContainer.temperaturePressure.set(6)# frame 3
        pm.setKeyframe(self.fluidContainer, attribute='temperaturePressure', time=3, value=6)
        #self.fluidContainer.temperaturePressure.set(0)# temperaturePressure 6
        pm.setKeyframe(self.fluidContainer, attribute='temperaturePressure', time=6, value=0)
        self.fluidContainer.temperaturePressureThreshold.set(0.5)

        self.fluidContainer.temperatureDissipation.set(1)
        self.fluidContainer.temperatureDiffusion.set(0.1)
        self.fluidContainer.temperatureTurbulence.set(6)
        self.fluidContainer.temperatureNoise.set(0.35)
        self.fluidContainer.temperatureTension.set(1)

    def setFuel(self):
        self.fluidContainer.fuelScale.set(1)
        self.fluidContainer.reactionSpeed.set(0.1)
        self.fluidContainer.airFuelRatio.set(8)
        self.fluidContainer.fuelIgnitionTemp.set(0.1)
        self.fluidContainer.maxReactionTemp.set(0.5)
        self.fluidContainer.heatReleased.set(2.5)
        self.fluidContainer.lightReleased.set(1)

    def setShading(self):
        self.fluidContainer.transparency.set(0.5, 0.5, 0.5, type="double3")
        self.fluidContainer.glowIntensity.set(0.075)

        # Density Color
        dr, dg, db = densityColor.explosionSmokeColor()
        self.fluidContainer.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluidContainer.colorInput.set(5)

        # Temperature Color
        self.fluidContainer.incandescence[0].incandescence_Position.set(0.08)
        self.fluidContainer.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")
        self.fluidContainer.incandescence[0].incandescence_Interp.set(3)

        self.fluidContainer.incandescence[1].incandescence_Position.set(0.1)
        self.fluidContainer.incandescence[1].incandescence_Color.set(0.143961, 0.0139806, 0.00832706, type="double3")
        self.fluidContainer.incandescence[1].incandescence_Interp.set(3)

        self.fluidContainer.incandescence[2].incandescence_Position.set(0.2)
        self.fluidContainer.incandescence[2].incandescence_Color.set(0.896, 0.201495, 0, type="double3")
        self.fluidContainer.incandescence[2].incandescence_Interp.set(3)

        self.fluidContainer.incandescence[3].incandescence_Position.set(0.5)
        self.fluidContainer.incandescence[3].incandescence_Color.set(2.5, 1.666667, 0.5, type="double3")
        self.fluidContainer.incandescence[3].incandescence_Interp.set(3)

        self.fluidContainer.incandescence[4].incandescence_Position.set(1)
        self.fluidContainer.incandescence[4].incandescence_Color.set(2.5, 2.5, 2.5, type="double3")
        self.fluidContainer.incandescence[4].incandescence_Interp.set(3)

        self.fluidContainer.incandescenceInputBias.set(0.35)

        # Opacity
        self.fluidContainer.opacityInput.set(5) # density
        self.opacityGraph()
        self.fluidContainer.opacityInputBias.set(0.65)

    def opacityGraph(self, sampling=20):
        step = 100/sampling
        for i in [round(x * 0.01, 4) for x in range(0, 100+1, step)]:
            y = mathFunction.repartFunction(i, l=15)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Position.set(i)
            self.fluidContainer.opacity[int(i * sampling)].opacity_FloatValue.set(y)
            self.fluidContainer.opacity[int(i * sampling)].opacity_Interp.set(1)


if __name__ == '__main__':
    explosion = Explosion()
