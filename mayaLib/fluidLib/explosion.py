__author__ = "Lorenzo Argentieri"

"""Explosion fluid effect preset.

Provides the Explosion class for creating explosion simulations with
rapid expansion and dissipation properties.
"""
import pymel.core as pm

from mayaLib.fluidLib.base.base_fluid import BaseFluid
from mayaLib.fluidLib.base.ramp_utils import setup_repart_opacity_ramp
from mayaLib.fluidLib.utility import density_color


class Explosion(BaseFluid):
    """
    Explosion Preset
    """

    def __init__(self, fluid_name="", base_res=32, emit_obj=None):
        """
        Constructor for the Explosion class.

        Args:
            fluid_name (str): The name of the fluid.
            base_res (int): The base resolution of the fluid.
            emit_obj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluid_name=fluid_name, base_res=base_res, emit_obj=emit_obj)
        self.fluid_container = BaseFluid.get_fluid_shape(self)
        self.fluid_emitter = BaseFluid.get_fluid_emitter(self)

        # Update Emitter Type
        if emit_obj is None:
            self.fluid_emitter.emitterType.set(4)
            self.fluid_emitter.volumeShape.set(1)

        self.set_emitter()

        # Update Dynamic Simulation
        self.fluid_container.velocityDamp.set(0.025)
        self.fluid_container.simulationRateScale.set(2.5)

        # Add Temperature and Fuel
        self.fluid_container.temperatureMethod.set(2)
        self.fluid_container.fuelMethod.set(2)

        # Parameter
        self.set_density()
        self.set_velocity()
        self.set_turbulence()
        self.set_temperature()
        self.set_fuel()

        # Shading
        self.set_shading()

        pm.select(self.fluid_container)

    def set_emitter(self, start_frame=1):
        """
        Set the emitter properties for the explosion.

        Args:
            start_frame (int): The start frame of the emitter.
        """
        pm.setKeyframe(self.fluid_emitter, attribute="fluidDensityEmission", time=1, value=8)
        pm.setKeyframe(self.fluid_emitter, attribute="fluidDensityEmission", time=6, value=0)

        pm.setKeyframe(self.fluid_emitter, attribute='fluidFuelEmission', time=1, value=5)
        pm.setKeyframe(self.fluid_emitter, attribute='fluidFuelEmission', time=6, value=0)

        self.fluid_emitter.turbulence.set(6)
        self.fluid_emitter.turbulenceSpeed.set(0.25)
        self.fluid_emitter.detailTurbulence.set(1)

    def set_density(self):
        """
        Set the density properties for the explosion.
        """
        self.fluid_container.densityScale.set(0.75)
        self.fluid_container.densityBuoyancy.set(2.5)
        self.fluid_container.densityDissipation.set(1.5)

        self.fluid_container.densityNoise.set(0.1)
        self.fluid_container.densityGradientForce.set(35)

    def set_velocity(self):
        """
        Set the velocity properties for the explosion.
        """
        # self.fluid_container.velocitySwirl.set(6) # al frame 1
        pm.setKeyframe(self.fluid_container, attribute='velocitySwirl', time=1, value=6)
        # self.fluid_container.velocitySwirl.set(2.5) # al frame 50
        pm.setKeyframe(self.fluid_container, attribute='velocitySwirl', time=50, value=2.5)
        self.fluid_container.velocityNoise.set(1)

    def set_turbulence(self):
        """
        Set the turbulence properties for the explosion.
        """
        # self.fluid_container.turbulenceStrength.set(3.5) # al frame 1
        pm.setKeyframe(self.fluid_container, attribute='turbulenceStrength', time=1, value=3.5)
        # self.fluid_container.turbulenceStrength.set(0.1) # al frame 6
        pm.setKeyframe(self.fluid_container, attribute='turbulenceStrength', time=6, value=0.1)
        self.fluid_container.turbulenceFrequency.set(0.5)
        self.fluid_container.turbulenceSpeed.set(0.5)

    def set_temperature(self):
        """
        Set the temperature properties for the explosion.
        """
        self.fluid_container.temperatureScale.set(2.5)

        # self.fluid_container.buoyancy.set(1) # frame 1
        pm.setKeyframe(self.fluid_container, attribute='buoyancy', time=1, value=1)
        # self.fluid_container.buoyancy.set(125) #frame 10
        pm.setKeyframe(self.fluid_container, attribute='buoyancy', time=10, value=125)

        # self.fluid_container.temperaturePressure.set(0)# frame 1
        pm.setKeyframe(self.fluid_container, attribute='temperaturePressure', time=1, value=0)
        # self.fluid_container.temperaturePressure.set(6)# frame 3
        pm.setKeyframe(self.fluid_container, attribute='temperaturePressure', time=3, value=6)
        # self.fluid_container.temperaturePressure.set(0)# temperaturePressure 6
        pm.setKeyframe(self.fluid_container, attribute='temperaturePressure', time=6, value=0)
        self.fluid_container.temperaturePressureThreshold.set(0.5)

        self.fluid_container.temperatureDissipation.set(1)
        self.fluid_container.temperatureDiffusion.set(0.1)
        self.fluid_container.temperatureTurbulence.set(6)
        self.fluid_container.temperatureNoise.set(0.35)
        self.fluid_container.temperatureTension.set(1)

    def set_fuel(self):
        """
        Set the fuel properties for the explosion.
        """
        self.fluid_container.fuelScale.set(1)
        self.fluid_container.reactionSpeed.set(0.1)
        self.fluid_container.airFuelRatio.set(8)
        self.fluid_container.fuelIgnitionTemp.set(0.1)
        self.fluid_container.maxReactionTemp.set(0.5)
        self.fluid_container.heatReleased.set(2.5)
        self.fluid_container.lightReleased.set(1)

    def set_shading(self):
        """
        Set the shading properties for the explosion.
        """
        self.fluid_container.transparency.set(0.5, 0.5, 0.5, type="double3")
        self.fluid_container.glowIntensity.set(0.075)

        # Density Color
        dr, dg, db = density_color.explosion_smoke_color()
        self.fluid_container.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluid_container.colorInput.set(5)

        # Temperature Color
        self.fluid_container.incandescence[0].incandescence_Position.set(0.08)
        self.fluid_container.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")
        self.fluid_container.incandescence[0].incandescence_Interp.set(3)

        self.fluid_container.incandescence[1].incandescence_Position.set(0.1)
        self.fluid_container.incandescence[1].incandescence_Color.set(0.143961, 0.0139806, 0.00832706, type="double3")
        self.fluid_container.incandescence[1].incandescence_Interp.set(3)

        self.fluid_container.incandescence[2].incandescence_Position.set(0.2)
        self.fluid_container.incandescence[2].incandescence_Color.set(0.896, 0.201495, 0, type="double3")
        self.fluid_container.incandescence[2].incandescence_Interp.set(3)

        self.fluid_container.incandescence[3].incandescence_Position.set(0.5)
        self.fluid_container.incandescence[3].incandescence_Color.set(2.5, 1.666667, 0.5, type="double3")
        self.fluid_container.incandescence[3].incandescence_Interp.set(3)

        self.fluid_container.incandescence[4].incandescence_Position.set(1)
        self.fluid_container.incandescence[4].incandescence_Color.set(2.5, 2.5, 2.5, type="double3")
        self.fluid_container.incandescence[4].incandescence_Interp.set(3)

        self.fluid_container.incandescenceInputBias.set(0.35)

        # Opacity
        self.fluid_container.opacityInput.set(5)  # density
        setup_repart_opacity_ramp(self.fluid_container, sampling=20, curve_parameter=15.0)
        self.fluid_container.opacityInputBias.set(0.65)


if __name__ == "__main__":
    explosion = Explosion()
