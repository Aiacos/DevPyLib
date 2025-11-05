__author__ = 'Lorenzo Argentieri'

"""HDRI exposure compensation utilities.

Provides tools for adjusting HDRI intensity and exposure
for consistent lighting.
"""

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

    def __init__(self, hdri_node, plate_r, plate_g, plate_b, render_r, render_g, render_b):
        """
        Constructor for Compensation class

        Args:
            hdri_node (str): Hdri node name
            plate_r (float): Plate red value
            plate_g (float): Plate green value
            plate_b (float): Plate blue value
            render_r (float): Render red value
            render_g (float): Render green value
            render_b (float): Render blue value
        """
        self.hdriNode = pm.ls(hdri_node)[0].getShape()

        r, g, b = self.compensation_formula(plate_r, plate_g, plate_b, render_r, render_g, render_b)

        if pm.objectType(self.hdriNode, isType='aiSkyDomeLight'):
            self.create_standard_color_correct()
            self.set_standard_gain(r, g, b)
        elif pm.objectType(self.hdriNode, isType='PxrDomeLight'):
            self.set_pxr_gain(r, g, b)
        else:
            print('invalid node')

    def compensation_formula(self, plate_r, plate_g, plate_b, render_r, render_g, render_b):
        """
        Method to calculate the compensation formula

        Args:
            plate_r (float): Plate red value
            plate_g (float): Plate green value
            plate_b (float): Plate blue value
            render_r (float): Render red value
            render_g (float): Render green value
            render_b (float): Render blue value

        Returns:
            tuple: r, g, b
        """
        r = plate_r / render_r
        g = plate_g / render_g
        b = plate_b / render_b

        return r, g, b

    def create_standard_color_correct(self):
        """
        Method to create standard color correct node
        """
        # get texture fileNode
        file_node = pm.listConnections(self.hdriNode.color, p=False, s=True, type='file')[0]
        self.colorCorrect_node = file_node

    def set_standard_gain(self, r=1, g=1, b=1):
        """
        Method to set standard color correct node gain

        Args:
            r (float, optional): Red value. Defaults to 1.
            g (float, optional): Green value. Defaults to 1.
            b (float, optional): Blue value. Defaults to 1.
        """
        self.colorCorrect_node.colorGain.set(r, g, b)

    def set_pxr_gain(self, r=1, g=1, b=1):
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
