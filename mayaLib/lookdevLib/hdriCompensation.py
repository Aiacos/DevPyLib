__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.shaderLib.utils import file


class Compensation():
    def __init__(self, hdriNode):
        self.hdriNode = hdriNode
        if pm.objectType(self.hdriNode, isType='aiSkyDomeLight'):
            self.createStandardColorCorrect()
        elif pm.objectType(self.hdriNode, isType='PxrDomeLight'):
            pass
        else:
            print 'invalid node'

    def compensationFormula(self, plateR, plateG, plateB, renderR, renderG, renderB):
        r = plateR / renderR
        g = plateG / renderG
        b = plateB / renderB

        return r, g, b

    def setGain(self, r=1, g=1, b=1, slot_name=None, colorCorrect_node=None):
        if pm.objectType(self.hdriNode, isType='aiSkyDomeLight'):
            self.setStandarGain(r, g, b)
        elif pm.objectType(self.hdriNode, isType='PxrDomeLight'):
            self.setPxrGain(r, g, b)
        elif slot_name != None and colorCorrect_node != None:
            # ToDo
            self.setStandarGain(r, g, b)
        else:
            print 'invalid node'

    def createStandardColorCorrect(self):
        # get texture fileNode
        file_node = pm.listConnections(self.hdriNode.color, p=True, s=True, type='file')[0]
        self.colorCorrect_node = file_node


    def createPxrColorCorrect(self, name):
        # get filenode plug
        path = self.hdriNode.lightColorMap.get()
        # create fileNode
        pxrtexture_node = pm.shadingNode("PxrTexture", name=name, asTexture=True)
        pxrtexture_node.filename.set(path)
        # create colorCorrect
        self.colorCorrect_node = pm.shadingNode('PxrColorCorrect', asTexture=True)
        # connect file node -> colorCorrect node
        pm.connectAttr(pxrtexture_node.resultRGB, self.colorCorrect_node.inputRGB)
        # connect colorCorrect node -> hdriNode
        pm.connectAttr(self.colorCorrect_node.resultRGB, self.hdriNode.lightColor)

    def setStandarGain(self, r=1, g=1, b=1):
        self.colorCorrect_node.colorGain.set(r, g, b)

    def setPxrGain(self, r=1, g=1, b=1):
        self.colorCorrect_node.rgbGain.set(r, g, b)


if __name__ == "__main__":
    sel = pm.ls('PxrDomeLightShape1', 'aiSkyDomeLightShape1')

    for s in sel:
        # print type(s)
        print pm.objectType(s, isType='aiSkyDomeLight')
        # Result: True #

    sel2 = pm.ls(type='PxrDomeLight')
    print sel2

