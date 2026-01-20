"""Fire fluid effect preset.

Provides the Fire class for creating fire simulations with appropriate
container, emitter, and shading settings.
"""

__author__ = "Lorenzo Argentieri"
import pymel.core as pm

from mayaLib.fluidLib.base.base_fluid import BaseFluid
from mayaLib.fluidLib.utility import density_color, math_function


class Fire(BaseFluid):
    """Fire Preset."""

    def __init__(self, fluid_name="", base_res=32, emit_obj=None):
        """Constructor for the Fire class.

        Args:
            fluid_name (str): The name of the fluid.
            base_res (int): The base resolution of the fluid.
            emit_obj (str): The name of the emitter object.
        """
        BaseFluid.__init__(self, fluid_name=fluid_name, base_res=base_res, emit_obj=emit_obj)
        self.fluid_container = BaseFluid.get_fluid_shape(self)

        self.fluid_container.temperatureMethod.set(2)
        self.fluid_container.fuelMethod.set(2)

        # Update Dynamic Simulation
        self.fluid_container.viscosity.set(0.005)
        self.fluid_container.velocityDamp.set(0.01)
        self.fluid_container.simulationRateScale.set(2)
        self.fluid_container.emitInSubsteps.set(1)

        # Parameter
        self.set_density()
        self.set_velocity()
        self.set_turbulence()
        self.set_temperature()

        # Shading
        self.set_shading()

        pm.select(self.fluid_container)

    def set_density(self):
        """Set the density parameters."""
        self.fluid_container.densityBuoyancy.set(2.5)
        self.fluid_container.densityDissipation.set(2.5)

        self.fluid_container.densityTension.set(0.01)
        self.fluid_container.tensionForce.set(0.05)
        self.fluid_container.densityGradientForce.set(15)

    def set_velocity(self):
        """Set the velocity parameters."""
        self.fluid_container.velocitySwirl.set(2.5)

    def set_turbulence(self):
        """Set the turbulence parameters."""
        self.fluid_container.turbulenceStrength.set(0.25)
        self.fluid_container.turbulenceFrequency.set(0.5)
        self.fluid_container.turbulenceSpeed.set(0.65)

    def set_temperature(self):
        """Set the temperature parameters."""
        self.fluid_container.temperatureScale.set(2)
        self.fluid_container.buoyancy.set(15)
        self.fluid_container.temperatureDissipation.set(2.5)
        self.fluid_container.temperatureDiffusion.set(0.01)
        self.fluid_container.temperatureTurbulence.set(2.5)
        self.fluid_container.temperatureNoise.set(0.25)

    def set_shading(self):
        """Set the shading parameters."""
        self.fluid_container.transparency.set(0.5, 0.5, 0.5, type="double3")
        self.fluid_container.glowIntensity.set(0.075)

        # Density Color
        dr, dg, db = density_color.smoke_color()
        self.fluid_container.color[0].color_Color.set(dr, dg, db, type="double3")
        self.fluid_container.colorInput.set(5)

        # Temperature Color
        self.fluid_container.incandescence[0].incandescence_Position.set(0.5)
        self.fluid_container.incandescence[0].incandescence_Color.set(0, 0, 0, type="double3")
        self.fluid_container.incandescence[0].incandescence_Interp.set(3)

        self.fluid_container.incandescence[1].incandescence_Position.set(0.75)
        self.fluid_container.incandescence[1].incandescence_Color.set(
            0.896, 0.201495, 0, type="double3"
        )
        self.fluid_container.incandescence[1].incandescence_Interp.set(3)

        self.fluid_container.incandescence[2].incandescence_Position.set(1)
        self.fluid_container.incandescence[2].incandescence_Color.set(
            2.5, 1.666667, 0.5, type="double3"
        )
        self.fluid_container.incandescence[2].incandescence_Interp.set(3)

        self.fluid_container.incandescenceInputBias.set(0.8)

        # Opacity
        self.fluid_container.opacityInput.set(5)  # density
        self.opacity_graph()
        self.fluid_container.opacityInputBias.set(0.35)

    def opacity_graph(self, sampling=20):
        """Create an opacity graph for the fire.

        The opacity graph is a simple curve that goes from 0 to 1 and then
        comes back to 0. It is used to fade out the fire at the end of its
        lifespan.

        Args:
            sampling (int): The number of points to sample in the opacity
                graph. Defaults to 20.
        """
        step = int(100 / sampling)
        for i in [round(x * 0.01, 4) for x in range(0, 100 + 1, step)]:
            y = math_function.laplace_distribution2(i)
            self.fluid_container.opacity[int(i * sampling)].opacity_Position.set(i)
            self.fluid_container.opacity[int(i * sampling)].opacity_FloatValue.set(y)
            self.fluid_container.opacity[int(i * sampling)].opacity_Interp.set(1)


if __name__ == "__main__":
    fire = Fire()
