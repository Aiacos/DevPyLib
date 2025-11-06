"""Base fluid container configuration class.

Provides the FluidContainer class for creating and configuring Maya 3D
fluid containers with emission and render properties.
"""

__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm


class FluidContainer():
    """
    Creates a 3D Fluid Container.

    Attributes:
        container (list): A list containing the created fluid container.
    """

    def __init__(self):
        """
        Initializes the FluidContainer class.
        """
        # Create the fluid container.
        self.container = pm.ls(mel.eval('create3DFluid 10 10 10 10 10 10;'))

    def get_container(self):
        """
        Returns the created fluid container.

        Returns:
            list: A list containing the created fluid container.
        """
        return self.container
