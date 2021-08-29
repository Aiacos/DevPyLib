__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class FlEmitter():
    def __init__(self, name='', obj=None):
        """
        Emitter
        :param name: str
        :param obj: str
        """
        if obj == None:
            emitter = pm.fluidEmitter(pos=(0, 0, 0), type='omni', der=1, her=1, fer=1, fdr=2, r=100.0, cye='none',
                                      cyi=1, mxd=1, mnd=0)
        else:
            objEmitter = pm.fluidEmitter(obj, type='surface', der=1, her=1, fer=1, fdr=2, r=100.0, cye='none', cyi=1,
                                         mxd=1, mnd=0)
            emitter = pm.listRelatives(objEmitter, type='fluidEmitter')

        if name != '':
            pm.rename(emitter, name)

        self.emitter = pm.ls(emitter)

    def getEmitter(self):
        return self.emitter


if __name__ == '__main__':
    f = FlEmitter()
    f.getEmitter()
