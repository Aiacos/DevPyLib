"""Fire with Smoke Preset.

This class is a preset for creating fire with smoke simulations
"""

__author__ = "Lorenzo Argentieri"

from mayaLib.fluidLib.base.base_fluid import BaseFluid
from mayaLib.fluidLib.base.ramp_utils import setup_repart_opacity_ramp


class FireSmoke(BaseFluid):
    """Fire with Smoke Preset.

    This class is a preset for creating fire with smoke simulations
    """

    def __init__(self, fluid_name="", base_res=32, emit_obj=None):
        """Fire with Smoke Preset.

        Args:
            fluid_name (str): The name of the fluid.
            base_res (int): The base resolution of the fluid.
            emit_obj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluid_name=fluid_name, base_res=base_res, emit_obj=emit_obj)
        self.fluid_container = BaseFluid.get_fluid_shape(self)

        # Set the temperature method to 2, which is the heat method.
        self.fluid_container.temperatureMethod.set(2)
        # Set the fuel method to 2, which is the standard fuel method.
        self.fluid_container.fuelMethod.set(2)

        # Set the density parameters.
        self.set_density()
        # Set the velocity parameters.
        self.set_velocity()
        # Set the turbulence parameters.
        self.set_turbulence()
        # Set the temperature parameters.
        self.set_temperature()
        # Set the fuel parameters.
        self.set_fuel()

        # Set the shading parameters.
        self.set_shading()

    def set_density(self):
        """Set the density parameters."""
        # Set the density dissipation to 1.
        self.fluid_container.densityDissipation.set(1)
        # Set the density tension to 0.01.
        self.fluid_container.densityTension.set(0.01)
        # Set the tension force to 0.05.
        self.fluid_container.tensionForce.set(0.05)
        # Set the density gradient force to 15.
        self.fluid_container.densityGradientForce.set(15)

    def set_velocity(self):
        """Set the velocity parameters."""
        # Set the velocity swirl to 6.
        self.fluid_container.velocitySwirl.set(6)

    def set_turbulence(self):
        """Set the turbulence parameters."""
        # Set the turbulence strength to 0.025.
        self.fluid_container.turbulenceStrength.set(0.025)
        # Set the turbulence frequency to 0.5.
        self.fluid_container.turbulenceFrequency.set(0.5)
        # Set the turbulence speed to 0.65.
        self.fluid_container.turbulenceSpeed.set(0.65)

    def set_temperature(self):
        """Set the temperature parameters."""
        # Set the temperature scale to 2.5.
        self.fluid_container.temperatureScale.set(2.5)
        # Set the buoyancy to 100.
        self.fluid_container.buoyancy.set(100)
        # Set the temperature dissipation to 4.
        self.fluid_container.temperatureDissipation.set(4)
        # Set the temperature diffusion to 0.
        self.fluid_container.temperatureDiffusion.set(0)
        # Set the temperature turbulence to 1.
        self.fluid_container.temperatureTurbulence.set(1)

    def set_fuel(self):
        """Set the fuel parameters."""
        # Set the reaction speed to 1.
        self.fluid_container.reactionSpeed.set(1)
        # Set the max reaction temperature to 0.01.
        self.fluid_container.maxReactionTemp.set(0.01)
        # Set the light released to 1.
        self.fluid_container.lightReleased.set(1)

    def set_shading(self):
        """Set the shading parameters."""
        # Set the transparency to 0.5.
        self.fluid_container.transparency.set(0.5, 0.5, 0.5, type="double3")
        # Set the glow intensity to 0.075.
        self.fluid_container.glowIntensity.set(0.075)

        # Set the density color.
        self.fluid_container.color[0].color_Position.set(0)
        self.fluid_container.color[0].color_Color.set(0.005, 0.005, 0.005, type="double3")

        self.fluid_container.color[1].color_Position.set(1)
        self.fluid_container.color[1].color_Color.set(0.5, 0.5, 0.5, type="double3")
        self.fluid_container.colorInputBias.set(1)
        self.fluid_container.colorInput.set(5)

        # Set the temperature color.
        self.fluid_container.incandescence[0].incandescence_Position.set(0.8)
        self.fluid_container.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")

        self.fluid_container.incandescence[1].incandescence_Position.set(0.815)
        self.fluid_container.incandescence[1].incandescence_Color.set(
            0.896, 0.201495, 0, type="double3"
        )

        self.fluid_container.incandescence[2].incandescence_Position.set(1)
        self.fluid_container.incandescence[2].incandescence_Color.set(
            2.5, 1.666667, 0.5, type="double3"
        )

        self.fluid_container.incandescenceInputBias.set(0.9)

        # Set the opacity.
        self.fluid_container.opacityInput.set(6)  # 5 Density / 6 Temperature
        setup_repart_opacity_ramp(self.fluid_container, sampling=20, curve_parameter=15.0)
        self.fluid_container.opacityInputBias.set(0.35)


if __name__ == "__main__":
    fire = FireSmoke()
