__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class BaseFluid():
    def __init__(self, fluidName=''):
        if fluidName != '':
            self.fluidEmitString = 'fluidEmitter -pos 0 0 0 -type omni  -name \"' + fluidName + '#\" -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'
        else:
            self.fluidEmitString = 'fluidEmitter -pos 0 0 0 -type omni -der 1 -her 1 -fer 1 -fdr 2 -r 100.0 -cye none -cyi 1 -mxd 1 -mnd 0 ;'

        mel.eval('dynExecFluidEmitterCommands 1 { "1", "' + self.fluidEmitString + '", 0, 0, 0, 0, 0, 0, 10, 10, 10, 10, 10, 10, 0, 0, 1} ;')

        if fluidName != '':
            self.fluidEmit_list = pm.ls('fluidEmitter?')
            self.fluidShape_list = pm.ls('fluidShape?')
        else:
            self.fluidEmit_list = pm.ls('fluidEmitter?')
            self.fluidShape_list = pm.ls('fluidShape?')

        self.fluidEmit = self.fluidEmit_list[-1]
        self.fluidShape = self.fluidShape_list[-1]

        print '/////////////////'
        print self.fluidEmit
        print self.fluidShape


if __name__ == '__main__':
    f = BaseFluid()
