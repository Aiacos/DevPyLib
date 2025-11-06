"""Smoke fluid effect presets.

Provides WispySmoke and ThickSmoke classes for creating smoke simulations
with appropriate container, emitter, and shading settings.
"""

__author__ = 'Lorenzo Argentieri'
import pymel.core as pm

from mayaLib.fluidLib.base.base_fluid import BaseFluid
from mayaLib.fluidLib.base.ramp_utils import (
    setup_manual_opacity_ramp,
    setup_repart_opacity_ramp,
)
from mayaLib.fluidLib.utility import density_color


class WispySmoke(BaseFluid):
    """
    Wispy Smoke Preset
    """

    def __init__(self, fluid_name='', base_res=32, emit_obj=None):
        """
        Initializes the WispySmoke class with fluid properties.

        Args:
            fluid_name (str): The name of the fluid.
            base_res (int): The base resolution of the fluid.
            emit_obj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluid_name=fluid_name, base_res=base_res, emit_obj=emit_obj)
        self.fluid_container = BaseFluid.get_fluid_shape(self)
        self.fluid_emitter = BaseFluid.get_fluid_emitter(self)

        self.set_emitter()

        # Update Dynamic Simulation
        self.fluid_container.viscosity.set(0.125)
        self.fluid_container.simulationRateScale.set(2)
        self.fluid_container.emitInSubsteps.set(1)

        # Parameter
        self.set_density()
        self.set_velocity()
        self.set_turbulence()

        # Shading
        self.set_shading()

        pm.select(self.fluid_container)

    def set_emitter(self):
        """Set the emitter properties for wispy smoke."""
        self.fluid_emitter.rate.set(250)
        self.fluid_emitter.maxDistance.set(0.2)
        self.fluid_emitter.fluidDensityEmission.set(2.5)

    def set_density(self):
        """Set the density parameters for wispy smoke."""
        self.fluid_container.densityScale.set(0.65)
        self.fluid_container.densityBuoyancy.set(25)
        self.fluid_container.densityDissipation.set(0.15)

        self.fluid_container.densityTension.set(0.025)
        self.fluid_container.tensionForce.set(0.1)
        self.fluid_container.densityGradientForce.set(10)

    def set_velocity(self):
        """Set the velocity parameters for wispy smoke."""
        self.fluid_container.velocitySwirl.set(5)

    def set_turbulence(self):
        """Set the turbulence parameters and keyframes for wispy smoke."""
        pm.setKeyframe(self.fluid_container, attribute='turbulenceStrength', time=1, value=5)
        pm.setKeyframe(self.fluid_container, attribute='turbulenceStrength', time=12, value=0.1)
        self.fluid_container.turbulenceFrequency.set(0.5)
        self.fluid_container.turbulenceSpeed.set(0.5)

    def set_shading(self):
        """Set the shading parameters for wispy smoke."""
        self.fluid_container.transparency.set(0.214037, 0.214037, 0.214037, type="double3")
        self.fluid_container.edgeDropoff.set(0)

        # Density Color
        dr, dg, db = density_color.wispy_smoke_color()
        self.fluid_container.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluid_container.colorInput.set(0)  # Constant

        # Opacity
        self.fluid_container.opacityInput.set(5)  # density
        setup_manual_opacity_ramp(
            self.fluid_container,
            [
                (0.0, 0.0, 3),
                (0.25, 0.1, 3),
                (0.5, 0.5, 3),
                (0.75, 0.1, 3),
                (1.0, 0.0, 3),
            ]
        )
        self.fluid_container.opacityInputBias.set(0.4)


class ThickSmoke(BaseFluid):
    """
    Thick Smoke Preset
    """

    def __init__(self, fluid_name='', base_res=32, emit_obj=None):
        """
        Initializes the ThickSmoke class with fluid properties.

        Args:
            fluid_name (str): The name of the fluid.
            base_res (int): The base resolution of the fluid.
            emit_obj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluid_name=fluid_name, base_res=base_res, emit_obj=emit_obj)
        self.fluid_container = BaseFluid.get_fluid_shape(self)
        self.fluid_emitter = BaseFluid.get_fluid_emitter(self)

        self.set_emitter()

        # Update Dynamic Simulation
        self.fluid_container.viscosity.set(0.005)
        self.fluid_container.velocityDamp.set(0.025)
        self.fluid_container.emitInSubsteps.set(1)

        # Parameter
        self.set_density()
        self.set_velocity()
        self.set_turbulence()

        # Shading
        self.set_shading()

        pm.select(self.fluid_container)

    def set_emitter(self):
        """Set the emitter properties for thick smoke."""
        self.fluid_emitter.fluidDensityEmission.set(6)
        self.fluid_emitter.turbulence.set(8)
        self.fluid_emitter.turbulenceSpeed.set(0.25)
        self.fluid_emitter.detailTurbulence.set(1)

    def set_density(self):
        """Set the density parameters for thick smoke."""
        self.fluid_container.densityScale.set(0.5)
        self.fluid_container.densityBuoyancy.set(10)
        self.fluid_container.densityDissipation.set(0.2)
        self.fluid_container.densityPressure.set(1.25)
        self.fluid_container.densityPressureThreshold.set(0.1)
        self.fluid_container.densityNoise.set(0.1)

        self.fluid_container.densityTension.set(0.010)
        self.fluid_container.tensionForce.set(0.05)
        self.fluid_container.densityGradientForce.set(35)

    def set_velocity(self):
        """Set the velocity parameters for thick smoke."""
        self.fluid_container.velocitySwirl.set(6)
        self.fluid_container.velocityNoise.set(1)

    def set_turbulence(self):
        """Set the turbulence parameters for thick smoke."""
        self.fluid_container.turbulenceStrength.set(0.35)
        self.fluid_container.turbulenceFrequency.set(0.5)
        self.fluid_container.turbulenceSpeed.set(0.5)

    def set_shading(self):
        """Set the shading parameters for thick smoke."""
        self.fluid_container.transparency.set(0.380057, 0.380057, 0.380057, type="double3")
        self.fluid_container.edgeDropoff.set(0)

        # Density Color
        dr, dg, db = density_color.wispy_smoke_color()
        self.fluid_container.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluid_container.colorInput.set(0)  # Constant

        # Opacity
        self.fluid_container.opacityInput.set(5)  # density
        setup_repart_opacity_ramp(self.fluid_container, sampling=20, curve_parameter=15.0)
        self.fluid_container.opacityInputBias.set(0.4)


if __name__ == '__main__':
    wsmoke = WispySmoke()
    tsmoke = ThickSmoke()
