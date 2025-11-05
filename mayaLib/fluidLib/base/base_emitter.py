__author__ = 'Lorenzo Argentieri'

"""Base fluid emitter configuration class.

Provides the FlEmitter class for creating and configuring fluid emitters
with volume and emission properties.
"""

import pymel.core as pm


class FlEmitter():
    """
    Emitter Class

    Attributes:
        emitter (list): A list containing the emitter object
    """

    def __init__(self, name='', obj=None):
        """
        Initializes an emitter object

        Args:
            name (str): The name of the emitter, defaults to ''
            obj (str): The object to attach the emitter to, defaults to None
        """
        if obj is None:
            emitter = pm.fluidEmitter(pos=(0, 0, 0), type='omni', der=1, her=1, fer=1, fdr=2, r=100.0, cye='none',
                                      cyi=1, mxd=1, mnd=0)
        else:
            obj_emitter = pm.fluidEmitter(obj, type='surface', der=1, her=1, fer=1, fdr=2, r=100.0, cye='none', cyi=1,
                                         mxd=1, mnd=0)
            emitter = pm.listRelatives(obj_emitter, type='fluidEmitter')

        if name != '':
            pm.rename(emitter, name)

        self.emitter = pm.ls(emitter)

    def get_emitter(self):
        """
        Returns the emitter object

        Returns:
            list: A list containing the emitter object
        """
        return self.emitter


if __name__ == '__main__':
    f = FlEmitter()
    f.get_emitter()
