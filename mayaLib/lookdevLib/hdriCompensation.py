__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


class Compensation():
    """
    Class for Hdri Compensations

    Attributes:
        hdriNode (str): Hdri node name
        plateR (float): Plate red value
        plateG (float): Plate green value
        plateB (float): Plate blue value
        renderR (float): Render red value
        renderG (float): Render green value
        renderB (float): Render blue value
    """

    def __init__(self, hdriNode, plateR, plateG, plateB, renderR, renderG, renderB):
        """
        Constructor for Compensation class

        Args:
            hdriNode (str): Hdri node name
            plateR (float): Plate red value
            plateG (float): Plate green value
            plateB (float): Plate blue value
            renderR (float): Render red value
            renderG (float): Render green value
            renderB (float): Render blue value
        """
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
        """
        Method to calculate the compensation formula

        Args:
            plateR (float): Plate red value
            plateG (float): Plate green value
            plateB (float): Plate blue value
            renderR (float): Render red value
            renderG (float): Render green value
            renderB (float): Render blue value

        Returns:
            tuple: r, g, b
        """
        r = plateR / renderR
        g = plateG / renderG
        b = plateB / renderB

        return r, g, b

    def createStandardColorCorrect(self):
        """
        Method to create standard color correct node
        """
        # get texture fileNode
        file_node = pm.listConnections(self.hdriNode.color, p=False, s=True, type='file')[0]
        self.colorCorrect_node = file_node

    def setStandarGain(self, r=1, g=1, b=1):
        """
        Method to set standard color correct node gain

        Args:
            r (float, optional): Red value. Defaults to 1.
            g (float, optional): Green value. Defaults to 1.
            b (float, optional): Blue value. Defaults to 1.
        """
        self.colorCorrect_node.colorGain.set(r, g, b)

    def setPxrGain(self, r=1, g=1, b=1):
        """
        Method to set Pxr gain

        Args:
            r (float, optional): Red value. Defaults to 1.
            g (float, optional): Green value. Defaults to 1.
            b (float, optional): Blue value. Defaults to 1.
        """
        self.hdriNode.lightColor.set(r, g, b)


if __name__ == "__main__":
    sel = pm.ls('PxrDomeLightShape1', 'aiSkyDomeLightShape1')

    for s in sel:
        # print(type(s))
        print(pm.objectType(s, isType='aiSkyDomeLight'))
        # Result: True #

    sel2 = pm.ls(type='PxrDomeLight')
    print(sel2)