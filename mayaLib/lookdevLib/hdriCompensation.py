__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class Compensation():
    def __init__(self, hdriNode, plateR, plateG, plateB, renderR, renderG, renderB):
        self.hdriNode = pm.ls(hdriNode)[0].getShape()

        r, g, b = self.compensationFormula(plateR, plateG, plateB, renderR, renderG, renderB)

        if pm.objectType(self.hdriNode, isType='aiSkyDomeLight'):
            self.createStandardColorCorrect()
            self.setStandarGain(r, g, b)
        elif pm.objectType(self.hdriNode, isType='PxrDomeLight'):
            self.setPxrGain(r, g, b)
        else:
            print('invalid node')

    def compensationFormula(self, plateR, plateG, plateB, renderR, renderG, renderB):
        r = plateR / renderR
        g = plateG / renderG
        b = plateB / renderB

        return r, g, b

    def createStandardColorCorrect(self):
        # get texture fileNode
        file_node = pm.listConnections(self.hdriNode.color, p=False, s=True, type='file')[0]
        self.colorCorrect_node = file_node

    def setStandarGain(self, r=1, g=1, b=1):
        self.colorCorrect_node.colorGain.set(r, g, b)

    def setPxrGain(self, r=1, g=1, b=1):
        self.hdriNode.lightColor.set(r, g, b)


if __name__ == "__main__":
    sel = pm.ls('PxrDomeLightShape1', 'aiSkyDomeLightShape1')

    for s in sel:
        # print(type(s))
        print(pm.objectType(s, isType='aiSkyDomeLight'))
        # Result: True #

    sel2 = pm.ls(type='PxrDomeLight')
    print(sel2)
