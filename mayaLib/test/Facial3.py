import os, sys
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from PySide2 import QtGui as QtG
import maya.cmds as cmds, maya.OpenMayaUI as omui, pymel.all as pm, maya.mel as mel, json, re
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import maya.OpenMaya as OpenMaya, logging
try:
    import cPickle as pickle
except:
    import _pickle as pickle

try:
    from past.builtins import basestring
except:
    pass

FILE_EXT = '.data'
PACK_EXT = '.list'

def maya_main_window():
    """
        Return the Maya main window widget as a Python object
        """
    main_window_ptr = omui.MQtUtil.mainWindow()
    pythonVersion = sys.version_info.major
    try:
        if pythonVersion == 2:
            return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)
        else:
            return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

    except:
        from Qt import QtCompat
        return QtCompat.wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


def findMainName():
    prCheckTest1 = 'pm.mel.moveJointsMode(0)'
    prCheckTest2 = 'cmds.aimConstraint(weight=1, upVector=(2, 1, 0),f=1)'
    prCheckTest3 = 'cmds.aimConstreint(weight=1, upVector=(0, 1, 0),h=0),r=0)'
    prCheckTest4 = 'name_LIPs_All_Jnt'
    prCheckTest5 = 'setStyleSheet'
    prCheckTest6 = 'QtWidgets.QPushButton'
    prCheckTest7 = 'self.edgeColor'
    prCheckTest8 = 'background-color'
    prCheckTest9 = 'self.LEyeLidMainBoxButton'
    prCheckTest10 = 'self.REyeLidMainBoxButton'
    wordA = prCheckTest4[7] + prCheckTest1[4] + prCheckTest3[53] + prCheckTest4[8] + prCheckTest4[3] + prCheckTest2[29] + prCheckTest1[16]
    wordB = prCheckTest10[5] + prCheckTest1[13] + prCheckTest6[5] + prCheckTest7[7] + prCheckTest6[3] + prCheckTest10[15] + prCheckTest6[5]
    wordC = str(3)
    wordD = prCheckTest3[8] + prCheckTest3[9] + prCheckTest1[0] + prCheckTest5[5]
    wordE = prCheckTest8[5] + prCheckTest6[3] + prCheckTest8[4] + prCheckTest5[9] + prCheckTest5[2]
    wordF = str(2017)
    wordG = prCheckTest6[2] + prCheckTest7[13] + wordE[1] + prCheckTest6[1] + prCheckTest6[1] + prCheckTest1[4] + prCheckTest4[0]
    wordH = prCheckTest8[0] + prCheckTest5[5]
    wordI = prCheckTest9[12] + prCheckTest3[9] + prCheckTest3[48] + prCheckTest8[1] + prCheckTest3[1] + prCheckTest2[1] + prCheckTest8[1] + prCheckTest6[4]
    wordJ = prCheckTest4[14] + prCheckTest4[1] + prCheckTest7[3] + prCheckTest8[1] + prCheckTest8[5] + prCheckTest9[10] + prCheckTest8[1] + prCheckTest4[0]
    wordK = prCheckTest2[19] + prCheckTest3[19] + prCheckTest2[19] + prCheckTest7[4]
    wordL = prCheckTest1[0] + prCheckTest1[4] + prCheckTest3[53] + prCheckTest4[8] + prCheckTest4[3] + prCheckTest2[29] + prCheckTest1[16]
    wordM = prCheckTest3[53] + prCheckTest1[13] + prCheckTest6[5] + prCheckTest7[7] + prCheckTest6[3] + prCheckTest10[15] + prCheckTest6[5]
    wordN = prCheckTest9[4] + prCheckTest3[0] + prCheckTest3[9] + prCheckTest2[7]
    wordSpace = prCheckTest2[28]
    checkButtonTest = wordSpace + wordA + wordSpace + wordB + wordSpace + wordC + wordSpace + wordD + wordE + wordSpace + wordF + wordSpace + wordG + wordSpace + wordH + wordSpace + wordI + wordSpace + wordJ + wordSpace + wordSpace + wordK + wordL + wordM + wordN + wordSpace
    return checkButtonTest


def findMainNameB():
    prCheckTest1 = 'pm.mel.moveJointsMode(0)'
    prCheckTest2 = 'cmds.aimConstraint(weight=1, upVector=(2, 1, 0),f=1)'
    prCheckTest3 = 'cmds.aimConstreint(weight=1, upVector=(0, 1, 0),h=0),r=0)'
    prCheckTest4 = 'name_LIPs_All_Jnt'
    prCheckTest5 = 'setStyleSheet'
    prCheckTest6 = 'QtWidgets.QPushButton'
    prCheckTest7 = 'self.edgeColor'
    prCheckTest8 = 'background-color'
    prCheckTest9 = 'self.LEyeLidMainBoxButton'
    prCheckTest10 = 'self.REyeLidMainBoxButton'
    wordA = prCheckTest4[7] + prCheckTest1[4] + prCheckTest3[53] + prCheckTest4[8] + prCheckTest4[3] + prCheckTest2[29] + prCheckTest1[16]
    wordB = prCheckTest10[5] + prCheckTest1[13] + prCheckTest6[5] + prCheckTest7[7] + prCheckTest6[3] + prCheckTest10[15] + prCheckTest6[5]
    wordC = str(3)
    wordD = prCheckTest3[8] + prCheckTest3[9] + prCheckTest1[0] + prCheckTest5[5]
    wordE = prCheckTest8[5] + prCheckTest6[3] + prCheckTest8[4] + prCheckTest5[9] + prCheckTest5[2]
    wordF = str(2017)
    wordG = prCheckTest6[2] + prCheckTest7[13] + wordE[1] + prCheckTest6[1] + prCheckTest6[1] + prCheckTest1[4] + prCheckTest4[0]
    wordH = prCheckTest8[0] + prCheckTest5[5]
    wordI = prCheckTest9[12] + prCheckTest3[9] + prCheckTest3[48] + prCheckTest8[1] + prCheckTest3[1] + prCheckTest2[1] + prCheckTest8[1] + prCheckTest6[4]
    wordJ = prCheckTest4[14] + prCheckTest4[1] + prCheckTest7[3] + prCheckTest8[1] + prCheckTest8[5] + prCheckTest9[10] + prCheckTest8[1] + prCheckTest4[0]
    wordK = prCheckTest2[19] + prCheckTest3[19] + prCheckTest2[19] + prCheckTest7[4]
    wordL = prCheckTest1[0] + prCheckTest1[4] + prCheckTest3[53] + prCheckTest4[8] + prCheckTest4[3] + prCheckTest2[29] + prCheckTest1[16]
    wordM = prCheckTest3[53] + prCheckTest1[13] + prCheckTest6[5] + prCheckTest7[7] + prCheckTest6[3] + prCheckTest10[15] + prCheckTest6[5]
    wordN = prCheckTest9[4] + prCheckTest3[0] + prCheckTest3[9] + prCheckTest2[7]
    wordSpace = prCheckTest2[28]
    wordO = prCheckTest10[12] + prCheckTest10[13] + prCheckTest9[7] + prCheckTest4[1]
    checkButtonTest = wordSpace + wordA + wordSpace + wordB + wordSpace + wordC + wordSpace + wordO + wordSpace
    return checkButtonTest


class headGeoWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(headGeoWidget, self).__init__(parent)
        self.font = QtG.QFont()
        self.font.setPointSize(10)
        self.font.setBold(False)
        self.edgeColor = 'background-color:rgb(255,102,51);color : black;'
        self.slColor = 'background-color:rgb(0,254,102);color : black;'
        self.edgeIndColor = 'background-color:rgb(0,179,255);color : black;'
        self.darkColorA = 'background-color:rgb(70,70,70);color : white;'
        self.darkColorB = 'background-color:rgb(50,50,50);color : white;'
        self.darkColorC = 'background-color:rgb(30,30,30);color : white;'
        self.defaultColor = 'background-color:rgb(90,90,90);color : white;'
        self.progressColor = 'background-color:rgb(76,50,50);color : white;'
        self.defineColor = 'color : white;'
        self.defineColor2 = 'color : black;'
        self.edgeLoopToggle = False
        self.nameLabelField = QtWidgets.QLabel('Name : ')
        self.nameField = QtWidgets.QLineEdit('name')
        self.nameField.setFixedSize(100, 25)
        self.mainNameRig = findMainName()
        self.perseusLabelField = QtWidgets.QLabel(self.mainNameRig)
        self.perseusLabelField.setStyleSheet(self.progressColor)
        self.chkPrefix = QtWidgets.QCheckBox('Remove Prefix')
        self.skinJntSuffixLabel = QtWidgets.QLabel('Skin Joints Suffix : ')
        self.skinJntSuffix = QtWidgets.QLineEdit('skin')
        self.HeadGeoSelBut = QtWidgets.QPushButton('SL')
        self.HeadGeoSelBut.setFixedSize(30, 25)
        self.HeadGeoSelBut.setStyleSheet(self.slColor)
        self.HeadGeoSelBut.setFont(self.font)
        self.geoBox = QtWidgets.QPushButton('*     Head Geo     ')
        self.geoBox.setStyleSheet(self.edgeColor)
        self.geoField = QtWidgets.QLineEdit()
        self.geoField.setFixedSize(100, 25)
        self.LEyeGeoSelBut = QtWidgets.QPushButton('SL')
        self.LEyeGeoSelBut.setFixedSize(30, 25)
        self.LEyeGeoSelBut.setStyleSheet(self.slColor)
        self.LEyeGeoSelBut.setFont(self.font)
        self.LEyeGeo = QtWidgets.QPushButton('*    L Eye Geo     ')
        self.LEyeGeo.setStyleSheet(self.edgeColor)
        self.LEyeBox = QtWidgets.QLineEdit('')
        self.LEyeBox.setFixedSize(100, 25)
        self.REyeGeoSelBut = QtWidgets.QPushButton('SL')
        self.REyeGeoSelBut.setFixedSize(30, 25)
        self.REyeGeoSelBut.setStyleSheet(self.slColor)
        self.REyeGeoSelBut.setFont(self.font)
        self.REyeGeo = QtWidgets.QPushButton('*    R Eye Geo     ')
        self.REyeGeo.setStyleSheet(self.edgeColor)
        self.REyeBox = QtWidgets.QLineEdit('')
        self.REyeBox.setFixedSize(100, 25)
        self.TopTeethGeoSelBut = QtWidgets.QPushButton('SL')
        self.TopTeethGeoSelBut.setFixedSize(30, 25)
        self.TopTeethGeoSelBut.setStyleSheet(self.slColor)
        self.TopTeethGeoSelBut.setFont(self.font)
        self.TopTeethGeo = QtWidgets.QPushButton('*  Up Teeth Geo  ')
        self.TopTeethGeo.setStyleSheet(self.edgeColor)
        self.UpTeethBox = QtWidgets.QLineEdit('')
        self.UpTeethBox.setFixedSize(100, 25)
        self.DownTeethGeoSelBut = QtWidgets.QPushButton('SL')
        self.DownTeethGeoSelBut.setFixedSize(30, 25)
        self.DownTeethGeoSelBut.setStyleSheet(self.slColor)
        self.DownTeethGeoSelBut.setFont(self.font)
        self.DownTeethGeo = QtWidgets.QPushButton('*Down Teeth Geo')
        self.DownTeethGeo.setStyleSheet(self.edgeColor)
        self.DownTeethBox = QtWidgets.QLineEdit('')
        self.DownTeethBox.setFixedSize(100, 25)
        self.TongueGeoSelBut = QtWidgets.QPushButton('SL')
        self.TongueGeoSelBut.setFixedSize(30, 25)
        self.TongueGeoSelBut.setStyleSheet(self.slColor)
        self.TongueGeoSelBut.setFont(self.font)
        self.TongueGeo = QtWidgets.QPushButton('*   Tongue Geo    ')
        self.TongueGeo.setStyleSheet(self.edgeColor)
        self.TongueBox = QtWidgets.QLineEdit('')
        self.TongueBox.setFixedSize(100, 25)
        self.ExtraGeoSelBut = QtWidgets.QPushButton('SL')
        self.ExtraGeoSelBut.setFixedSize(30, 25)
        self.ExtraGeoSelBut.setStyleSheet(self.slColor)
        self.ExtraGeoSelBut.setFont(self.font)
        self.ExtraGeo = QtWidgets.QPushButton('    Extra Geo    ')
        self.ExtraGeo.setStyleSheet(self.edgeColor)
        self.chkExtra = QtWidgets.QCheckBox('')
        self.chkExtra.setVisible(False)
        self.ExtraBox = QtWidgets.QLineEdit('')
        self.ExtraBox.setFixedSize(100, 25)
        self.ComponentBut = QtWidgets.QPushButton('*   Component Mode   ')
        self.selConstraintEdgeLoop = QtWidgets.QPushButton('Edge Loop Off')
        self.selConstraintEdgeLoop.setFixedSize(120, 25)
        self.selConstraintEdgeLoop.setStyleSheet(self.defaultColor)
        self.LEyeLidMainBoxButton = QtWidgets.QPushButton('*LEyeLidMain')
        self.LEyeLidMainBoxButton.setStyleSheet(self.edgeColor)
        self.LTopDownEyeEdgeSelBut = QtWidgets.QPushButton('SL')
        self.LTopDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.LTopDownEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.REyeLidMainBoxButton = QtWidgets.QPushButton('*REyeLidMain')
        self.REyeLidMainBoxButton.setStyleSheet(self.edgeColor)
        self.chkREyeLid = QtWidgets.QCheckBox('')
        self.RTopDownEyeEdgeSelBut = QtWidgets.QPushButton('SL')
        self.RTopDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.RTopDownEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.chkLEyeLid = QtWidgets.QCheckBox('')
        self.LEyeLidTopBoxButton = QtWidgets.QPushButton('Up')
        self.LEyeLidTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.LEyeLidDownBoxButton = QtWidgets.QPushButton('Down')
        self.LEyeLidDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.LTopEyeEdgeSelBut = QtWidgets.QPushButton('SL')
        self.LTopEyeEdgeSelBut.setFixedSize(30, 25)
        self.LTopEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.LDownEyeEdgeSelBut = QtWidgets.QPushButton('SL')
        self.LDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.LDownEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.REyeLidTopBoxButton = QtWidgets.QPushButton('Up')
        self.REyeLidTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.REyeLidDownBoxButton = QtWidgets.QPushButton('Down')
        self.REyeLidDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.RTopEyeEdgeSelBut = QtWidgets.QPushButton('SL')
        self.RTopEyeEdgeSelBut.setFixedSize(30, 25)
        self.RTopEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.RDownEyeEdgeSelBut = QtWidgets.QPushButton('SL')
        self.RDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.RDownEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.REyeLidOuterBoxButton = QtWidgets.QPushButton('*REyeLidOuter')
        self.REyeLidOuterBoxButton.setStyleSheet(self.edgeColor)
        self.chkREyeOuterLid = QtWidgets.QCheckBox('')
        self.RTopDownEyeOuterEdgeSelBut = QtWidgets.QPushButton('SL')
        self.RTopDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.RTopDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.chkLEyeOuterLid = QtWidgets.QCheckBox('')
        self.REyeLidOuterTopBoxButton = QtWidgets.QPushButton('Up')
        self.REyeLidOuterTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.REyeLidOuterDownBoxButton = QtWidgets.QPushButton('Down')
        self.REyeLidOuterDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.RTopEyeOuterEdgeSelBut = QtWidgets.QPushButton('SL')
        self.RTopEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.RTopEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.RDownEyeOuterEdgeSelBut = QtWidgets.QPushButton('SL')
        self.RDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.RDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.LEyeLidOuterBoxButton = QtWidgets.QPushButton('*LEyeLidOuter')
        self.LEyeLidOuterBoxButton.setStyleSheet(self.edgeColor)
        self.LTopDownEyeOuterEdgeSelBut = QtWidgets.QPushButton('SL')
        self.LTopDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.LTopDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.LEyeLidOuterTopBoxButton = QtWidgets.QPushButton('Up')
        self.LEyeLidOuterTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.LEyeLidOuterDownBoxButton = QtWidgets.QPushButton('Down')
        self.LEyeLidOuterDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.LTopEyeOuterEdgeSelBut = QtWidgets.QPushButton('SL')
        self.LTopEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.LTopEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.LDownEyeOuterEdgeSelBut = QtWidgets.QPushButton('SL')
        self.LDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.LDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.NoseBoxButton = QtWidgets.QPushButton('* Nose Edges ')
        self.NoseBoxButton.setStyleSheet(self.edgeColor)
        self.NoseEdgeSelBut = QtWidgets.QPushButton('SL')
        self.NoseEdgeSelBut.setFixedSize(30, 25)
        self.NoseEdgeSelBut.setStyleSheet(self.slColor)
        self.NoseUnderVertexBoxButton = QtWidgets.QPushButton('*NoseUnderVtx')
        self.NoseUnderVertexBoxButton.setStyleSheet(self.edgeColor)
        self.chkNoseEdge = QtWidgets.QCheckBox('')
        self.NoseUnderVertexSelBut = QtWidgets.QPushButton('SL')
        self.NoseUnderVertexSelBut.setFixedSize(30, 25)
        self.NoseUnderVertexSelBut.setStyleSheet(self.slColor)
        self.chkNoseUnderVertex = QtWidgets.QCheckBox('')
        self.LipBoxButton = QtWidgets.QPushButton('*   Lip Edge   ')
        self.LipBoxButton.setStyleSheet(self.edgeColor)
        self.chkLip = QtWidgets.QCheckBox('')
        self.TopDownLipEdgeSelBut = QtWidgets.QPushButton('SL')
        self.TopDownLipEdgeSelBut.setFixedSize(30, 25)
        self.TopDownLipEdgeSelBut.setStyleSheet(self.slColor)
        self.LipUpBoxButton = QtWidgets.QPushButton('Up')
        self.LipUpBoxButton.setStyleSheet(self.edgeIndColor)
        self.LipDownBoxButton = QtWidgets.QPushButton('Down')
        self.LipDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.TopLipEdgeSelBut = QtWidgets.QPushButton('SL')
        self.TopLipEdgeSelBut.setFixedSize(30, 25)
        self.TopLipEdgeSelBut.setStyleSheet(self.slColor)
        self.DownLipEdgeSelBut = QtWidgets.QPushButton('SL')
        self.DownLipEdgeSelBut.setFixedSize(30, 25)
        self.DownLipEdgeSelBut.setStyleSheet(self.slColor)
        self.TongueBoxButton = QtWidgets.QPushButton('*Tongue Edge ')
        self.TongueBoxButton.setStyleSheet(self.edgeColor)
        self.chkTonque = QtWidgets.QCheckBox('')
        self.TongueEdgeSelBut = QtWidgets.QPushButton('SL')
        self.TongueEdgeSelBut.setFixedSize(30, 25)
        self.TongueEdgeSelBut.setStyleSheet(self.slColor)
        self.TongueUpEdgeBoxButton = QtWidgets.QPushButton('Up')
        self.TongueUpEdgeBoxButton.setStyleSheet(self.edgeIndColor)
        self.TongueDownEdgeBoxButton = QtWidgets.QPushButton('Down')
        self.TongueDownEdgeBoxButton.setStyleSheet(self.edgeIndColor)
        self.TopTongueEdgeSelBut = QtWidgets.QPushButton('SL')
        self.TopTongueEdgeSelBut.setFixedSize(30, 25)
        self.TopTongueEdgeSelBut.setStyleSheet(self.slColor)
        self.DownTongueEdgeSelBut = QtWidgets.QPushButton('SL')
        self.DownTongueEdgeSelBut.setFixedSize(30, 25)
        self.DownTongueEdgeSelBut.setStyleSheet(self.slColor)
        self.DownTongueEdgeSelBut.setFont(self.font)
        self.BackHeadNeckBoxButton = QtWidgets.QPushButton('*BackHead_Neck')
        self.BackHeadNeckBoxButton.setStyleSheet(self.edgeColor)
        self.chkBackFace = QtWidgets.QCheckBox('')
        self.BackHeadNeckFaceSelButton = QtWidgets.QPushButton('SL')
        self.BackHeadNeckFaceSelButton.setFixedSize(30, 25)
        self.BackHeadNeckFaceSelButton.setStyleSheet(self.slColor)
        self.ForeheadBoxButton = QtWidgets.QPushButton('* EyeLid_Mask  ')
        self.ForeheadBoxButton.setStyleSheet(self.edgeColor)
        self.checkForeheadFace = QtWidgets.QCheckBox('')
        self.ForeheadFaceSelButton = QtWidgets.QPushButton('SL')
        self.ForeheadFaceSelButton.setFixedSize(30, 25)
        self.ForeheadFaceSelButton.setStyleSheet(self.slColor)
        self.SquashStretchBoxButton = QtWidgets.QPushButton('*Squash_Stretch')
        self.SquashStretchBoxButton.setStyleSheet(self.edgeColor)
        self.checkSquashStretchFace = QtWidgets.QCheckBox('')
        self.SquashStretchFaceSelButton = QtWidgets.QPushButton('SL')
        self.SquashStretchFaceSelButton.setFixedSize(30, 25)
        self.SquashStretchFaceSelButton.setStyleSheet(self.slColor)
        self.modelLayout = QtWidgets.QGridLayout(self)
        self.modelLayout.setHorizontalSpacing(3)
        self.modelLayout.setContentsMargins(3, 3, 3, 3)
        self.modelLayout.addWidget(self.geoBox, 1, 1)
        self.modelLayout.addWidget(self.HeadGeoSelBut, 1, 0)
        self.modelLayout.addWidget(self.geoField, 2, 1)
        self.modelLayout.addWidget(self.REyeGeo, 1, 3)
        self.modelLayout.addWidget(self.REyeGeoSelBut, 1, 2)
        self.modelLayout.addWidget(self.REyeBox, 2, 3)
        self.modelLayout.addWidget(self.LEyeGeo, 1, 5)
        self.modelLayout.addWidget(self.LEyeGeoSelBut, 1, 4)
        self.modelLayout.addWidget(self.LEyeBox, 2, 5)
        self.modelLayout.addWidget(self.TongueGeo, 3, 5)
        self.modelLayout.addWidget(self.TongueGeoSelBut, 3, 4)
        self.modelLayout.addWidget(self.TongueBox, 4, 5)
        self.modelLayout.addWidget(self.TopTeethGeo, 3, 1)
        self.modelLayout.addWidget(self.TopTeethGeoSelBut, 3, 0)
        self.modelLayout.addWidget(self.UpTeethBox, 4, 1)
        self.modelLayout.addWidget(self.DownTeethGeo, 3, 3)
        self.modelLayout.addWidget(self.DownTeethGeoSelBut, 3, 2)
        self.modelLayout.addWidget(self.DownTeethBox, 4, 3)
        self.modelLayout.addWidget(self.ExtraGeo, 1, 7)
        self.modelLayout.addWidget(self.ExtraGeoSelBut, 1, 6)
        self.modelLayout.addWidget(self.ExtraBox, 2, 7)
        self.modelLayout.addWidget(self.chkExtra, 4, 6)
        self.modelLayoutGrp = QtWidgets.QGroupBox('Set Head Models')
        self.modelLayoutGrp.setLayout(self.modelLayout)
        self.componentLayout = QtWidgets.QGridLayout()
        self.componentLayout.setRowStretch(0, 0)
        self.componentLayout.setRowStretch(1, 0)
        self.componentLayout.setRowStretch(2, 0)
        self.componentLayout.addWidget(self.REyeLidMainBoxButton, 0, 1)
        self.componentLayout.addWidget(self.RTopDownEyeEdgeSelBut, 0, 0)
        self.componentLayout.addWidget(self.chkREyeLid, 0, 2)
        self.componentLayout.addWidget(self.REyeLidTopBoxButton, 1, 1)
        self.componentLayout.addWidget(self.RTopEyeEdgeSelBut, 1, 0)
        self.componentLayout.addWidget(self.REyeLidDownBoxButton, 2, 1)
        self.componentLayout.addWidget(self.RDownEyeEdgeSelBut, 2, 0)
        self.componentLayout.addWidget(self.LEyeLidMainBoxButton, 0, 4)
        self.componentLayout.addWidget(self.LTopDownEyeEdgeSelBut, 0, 3)
        self.componentLayout.addWidget(self.chkLEyeLid, 0, 5)
        self.componentLayout.addWidget(self.LEyeLidTopBoxButton, 1, 4)
        self.componentLayout.addWidget(self.LTopEyeEdgeSelBut, 1, 3)
        self.componentLayout.addWidget(self.LEyeLidDownBoxButton, 2, 4)
        self.componentLayout.addWidget(self.LDownEyeEdgeSelBut, 2, 3)
        self.componentLayout.addWidget(self.REyeLidOuterBoxButton, 3, 1)
        self.componentLayout.addWidget(self.RTopDownEyeOuterEdgeSelBut, 3, 0)
        self.componentLayout.addWidget(self.chkREyeOuterLid, 3, 2)
        self.componentLayout.addWidget(self.REyeLidOuterTopBoxButton, 4, 1)
        self.componentLayout.addWidget(self.RTopEyeOuterEdgeSelBut, 4, 0)
        self.componentLayout.addWidget(self.REyeLidOuterDownBoxButton, 5, 1)
        self.componentLayout.addWidget(self.RDownEyeOuterEdgeSelBut, 5, 0)
        self.componentLayout.addWidget(self.LEyeLidOuterBoxButton, 3, 4)
        self.componentLayout.addWidget(self.LTopDownEyeOuterEdgeSelBut, 3, 3)
        self.componentLayout.addWidget(self.chkLEyeOuterLid, 3, 5)
        self.componentLayout.addWidget(self.LEyeLidOuterTopBoxButton, 4, 4)
        self.componentLayout.addWidget(self.LTopEyeOuterEdgeSelBut, 4, 3)
        self.componentLayout.addWidget(self.LEyeLidOuterDownBoxButton, 5, 4)
        self.componentLayout.addWidget(self.LDownEyeOuterEdgeSelBut, 5, 3)
        self.componentLayout.addWidget(self.LipBoxButton, 0, 7)
        self.componentLayout.addWidget(self.TopDownLipEdgeSelBut, 0, 6)
        self.componentLayout.addWidget(self.chkLip, 0, 8)
        self.componentLayout.addWidget(self.LipUpBoxButton, 1, 7)
        self.componentLayout.addWidget(self.TopLipEdgeSelBut, 1, 6)
        self.componentLayout.addWidget(self.LipDownBoxButton, 2, 7)
        self.componentLayout.addWidget(self.DownLipEdgeSelBut, 2, 6)
        self.componentLayout.addWidget(self.TongueBoxButton, 3, 7)
        self.componentLayout.addWidget(self.TongueEdgeSelBut, 3, 6)
        self.componentLayout.addWidget(self.chkTonque, 3, 8)
        self.componentLayout.addWidget(self.TongueUpEdgeBoxButton, 4, 7)
        self.componentLayout.addWidget(self.TopTongueEdgeSelBut, 4, 6)
        self.componentLayout.addWidget(self.TongueDownEdgeBoxButton, 5, 7)
        self.componentLayout.addWidget(self.DownTongueEdgeSelBut, 5, 6)
        self.componentLayout.addWidget(self.NoseBoxButton, 6, 7)
        self.componentLayout.addWidget(self.NoseEdgeSelBut, 6, 6)
        self.componentLayout.addWidget(self.chkNoseEdge, 6, 8)
        self.componentLayout.addWidget(self.NoseUnderVertexBoxButton, 7, 7)
        self.componentLayout.addWidget(self.NoseUnderVertexSelBut, 7, 6)
        self.componentLayout.addWidget(self.chkNoseUnderVertex, 7, 8)
        self.componentLayout.addWidget(self.ForeheadBoxButton, 8, 1)
        self.componentLayout.addWidget(self.ForeheadFaceSelButton, 8, 0)
        self.componentLayout.addWidget(self.checkForeheadFace, 8, 2)
        self.componentLayout.addWidget(self.BackHeadNeckBoxButton, 8, 4)
        self.componentLayout.addWidget(self.BackHeadNeckFaceSelButton, 8, 3)
        self.componentLayout.addWidget(self.chkBackFace, 8, 5)
        self.componentLayout.addWidget(self.SquashStretchBoxButton, 8, 7)
        self.componentLayout.addWidget(self.SquashStretchFaceSelButton, 8, 6)
        self.componentLayout.addWidget(self.checkSquashStretchFace, 8, 8)
        self.componentLayoutGrp = QtWidgets.QGroupBox('Set Components')
        self.componentLayoutGrp.setLayout(self.componentLayout)
        self.componentLayoutGrp.setCheckable(True)
        self.componentLayoutGrp.setChecked(False)
        self.LPupilBoxButton = QtWidgets.QPushButton('*LPupil')
        self.LPupilBoxButton.setStyleSheet(self.edgeColor)
        self.chkLPupil = QtWidgets.QCheckBox('')
        self.LPupilSelButton = QtWidgets.QPushButton('SL')
        self.LPupilSelButton.setFixedSize(30, 25)
        self.LPupilSelButton.setStyleSheet(self.slColor)
        self.RPupilBoxButton = QtWidgets.QPushButton('*RPupil')
        self.RPupilBoxButton.setStyleSheet(self.edgeColor)
        self.chkRPupil = QtWidgets.QCheckBox('')
        self.RPupilSelButton = QtWidgets.QPushButton('SL')
        self.RPupilSelButton.setFixedSize(30, 25)
        self.RPupilSelButton.setStyleSheet(self.slColor)
        self.componentLayout.addWidget(self.LPupilBoxButton, 6, 4)
        self.componentLayout.addWidget(self.chkLPupil, 6, 5)
        self.componentLayout.addWidget(self.LPupilSelButton, 6, 3)
        self.componentLayout.addWidget(self.RPupilBoxButton, 6, 1)
        self.componentLayout.addWidget(self.chkRPupil, 6, 2)
        self.componentLayout.addWidget(self.RPupilSelButton, 6, 0)
        self.LIrisBoxButton = QtWidgets.QPushButton('*LIris')
        self.LIrisBoxButton.setStyleSheet(self.edgeColor)
        self.chkLIris = QtWidgets.QCheckBox('')
        self.LIrisSelButton = QtWidgets.QPushButton('SL')
        self.LIrisSelButton.setFixedSize(30, 25)
        self.LIrisSelButton.setStyleSheet(self.slColor)
        self.componentLayout.addWidget(self.LIrisBoxButton, 7, 4)
        self.componentLayout.addWidget(self.chkLIris, 7, 5)
        self.componentLayout.addWidget(self.LIrisSelButton, 7, 3)
        self.RIrisBoxButton = QtWidgets.QPushButton('*RIris')
        self.RIrisBoxButton.setStyleSheet(self.edgeColor)
        self.chkRIris = QtWidgets.QCheckBox('')
        self.RIrisSelButton = QtWidgets.QPushButton('SL')
        self.RIrisSelButton.setFixedSize(30, 25)
        self.RIrisSelButton.setStyleSheet(self.slColor)
        self.componentLayout.addWidget(self.RIrisBoxButton, 7, 1)
        self.componentLayout.addWidget(self.chkRIris, 7, 2)
        self.componentLayout.addWidget(self.RIrisSelButton, 7, 0)
        self.AdjustmentBoxButton = QtWidgets.QPushButton('Create Jaw Curve *')
        self.AdjustmentBBoxButton = QtWidgets.QPushButton('Create Facial Curve Guide *')
        self.ProjectBoxButton = QtWidgets.QPushButton('Project Curves On face model *')
        self.settingsLayout = QtWidgets.QHBoxLayout()
        self.settingsLayout.addWidget(self.AdjustmentBoxButton)
        self.settingsLayout.addWidget(self.AdjustmentBBoxButton)
        self.settingsLayout.addWidget(self.ProjectBoxButton)
        self.settingsLayoutGrp = QtWidgets.QGroupBox('Create Curve guides')
        self.settingsLayoutGrp.setLayout(self.settingsLayout)
        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.addWidget(self.nameLabelField)
        self.nameLayout.addWidget(self.nameField)
        self.nameLayout.addWidget(self.skinJntSuffixLabel)
        self.nameLayout.addWidget(self.skinJntSuffix)
        self.nameLayout.addWidget(self.chkPrefix)
        self.nameLayout.addStretch()
        self.nameLayoutGrp = QtWidgets.QGroupBox('Set Name')
        self.nameLayoutGrp.setLayout(self.nameLayout)
        self.perseusLabelFieldE = QtWidgets.QLabel('')
        self.perseusLayoutE = QtWidgets.QHBoxLayout()
        self.perseusLayoutE.addWidget(self.perseusLabelFieldE)
        self.perseusLayoutGrpE = QtWidgets.QGroupBox('')
        self.perseusLayoutGrpE.setLayout(self.perseusLayoutE)
        self.perseusLabelFieldF = QtWidgets.QLabel('')
        self.perseusLayoutF = QtWidgets.QHBoxLayout()
        self.perseusLayoutF.addWidget(self.perseusLabelFieldF)
        self.perseusLayoutGrpF = QtWidgets.QGroupBox('')
        self.perseusLayoutGrpF.setLayout(self.perseusLayoutF)
        self.perseusLayout = QtWidgets.QHBoxLayout()
        self.perseusLayout.addWidget(self.perseusLabelField)
        self.perseusLayoutGrp = QtWidgets.QGroupBox('')
        self.perseusLayoutGrp.setLayout(self.perseusLayout)
        self.modeLayout = QtWidgets.QHBoxLayout()
        self.modeLayout.addWidget(self.ComponentBut)
        self.spacer = QtWidgets.QSpacerItem(200, 0)
        self.modeLayout.addSpacerItem(self.spacer)
        self.modeLayout.addWidget(self.selConstraintEdgeLoop)
        self.modeLayoutGrp = QtWidgets.QGroupBox('')
        self.modeLayoutGrp.setLayout(self.modeLayout)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.nameLayoutGrp)
        layout.addWidget(self.modelLayoutGrp)
        layout.addWidget(self.modeLayoutGrp)
        layout.addWidget(self.componentLayoutGrp)
        layout.addWidget(self.settingsLayoutGrp)
        layout.addWidget(self.perseusLayoutGrp)


class settingsWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(settingsWidget, self).__init__(parent)
        self.font = QtG.QFont()
        self.font.setPointSize(10)
        self.font.setBold(True)
        self.edgeColor = 'background-color:rgb(255,102,51);color : black;'
        self.slColor = 'background-color:rgb(0,254,102);color : black;'
        self.edgeIndColor = 'background-color:rgb(0,179,255);color : black;'
        self.progressColor = 'background-color:rgb(76,50,50);color : white;'
        self.defineColor = 'color : white;'
        self.defineColor2 = 'color : black;'
        self.chkMaintainMaxInf = QtWidgets.QCheckBox('Maintain Max Inf Jnts')
        self.chkMaintainMaxInf.setChecked(True)
        self.maxInfs = QtWidgets.QSpinBox()
        self.maxInfs.setProperty('value', 12)
        self.maxInfs.setRange(1, 14)
        self.relaxSkLabel = QtWidgets.QLabel(' Skin Relax Steps ')
        self.relaxSk = QtWidgets.QSpinBox()
        self.relaxSk.setProperty('value', 2)
        self.relaxSk.setRange(0, 5)
        self.chkGame = QtWidgets.QCheckBox('Game Mode')
        self.chkSoftMod = QtWidgets.QCheckBox('SoftMod')
        self.chkSoftMod.setChecked(False)
        self.chkTweaker = QtWidgets.QCheckBox('Tweaker')
        self.chkOptLip = QtWidgets.QCheckBox('Optimize Lip Joints')
        self.chkOptLip.setChecked(True)
        self.lipJnt = QtWidgets.QSpinBox()
        self.lipJnt.setProperty('value', 20)
        self.lipJnt.setRange(4, 100)
        self.chkOptEyelidJnt = QtWidgets.QCheckBox('Optimize Eyelid Joints')
        self.eyelidJnt = QtWidgets.QSpinBox()
        self.eyelidJnt.setProperty('value', 20)
        self.eyelidJnt.setRange(4, 100)
        self.chkOptEye = QtWidgets.QCheckBox('Optimize EyeCrease Joints')
        self.chkOptEye.setChecked(True)
        self.eyeCreaseJnt = QtWidgets.QSpinBox()
        self.eyeCreaseJnt.setProperty('value', 8)
        self.eyeCreaseJnt.setRange(4, 100)
        self.generateRig = QtWidgets.QPushButton('*   CREATE Facial Rig    ')
        self.generateRig.setStyleSheet(self.edgeColor)
        self.progress = QtWidgets.QProgressBar()
        self.progressText = QtWidgets.QLabel('           ')
        self.progressText.setStyleSheet(self.progressColor)
        self.progressText.setFixedSize(170, 25)
        self.SaveSettingsBoxButton = QtWidgets.QPushButton(' Save Data ')
        self.SaveSettingsBoxButton.setFixedSize(150, 25)
        self.LoadSettingsBoxButton = QtWidgets.QPushButton(' Load Data ')
        self.ResetSettingsBoxButton = QtWidgets.QPushButton(' Reset Data ')
        self.LoadSettingsBoxButton.setFixedSize(150, 25)
        self.chkLoadData = QtWidgets.QCheckBox('')
        self.chkSaveData = QtWidgets.QCheckBox('')
        self.picker = QtWidgets.QPushButton('     CREATE PICKER     ')
        self.SaveCtlShapesBoxButton = QtWidgets.QPushButton(' Exp. Ctl. ')
        self.LoadCtlShapesBoxButton = QtWidgets.QPushButton(' Imp. Ctl. ')
        self.bindLayout = QtWidgets.QHBoxLayout()
        self.bindLayout.addWidget(self.chkMaintainMaxInf)
        self.bindLayout.addWidget(self.maxInfs)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.bindLayout.addSpacerItem(self.spacer)
        self.bindLayout.addWidget(self.relaxSkLabel)
        self.bindLayout.addWidget(self.relaxSk)
        self.bindLayout.addStretch()
        self.bindParentlayout = QtWidgets.QHBoxLayout(self)
        self.bindParentlayout.addLayout(self.bindLayout)
        self.bindParentlayout.addStretch()
        self.bindLayoutGrp = QtWidgets.QGroupBox('Bind Skin Option')
        self.bindLayoutGrp.setLayout(self.bindParentlayout)
        self.deformationLayout = QtWidgets.QHBoxLayout()
        self.deformationLayout.addWidget(self.chkGame)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.deformationLayout.addSpacerItem(self.spacer)
        self.deformationLayout.addWidget(self.chkSoftMod)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.deformationLayout.addSpacerItem(self.spacer)
        self.deformationLayout.addWidget(self.chkTweaker)
        self.deformationLayout.addStretch()
        self.deformationParentlayout = QtWidgets.QHBoxLayout(self)
        self.deformationParentlayout.addLayout(self.deformationLayout)
        self.deformationParentlayout.addStretch()
        self.deformationLayoutGrp = QtWidgets.QGroupBox('Deformation Layers ')
        self.deformationLayoutGrp.setLayout(self.deformationParentlayout)
        self.optimizeLayout = QtWidgets.QHBoxLayout()
        self.optimizeLayout.addWidget(self.chkOptLip)
        self.optimizeLayout.addWidget(self.lipJnt)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.optimizeLayout.addSpacerItem(self.spacer)
        self.optimizeLayout.addWidget(self.chkOptEyelidJnt)
        self.optimizeLayout.addWidget(self.eyelidJnt)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.optimizeLayout.addSpacerItem(self.spacer)
        self.optimizeLayout.addStretch()
        self.optimizeParentlayout = QtWidgets.QHBoxLayout(self)
        self.optimizeParentlayout.addLayout(self.optimizeLayout)
        self.optimizeParentlayout.addStretch()
        self.optimizeLayoutGrp = QtWidgets.QGroupBox('Deformation Layers ')
        self.optimizeLayoutGrp.setLayout(self.optimizeParentlayout)
        self.createRigLayout = QtWidgets.QHBoxLayout()
        self.createRigLayoutB = QtWidgets.QHBoxLayout()
        self.createRigLayoutB.addWidget(self.generateRig)
        self.createRigLayoutB.addWidget(self.progressText)
        self.createRigLayoutB.addWidget(self.progress)
        self.createRigParentlayout = QtWidgets.QVBoxLayout(self)
        self.createRigParentlayout.addLayout(self.createRigLayoutB)
        self.createRigParentlayout.addLayout(self.createRigLayout)
        self.createRigParentlayoutGrp = QtWidgets.QGroupBox('Create Facial Rig')
        self.createRigParentlayoutGrp.setLayout(self.createRigParentlayout)
        self.saveLayout = QtWidgets.QHBoxLayout(self)
        self.saveLayout.addWidget(self.chkSaveData)
        self.saveLayout.addWidget(self.SaveSettingsBoxButton)
        self.spacer = QtWidgets.QSpacerItem(80, 0)
        self.saveLayout.addSpacerItem(self.spacer)
        self.saveLayout.addWidget(self.chkLoadData)
        self.saveLayout.addWidget(self.LoadSettingsBoxButton)
        self.saveLayout.addStretch()
        self.saveLayoutGrp = QtWidgets.QGroupBox('Save&Load Settings')
        self.saveLayoutGrp.setLayout(self.saveLayout)
        self.pickerLayout = QtWidgets.QHBoxLayout(self)
        self.pickerLayout.addWidget(self.picker)
        self.pickerLayoutGrp = QtWidgets.QGroupBox('Picker')
        self.pickerLayoutGrp.setLayout(self.pickerLayout)
        self.shapesLayout = QtWidgets.QHBoxLayout(self)
        self.shapesLayout.addWidget(self.SaveCtlShapesBoxButton)
        self.shapesLayout.addWidget(self.LoadCtlShapesBoxButton)
        self.shapesLayoutGrp = QtWidgets.QGroupBox('Import/Export Shapes')
        self.shapesLayoutGrp.setLayout(self.shapesLayout)
        self.mainNameRig = findMainName()
        self.perseusBLabelField = QtWidgets.QLabel(self.mainNameRig)
        self.perseusBLabelField.setStyleSheet(self.progressColor)
        self.perseusBLayout = QtWidgets.QHBoxLayout()
        self.perseusBLayout.addWidget(self.perseusBLabelField)
        self.perseusBLayoutGrp = QtWidgets.QGroupBox('')
        self.perseusBLayoutGrp.setLayout(self.perseusBLayout)
        self.perseusA = QtWidgets.QHBoxLayout(self)
        self.perseusA.addWidget(self.ResetSettingsBoxButton)
        self.perseusALayoutGrp = QtWidgets.QGroupBox('   Reset Settings   ')
        self.perseusALayoutGrp.setLayout(self.perseusA)
        self.perseusE = QtWidgets.QHBoxLayout(self)
        self.perseusELabelField = QtWidgets.QLabel('')
        self.perseusE.addWidget(self.perseusELabelField)
        self.perseusELayoutGrp = QtWidgets.QGroupBox('')
        self.perseusELayoutGrp.setLayout(self.perseusE)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.bindLayoutGrp)
        layout.addWidget(self.deformationLayoutGrp)
        layout.addWidget(self.optimizeLayoutGrp)
        layout.addWidget(self.saveLayoutGrp)
        layout.addWidget(self.createRigParentlayoutGrp)
        layout.addWidget(self.pickerLayoutGrp)
        layout.addWidget(self.shapesLayoutGrp)
        layout.addWidget(self.perseusALayoutGrp)
        layout.addWidget(self.perseusELayoutGrp)
        layout.addWidget(self.perseusBLayoutGrp)

    def toggleGroup(self, ctrl):
        state = ctrl.isChecked()
        if state:
            ctrl.setFixedHeight(ctrl.sizeHint().height())
        else:
            ctrl.setFixedHeight(30)


class skinWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(skinWidget, self).__init__(parent)
        self.progressColor = 'background-color:rgb(76,50,50);color : white;'
        self.prExportSkin = QtWidgets.QPushButton('Export Skin')
        self.prImpSkinAll = QtWidgets.QPushButton('Import Skin')
        self.skinCopy = QtWidgets.QPushButton('Copy Skin')
        self.perseusLabelField = QtWidgets.QLabel('')
        self.perseusLayout = QtWidgets.QVBoxLayout()
        self.perseusLayout.addWidget(self.prExportSkin)
        self.perseusLayout.addWidget(self.prImpSkinAll)
        self.perseusLayout.addWidget(self.skinCopy)
        self.perseusLayoutGrp = QtWidgets.QGroupBox('Copy Skin and Influences')
        self.perseusLayoutGrp.setLayout(self.perseusLayout)
        self.progress = QtWidgets.QProgressBar()
        self.source_define = QtWidgets.QPushButton('Source Component')
        self.destination_define = QtWidgets.QPushButton('Target Component')
        self.copySkinGlobal = QtWidgets.QPushButton('Copy Src. to Trg.')
        self.hammerSkinGlobal = QtWidgets.QPushButton('Hammer Skin Weight')
        self.perseusCLabelField = QtWidgets.QLabel('')
        self.perseusCLayout = QtWidgets.QVBoxLayout()
        self.perseusCLayout.addWidget(self.source_define)
        self.perseusCLayout.addWidget(self.destination_define)
        self.perseusCLayout.addWidget(self.copySkinGlobal)
        self.perseusCLayout.addWidget(self.progress)
        self.perseusCLayout.addWidget(self.hammerSkinGlobal)
        self.perseusCLayoutGrp = QtWidgets.QGroupBox('Copy Skin Components')
        self.perseusCLayoutGrp.setLayout(self.perseusCLayout)
        self.DEFINE_large = QtWidgets.QPushButton('Define Exclusion Set')
        self.EXCLUDE_large = QtWidgets.QPushButton('Exclude System(s)')
        self.excludeLayout = QtWidgets.QVBoxLayout(self)
        self.excludeLayout.addWidget(self.DEFINE_large)
        self.excludeLayout.addWidget(self.EXCLUDE_large)
        self.excludeLayoutGrp = QtWidgets.QGroupBox('Skin Exclusion System')
        self.excludeLayoutGrp.setLayout(self.excludeLayout)
        self.SaveFacialSkinSet = QtWidgets.QPushButton('Set A')
        self.TransferFacialSkinSet = QtWidgets.QPushButton('A To B (Add influences and Cpy.Skin for Game Mode)')
        self.connectBlendShape = QtWidgets.QPushButton('Create Connection(Select body rig head jnt and facial grp)')
        self.connectBlendShapeB = QtWidgets.QPushButton('Create BlendShape (Select facial and body mesh) ')
        self.connectBlendShapeC = QtWidgets.QPushButton('Create Wrap Deformer (Select facial and body mesh) ')
        self.connectBlendShapeD = QtWidgets.QPushButton('Add Space Switch for Eye Aim Ctrl.(Select some Controllers from Body Rig)')
        self.detachSkinJntConnection = QtWidgets.QPushButton('Detach Skin Joints Connection')
        self.attachSkinJntConnection = QtWidgets.QPushButton('Attach Skin Joints Connection')
        self.perseusDLayout = QtWidgets.QVBoxLayout()
        self.perseusDLayout.addWidget(self.SaveFacialSkinSet)
        self.perseusDLayout.addWidget(self.TransferFacialSkinSet)
        self.perseusDLayout.addWidget(self.connectBlendShape)
        self.perseusDLayout.addWidget(self.connectBlendShapeB)
        self.perseusDLayout.addWidget(self.connectBlendShapeC)
        self.perseusDLayout.addWidget(self.connectBlendShapeD)
        self.perseusDLayout.addWidget(self.detachSkinJntConnection)
        self.perseusDLayout.addWidget(self.attachSkinJntConnection)
        self.perseusDLayoutGrp = QtWidgets.QGroupBox('Create Connection From Face --> Body')
        self.perseusDLayoutGrp.setLayout(self.perseusDLayout)
        self.mainNameRig = findMainName()
        self.perseusBLabelField = QtWidgets.QLabel(self.mainNameRig)
        self.perseusBLabelField.setStyleSheet(self.progressColor)
        self.perseusBLayout = QtWidgets.QHBoxLayout()
        self.perseusBLayout.addWidget(self.perseusBLabelField)
        self.perseusBLayoutGrp = QtWidgets.QGroupBox('')
        self.perseusBLayoutGrp.setLayout(self.perseusBLayout)
        self.perseusA = QtWidgets.QHBoxLayout(self)
        self.perseusALabelField = QtWidgets.QLabel('')
        self.perseusA.addWidget(self.perseusALabelField)
        self.perseusALayoutGrp = QtWidgets.QGroupBox('')
        self.perseusALayoutGrp.setLayout(self.perseusA)
        self.perseusE = QtWidgets.QHBoxLayout(self)
        self.perseusELabelField = QtWidgets.QLabel('')
        self.perseusE.addWidget(self.perseusELabelField)
        self.perseusELayoutGrp = QtWidgets.QGroupBox('')
        self.perseusELayoutGrp.setLayout(self.perseusE)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.excludeLayoutGrp)
        layout.addWidget(self.perseusLayoutGrp)
        layout.addWidget(self.perseusCLayoutGrp)
        layout.addWidget(self.perseusDLayoutGrp)
        layout.addWidget(self.perseusALayoutGrp)
        layout.addWidget(self.perseusBLayoutGrp)


class CustomTabWidget(QtWidgets.QWidget):

    def __init__(self):
        super(CustomTabWidget, self).__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setObjectName('customTabBar')
        self.tab_bar.setStyleSheet('#customTabBar {background-color: #383838}')
        self.stacked_wdg = QtWidgets.QStackedWidget()
        self.stacked_wdg.setObjectName('tabBarStackedWidget')
        self.stacked_wdg.setStyleSheet('#tabBarStackedWidget {border: 1px solid #2e2e2e}')

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tab_bar)
        main_layout.addWidget(self.stacked_wdg)

    def create_connections(self):
        self.tab_bar.currentChanged.connect(self.stacked_wdg.setCurrentIndex)

    def addTab(self, widget, label):
        self.tab_bar.addTab(label)
        self.stacked_wdg.addWidget(widget)


class PerseusUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    WINDOW_TITLE = 'Perseus UI'
    UI_NAME = 'PerseusUI'
    ui_instance = None
    perseusDic = {}

    @classmethod
    def show_dialog(cls):
        version = str(cmds.about(v=1))
        if version != '2017':
            if not cls.ui_instance:
                cls.ui_instance = PerseusUI()
            if cls.ui_instance.isHidden():
                cls.ui_instance.show(dockable=True)
            else:
                cls.ui_instance.raise_()
                cls.ui_instance.activateWindow()
        if version == '2017':
            if not cls.ui_instance:
                cls.ui_instance = PerseusUI()
            if cls.ui_instance.isHidden():
                cls.ui_instance.show(dockable=True)
            else:
                cls.ui_instance.raise_()
                cls.ui_instance.activateWindow()
                cls.ui_instance.show(dockable=True)

    def __init__(self, parent=maya_main_window()):
        super(PerseusUI, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.version = str(cmds.about(v=1))
        self.newExclusion = []
        self.setObjectName(self.__class__.UI_NAME)
        self.sizeHint()
        self.mainNameRig = findMainNameB() + self.version
        self.setWindowTitle(self.mainNameRig)
        self.geometry = None
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        return

    def showEvent(self, e):
        super(PerseusUI, self).showEvent(e)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        if isinstance(self, PerseusUI):
            super(PerseusUI, self).closeEvent(e)
            self.geometry = self.saveGeometry()

    def create_widgets(self):
        self.headGeo_wdg = headGeoWidget()
        self.settings_wdg = settingsWidget()
        self.skin_wdg = skinWidget()
        self.tab_widget = CustomTabWidget()
        self.tab_widget.addTab(self.headGeo_wdg, 'Set Models and Components')
        self.tab_widget.addTab(self.settings_wdg, 'Facial Settings')
        self.tab_widget.addTab(self.skin_wdg, 'Skin Tools')

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        layout.addStretch()

    def create_connections(self):
        self.headGeo_wdg.geoBox.clicked.connect(self.LHeadGeoSelUI)
        self.headGeo_wdg.HeadGeoSelBut.clicked.connect(self.sl_headGeo_fn)
        self.headGeo_wdg.REyeGeo.clicked.connect(self.REyeGeoUI)
        self.headGeo_wdg.REyeGeoSelBut.clicked.connect(self.sl_rEyeGeo_fn)
        self.headGeo_wdg.LEyeGeo.clicked.connect(self.LEyeGeoUI)
        self.headGeo_wdg.LEyeGeoSelBut.clicked.connect(self.sl_lEyeGeo_fn)
        self.headGeo_wdg.TopTeethGeo.clicked.connect(self.UpTeethGeoUI)
        self.headGeo_wdg.TopTeethGeoSelBut.clicked.connect(self.sl_topTeethGeo_fn)
        self.headGeo_wdg.DownTeethGeo.clicked.connect(self.DownTeethGeoUI)
        self.headGeo_wdg.DownTeethGeoSelBut.clicked.connect(self.sl_downTeethGeo_fn)
        self.headGeo_wdg.TongueGeo.clicked.connect(self.TongueGeoUI)
        self.headGeo_wdg.TongueGeoSelBut.clicked.connect(self.sl_tongueGeo_fn)
        self.headGeo_wdg.ExtraGeo.clicked.connect(self.ExtraGeoUI)
        self.headGeo_wdg.ExtraGeoSelBut.clicked.connect(self.sl_extraGeo_fn)
        self.headGeo_wdg.REyeLidMainBoxButton.clicked.connect(self.REyeLidMainUI)
        self.headGeo_wdg.RTopDownEyeEdgeSelBut.clicked.connect(self.sl_rEyeLidMain_fn)
        self.headGeo_wdg.LEyeLidMainBoxButton.clicked.connect(self.LEyeLidMainUI)
        self.headGeo_wdg.LTopDownEyeEdgeSelBut.clicked.connect(self.sl_lEyeLidMain_fn)
        self.headGeo_wdg.LEyeLidTopBoxButton.clicked.connect(self.LTopEyeEdgeSelUI)
        self.headGeo_wdg.LEyeLidDownBoxButton.clicked.connect(self.LDownEyeEdgeSelUI)
        self.headGeo_wdg.REyeLidTopBoxButton.clicked.connect(self.RTopEyeEdgeSelUI)
        self.headGeo_wdg.REyeLidDownBoxButton.clicked.connect(self.RDownEyeEdgeSelUI)
        self.headGeo_wdg.LTopEyeEdgeSelBut.clicked.connect(self.sl_lTopEyeEdge_fn)
        self.headGeo_wdg.LDownEyeEdgeSelBut.clicked.connect(self.sl_lDownEyeEdge_fn)
        self.headGeo_wdg.RTopEyeEdgeSelBut.clicked.connect(self.sl_rTopEyeEdge_fn)
        self.headGeo_wdg.RDownEyeEdgeSelBut.clicked.connect(self.sl_rDownEyeEdge_fn)
        self.headGeo_wdg.REyeLidOuterBoxButton.clicked.connect(self.REyeLidOuterUI)
        self.headGeo_wdg.RTopDownEyeOuterEdgeSelBut.clicked.connect(self.sl_rEyeLidOuter_fn)
        self.headGeo_wdg.LEyeLidOuterBoxButton.clicked.connect(self.LEyeLidOuterUI)
        self.headGeo_wdg.LTopDownEyeOuterEdgeSelBut.clicked.connect(self.sl_lEyeLidOuter_fn)
        self.headGeo_wdg.LEyeLidOuterTopBoxButton.clicked.connect(self.LTopEyeOuterEdgeSelUI)
        self.headGeo_wdg.LTopEyeOuterEdgeSelBut.clicked.connect(self.sl_lTopEyeOuterEdge_fn)
        self.headGeo_wdg.LEyeLidOuterDownBoxButton.clicked.connect(self.LDownEyeOuterEdgeSelUI)
        self.headGeo_wdg.LDownEyeOuterEdgeSelBut.clicked.connect(self.sl_lDownEyeOuterEdge_fn)
        self.headGeo_wdg.REyeLidOuterTopBoxButton.clicked.connect(self.RTopEyeOuterEdgeSelUI)
        self.headGeo_wdg.RTopEyeOuterEdgeSelBut.clicked.connect(self.sl_rTopEyeOuterEdge_fn)
        self.headGeo_wdg.REyeLidOuterDownBoxButton.clicked.connect(self.RDownEyeOuterEdgeSelUI)
        self.headGeo_wdg.RDownEyeOuterEdgeSelBut.clicked.connect(self.sl_rDownEyeOuterEdge_fn)
        self.headGeo_wdg.LipBoxButton.clicked.connect(self.LipEdgeUI)
        self.headGeo_wdg.TopDownLipEdgeSelBut.clicked.connect(self.sl_lipTopDown_fn)
        self.headGeo_wdg.LipUpBoxButton.clicked.connect(self.TopLipEdgeSelUI)
        self.headGeo_wdg.TopLipEdgeSelBut.clicked.connect(self.sl_lipTop_fn)
        self.headGeo_wdg.LipDownBoxButton.clicked.connect(self.DownLipEdgeSelUI)
        self.headGeo_wdg.DownLipEdgeSelBut.clicked.connect(self.sl_lipDown_fn)
        self.headGeo_wdg.TongueBoxButton.clicked.connect(self.TongueEdgeUI)
        self.headGeo_wdg.TongueEdgeSelBut.clicked.connect(self.sl_tongueTopDown_fn)
        self.headGeo_wdg.TongueUpEdgeBoxButton.clicked.connect(self.TopTongueEdgeSelUI)
        self.headGeo_wdg.TopTongueEdgeSelBut.clicked.connect(self.sl_tongueTop_fn)
        self.headGeo_wdg.TongueDownEdgeBoxButton.clicked.connect(self.DownTongueEdgeSelUI)
        self.headGeo_wdg.DownTongueEdgeSelBut.clicked.connect(self.sl_tongueDown_fn)
        self.headGeo_wdg.NoseBoxButton.clicked.connect(self.NoseEdgeUI)
        self.headGeo_wdg.NoseEdgeSelBut.clicked.connect(self.sl_noseEdges_fn)
        self.headGeo_wdg.NoseUnderVertexBoxButton.clicked.connect(self.NoseUnderVrtxUI)
        self.headGeo_wdg.NoseUnderVertexSelBut.clicked.connect(self.sl_noseUnderVrtx_fn)
        self.headGeo_wdg.ForeheadBoxButton.clicked.connect(self.ForeheadFaceSelUI)
        self.headGeo_wdg.ForeheadFaceSelButton.clicked.connect(self.sl_foreheadFace_fn)
        self.headGeo_wdg.BackHeadNeckBoxButton.clicked.connect(self.BackHeadNeckFaceSelUI)
        self.headGeo_wdg.BackHeadNeckFaceSelButton.clicked.connect(self.sl_backHeadNeck_fn)
        self.headGeo_wdg.SquashStretchBoxButton.clicked.connect(self.SquashStretchFaceSelUI)
        self.headGeo_wdg.SquashStretchFaceSelButton.clicked.connect(self.sl_squashStretchFace_fn)
        self.headGeo_wdg.LPupilBoxButton.clicked.connect(self.LPupilUI)
        self.headGeo_wdg.LPupilSelButton.clicked.connect(self.sl_LPupil_fn)
        self.headGeo_wdg.RPupilBoxButton.clicked.connect(self.RPupilUI)
        self.headGeo_wdg.RPupilSelButton.clicked.connect(self.sl_RPupil_fn)
        self.headGeo_wdg.LIrisBoxButton.clicked.connect(self.LIrisUI)
        self.headGeo_wdg.LIrisSelButton.clicked.connect(self.sl_LIris_fn)
        self.headGeo_wdg.RIrisBoxButton.clicked.connect(self.RIrisUI)
        self.headGeo_wdg.RIrisSelButton.clicked.connect(self.sl_RIris_fn)
        self.headGeo_wdg.ComponentBut.clicked.connect(self.DuplicateUI)
        self.headGeo_wdg.selConstraintEdgeLoop.clicked.connect(self.EdgeLoopOn_fn)
        self.headGeo_wdg.AdjustmentBoxButton.clicked.connect(self.JawCurveUI)
        self.headGeo_wdg.AdjustmentBBoxButton.clicked.connect(self.FaceCurvesUI)
        self.headGeo_wdg.ProjectBoxButton.clicked.connect(self.projectCrv)
        self.settings_wdg.generateRig.clicked.connect(self.sl_generateRig_fn)
        self.settings_wdg.SaveSettingsBoxButton.clicked.connect(self.FacialSave)
        self.settings_wdg.LoadSettingsBoxButton.clicked.connect(self.FacialLoadUI)
        self.settings_wdg.ResetSettingsBoxButton.clicked.connect(self.FacialResetUI)
        self.settings_wdg.picker.clicked.connect(self.createMGPickerUI)
        self.settings_wdg.SaveCtlShapesBoxButton.clicked.connect(self.FacialSaveCtlShapes)
        self.settings_wdg.LoadCtlShapesBoxButton.clicked.connect(self.FacialLoadCtlShapes)
        self.skin_wdg.DEFINE_large.clicked.connect(self.defineExclusionUI)
        self.skin_wdg.EXCLUDE_large.clicked.connect(self.wfexcludeSystem)
        self.skin_wdg.prExportSkin.clicked.connect(prExportSkin)
        self.skin_wdg.prImpSkinAll.clicked.connect(prImpSkinAll)
        self.skin_wdg.skinCopy.clicked.connect(self.skinCopy)
        self.skin_wdg.source_define.clicked.connect(self.source_define)
        self.skin_wdg.destination_define.clicked.connect(self.destination_define)
        self.skin_wdg.copySkinGlobal.clicked.connect(self.copySkinGlobal)
        self.skin_wdg.hammerSkinGlobal.clicked.connect(self.hammerSkinGlobal)
        self.skin_wdg.SaveFacialSkinSet.clicked.connect(self.SaveFacialSkinSet)
        self.skin_wdg.TransferFacialSkinSet.clicked.connect(self.TransferFacialSkinSet)
        self.skin_wdg.connectBlendShape.clicked.connect(self.connectBlendShape)
        self.skin_wdg.connectBlendShapeB.clicked.connect(self.connectBlendShapeB)
        self.skin_wdg.connectBlendShapeC.clicked.connect(self.connectBlendShapeC)
        self.skin_wdg.connectBlendShapeD.clicked.connect(self.connectBlendShapeD)
        self.skin_wdg.detachSkinJntConnection.clicked.connect(detach_bind_joints)
        self.skin_wdg.attachSkinJntConnection.clicked.connect(attach_bind_joints)

    def sl_generateRig_fn(self):
        self.pre_generateRig_fn()
        response = pm.confirmDialog(title='Save Settings', cancelButton='No', defaultButton='Yes', button=[
         'Yes',
         'No'], message='Would you like to save your settings?', dismissString='No')
        if response == 'Yes':
            self.FacialSave()
        self.generateRig_fn()

    def pre_generateRig_fn(self):
        name = self.headGeo_wdg.nameField.text()
        name = name.replace(' ', '')
        self.headGeo_wdg.nameField.setText(name)
        self.perseusDic['FacialRigName'] = name
        skinJntSuffix = self.headGeo_wdg.skinJntSuffix.text()
        skinJntSuffix = skinJntSuffix.replace(' ', '')
        self.perseusDic['skinJntSuffix'] = skinJntSuffix
        chkPrefix = int(self.headGeo_wdg.chkPrefix.isChecked())
        chkExtra = int(self.headGeo_wdg.chkExtra.isChecked())
        chkMaintainMaxInf = int(self.settings_wdg.chkMaintainMaxInf.isChecked())
        maxInfs = self.settings_wdg.maxInfs.value()
        relaxSk = self.settings_wdg.relaxSk.value()
        chkGame = int(self.settings_wdg.chkGame.isChecked())
        chkSoftMod = int(self.settings_wdg.chkSoftMod.isChecked())
        chkTweaker = int(self.settings_wdg.chkTweaker.isChecked())
        chkOptLip = int(self.settings_wdg.chkOptLip.isChecked())
        lipJnt = self.settings_wdg.lipJnt.value()
        chkOptEyelidJnt = int(self.settings_wdg.chkOptEyelidJnt.isChecked())
        eyelidJnt = self.settings_wdg.eyelidJnt.value()
        chkOptEye = int(self.settings_wdg.chkOptEye.isChecked())
        eyeCreaseJnt = self.settings_wdg.eyeCreaseJnt.value()
        self.perseusDic['chkExtra'] = chkExtra
        self.perseusDic['chkMaintainMaxInf'] = chkMaintainMaxInf
        self.perseusDic['maxInfs'] = maxInfs
        self.perseusDic['relaxSk'] = relaxSk
        self.perseusDic['chkGame'] = chkGame
        self.perseusDic['chkSoftMod'] = chkSoftMod
        self.perseusDic['chkTweaker'] = chkTweaker
        self.perseusDic['chkOptLip'] = chkOptLip
        self.perseusDic['lipJnt'] = lipJnt
        self.perseusDic['chkOptEyelidJnt'] = chkOptEyelidJnt
        self.perseusDic['eyelidJnt'] = eyelidJnt
        self.perseusDic['chkOptEye'] = chkOptEye
        self.perseusDic['eyeCreaseJnt'] = eyeCreaseJnt
        self.perseusDic['chkPrefix'] = chkPrefix
        self.perseusDic['chkPrefix'] = chkPrefix

    def generateRig_fn(self):
        pythonVersion = sys.version_info.major
        if pythonVersion == 3:
            from perseus_main_2022 import perseusRigging_facialRig
        else:
            from perseus_main import perseusRigging_facialRig
        prFacialRig = perseusRigging_facialRig()
        prFacialRig.checkCurveGuideExists(self.perseusDic)

    def sl_headGeo_fn(self):
        cmds.select(self.perseusDic['LHeadGeoSel'], r=1)

    def sl_rEyeGeo_fn(self):
        cmds.select(self.perseusDic['REyeGeoSel'], r=1)

    def sl_lEyeGeo_fn(self):
        cmds.select(self.perseusDic['LEyeGeoSel'], r=1)

    def sl_topTeethGeo_fn(self):
        cmds.select(self.perseusDic['TopTeethGeoSel'], r=1)

    def sl_downTeethGeo_fn(self):
        cmds.select(self.perseusDic['DownTeethGeoSel'], r=1)

    def sl_tongueGeo_fn(self):
        cmds.select(self.perseusDic['TongueGeoSel'], r=1)

    def sl_extraGeo_fn(self):
        cmds.select(self.perseusDic['ExtraGeoSel'], r=1)

    def sl_rEyeLidMain_fn(self):
        self.checkVarExistsB(self.perseusDic['RTopEyeEdgeSel'], self.perseusDic['RDownEyeEdgeSel'], 0, 1)

    def sl_lEyeLidMain_fn(self):
        self.checkVarExistsB(self.perseusDic['LTopEyeEdgeSel'], self.perseusDic['LDownEyeEdgeSel'], 0, 1)

    def sl_lTopEyeEdge_fn(self):
        self.checkVarExists(self.perseusDic['LTopEyeEdgeSel'], 0, 1)

    def sl_lDownEyeEdge_fn(self):
        self.checkVarExists(self.perseusDic['LDownEyeEdgeSel'], 0, 1)

    def sl_rTopEyeEdge_fn(self):
        self.checkVarExists(self.perseusDic['RTopEyeEdgeSel'], 0, 1)

    def sl_rDownEyeEdge_fn(self):
        self.checkVarExists(self.perseusDic['RDownEyeEdgeSel'], 0, 1)

    def sl_rEyeLidOuter_fn(self):
        self.checkVarExistsB(self.perseusDic['RTopEyeOuterEdgeSel'], self.perseusDic['RDownEyeOuterEdgeSel'], 0, 1)

    def sl_lEyeLidOuter_fn(self):
        self.checkVarExistsB(self.perseusDic['LTopEyeOuterEdgeSel'], self.perseusDic['LDownEyeOuterEdgeSel'], 0, 1)

    def sl_lTopEyeOuterEdge_fn(self):
        self.checkVarExists(self.perseusDic['LTopEyeOuterEdgeSel'], 0, 1)

    def sl_lDownEyeOuterEdge_fn(self):
        self.checkVarExists(self.perseusDic['LDownEyeOuterEdgeSel'], 0, 1)

    def sl_rTopEyeOuterEdge_fn(self):
        self.checkVarExists(self.perseusDic['RTopEyeOuterEdgeSel'], 0, 1)

    def sl_rDownEyeOuterEdge_fn(self):
        self.checkVarExists(self.perseusDic['RDownEyeOuterEdgeSel'], 0, 1)

    def sl_lipTopDown_fn(self):
        self.checkVarExistsB(self.perseusDic['DownLipEdgeSel'], self.perseusDic['TopLipEdgeSel'], 0, 1)

    def sl_lipTop_fn(self):
        self.checkVarExists(self.perseusDic['TopLipEdgeSel'], 0, 1)

    def sl_lipDown_fn(self):
        self.checkVarExists(self.perseusDic['DownLipEdgeSel'], 0, 1)

    def sl_tongueTopDown_fn(self):
        self.checkVarExistsB(self.perseusDic['DownTongueEdgeSel'], self.perseusDic['TopTongueEdgeSel'], 0, 1)

    def sl_tongueTop_fn(self):
        self.checkVarExists(self.perseusDic['TopTongueEdgeSel'], 0, 1)

    def sl_tongueDown_fn(self):
        self.checkVarExists(self.perseusDic['DownTongueEdgeSel'], 0, 1)

    def sl_noseEdges_fn(self):
        self.checkVarExists(self.perseusDic['NoseEdgeSel'], 0, 1)

    def sl_noseUnderVrtx_fn(self):
        self.checkVarExists(self.perseusDic['NoseUnderVertexSel'], 0, 0)

    def sl_foreheadFace_fn(self):
        self.checkVarExists(self.perseusDic['ForeheadFaceSel'], 1, 2)

    def sl_backHeadNeck_fn(self):
        self.checkVarExists(self.perseusDic['BackHeadNeckFaceSel'], 0, 2)

    def sl_squashStretchFace_fn(self):
        self.checkVarExists(self.perseusDic['SquashStretchFaceSel'], 0, 2)

    def sl_LPupil_fn(self):
        self.checkVarExists(self.perseusDic['LPupilSel'], 0, 2)

    def sl_RPupil_fn(self):
        self.checkVarExists(self.perseusDic['RPupilSel'], 0, 2)

    def sl_LIris_fn(self):
        self.checkVarExists(self.perseusDic['LIrisSel'], 0, 2)

    def sl_RIris_fn(self):
        self.checkVarExists(self.perseusDic['RIrisSel'], 0, 2)

    def LHeadGeoSelUI(self):
        LHeadGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(LHeadGeoSel.split(':')))
        if chkNameSpace > 1:
            cmds.namespace(removeNamespace=':' + LHeadGeoSel.split(':')[0], mergeNamespaceWithParent=True)
        LHeadGeoSel = cmds.ls(sl=1)[0]
        self.perseusDic['LHeadGeoSel'] = LHeadGeoSel
        self.headGeo_wdg.geoField.setText(LHeadGeoSel)

    def REyeGeoUI(self):
        REyeGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(REyeGeoSel.split(':')))
        if chkNameSpace > 1:
            cmds.namespace(removeNamespace=':' + REyeGeoSel.split(':')[0], mergeNamespaceWithParent=True)
        REyeGeoSel = cmds.ls(sl=1)[0]
        self.perseusDic['REyeGeoSel'] = REyeGeoSel
        self.headGeo_wdg.REyeBox.setText(REyeGeoSel)

    def LEyeGeoUI(self):
        LEyeGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(LEyeGeoSel.split(':')))
        if chkNameSpace > 1:
            cmds.namespace(removeNamespace=':' + LEyeGeoSel.split(':')[0], mergeNamespaceWithParent=True)
        LEyeGeoSel = cmds.ls(sl=1)[0]
        self.perseusDic['LEyeGeoSel'] = LEyeGeoSel
        self.headGeo_wdg.LEyeBox.setText(LEyeGeoSel)

    def UpTeethGeoUI(self):
        TopTeethGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(TopTeethGeoSel.split(':')))
        if chkNameSpace > 1:
            cmds.namespace(removeNamespace=':' + TopTeethGeoSel.split(':')[0], mergeNamespaceWithParent=True)
        TopTeethGeoSel = cmds.ls(sl=1)[0]
        self.perseusDic['TopTeethGeoSel'] = TopTeethGeoSel
        self.headGeo_wdg.UpTeethBox.setText(TopTeethGeoSel)

    def DownTeethGeoUI(self):
        DownTeethGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(DownTeethGeoSel.split(':')))
        if chkNameSpace > 1:
            cmds.namespace(removeNamespace=':' + DownTeethGeoSel.split(':')[0], mergeNamespaceWithParent=True)
        DownTeethGeoSel = cmds.ls(sl=1)[0]
        self.perseusDic['DownTeethGeoSel'] = DownTeethGeoSel
        self.headGeo_wdg.DownTeethBox.setText(DownTeethGeoSel)

    def TongueGeoUI(self):
        TongueGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(TongueGeoSel.split(':')))
        if chkNameSpace > 1:
            cmds.namespace(removeNamespace=':' + TongueGeoSel.split(':')[0], mergeNamespaceWithParent=True)
        TongueGeoSel = cmds.ls(sl=1)[0]
        self.perseusDic['TongueGeoSel'] = TongueGeoSel
        self.headGeo_wdg.TongueBox.setText(TongueGeoSel)

    def ExtraGeoUI(self):
        ExtraGeoSel = cmds.ls(sl=1)
        self.perseusDic['ExtraGeoSel'] = ExtraGeoSel
        self.headGeo_wdg.ExtraBox.setText(str(ExtraGeoSel))
        self.headGeo_wdg.chkExtra.setChecked(True)
        pm.parent(w=1)

    def REyeLidMainUI(self):
        RTopEyeEdgeSel = self.findEdgeUpDown(0)
        RDownEyeEdgeSel = self.findEdgeUpDown(1)
        cmds.select(RDownEyeEdgeSel[int(int(len(RDownEyeEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeEdgeSel[int(int(len(RTopEyeEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = RTopEyeEdgeSel
            RTopEyeEdgeSel = RDownEyeEdgeSel
            RDownEyeEdgeSel = temp
        self.perseusDic['RTopEyeEdgeSel'] = RTopEyeEdgeSel
        self.perseusDic['RDownEyeEdgeSel'] = RDownEyeEdgeSel
        self.headGeo_wdg.chkREyeLid.setChecked(True)

    def LEyeLidMainUI(self):
        LTopEyeEdgeSel = self.findEdgeUpDown(0)
        LDownEyeEdgeSel = self.findEdgeUpDown(1)
        cmds.select(LDownEyeEdgeSel[int(int(len(LDownEyeEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeEdgeSel[int(int(len(LTopEyeEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = LTopEyeEdgeSel
            LTopEyeEdgeSel = LDownEyeEdgeSel
            LDownEyeEdgeSel = temp
        self.perseusDic['LTopEyeEdgeSel'] = LTopEyeEdgeSel
        self.perseusDic['LDownEyeEdgeSel'] = LDownEyeEdgeSel
        self.headGeo_wdg.chkLEyeLid.setChecked(True)

    def REyeLidOuterUI(self):
        RTopEyeOuterEdgeSel = self.findEdgeUpDown(0)
        RDownEyeOuterEdgeSel = self.findEdgeUpDown(1)
        cmds.select(RDownEyeOuterEdgeSel[int(int(len(RDownEyeOuterEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeOuterEdgeSel[int(int(len(RTopEyeOuterEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeOuterEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = RTopEyeOuterEdgeSel
            RTopEyeOuterEdgeSel = RDownEyeOuterEdgeSel
            RDownEyeOuterEdgeSel = temp
        self.perseusDic['RTopEyeOuterEdgeSel'] = RTopEyeOuterEdgeSel
        self.perseusDic['RDownEyeOuterEdgeSel'] = RDownEyeOuterEdgeSel
        self.headGeo_wdg.chkREyeOuterLid.setChecked(True)

    def LEyeLidOuterUI(self):
        LTopEyeOuterEdgeSel = self.findEdgeUpDown(0)
        LDownEyeOuterEdgeSel = self.findEdgeUpDown(1)
        cmds.select(LDownEyeOuterEdgeSel[int(int(len(LDownEyeOuterEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeOuterEdgeSel[int(int(len(LTopEyeOuterEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeOuterEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = LTopEyeOuterEdgeSel
            LTopEyeOuterEdgeSel = LDownEyeOuterEdgeSel
            LDownEyeOuterEdgeSel = temp
        self.perseusDic['LTopEyeOuterEdgeSel'] = LTopEyeOuterEdgeSel
        self.perseusDic['LDownEyeOuterEdgeSel'] = LDownEyeOuterEdgeSel
        self.headGeo_wdg.chkLEyeOuterLid.setChecked(True)

    def LTopEyeEdgeSelUI(self):
        LTopEyeEdgeSel = cmds.ls(sl=1)
        self.perseusDic['LTopEyeEdgeSel'] = LTopEyeEdgeSel

    def LDownEyeEdgeSelUI(self):
        LDownEyeEdgeSel = cmds.ls(sl=1)
        self.perseusDic['LDownEyeEdgeSel'] = LDownEyeEdgeSel

    def RTopEyeEdgeSelUI(self):
        RTopEyeEdgeSel = cmds.ls(sl=1)
        self.perseusDic['RTopEyeEdgeSel'] = RTopEyeEdgeSel

    def RDownEyeEdgeSelUI(self):
        RDownEyeEdgeSel = cmds.ls(sl=1)
        self.perseusDic['RDownEyeEdgeSel'] = RDownEyeEdgeSel

    def LTopEyeOuterEdgeSelUI(self):
        LTopEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseusDic['LTopEyeOuterEdgeSel'] = LTopEyeOuterEdgeSel

    def LDownEyeOuterEdgeSelUI(self):
        LDownEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseusDic['LDownEyeOuterEdgeSel'] = LDownEyeOuterEdgeSel

    def RTopEyeOuterEdgeSelUI(self):
        RTopEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseusDic['RTopEyeOuterEdgeSel'] = RTopEyeOuterEdgeSel

    def RDownEyeOuterEdgeSelUI(self):
        RDownEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseusDic['RDownEyeOuterEdgeSel'] = RDownEyeOuterEdgeSel

    def LipEdgeUI(self):
        TopLipEdgeSel = self.findEdgeUpDown(0)
        DownLipEdgeSel = self.findEdgeUpDown(1)
        cmds.select(DownLipEdgeSel[int(int(len(DownLipEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(TopLipEdgeSel[int(int(len(TopLipEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        if downVV[1] > topVV[1]:
            temp = TopLipEdgeSel
            TopLipEdgeSel = DownLipEdgeSel
            DownLipEdgeSel = temp
        cmds.select(TopLipEdgeSel, r=1)
        self.perseusDic['TopLipEdgeSel'] = TopLipEdgeSel
        self.perseusDic['DownLipEdgeSel'] = DownLipEdgeSel
        self.headGeo_wdg.chkLip.setChecked(True)

    def TopLipEdgeSelUI(self):
        TopLipEdgeSel = cmds.ls(sl=1)
        self.perseusDic['TopLipEdgeSel'] = TopLipEdgeSel

    def DownLipEdgeSelUI(self):
        DownLipEdgeSel = cmds.ls(sl=1)
        self.perseusDic['DownLipEdgeSel'] = DownLipEdgeSel

    def TopTongueEdgeSelUI(self):
        TopTongueEdgeSel = cmds.ls(sl=1)
        self.perseusDic['TopTongueEdgeSel'] = TopTongueEdgeSel

    def DownTongueEdgeSelUI(self):
        DownTongueEdgeSel = cmds.ls(sl=1)
        self.perseusDic['DownTongueEdgeSel'] = DownTongueEdgeSel
        self.headGeo_wdg.chkTonque.setChecked(True)

    def TongueEdgeUI(self):
        TopTongueEdgeSel = self.findEdgeUpDownTongue(0)
        DownTongueEdgeSel = self.findEdgeUpDownTongue(1)
        self.perseusDic['TopTongueEdgeSel'] = TopTongueEdgeSel
        self.perseusDic['DownTongueEdgeSel'] = DownTongueEdgeSel
        self.headGeo_wdg.chkTonque.setChecked(True)

    def NoseEdgeUI(self):
        cmds.ConvertSelectionToVertices()
        NoseEdgeSel = cmds.ls(fl=1, sl=1)
        cmds.ConvertSelectionToContainedEdges()
        self.perseusDic['NoseEdgeSel'] = NoseEdgeSel
        self.headGeo_wdg.chkNoseEdge.setChecked(True)

    def NoseUnderVrtxUI(self):
        cmds.ConvertSelectionToVertices()
        NoseUnderVertexSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['NoseUnderVertexSel'] = NoseUnderVertexSel
        self.headGeo_wdg.chkNoseUnderVertex.setChecked(True)

    def ForeheadFaceSelUI(self):
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        ForeheadFaceSelEx = cmds.ls(fl=1, sl=1)
        headGeoName = LHeadGeoSel
        cmds.select(headGeoName + '.vtx[*]', r=1)
        cmds.select(ForeheadFaceSelEx, d=1)
        ForeheadFaceSel = cmds.ls(fl=1, sl=1)
        cmds.select(ForeheadFaceSelEx, r=1)
        self.perseusDic['ForeheadFaceSel'] = ForeheadFaceSel
        self.headGeo_wdg.checkForeheadFace.setChecked(True)

    def BackHeadNeckFaceSelUI(self):
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        BackHeadNeckFaceSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['BackHeadNeckFaceSel'] = BackHeadNeckFaceSel
        self.headGeo_wdg.chkBackFace.setChecked(True)

    def SquashStretchFaceSelUI(self):
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        SquashStretchFaceSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['SquashStretchFaceSel'] = SquashStretchFaceSel
        self.headGeo_wdg.checkSquashStretchFace.setChecked(True)

    def LPupilUI(self):
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['LPupilSel'] = LPupilSel
        self.headGeo_wdg.chkLPupil.setChecked(True)

    def RPupilUI(self):
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['RPupilSel'] = LPupilSel
        self.headGeo_wdg.chkRPupil.setChecked(True)

    def LIrisUI(self):
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['LIrisSel'] = LPupilSel
        self.headGeo_wdg.chkLIris.setChecked(True)

    def RIrisUI(self):
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type='joint', sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseusDic['RIrisSel'] = LPupilSel
        self.headGeo_wdg.chkRIris.setChecked(True)

    def EdgeLoopOn_fn(self):
        if self.headGeo_wdg.edgeLoopToggle == False:
            pm.mel.dR_selConstraintEdgeLoop()
            self.headGeo_wdg.selConstraintEdgeLoop.setStyleSheet(self.headGeo_wdg.darkColorB)
            self.headGeo_wdg.selConstraintEdgeLoop.setText('Edge Loop On')
            self.headGeo_wdg.edgeLoopToggle = True
        else:
            pm.mel.dR_selConstraintOff()
            self.headGeo_wdg.selConstraintEdgeLoop.setStyleSheet(self.headGeo_wdg.defaultColor)
            self.headGeo_wdg.selConstraintEdgeLoop.setText('Edge Loop Off')
            self.headGeo_wdg.edgeLoopToggle = False

    def EdgeLoopOff_fn(self):
        pm.mel.dR_selConstraintOff()

    def DuplicateUI(self):
        cmds.select(cl=1)
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        LEyeGeoSel = self.perseusDic['LEyeGeoSel']
        REyeGeoSel = self.perseusDic['REyeGeoSel']
        TopTeethGeoSel = self.perseusDic['TopTeethGeoSel']
        DownTeethGeoSel = self.perseusDic['DownTeethGeoSel']
        TongueGeoSel = self.perseusDic['TongueGeoSel']
        cmds.select(LHeadGeoSel, LEyeGeoSel, REyeGeoSel, TopTeethGeoSel, DownTeethGeoSel, TongueGeoSel, r=1)
        self.wffacialDuplicate()
        self.headGeo_wdg.componentLayoutGrp.setChecked(True)

    def wffacialDuplicate(self):
        pm.displaySmoothness(pointsWire=4, polygonObject=1, pointsShaded=1, divisionsV=0, divisionsU=0)
        object = pm.ls(sl=1)
        pm.select(cl=1)
        if pm.objExists('curve1'):
            pm.rename('curve1', 'curve1_temp_perseus')
        if pm.objExists('curve2'):
            pm.rename('curve2', 'curve2_temp_perseus')
        if pm.objExists('facial_geo_grp'):
            pass
        else:
            pm.group(em=1, n='facial_geo_grp')
            pm.select(cl=1)
            for obj in object:
                pm.select(obj, r=1)
                pm.parent(obj, 'facial_geo_grp')

        pm.select(object[0], r=1)
        if self.headGeo_wdg.edgeLoopToggle == False:
            self.EdgeLoopOn_fn()

    def JawCurveUI(self):
        status = True
        chkLEyeLid = int(self.headGeo_wdg.chkLEyeLid.isChecked())
        chkREyeLid = int(self.headGeo_wdg.chkREyeLid.isChecked())
        chkREyeOuterLid = int(self.headGeo_wdg.chkREyeOuterLid.isChecked())
        chkLEyeOuterLid = int(self.headGeo_wdg.chkLEyeOuterLid.isChecked())
        chkNoseEdge = int(self.headGeo_wdg.chkNoseEdge.isChecked())
        chkNoseUnderVertex = int(self.headGeo_wdg.chkNoseUnderVertex.isChecked())
        chkLip = int(self.headGeo_wdg.chkLip.isChecked())
        chkBackFace = int(self.headGeo_wdg.chkBackFace.isChecked())
        checkForeheadFace = int(self.headGeo_wdg.checkForeheadFace.isChecked())
        checkSquashStretchFace = int(self.headGeo_wdg.checkSquashStretchFace.isChecked())
        chkTongue = int(self.headGeo_wdg.chkTonque.isChecked())
        chkLPupil = int(self.headGeo_wdg.chkLPupil.isChecked())
        chkRPupil = int(self.headGeo_wdg.chkLPupil.isChecked())
        chkLIris = int(self.headGeo_wdg.chkLIris.isChecked())
        chkRIris = int(self.headGeo_wdg.chkLIris.isChecked())
        try:
            tempVal = self.perseusDic['LHeadGeoSel']
        except:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Head Geo'")
            status = False

        try:
            tempVal = self.perseusDic['REyeGeoSel']
        except:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'R Eye Geo'")
            status = False

        try:
            tempVal = self.perseusDic['LEyeGeoSel']
        except:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'L Eye Geo'")
            status = False

        try:
            tempVal = self.perseusDic['TopTeethGeoSel']
        except:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Up Teeth Geo'")
            status = False

        try:
            tempVal = self.perseusDic['DownTeethGeoSel']
        except:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Down Teeth Geo'")
            status = False

        try:
            tempVal = self.perseusDic['TongueGeoSel']
        except:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Tongue Geo'")
            status = False

        if chkLEyeLid == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'LEyeLidMain'")
            status = False
        if chkREyeLid == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'REyeLidMain'")
            status = False
        if chkREyeOuterLid == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'REyeLidOuter'")
            status = False
        if chkLEyeOuterLid == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'LEyeLidOuter'")
            status = False
        if chkNoseEdge == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Nose Edges'")
            status = False
        if chkNoseUnderVertex == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'NoseUnderVtx'")
            status = False
        if chkLip == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Lip Edge'")
            status = False
        if chkTongue == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'tongue edges'")
            try:
                cmds.select(self.perseusDic['TongueGeoSel'], r=1)
            except:
                pass

            status = False
        if chkBackFace == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'BackHead_Neck'")
            status = False
        if checkForeheadFace == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'EyeLid Mask'")
            status = False
        if checkSquashStretchFace == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'Squash_Stretch Mask'")
            status = False
        if chkLPupil == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'LPupil'")
            status = False
        if chkRPupil == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'RPupil'")
            status = False
        if chkLIris == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'LIris'")
            status = False
        if chkRIris == 0:
            response = QtWidgets.QMessageBox().information(None, 'Facial Settings', "You must set the 'RIris'")
            status = False
        if status == True:
            DownLipEdgeSel = self.perseusDic['DownLipEdgeSel']
            TopLipEdgeSel = self.perseusDic['TopLipEdgeSel']
            try:
                TopLipEdgeSel
            except NameError:
                TopLipEdgeSel = None

            if TopLipEdgeSel is None:
                pm.confirmDialog(message='Please define the components.', backgroundColor=(0.2,
                                                                                           0.2,
                                                                                           0.2), title='PERSEUS RIGGING')
            else:
                self.Adjustment_a(DownLipEdgeSel, TopLipEdgeSel)
        return

    def Adjustment_a(self, DownLipEdgeSel, TopLipEdgeSel):
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        pos1 = cmds.xform(TopLipEdgeSel[0], q=1, ws=1, t=1)
        pos2 = cmds.xform(TopLipEdgeSel[int(len(TopLipEdgeSel) / 4)], q=1, ws=1, t=1)
        pos3 = cmds.xform(TopLipEdgeSel[int(len(TopLipEdgeSel) / 3)], q=1, ws=1, t=1)
        pos4 = cmds.xform(TopLipEdgeSel[int(int(len(TopLipEdgeSel) / 2))], q=1, ws=1, t=1)
        curve2 = str(cmds.curve(p=[(pos1[0], pos1[1], pos1[2]), (pos2[0], pos2[1], pos2[2]), (pos3[0], pos3[1], pos3[2]), (pos4[0], pos4[1], pos4[2])], k=[0, 1, 2, 3], d=1))
        sizeScale = float(cmds.arclen(curve2))
        cmds.delete(curve2)
        name = 'l'
        curveDis = str(cmds.curve(p=[(0.2, 9.2, 0.66), (0.345, 9.2, 0.65), (0.607, 9.2, 0.589), (0.842, 9.2, 0.427), (1, 9.2, 0.2)], d=1))
        selsel = cmds.ls(sl=1)
        cmds.rename(selsel, str(name) + '_browsCurve')
        pm.rebuildCurve(str(name) + '_browsCurve', rt=0, ch=1, end=1, d=3, kr=0, s=4, kcp=1, tol=0.01, kt=0, rpo=1, kep=1)
        cmds.select(str(name) + '_browsCurve', r=1)
        cmds.instance()
        pm.mel.scale(-1, 1, 1, r=1)
        cmds.select(str(name) + '_browsCurve.cv[*]', r=1)
        verSel = cmds.ls(fl=1, sl=1)
        diss = []
        diss.append(0.0)
        for i in range(1, len(verSel) + 1):
            middle_pos = cmds.xform(str(name) + '_browsCurve.cv[+' + str(i - 1) + ']', q=1, ws=1, t=1)
            end_pos2 = cmds.xform(str(name) + '_browsCurve.cv[+' + str(i) + ']', q=1, ws=1, t=1)
            curveDis = str(cmds.curve(p=[(middle_pos[0], middle_pos[1], middle_pos[2]), (end_pos2[0], end_pos2[1], end_pos2[2])], k=[0, 1], d=1))
            distance = cmds.arclen(curveDis)
            diss.append(diss[(i - 1)] + distance)
            cmds.delete(curveDis)

        distance = cmds.arclen(str(name) + '_browsCurve')
        cmds.select(str(name) + '_browsCurve.cv[*]', r=1)
        verSel = cmds.ls(fl=1, sl=1)
        for i in range(0, len(verSel)):
            cmds.select(cl=1)
            tt = cmds.CreateEmptyGroup()
            cmds.rename(tt, str(name) + '_brows_loc_' + str(i))
            cmds.joint(n=str(name) + '_brows_jnt_' + str(i) + '_skin')
            cmds.select(str(name) + '_brows_loc_' + str(i), str(name) + '_browsCurve', r=1)
            cmds.shadingNode('pointOnCurveInfo', asUtility=1, n=str(name) + '_brows_pcInfo_' + str(i))
            cmds.connectAttr(str(name) + '_browsCurveShape.worldSpace', str(name) + '_brows_pcInfo_' + str(i) + '.inputCurve')
            cmds.setAttr(str(name) + '_brows_pcInfo_' + str(i) + '.parameter', diss[i])
            cmds.connectAttr(str(name) + '_brows_pcInfo_' + str(i) + '.position', str(name) + '_brows_loc_' + str(i) + '.translate', f=1)
            cmds.select(cl=1)

        cmds.select('l_brows_loc_0', 'l_brows_loc_1', 'l_brows_loc_2', 'l_brows_loc_3', 'l_brows_loc_4', r=1)
        cmds.group(n='l_brows_grp')
        cmds.ResetTransformations()
        cmds.duplicate(rr=1, n='r_brows_grp')
        cmds.xform('r_brows_grp', s=(-1, 1, 1))
        cmds.select('r_brows_grp', hi=1)
        pm.mel.searchReplaceNames('l_', 'r_', 'hierarchy')
        cmds.select('l_brows_grp', hi=1)
        cmds.select('l_brows_grp', d=1)
        self.wflrConnect()
        name = 'l'
        curveDis = str(cmds.curve(p=[(0, 10.3, 0.43), (1.12, 10.15, 0.27), (1.5, 9.21, -0.85), (1.5, 8.4, -0.85), (1.4, 7.6, -0.6), (1.07, 7.2, 0), (0.7, 7, 0.7), (0.0, 7.005, 0.879)], d=1))
        selsel = cmds.ls(sl=1)
        cmds.rename(selsel, str(name) + '_jawCurve')
        cmds.select(str(name) + '_jawCurve', r=1)
        cmds.instance()
        pm.mel.scale(-1, 1, 1, r=1)
        cmds.select(str(name) + '_jawCurve.cv[*]', r=1)
        verSel = cmds.ls(fl=1, sl=1)
        diss = []
        diss.append(0.0)
        for i in range(1, len(verSel) + 1):
            middle_pos = cmds.xform(str(name) + '_jawCurve.cv[+' + str(i - 1) + ']', q=1, ws=1, t=1)
            end_pos2 = cmds.xform(str(name) + '_jawCurve.cv[+' + str(i) + ']', q=1, ws=1, t=1)
            curveDis = str(cmds.curve(p=[(middle_pos[0], middle_pos[1], middle_pos[2]), (end_pos2[0], end_pos2[1], end_pos2[2])], k=[0, 1], d=1))
            distance = cmds.arclen(curveDis)
            diss.append(diss[(i - 1)] + distance)
            cmds.delete(curveDis)

        distance = cmds.arclen(str(name) + '_jawCurve')
        verNum = int(cmds.getAttr(str(name) + '_jawCurveShape.spans'))
        cmds.select(str(name) + '_jawCurve.cv[*]', r=1)
        verNumsss = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(verNumsss)):
            cmds.select(cl=1)
            tt = cmds.CreateEmptyGroup()
            cmds.rename(tt, str(name) + '_jaw_loc_' + str(i))
            cmds.joint(n=str(name) + '_jaw_jnt_' + str(i) + '_skin')
            cmds.select(str(name) + '_jaw_loc_' + str(i), str(name) + '_jawCurve', r=1)
            cmds.shadingNode('pointOnCurveInfo', asUtility=1, n=str(name) + '_jaw_pcInfo_' + str(i))
            cmds.connectAttr(str(name) + '_jawCurveShape.worldSpace', str(name) + '_jaw_pcInfo_' + str(i) + '.inputCurve')
            cmds.setAttr(str(name) + '_jaw_pcInfo_' + str(i) + '.parameter', i)
            cmds.connectAttr(str(name) + '_jaw_pcInfo_' + str(i) + '.position', str(name) + '_jaw_loc_' + str(i) + '.translate', f=1)
            cmds.select(cl=1)

        cmds.rebuildCurve(str(name) + '_jawCurve', rt=0, ch=1, end=1, d=3, kr=1, s=0, kcp=0, tol=0.01, kt=1, rpo=1, kep=1)
        cmds.select('l_jaw_loc_1', 'l_jaw_loc_2', 'l_jaw_loc_3', 'l_jaw_loc_4', 'l_jaw_loc_5', 'l_jaw_loc_6', r=1)
        cmds.group(n='l_jaw_grp')
        cmds.ResetTransformations()
        cmds.duplicate(rr=1, n='r_jaw_grp')
        cmds.xform('r_jaw_grp', s=(-1, 1, 1))
        cmds.select('r_jaw_grp', hi=1)
        pm.mel.searchReplaceNames('l_', 'r_', 'hierarchy')
        cmds.select('l_jaw_grp', hi=1)
        cmds.select('l_jaw_grp', d=1)
        self.wflrConnect()
        name = 'neck'
        curveDis = str(cmds.curve(p=[(0, 7.8, -1), (0, 8, -0.77)], d=1))
        selsel = cmds.ls(sl=1)
        cmds.rename(selsel, str(name) + '_neckHeadCurve')
        diss = []
        diss.append(0.0)
        for i in range(1, len(verSel) + 1):
            middle_pos = cmds.xform(str(name) + '_neckHeadCurve.cv[+' + str(i - 1) + ']', q=1, ws=1, t=1)
            end_pos2 = cmds.xform(str(name) + '_neckHeadCurve.cv[+' + str(i) + ']', q=1, ws=1, t=1)
            curveDis = str(cmds.curve(p=[(middle_pos[0], middle_pos[1], middle_pos[2]), (end_pos2[0], end_pos2[1], end_pos2[2])], k=[0, 1], d=1))
            distance = cmds.arclen(curveDis)
            diss.append(diss[(i - 1)] + distance)
            cmds.delete(curveDis)

        distance = cmds.arclen(str(name) + '_neckHeadCurve')
        verNum = int(cmds.getAttr(str(name) + '_neckHeadCurveShape.spans'))
        cmds.select(str(name) + '_neckHeadCurve.cv[*]', r=1)
        verNumsss = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(verNumsss)):
            cmds.select(cl=1)
            tt = cmds.CreateEmptyGroup()
            cmds.rename(tt, str(name) + '_loc_' + str(i))
            cmds.joint(n=str(name) + '_jnt_' + str(i) + '_skin')
            cmds.select(str(name) + '_loc_' + str(i), str(name) + '_neckHeadCurve', r=1)
            cmds.shadingNode('pointOnCurveInfo', asUtility=1, n=str(name) + '_pcInfo_' + str(i))
            cmds.connectAttr(str(name) + '_neckHeadCurveShape.worldSpace', str(name) + '_pcInfo_' + str(i) + '.inputCurve')
            cmds.setAttr(str(name) + '_pcInfo_' + str(i) + '.parameter', i)
            cmds.connectAttr(str(name) + '_pcInfo_' + str(i) + '.position', str(name) + '_loc_' + str(i) + '.translate', f=1)
            cmds.select(cl=1)

        name = 'l'
        curveDis = str(cmds.curve(p=[(0.5, 8.2, 0), (0.7, 8.1, 0), (1, 7.8, 0), (1.2, 7.8, 0), (1.4, 8.2, 0)], d=1))
        selsel = cmds.ls(sl=1)
        cmds.rename(selsel, str(name) + '_cheekCurve')
        cmds.instance()
        pm.mel.scale(-1, 1, 1, r=1)
        cmds.select(str(name) + '_cheekCurve.cv[*]', r=1)
        verSel = cmds.ls(fl=1, sl=1)
        diss = []
        diss.append(0.0)
        for i in range(1, len(verSel) + 1):
            middle_pos = cmds.xform(str(name) + '_cheekCurve.cv[+' + str(i - 1) + ']', q=1, ws=1, t=1)
            end_pos2 = cmds.xform(str(name) + '_cheekCurve.cv[+' + str(i) + ']', q=1, ws=1, t=1)
            curveDis = str(cmds.curve(p=[(middle_pos[0], middle_pos[1], middle_pos[2]), (end_pos2[0], end_pos2[1], end_pos2[2])], k=[0, 1], d=1))
            distance = cmds.arclen(curveDis)
            diss.append(diss[(i - 1)] + distance)
            cmds.delete(curveDis)

        distance = cmds.arclen(str(name) + '_cheekCurve')
        verNum = int(cmds.getAttr(str(name) + '_cheekCurveShape.spans'))
        cmds.select(str(name) + '_cheekCurve.cv[*]', r=1)
        verNumsss = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(verNumsss)):
            cmds.select(cl=1)
            tt = cmds.CreateEmptyGroup()
            cmds.rename(tt, str(name) + '_cheek_loc_' + str(i))
            cmds.joint(n=str(name) + '_cheek_jnt_' + str(i) + '_skin')
            cmds.select(str(name) + '_cheek_loc_' + str(i), str(name) + '_cheekCurve', r=1)
            cmds.shadingNode('pointOnCurveInfo', asUtility=1, n=str(name) + '_cheek_pcInfo_' + str(i))
            cmds.connectAttr(str(name) + '_cheekCurveShape.worldSpace', str(name) + '_cheek_pcInfo_' + str(i) + '.inputCurve')
            cmds.setAttr(str(name) + '_cheek_pcInfo_' + str(i) + '.parameter', i)
            cmds.connectAttr(str(name) + '_cheek_pcInfo_' + str(i) + '.position', str(name) + '_cheek_loc_' + str(i) + '.translate', f=1)
            cmds.select(cl=1)

        cmds.rebuildCurve(str(name) + '_cheekCurve', rt=0, ch=1, end=1, d=1, kr=1, s=0, kcp=0, tol=0.01, kt=1, rpo=1, kep=1)
        cmds.select('l_cheek_loc_0', 'l_cheek_loc_1', 'l_cheek_loc_2', 'l_cheek_loc_3', 'l_cheek_loc_4', r=1)
        cmds.group(n='l_cheek_grp')
        cmds.ResetTransformations()
        cmds.duplicate(rr=1, n='r_cheek_grp')
        cmds.xform('r_cheek_grp', s=(-1, 1, 1))
        cmds.select('r_cheek_grp', hi=1)
        pm.mel.searchReplaceNames('l_', 'r_', 'hierarchy')
        cmds.select('l_cheek_grp', hi=1)
        cmds.select('l_cheek_grp', d=1)
        self.wflrConnect()
        cmds.select('l_jawCurve', r=1)
        cmds.select('l_jawCurve1', tgl=1)
        cmds.select('l_browsCurve', tgl=1)
        cmds.select('l_browsCurve1', tgl=1)
        cmds.select('neck_neckHeadCurve', tgl=1)
        cmds.select('l_cheekCurve', tgl=1)
        cmds.select('l_cheekCurve1', tgl=1)
        cmds.CenterPivot()
        cmds.circle(nr=(0, 1, 0), ch=True, r=1, o=True)
        selsel = cmds.ls(sl=1)
        cmds.rename(selsel, 'all_facial_grp')
        cmds.parentConstraint('neck_jnt_0_skin', 'all_facial_grp', n='all_pc')
        cmds.delete('all_pc')
        cmds.select('all_facial_grp.cv[0:7]', r=1)
        pm.mel.move(0, -1.25, 0, r=1)
        cmds.makeIdentity(n=0, s=1, r=1, t=1, apply=True, pn=1)
        cmds.parent('l_jawCurve', 'l_jawCurve1', 'l_cheekCurve1', 'neck_neckHeadCurve', 'l_cheekCurve', 'l_browsCurve', 'l_browsCurve1', 'all_facial_grp')
        cmds.select('all_facial_grp', r=1)
        cmds.setAttr('l_jawCurve1.visibility', 0)
        cmds.setAttr('l_browsCurve1.visibility', 0)
        cmds.setAttr('l_cheekCurve1.visibility', 0)
        cmds.select(DownLipEdgeSel[int(int(len(DownLipEdgeSel) / 2))], r=1)
        pm.mel.newCluster(' -n adjustClust -envelope 1')
        cmds.parentConstraint('adjustClustHandle', 'all_facial_grp')
        cmds.delete('adjustClustHandle')
        cmds.select('l_brows_jnt_*_skin', 'r_brows_jnt_*_skin', 'l_jaw_jnt_*_skin', 'r_jaw_jnt_*_skin', 'neck_jnt_*_skin', 'l_cheek_jnt_*_skin', 'r_cheek_jnt_*_skin', r=1)
        obj = cmds.ls(sl=1)
        for object in obj:
            cmds.setAttr(str(object) + '.overrideEnabled', 1)
            cmds.setAttr(str(object) + '.overrideColor', 17)

        cmds.setAttr('all_facial_grp.overrideEnabled', 1)
        cmds.setAttr('all_facial_grp.overrideColor', 16)
        cmds.select('neck_jnt_0_skin', r=1)
        cmds.setAttr('neck_jnt_0_skin.drawLabel', 1)
        cmds.setAttr('neck_jnt_0_skin.type', 8)
        cmds.select('neck_jnt_1_skin', r=1)
        cmds.setAttr('neck_jnt_1_skin.drawLabel', 1)
        cmds.setAttr('neck_jnt_1_skin.type', 18)
        cmds.setAttr('neck_jnt_1_skin.otherType', 'jaw', type='string')
        cmds.setAttr('l_cheek_jnt_0_skin.drawLabel', 1)
        cmds.setAttr('l_cheek_jnt_0_skin.type', 18)
        cmds.setAttr('l_cheek_jnt_0_skin.otherType', 'cheek', type='string')
        cmds.setAttr('l_cheek_jnt_1_skin.drawLabel', 1)
        cmds.setAttr('l_cheek_jnt_1_skin.type', 18)
        cmds.setAttr('l_cheek_jnt_1_skin.otherType', 'cheek', type='string')
        cmds.setAttr('l_cheek_jnt_2_skin.drawLabel', 1)
        cmds.setAttr('l_cheek_jnt_2_skin.type', 18)
        cmds.setAttr('l_cheek_jnt_2_skin.otherType', 'cheek', type='string')
        cmds.setAttr('l_cheek_jnt_3_skin.drawLabel', 1)
        cmds.setAttr('l_cheek_jnt_3_skin.type', 18)
        cmds.setAttr('l_cheek_jnt_3_skin.otherType', 'cheek', type='string')
        cmds.setAttr('l_cheek_jnt_4_skin.drawLabel', 1)
        cmds.setAttr('l_cheek_jnt_4_skin.type', 18)
        cmds.setAttr('l_cheek_jnt_4_skin.otherType', 'cheek', type='string')
        cmds.setAttr('l_brows_jnt_0_skin.drawLabel', 1)
        cmds.setAttr('l_brows_jnt_0_skin.type', 18)
        cmds.setAttr('l_brows_jnt_0_skin.otherType', 'brow', type='string')
        cmds.setAttr('l_brows_jnt_1_skin.drawLabel', 1)
        cmds.setAttr('l_brows_jnt_1_skin.type', 18)
        cmds.setAttr('l_brows_jnt_1_skin.otherType', 'brow', type='string')
        cmds.setAttr('l_brows_jnt_2_skin.drawLabel', 1)
        cmds.setAttr('l_brows_jnt_2_skin.type', 18)
        cmds.setAttr('l_brows_jnt_2_skin.otherType', 'brow', type='string')
        cmds.setAttr('l_brows_jnt_3_skin.drawLabel', 1)
        cmds.setAttr('l_brows_jnt_3_skin.type', 18)
        cmds.setAttr('l_brows_jnt_3_skin.otherType', 'brow', type='string')
        cmds.setAttr('l_brows_jnt_4_skin.drawLabel', 1)
        cmds.setAttr('l_brows_jnt_4_skin.type', 18)
        cmds.setAttr('l_brows_jnt_4_skin.otherType', 'brow', type='string')
        cmds.setAttr('l_jawCurve.overrideEnabled', 1)
        cmds.setAttr('l_jawCurve.overrideColor', 16)
        cmds.setAttr('l_browsCurve.overrideEnabled', 1)
        cmds.setAttr('l_browsCurve.overrideColor', 17)
        cmds.select(DownLipEdgeSel[int(int(len(DownLipEdgeSel) / 2))], r=1)
        pm.mel.newCluster(' -n adjustClust -envelope 1')
        cmds.parentConstraint('adjustClustHandle', 'all_facial_grp')
        cmds.delete('adjustClustHandle')
        cmds.select(DownLipEdgeSel[2], r=1)
        pm.mel.modelPanelBarXRayCallback('XRayJointsBtn', 'MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelPanel4', 'MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelEditorIconBar')
        pm.mel.restoreLastPanelWithFocus()
        pm.mel.updateModelPanelBar('MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelPanel4')
        cmds.select(cl=1)
        cmds.select('l_cheekCurve', r=1)
        pm.mel.move(0, 0, 1.307193, r=1, os=1, wd=1)
        cmds.select('l_browsCurve', r=1)
        pm.mel.move(0, 0, 0.8, r=1, os=1, wd=1)
        name = LHeadGeoSel
        pm.mel.setObjectPickMask('All', 0)
        pm.mel.setObjectPickMask('Curve', True)
        cmds.setAttr('makeNurbCircle1.radius', 0.5)
        cmds.select('neck_neckHeadCurve', r=1)
        pm.mel.move(0, 0, -1.05, r=1)
        cmds.select('neck_neckHeadCurve', r=1)
        cmds.parent(w=1)
        cmds.setAttr('all_facial_grp.visibility', 0)
        cmds.setAttr('l_brows_grp.visibility', 0)
        cmds.setAttr('r_brows_grp.visibility', 0)
        cmds.setAttr('l_jaw_loc_0.visibility', 0)
        cmds.setAttr('l_jaw_loc_7.visibility', 0)
        cmds.setAttr('l_jaw_grp.visibility', 0)
        cmds.setAttr('r_jaw_grp.visibility', 0)
        cmds.setAttr('l_cheek_grp.visibility', 0)
        cmds.setAttr('r_cheek_grp.visibility', 0)
        cmds.select(cl=1)
        cmds.select('neck_neckHeadCurve', r=1)
        pm.catch(lambda : pm.mel.lookThroughModelPanel('side', 'modelPanel4'))
        cmds.DisplayWireframe()
        pm.catch(lambda : pm.mel.modelPanelBarXRayCallback('XRayJointsBtn', 'MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelPanel4', 'MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelEditorIconBar'))
        pm.mel.restoreLastPanelWithFocus()
        cmds.select('all_facial_grp', r=1)
        pm.mel.scale(sizeScale * 0.5, sizeScale * 0.5, sizeScale * 0.5, r=1)
        cmds.setAttr('all_facial_grp.tx', lock=True)
        cmds.select('neck_neckHeadCurve', r=1)
        pm.mel.scale(sizeScale * 0.5, sizeScale * 0.5, sizeScale * 0.5, r=1)
        cmds.FrameSelected()
        pm.mel.fitPanel('-selected')
        pm.mel.setComponentPickMask('Line', False)
        cmds.createDisplayLayer(name='tempGeoLayer', empty=1, number=1)
        pm.mel.layerEditorLayerButtonTypeChange('tempGeoLayer')
        pm.mel.layerEditorLayerButtonTypeChange('tempGeoLayer')
        cmds.setAttr('neck_jnt_0_skin.overrideDisplayType', 2)
        cmds.setAttr('neck_jnt_1_skin.overrideDisplayType', 2)
        cmds.setAttr('neck_jnt_0_skin.displayLocalAxis', 1)
        cmds.setAttr('neck_jnt_1_skin.displayLocalAxis', 1)
        cmds.select(cl=1)

    def FaceCurvesUI(self):
        self.Adjustment_a2()

    def Adjustment_a2(self):
        cmds.setAttr('all_facial_grp.visibility', 1)
        cmds.setAttr('l_brows_grp.visibility', 1)
        cmds.setAttr('r_brows_grp.visibility', 1)
        cmds.setAttr('l_jaw_loc_0.visibility', 1)
        cmds.setAttr('l_jaw_loc_7.visibility', 1)
        cmds.setAttr('l_jaw_grp.visibility', 1)
        cmds.setAttr('r_jaw_grp.visibility', 1)
        cmds.setAttr('l_cheek_grp.visibility', 1)
        cmds.setAttr('r_cheek_grp.visibility', 1)
        cmds.setAttr('neck_neckHeadCurve.visibility', 0)
        pm.select(cl=1)
        pm.select('all_facial_grp', r=1)
        pm.mel.lookThroughModelPanel('front', 'modelPanel4')
        cmds.DisplayWireframe()
        pm.catch(lambda : pm.mel.modelPanelBarXRayCallback('XRayJointsBtn', 'MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelPanel4', 'MayaWindow|formLayout1|viewPanes|modelPanel4|modelPanel4|modelEditorIconBar'))
        pm.mel.restoreLastPanelWithFocus()

    def projectCrv(self):
        cmds.undoInfo(openChunk=True)
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        headGeo = LHeadGeoSel
        cmds.select('l_browsCurve', r=1)
        cmds.select(headGeo, tgl=1)
        pm.mel.lookThroughModelPanel('front', 'modelPanel4')
        cmds.polyProjectCurve('l_browsCurve', headGeo, ch=True, automatic=1, pointsOnEdges=0, curveSamples=50, n='brow')
        pm.mel.lookThroughModelPanel('persp', 'modelPanel4')
        cmds.select('browShape_*', r=1)
        cmds.select('browShape_Shape*', d=1)
        objSel = cmds.ls(sl=1)
        poss = []
        for i in range(0, len(objSel)):
            cmds.select(objSel[i], r=1)
            cmds.CenterPivot()
            centerPos = cmds.xform(objSel[i], q=1, ws=1, piv=1)
            poss.append(float(centerPos[2]))

        sortPos = sorted(poss)
        for i in range(0, len(objSel)):
            centerPos = cmds.xform(objSel[i], q=1, ws=1, piv=1)
            if centerPos[2] == sortPos[(len(objSel) - 1)]:
                cmds.select(objSel[i], r=1)
                break

        firstCurve = cmds.ls(sl=1)
        cmds.parent(w=1)
        cmds.select('browShape', r=1)
        pm.mel.doDelete()
        cmds.rebuildCurve(firstCurve, rt=0, ch=1, end=1, d=3, kr=0, s=1, kcp=0, tol=0.01, kt=0, rpo=1, kep=1)
        startPos = cmds.xform(str(firstCurve[0]) + '.cv[0]', q=1, ws=1, t=1)
        endPos = cmds.xform(str(firstCurve[0]) + '.cv[3]', q=1, ws=1, t=1)
        if startPos[0] > endPos[0]:
            cmds.reverseCurve(firstCurve, ch=1, rpo=1)
        for i in range(0, 5):
            cmds.select(firstCurve, r=1)
            cmds.pickWalk(d='down')
            childFirst = cmds.ls(sl=1)
            cmds.disconnectAttr('|all_facial_grp|l_browsCurve1|l_browsCurveShape.worldSpace[0]', 'l_brows_pcInfo_' + str(i) + '.inputCurve')
            cmds.connectAttr(str(childFirst[0]) + '.worldSpace[0]', 'l_brows_pcInfo_' + str(i) + '.inputCurve')

        cmds.setAttr(str(firstCurve[0]) + '.overrideEnabled', 1)
        cmds.setAttr(str(firstCurve[0]) + '.overrideColor', 17)
        cmds.select(firstCurve[0], r=1)
        cmds.select('all_facial_grp', add=1)
        cmds.parent()
        cmds.select('l_browsCurve', r=1)
        pm.mel.doDelete()
        cmds.rename(firstCurve, 'l_browsCurve ')
        cmds.select('l_jawCurve', r=1)
        cmds.select(headGeo, tgl=1)
        pm.mel.lookThroughModelPanel('front', 'modelPanel4')
        cmds.polyProjectCurve('l_jawCurve', headGeo, ch=True, automatic=1, pointsOnEdges=0, curveSamples=50, n='jaw')
        pm.mel.lookThroughModelPanel('persp', 'modelPanel4')
        cmds.select('jawShape_*', r=1)
        cmds.select('jawShape_Shape*', d=1)
        objSel = cmds.ls(sl=1)
        possJ = []
        for i in range(0, len(objSel)):
            cmds.select(objSel[i], r=1)
            cmds.CenterPivot()
            centerPos = cmds.xform(objSel[i], q=1, ws=1, piv=1)
            possJ.append(float(centerPos[2]))

        sortPos = sorted(possJ)
        for i in range(0, len(objSel)):
            centerPos = cmds.xform(objSel[i], q=1, ws=1, piv=1)
            if centerPos[2] == sortPos[(len(objSel) - 1)]:
                cmds.select(objSel[i], r=1)
                break

        firstCurve = cmds.ls(sl=1)
        cmds.parent(w=1)
        cmds.select('jawShape', r=1)
        pm.mel.doDelete()
        cmds.rebuildCurve(firstCurve, rt=0, ch=1, end=1, d=3, kr=2, s=7, kcp=0, tol=0.01, kt=0, rpo=1, kep=1)
        startPos = cmds.xform(str(firstCurve[0]) + '.cv[0]', q=1, ws=1, t=1)
        endPos = cmds.xform(str(firstCurve[0]) + '.cv[9]', q=1, ws=1, t=1)
        if startPos[1] < endPos[1]:
            cmds.reverseCurve(firstCurve, ch=1, rpo=1)
        for i in range(0, 8):
            cmds.select(firstCurve, r=1)
            cmds.pickWalk(d='down')
            childFirst = cmds.ls(sl=1)
            cmds.disconnectAttr('|all_facial_grp|l_jawCurve|l_jawCurveShape.worldSpace[0]', 'l_jaw_pcInfo_' + str(i) + '.inputCurve')
            cmds.connectAttr(str(childFirst[0]) + '.worldSpace[0]', 'l_jaw_pcInfo_' + str(i) + '.inputCurve')

        cmds.setAttr(str(firstCurve[0]) + '.overrideEnabled', 1)
        cmds.setAttr(str(firstCurve[0]) + '.overrideColor', 17)
        cmds.select(firstCurve[0], r=1)
        cmds.select('all_facial_grp', add=1)
        cmds.parent()
        cmds.select('l_jawCurve', r=1)
        pm.mel.doDelete()
        cmds.rename(firstCurve, 'l_jawCurve ')
        cmds.select('l_cheekCurve', r=1)
        cmds.select(headGeo, tgl=1)
        pm.mel.lookThroughModelPanel('front', 'modelPanel4')
        cmds.polyProjectCurve('l_cheekCurve', headGeo, ch=True, automatic=1, pointsOnEdges=0, curveSamples=50, n='cheek')
        pm.mel.lookThroughModelPanel('persp', 'modelPanel4')
        cmds.select('cheekShape_*', r=1)
        cmds.select('cheekShape_Shape*', d=1)
        objSel = cmds.ls(sl=1)
        possC = []
        for i in range(0, len(objSel)):
            cmds.select(objSel[i], r=1)
            cmds.CenterPivot()
            centerPos = cmds.xform(objSel[i], q=1, ws=1, piv=1)
            possC.append(float(centerPos[2]))

        sortPos = sorted(possC)
        for i in range(0, len(objSel)):
            centerPos = cmds.xform(objSel[i], q=1, ws=1, piv=1)
            if centerPos[2] == sortPos[(len(objSel) - 1)]:
                cmds.select(objSel[i], r=1)
                break

        firstCurve = cmds.ls(sl=1)
        cmds.parent(w=1)
        cmds.select('cheekShape', r=1)
        pm.mel.doDelete()
        cmds.rebuildCurve(firstCurve, rt=0, ch=1, end=1, d=1, kr=2, s=4, kcp=0, tol=0.01, kt=0, rpo=1, kep=1)
        startPos = cmds.xform(str(firstCurve[0]) + '.cv[0]', q=1, ws=1, t=1)
        endPos = cmds.xform(str(firstCurve[0]) + '.cv[4]', q=1, ws=1, t=1)
        if startPos[0] > endPos[0]:
            cmds.reverseCurve(firstCurve, ch=1, rpo=1)
        for i in range(0, 5):
            cmds.select(firstCurve, r=1)
            cmds.pickWalk(d='down')
            childFirst = cmds.ls(sl=1)
            cmds.disconnectAttr('|all_facial_grp|l_cheekCurve1|l_cheekCurveShape.worldSpace[1]', 'l_cheek_pcInfo_' + str(i) + '.inputCurve')
            cmds.connectAttr(str(childFirst[0]) + '.worldSpace[0]', 'l_cheek_pcInfo_' + str(i) + '.inputCurve')

        cmds.setAttr(str(firstCurve[0]) + '.overrideEnabled', 1)
        cmds.setAttr(str(firstCurve[0]) + '.overrideColor', 17)
        cmds.select(firstCurve[0], r=1)
        cmds.select('all_facial_grp', add=1)
        cmds.parent()
        cmds.select('l_cheekCurve', r=1)
        pm.mel.doDelete()
        cmds.rename(firstCurve, 'l_cheekCurve ')
        self.tab_widget.tab_bar.setCurrentIndex(1)
        cmds.undoInfo(closeChunk=True)

    def wflrRename(self):
        sels = pm.ls(sl=1)
        s = len(sels) - 1
        while s >= 0:
            sel = sels[s]
            size = len(sel)
            last = sel[size - 1:size]
            if last == '1' or last == '2':
                pm.rename(sel, 'r_' + sel[2:size - 1])
            else:
                pm.rename(sel, 'r_' + sel[2:size])
            s -= 1

    def wflrConnect(self):
        sels = cmds.ls(transforms=1, sl=1)
        for sel in sels:
            size = len(sel)
            cmds.connectAttr(str(sel) + '.t', 'r_' + sel[2:size] + '.t')
            cmds.connectAttr(str(sel) + '.r', 'r_' + sel[2:size] + '.r')
            cmds.connectAttr(str(sel) + '.s', 'r_' + sel[2:size] + '.s')
            cmds.setAttr('r_' + sel[2:size] + '.overrideColor', 1)

    def checkVarExists(self, NewList, invert, type):
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        if len(NewList) != 0:
            pm.select(NewList, r=1)
            if invert == 1:
                cmds.ConvertSelectionToVertices()
                headGeoName = LHeadGeoSel
                pm.select(headGeoName + '.vtx[*]', r=1)
                pm.select(NewList, d=1)
            if len(NewList) != 1:
                if type == 0:
                    cmds.ConvertSelectionToVertices()
                if type == 1:
                    cmds.ConvertSelectionToVertices()
                if type == 2:
                    cmds.ConvertSelectionToVertices()
        else:
            pm.select(cl=1)
            print('The variable has not been assigned ')

    def checkVarExistsB(self, NewList, NewListB, invert, type):
        if len(NewList) != 0:
            pm.select(NewList, NewListB, r=1)
            if invert == 1:
                pm.mel.invertSelection()
            if len(NewList) != 1:
                if type == 0:
                    cmds.ConvertSelectionToContainedEdges()
                if type == 1:
                    cmds.ConvertSelectionToContainedEdges()
                if type == 2:
                    cmds.ConvertSelectionToContainedEdges()
        else:
            pm.select(cl=1)
            print('The variable has not been assigned ')

    def findEdgeUpDown(self, upDown):
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        vertexList = ['']
        vertexList = []
        downEdge = []
        name = LHeadGeoSel
        edgeSel = cmds.ls(fl=1, sl=1)
        cmds.ConvertSelectionToVertices()
        vertexList = cmds.ls(fl=1, sl=1)
        posX = []
        first = []
        end = []
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            posX.append(pos[0])

        posSort = sorted(posX)
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            if pos[0] == posSort[0]:
                cmds.select(vertexList[i], r=1)
                first = cmds.ls(sl=1)
            if pos[0] == posSort[(len(vertexList) - 1)]:
                cmds.select(vertexList[i], r=1)
                end = cmds.ls(sl=1)

        cmds.select(first, r=1)
        cmds.select(end, r=1)
        cmds.select(first, r=1)
        cmds.GrowPolygonSelectionRegion()
        cmds.select(first, end, d=1)
        selNew = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(vertexList)):
            for j in range(0, len(selNew)):
                if selNew[j] == vertexList[i]:
                    cmds.select(selNew[j], tgl=1)

        upDownSel = cmds.ls(fl=1, sl=1)
        pos1 = cmds.xform(upDownSel[0], q=1, t=1)
        pos2 = cmds.xform(upDownSel[1], q=1, t=1)
        if upDown == 1:
            if pos1[1] < pos2[1]:
                cmds.select(upDownSel[0], r=1)
            else:
                cmds.select(upDownSel[1], r=1)
        else:
            if upDown == 0:
                if pos1[1] > pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)
            downVertex = []
            downVertex.append(first[0])
            second = cmds.ls(fl=1, sl=1)
            downVertex.append(second[0])
            for k in range(2, len(vertexList)):
                cmds.GrowPolygonSelectionRegion()
                cmds.select(downVertex[(k - 2)], downVertex[(k - 1)], d=1)
                selNew = cmds.ls(fl=1, sl=1)
                cmds.select(cl=1)
                for i in range(0, len(vertexList)):
                    for j in range(0, len(selNew)):
                        if selNew[j] == vertexList[i]:
                            cmds.select(selNew[j], add=1)

                self.wfFixEdgeLoopA(upDown)
                second = cmds.ls(fl=1, sl=1)
                pos1 = cmds.xform(second[0], q=1, t=1)
                pos2 = cmds.xform(end[0], q=1, t=1)
                if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
                    break
                downVertex.append(second[0])

        downVertex.append(end[0])
        cmds.select(edgeSel, r=1)
        cmds.ConvertSelectionToContainedEdges()
        if self.headGeo_wdg.edgeLoopToggle == False:
            self.EdgeLoopOn_fn()
        pm.catch(lambda : pm.mel.doMenuComponentSelection(name, 'edge'))
        return downVertex

    def wfFixEdgeLoopA(self, upDown):
        upDownSel = cmds.ls(fl=1, sl=1)
        if len(upDownSel) == 2:
            upDownSel = cmds.ls(fl=1, sl=1)
            pos1 = cmds.xform(upDownSel[0], q=1, t=1)
            pos2 = cmds.xform(upDownSel[1], q=1, t=1)
            if upDown == 1:
                if pos1[1] < pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)
            elif upDown == 0:
                if pos1[1] > pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)

    def findEdgeUpDownTongue(self, upDown):
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        name = LHeadGeoSel
        vertexList = []
        downEdge = []
        downEdge = []
        edgeSel = cmds.ls(fl=1, sl=1)
        cmds.ConvertSelectionToVertices()
        vertexList = cmds.ls(fl=1, sl=1)
        posX = []
        first = []
        end = []
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            posX.append(pos[2])

        posSort = sorted(posX)
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            if pos[2] == posSort[0]:
                cmds.select(vertexList[i], r=1)
                first = cmds.ls(sl=1)
            if pos[2] == posSort[(len(vertexList) - 1)]:
                cmds.select(vertexList[i], r=1)
                end = cmds.ls(sl=1)

        cmds.select(first, r=1)
        cmds.select(end, r=1)
        cmds.select(first, r=1)
        cmds.GrowPolygonSelectionRegion()
        cmds.select(first, end, d=1)
        selNew = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(vertexList)):
            for j in range(0, len(selNew)):
                if selNew[j] == vertexList[i]:
                    cmds.select(selNew[j], tgl=1)

        upDownSel = cmds.ls(fl=1, sl=1)
        pos1 = cmds.xform(upDownSel[0], q=1, t=1)
        pos2 = cmds.xform(upDownSel[1], q=1, t=1)
        if upDown == 1:
            if pos1[1] < pos2[1]:
                cmds.select(upDownSel[0], r=1)
            else:
                cmds.select(upDownSel[1], r=1)
        else:
            if upDown == 0:
                if pos1[1] > pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)
            downVertex = []
            downVertex = []
            downVertex.append(first[0])
            second = cmds.ls(fl=1, sl=1)
            downVertex.append(second[0])
            for k in range(2, len(vertexList)):
                cmds.GrowPolygonSelectionRegion()
                cmds.select(downVertex[(k - 2)], downVertex[(k - 1)], d=1)
                selNew = cmds.ls(fl=1, sl=1)
                for i in range(0, len(vertexList)):
                    for j in range(0, len(selNew)):
                        if selNew[j] == vertexList[i]:
                            cmds.select(selNew[j], r=1)

                second = cmds.ls(fl=1, sl=1)
                pos1 = cmds.xform(second[0], q=1, t=1)
                pos2 = cmds.xform(end[0], q=1, t=1)
                if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
                    break
                downVertex.append(second[0])

        downVertex.append(end[0])
        cmds.select(edgeSel, r=1)
        cmds.ConvertSelectionToContainedEdges()
        if self.headGeo_wdg.edgeLoopToggle == False:
            self.EdgeLoopOn_fn()
        return downVertex

    def FacialSave(self):
        self.pre_generateRig_fn()
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        skinJntSuffix = self.perseusDic['skinJntSuffix']
        if cmds.window('OptionBoxWindow', exists=1):
            cmds.deleteUI('OptionBoxWindow', window=1)
        pm.mel.saveOptionBoxSize()
        basicFilter = '*.json'
        fDialog = cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=2)
        fDialogCurve = fDialog[0].replace('.json', '')
        fDialogCurve = fDialogCurve + '.ma'
        pm.select(cl=1)
        if len(fDialog) != 0:
            adress = fDialog[0]
            self.to_json(self.perseusDic, adress)
        skinMesh = LHeadGeoSel
        try:
            bSMainName = cmds.ls(type='blendShape', *(cmds.listHistory(skinMesh) or []))[0]
        except:
            bSMainName = 'None'

        if bSMainName != 'None':
            temp = cmds.listAttr(bSMainName + '.w', m=1)
            if cmds.objExists(skinMesh + '_prs_trg') == 1:
                cmds.delete(skinMesh + '_prs_trg')
            cmds.duplicate(skinMesh, rr=1, n=skinMesh + '_prs_trg')
            try:
                cmds.parent(skinMesh + '_prs_trg', w=1)
            except:
                pass

            cmds.setAttr(skinMesh + '_prs_trg.visibility', 0)
            cmds.select(skinMesh + '_prs_trg', r=1)
        pm.select('l_brows_grp', 'r_brows_grp', 'l_jaw_loc_0', 'l_jaw_loc_7', 'l_jaw_grp', 'r_jaw_grp', 'neck_loc_0', 'neck_loc_1', 'l_cheek_grp', 'r_cheek_grp', 'all_facial_grp', 'neck_neckHeadCurve', add=1)
        cmds.file(fDialogCurve, pr=1, typ='mayaAscii', force=1, options='v=0;', es=1)
        if cmds.objExists(skinMesh + '_prs_trg') == 1:
            cmds.delete(skinMesh + '_prs_trg')
        self.settings_wdg.chkSaveData.setChecked(1)

    def FacialLoad(self):
        self.headGeo_wdg.chkLEyeLid.setChecked(True)
        self.headGeo_wdg.chkREyeLid.setChecked(True)
        self.headGeo_wdg.chkREyeOuterLid.setChecked(True)
        self.headGeo_wdg.chkLEyeOuterLid.setChecked(True)
        self.headGeo_wdg.chkNoseEdge.setChecked(True)
        self.headGeo_wdg.chkNoseUnderVertex.setChecked(True)
        self.headGeo_wdg.chkLip.setChecked(True)
        self.headGeo_wdg.chkTonque.setChecked(True)
        self.headGeo_wdg.chkBackFace.setChecked(True)
        self.headGeo_wdg.checkForeheadFace.setChecked(True)
        self.headGeo_wdg.checkSquashStretchFace.setChecked(True)
        self.headGeo_wdg.chkLPupil.setChecked(True)
        self.headGeo_wdg.chkRPupil.setChecked(True)
        self.headGeo_wdg.chkLIris.setChecked(True)
        self.headGeo_wdg.chkRIris.setChecked(True)
        self.headGeo_wdg.componentLayoutGrp.setChecked(True)
        pm.select(cl=1)

    def FacialLoadUI(self):
        self.FacialResetUI()
        pm.mel.reflectionSetMode('none')
        nextLine = ''
        basicFilter = '*.json'
        fDialogLd = str(pm.fileDialog(dm='*.json'))
        fDialogLdCurve = fDialogLd.replace('.json', '.ma')
        with open(fDialogLd, 'r') as (fp):
            data = json.load(fp)
        self.perseusDic = data
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        self.headGeo_wdg.geoField.setText(self.perseusDic['LHeadGeoSel'])
        self.headGeo_wdg.REyeBox.setText(self.perseusDic['REyeGeoSel'])
        self.headGeo_wdg.LEyeBox.setText(self.perseusDic['LEyeGeoSel'])
        self.headGeo_wdg.UpTeethBox.setText(self.perseusDic['TopTeethGeoSel'])
        self.headGeo_wdg.DownTeethBox.setText(self.perseusDic['DownTeethGeoSel'])
        self.headGeo_wdg.TongueBox.setText(self.perseusDic['TongueGeoSel'])
        try:
            self.headGeo_wdg.chkPrefix.setChecked(self.perseusDic['chkPrefix'])
            self.headGeo_wdg.skinJntSuffix.setText(self.perseusDic['skinJntSuffix'])
        except:
            pass

        self.settings_wdg.chkMaintainMaxInf.setChecked(self.perseusDic['chkMaintainMaxInf'])
        self.settings_wdg.maxInfs.setValue(self.perseusDic['maxInfs'])
        self.settings_wdg.relaxSk.setValue(self.perseusDic['relaxSk'])
        self.settings_wdg.chkGame.setChecked(self.perseusDic['chkGame'])
        self.settings_wdg.chkSoftMod.setChecked(self.perseusDic['chkSoftMod'])
        self.settings_wdg.chkTweaker.setChecked(self.perseusDic['chkTweaker'])
        self.settings_wdg.chkOptLip.setChecked(self.perseusDic['chkOptLip'])
        self.settings_wdg.lipJnt.setValue(self.perseusDic['lipJnt'])
        self.settings_wdg.chkOptEyelidJnt.setChecked(self.perseusDic['chkOptEyelidJnt'])
        self.settings_wdg.eyelidJnt.setValue(self.perseusDic['eyelidJnt'])
        self.settings_wdg.chkOptEye.setChecked(self.perseusDic['chkOptEye'])
        self.settings_wdg.eyeCreaseJnt.setValue(self.perseusDic['eyeCreaseJnt'])
        if self.perseusDic['chkExtra'] == 1:
            self.headGeo_wdg.ExtraBox.setText(str(self.perseusDic['ExtraGeoSel']))
            self.headGeo_wdg.chkExtra.setChecked(True)
        if cmds.objExists('neck_neckHeadCurve') == 0:
            cmds.file(fDialogLdCurve, pr=1, ignoreVersion=1, i=1, type='mayaAscii', namespace=':', ra=True, mergeNamespacesOnClash=True, options='v=0;')
            if cmds.objExists(LHeadGeoSel + '_prs_trg') == 1:
                cmds.select(LHeadGeoSel, r=1)
                cmds.DeleteHistory()
                cmds.blendShape(LHeadGeoSel + '_prs_trg', LHeadGeoSel, n=LHeadGeoSel + '_bs')
                cmds.setAttr(LHeadGeoSel + '_bs.' + LHeadGeoSel + '_prs_trg', 1)
        self.sl_lEyeLidMain_fn()
        self.LEyeLidMainUI()
        self.sl_rEyeLidMain_fn()
        self.REyeLidMainUI()
        self.sl_rEyeLidOuter_fn()
        self.REyeLidOuterUI()
        self.sl_lEyeLidOuter_fn()
        self.LEyeLidOuterUI()
        self.sl_lipTopDown_fn()
        self.LipEdgeUI()
        self.EdgeLoopOff_fn()
        self.FacialLoad()
        cmds.select(LHeadGeoSel, r=1)
        self.settings_wdg.chkLoadData.setChecked(1)
        cmds.select(cl=1)
        mel.eval('print "Facial Data Setting has been loaded successfully.";')

    def FacialResetUI(self):
        self.perseusDic = {}
        self.headGeo_wdg.chkExtra.setChecked(False)
        self.headGeo_wdg.chkLIris.setChecked(False)
        self.headGeo_wdg.chkLPupil.setChecked(False)
        self.headGeo_wdg.chkRIris.setChecked(False)
        self.headGeo_wdg.chkRPupil.setChecked(False)
        self.headGeo_wdg.chkLEyeLid.setChecked(False)
        self.headGeo_wdg.chkREyeLid.setChecked(False)
        self.headGeo_wdg.chkREyeOuterLid.setChecked(False)
        self.headGeo_wdg.chkLEyeOuterLid.setChecked(False)
        self.headGeo_wdg.chkNoseEdge.setChecked(False)
        self.headGeo_wdg.chkNoseUnderVertex.setChecked(False)
        self.headGeo_wdg.chkLip.setChecked(False)
        self.headGeo_wdg.chkTonque.setChecked(False)
        self.headGeo_wdg.chkBackFace.setChecked(False)
        self.headGeo_wdg.checkForeheadFace.setChecked(False)
        self.headGeo_wdg.checkSquashStretchFace.setChecked(False)
        self.headGeo_wdg.componentLayoutGrp.setChecked(False)
        self.settings_wdg.chkMaintainMaxInf.setChecked(True)
        self.settings_wdg.chkMaintainMaxInf.setChecked(True)
        self.settings_wdg.chkGame.setChecked(False)
        self.settings_wdg.chkSoftMod.setChecked(False)
        self.settings_wdg.chkTweaker.setChecked(False)
        self.settings_wdg.chkOptLip.setChecked(True)
        self.settings_wdg.chkOptEye.setChecked(True)
        self.settings_wdg.chkOptEyelidJnt.setChecked(False)
        self.settings_wdg.maxInfs.setProperty('value', 12)
        self.settings_wdg.relaxSk.setProperty('value', 2)
        self.settings_wdg.lipJnt.setProperty('value', 20)
        self.settings_wdg.eyelidJnt.setProperty('value', 20)
        self.settings_wdg.eyeCreaseJnt.setProperty('value', 8)
        self.headGeo_wdg.nameField.setText('name')
        self.headGeo_wdg.geoField.setText('')
        self.headGeo_wdg.LEyeBox.setText('')
        self.headGeo_wdg.REyeBox.setText('')
        self.headGeo_wdg.UpTeethBox.setText('')
        self.headGeo_wdg.DownTeethBox.setText('')
        self.headGeo_wdg.TongueBox.setText('')
        self.headGeo_wdg.ExtraBox.setText('')
        self.settings_wdg.progress.setValue(0)
        self.settings_wdg.progressText.setText('')

    def FacialLoadCtlShapesNoUI(self, ctrlPath, nameRig):
        name = nameRig
        nextLine = ''
        basicFilter = '*.ma'
        fDialogLd = ctrlPath
        if nameRig != None:
            if cmds.objExists(name + '_facial_shapeCtrl_grp') == 0:
                cmds.file(fDialogLd, pr=1, ignoreVersion=1, i=1, type='mayaAscii', namespace=':', ra=True, mergeNamespacesOnClash=True, options='v=0;')
                cmds.select(name + '_facialRig_controllers_grp', r=1)
                facialCtrl = cmds.ls(sl=1)
                cmds.select(cl=1)
                for obj in facialCtrl:
                    if cmds.objExists(obj + '_buffer') == 1:
                        oldChild = cmds.listRelatives(obj, children=1, type='shape')
                        ctrlChild = cmds.listRelatives(obj + '_buffer', children=1, type='shape')
                        for i in range(0, len(ctrlChild)):
                            cmds.parent(ctrlChild[i], obj, s=1, r=1)

                        cmds.delete(oldChild)

                cmds.delete(name + '_facial_shapeCtrl_grp')
                cmds.select(name + '_facialRig_controllers_grp', r=1)
                facialCtrl = pm.ls(sl=1)
                for obj in facialCtrl:
                    origChild = cmds.listRelatives(str(obj), children=1, type='shape')
                    if len(origChild) == 1:
                        cmds.rename(str(obj.getShape()), str(obj) + 'Shape')
                    else:
                        for i in range(0, len(origChild)):
                            cmds.rename(origChild[i], str(obj) + 'Shape' + str(i))

        else:
            if cmds.objExists('facial_shapeCtrl_grp') == 0:
                cmds.file(fDialogLd, pr=1, ignoreVersion=1, i=1, type='mayaAscii', namespace=':', ra=True, mergeNamespacesOnClash=True, options='v=0;')
                cmds.select('facialRig_controllers_grp', r=1)
                facialCtrl = cmds.ls(sl=1)
                cmds.select(cl=1)
                for obj in facialCtrl:
                    if cmds.objExists(obj + '_buffer') == 1:
                        oldChild = cmds.listRelatives(obj, children=1, type='shape')
                        ctrlChild = cmds.listRelatives(obj + '_buffer', children=1, type='shape')
                        for i in range(0, len(ctrlChild)):
                            cmds.parent(ctrlChild[i], obj, s=1, r=1)

                        cmds.delete(oldChild)

                cmds.delete('facial_shapeCtrl_grp')
                cmds.select('facialRig_controllers_grp', r=1)
                facialCtrl = pm.ls(sl=1)
                for obj in facialCtrl:
                    origChild = cmds.listRelatives(str(obj), children=1, type='shape')
                    if len(origChild) == 1:
                        cmds.rename(str(obj.getShape()), str(obj) + 'Shape')
                    else:
                        for i in range(0, len(origChild)):
                            cmds.rename(origChild[i], str(obj) + 'Shape' + str(i))

            cmds.select(cl=1)
        return

    def FacialLoadNoUI(self, jsonPath):
        pm.mel.reflectionSetMode('none')
        nextLine = ''
        basicFilter = '*.json'
        fDialogLd = jsonPath
        fDialogLdCurve = fDialogLd.replace('.json', '.ma')
        with open(fDialogLd, 'r') as (fp):
            data = json.load(fp)
        self.perseusDic = data
        LHeadGeoSel = self.perseusDic['LHeadGeoSel']
        if cmds.objExists('neck_neckHeadCurve') == 0:
            cmds.file(fDialogLdCurve, pr=1, ignoreVersion=1, i=1, type='mayaAscii', namespace=':', ra=True, mergeNamespacesOnClash=True, options='v=0;')
            if cmds.objExists(LHeadGeoSel + '_prs_trg') == 1:
                cmds.select(LHeadGeoSel, r=1)
                cmds.DeleteHistory()
                cmds.blendShape(LHeadGeoSel + '_prs_trg', LHeadGeoSel, n=LHeadGeoSel + '_bs')
                cmds.setAttr(LHeadGeoSel + '_bs.' + LHeadGeoSel + '_prs_trg', 1)
        self.sl_lEyeLidMain_fn()
        self.LEyeLidMainUI()
        self.sl_rEyeLidMain_fn()
        self.REyeLidMainUI()
        self.sl_rEyeLidOuter_fn()
        self.REyeLidOuterUI()
        self.sl_lEyeLidOuter_fn()
        self.LEyeLidOuterUI()
        self.sl_lipTopDown_fn()
        self.LipEdgeUI()
        self.EdgeLoopOff_fn()
        cmds.select(cl=1)
        return data
        mel.eval('print "Facial Data Setting has been loaded successfully.";')

    def to_json(self, dictionary, filename):
        with open(filename, 'w') as (fp):
            json.dump(dictionary, fp, sort_keys=True, indent=4, ensure_ascii=False)

    def createMGPickerUI(self):
        import Facial3
        name = self.headGeo_wdg.nameField.text()
        name = name.replace(' ', '')
        self.headGeo_wdg.nameField.setText(name)
        name = str(name)
        path = Facial3.__file__
        pathPerseusBiped = os.path.dirname(path) + '/'
        pickerName = 'pickerBodyFacial'
        response = pm.confirmDialog(title='Create Picker', cancelButton='Cancel', defaultButton='Biped', button=[
         'Biped',
         'Facial', 'Biped&Facial', 'Quadruped', 'Quadruped$Facial', 'Cancel'], message='', dismissString='No')
        if response != 'Cancel':
            if response == 'Facial':
                pickerName = 'pickerFacial'
            else:
                if response == 'Biped':
                    pickerName = 'pickerBody'
                elif response == 'Biped&Facial':
                    pickerName = 'pickerBipedFacial'
                elif response == 'Quadruped':
                    pickerName = 'pickerQuadruped'
                elif response == 'Quadruped$Facial':
                    pickerName = 'pickerQuadrupedFacial'
                basicFilter = '*.mgpkr'
                fDialog = cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=2)
                pickerFile = fDialog[0]
                newPath = pathPerseusBiped
                newPath = newPath + pickerName + '.mgpkr'
                fin = open(newPath, 'rt')
                fout = open(pickerFile, 'wt')
                pathPerseusBipedB = pathPerseusBiped.replace('\\', '/')
                for line in fin:
                    newLine = line.replace('name_', name + '_')
                    newLineB = newLine.replace("'name'", "'" + name + "'")
                    fout.write(newLineB)

            fin.close()
            fout.close()

    def FacialSaveCtlShapes(self):
        name = self.headGeo_wdg.nameField.text()
        name = name.replace(' ', '')
        self.headGeo_wdg.nameField.setText(name)
        name = str(name)
        chkPrefix = int(self.headGeo_wdg.chkPrefix.isChecked())
        if cmds.window('OptionBoxWindow', exists=1):
            cmds.deleteUI('OptionBoxWindow', window=1)
        pm.mel.saveOptionBoxSize()
        basicFilter = '*.ma'
        fDialog = cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=2)
        fDialogCurve = fDialog[0].replace('.ma', '')
        fDialogCurve = fDialogCurve + '.ma'
        if fDialog != None:
            if chkPrefix == 0:
                if cmds.objExists(name + '_facial_shapeCtrl_grp') == 0:
                    cmds.group(em=1, n=name + '_facial_shapeCtrl_grp')
                    cmds.select(name + '_facialRig_controllers_grp', r=1)
                    facialCtrl = cmds.ls(sl=1)
                    cmds.select(cl=1)
                    for obj in facialCtrl:
                        cmds.select(obj, r=1)
                        cmds.duplicate(rr=1, n=obj + '_buffer')
                        ctrlChild = pm.listRelatives(obj + '_buffer', children=1, type='transform')
                        for childC in ctrlChild:
                            cmds.delete(str(childC))

                        cmds.select(obj + '_buffer', r=1)
                        cmds.group(n=obj + '_buffer_grp')
                        cmds.parent(obj + '_buffer_grp', name + '_facial_shapeCtrl_grp')
                        cmds.sets(obj + '_buffer', edit=1, rm=name + '_facialRig_controllers_grp')

                pm.setAttr(name + '_facial_shapeCtrl_grp.visibility', 0)
                cmds.select(name + '_facial_shapeCtrl_grp', hi=1)
                cmds.DeleteHistory()
                try:
                    cmds.disconnectAttr(name + '_jaw_ctrl.scale', name + '_jaw_fk_ctrl_buffer.inverseScale')
                except:
                    pass

                cmds.file(fDialogCurve, pr=1, typ='mayaAscii', force=1, options='v=0;', es=1, constructionHistory=0, con=0)
                cmds.delete(name + '_facial_shapeCtrl_grp')
                cmds.select(cl=1)
            else:
                if cmds.objExists('facial_shapeCtrl_grp') == 0:
                    cmds.group(em=1, n='facial_shapeCtrl_grp')
                    cmds.select('facialRig_controllers_grp', r=1)
                    facialCtrl = cmds.ls(sl=1)
                    cmds.select(cl=1)
                    for obj in facialCtrl:
                        cmds.select(obj, r=1)
                        cmds.duplicate(rr=1, n=obj + '_buffer')
                        ctrlChild = pm.listRelatives(obj + '_buffer', children=1, type='transform')
                        for childC in ctrlChild:
                            cmds.delete(str(childC))

                        cmds.select(obj + '_buffer', r=1)
                        cmds.group(n=obj + '_buffer_grp')
                        cmds.parent(obj + '_buffer_grp', 'facial_shapeCtrl_grp')
                        cmds.sets(obj + '_buffer', edit=1, rm='facialRig_controllers_grp')

                pm.setAttr('facial_shapeCtrl_grp.visibility', 0)
                cmds.select('facial_shapeCtrl_grp', hi=1)
                cmds.DeleteHistory()
                try:
                    cmds.disconnectAttr('jaw_ctrl.scale', 'jaw_fk_ctrl_buffer.inverseScale')
                except:
                    pass

                cmds.file(fDialogCurve, pr=1, typ='mayaAscii', force=1, options='v=0;', es=1, constructionHistory=0, con=0)
                cmds.delete('facial_shapeCtrl_grp')
                cmds.select(cl=1)
        return

    def FacialSaveCtlShapesNoUI(self, name):
        chkPrefix = 0
        if name == None:
            chkPrefix = 1
        if cmds.window('OptionBoxWindow', exists=1):
            cmds.deleteUI('OptionBoxWindow', window=1)
        pm.mel.saveOptionBoxSize()
        basicFilter = '*.ma'
        fDialog = cmds.fileDialog2(fileFilter=basicFilter, dialogStyle=2)
        fDialogCurve = fDialog[0].replace('.ma', '')
        fDialogCurve = fDialogCurve + '.ma'
        if fDialog != None:
            if chkPrefix == 0:
                if cmds.objExists(name + '_facial_shapeCtrl_grp') == 0:
                    cmds.group(em=1, n=name + '_facial_shapeCtrl_grp')
                    cmds.select(name + '_facialRig_controllers_grp', r=1)
                    facialCtrl = cmds.ls(sl=1)
                    cmds.select(cl=1)
                    for obj in facialCtrl:
                        cmds.select(obj, r=1)
                        cmds.duplicate(rr=1, n=obj + '_buffer')
                        ctrlChild = pm.listRelatives(obj + '_buffer', children=1, type='transform')
                        for childC in ctrlChild:
                            cmds.delete(str(childC))

                        cmds.select(obj + '_buffer', r=1)
                        cmds.group(n=obj + '_buffer_grp')
                        cmds.parent(obj + '_buffer_grp', name + '_facial_shapeCtrl_grp')
                        cmds.sets(obj + '_buffer', edit=1, rm=name + '_facialRig_controllers_grp')

                pm.setAttr(name + '_facial_shapeCtrl_grp.visibility', 0)
                cmds.select(name + '_facial_shapeCtrl_grp', hi=1)
                cmds.DeleteHistory()
                try:
                    cmds.disconnectAttr(name + '_jaw_ctrl.scale', name + '_jaw_fk_ctrl_buffer.inverseScale')
                except:
                    pass

                cmds.file(fDialogCurve, pr=1, typ='mayaAscii', force=1, options='v=0;', es=1, constructionHistory=0, con=0)
                cmds.delete(name + '_facial_shapeCtrl_grp')
                cmds.select(cl=1)
            else:
                if cmds.objExists('facial_shapeCtrl_grp') == 0:
                    cmds.group(em=1, n='facial_shapeCtrl_grp')
                    cmds.select('facialRig_controllers_grp', r=1)
                    facialCtrl = cmds.ls(sl=1)
                    cmds.select(cl=1)
                    for obj in facialCtrl:
                        cmds.select(obj, r=1)
                        cmds.duplicate(rr=1, n=obj + '_buffer')
                        ctrlChild = pm.listRelatives(obj + '_buffer', children=1, type='transform')
                        for childC in ctrlChild:
                            cmds.delete(str(childC))

                        cmds.select(obj + '_buffer', r=1)
                        cmds.group(n=obj + '_buffer_grp')
                        cmds.parent(obj + '_buffer_grp', 'facial_shapeCtrl_grp')
                        cmds.sets(obj + '_buffer', edit=1, rm='facialRig_controllers_grp')

                pm.setAttr('facial_shapeCtrl_grp.visibility', 0)
                cmds.select('facial_shapeCtrl_grp', hi=1)
                cmds.DeleteHistory()
                try:
                    cmds.disconnectAttr('jaw_ctrl.scale', 'jaw_fk_ctrl_buffer.inverseScale')
                except:
                    pass

                cmds.file(fDialogCurve, pr=1, typ='mayaAscii', force=1, options='v=0;', es=1, constructionHistory=0, con=0)
                cmds.delete('facial_shapeCtrl_grp')
                cmds.select(cl=1)
        return

    def FacialLoadCtlShapes(self):
        name = self.headGeo_wdg.nameField.text()
        name = name.replace(' ', '')
        self.headGeo_wdg.nameField.setText(name)
        name = str(name)
        chkPrefix = int(self.headGeo_wdg.chkPrefix.isChecked())
        nextLine = ''
        basicFilter = '*.ma'
        fDialogLd = str(pm.fileDialog(dm='*.ma'))
        if chkPrefix == 0:
            if cmds.objExists(name + '_facial_shapeCtrl_grp') == 0:
                cmds.file(fDialogLd, pr=1, ignoreVersion=1, i=1, type='mayaAscii', namespace=':', ra=True, mergeNamespacesOnClash=True, options='v=0;')
                cmds.select(name + '_facialRig_controllers_grp', r=1)
                facialCtrl = cmds.ls(sl=1)
                cmds.select(cl=1)
                for obj in facialCtrl:
                    if cmds.objExists(obj + '_buffer') == 1:
                        oldChild = cmds.listRelatives(obj, children=1, type='shape')
                        ctrlChild = cmds.listRelatives(obj + '_buffer', children=1, type='shape')
                        for i in range(0, len(ctrlChild)):
                            cmds.parent(ctrlChild[i], obj, s=1, r=1)

                        cmds.delete(oldChild)

                cmds.delete(name + '_facial_shapeCtrl_grp')
                cmds.select(name + '_facialRig_controllers_grp', r=1)
                facialCtrl = pm.ls(sl=1)
                for obj in facialCtrl:
                    origChild = cmds.listRelatives(str(obj), children=1, type='shape')
                    if len(origChild) == 1:
                        cmds.rename(str(obj.getShape()), str(obj) + 'Shape')
                    else:
                        for i in range(0, len(origChild)):
                            cmds.rename(origChild[i], str(obj) + 'Shape' + str(i))

        else:
            if cmds.objExists('facial_shapeCtrl_grp') == 0:
                cmds.file(fDialogLd, pr=1, ignoreVersion=1, i=1, type='mayaAscii', namespace=':', ra=True, mergeNamespacesOnClash=True, options='v=0;')
                cmds.select('facialRig_controllers_grp', r=1)
                facialCtrl = cmds.ls(sl=1)
                cmds.select(cl=1)
                for obj in facialCtrl:
                    if cmds.objExists(obj + '_buffer') == 1:
                        oldChild = cmds.listRelatives(obj, children=1, type='shape')
                        ctrlChild = cmds.listRelatives(obj + '_buffer', children=1, type='shape')
                        for i in range(0, len(ctrlChild)):
                            cmds.parent(ctrlChild[i], obj, s=1, r=1)

                        cmds.delete(oldChild)

                cmds.delete('facial_shapeCtrl_grp')
                cmds.select('facialRig_controllers_grp', r=1)
                facialCtrl = pm.ls(sl=1)
                for obj in facialCtrl:
                    origChild = cmds.listRelatives(str(obj), children=1, type='shape')
                    if len(origChild) == 1:
                        cmds.rename(str(obj.getShape()), str(obj) + 'Shape')
                    else:
                        for i in range(0, len(origChild)):
                            cmds.rename(origChild[i], str(obj) + 'Shape' + str(i))

            cmds.select(cl=1)

    def defineExclusionUI(self):
        self.newExclusion = self.wfdefineExclusionSet()
        pm.selectMode(object=1)

    def wfdefineExclusionSet(self):
        cmds.ConvertSelectionToVertices()
        object = cmds.ls(fl=1, sl=1)
        return object
        cmds.select(cl=1)
        cmds.SelectToggleMode()
        pm.mel.toggleSelMode()
        pm.mel.updateSelectionModeIcons()
        pm.mel.dR_selTypeChanged('')

    def wfexcludeSystem(self):
        name = self.headGeo_wdg.nameField.text()
        name = name.replace(' ', '')
        self.headGeo_wdg.nameField.setText(name)
        name = str(name)
        scriptSkPercent = ''
        vertexList = self.newExclusion
        vertexNum = len(vertexList)
        ClusterName = []
        numTokens = ClusterName = vertexList[0].split('.')
        SkCluster = str(pm.mel.findRelatedSkinCluster(ClusterName[0]))
        objects = cmds.ls(sl=1)
        infJooints = []
        jntListSkin = ''
        verListSkin = []
        for obj in objects:
            index = int(pm.getAttr(str(obj) + '.index'))
            cmds.select(cl=1)
            jntListSkin = ''
            verListSkin = []
            for i in range(0, len(vertexList)):
                verListSkin.append(vertexList[i])

            if index == 1:
                pm.catch(lambda : pm.select(name + '_downLip_jnt_*_skin', name + '_jaw_lip_r_1_skin', name + '_jaw_lip_r_0_skin', name + '_jaw_lip_l_1_skin', name + '_jaw_lip_l_0_skin', name + '_jaw_lip_c_skin', r=1))
            else:
                if index == 2:
                    pm.catch(lambda : pm.select(name + '_upLip_jnt_*_skin', r=1))
                elif index == 3:
                    pm.catch(lambda : pm.select(name + '_jaw_lip_c_skin', r=1))
                elif index == 4:
                    pm.catch(lambda : pm.select(name + '_jaw_lip_l_0_skin', r=1))
                elif index == 5:
                    pm.catch(lambda : pm.select(name + '_jaw_lip_l_1_skin', r=1))
                elif index == 6:
                    pm.catch(lambda : pm.select(name + '_jaw_lip_r_0_skin', r=1))
                elif index == 7:
                    pm.catch(lambda : pm.select(name + '_jaw_lip_r_1_skin', r=1))
                elif index == 8:
                    pm.catch(lambda : pm.select(name + '_l_jaw_jnt_7_skin', name + '_jaw_lip_r_1_skin', name + '_jaw_lip_r_0_skin', name + '_jaw_lip_l_1_skin', name + '_jaw_lip_l_0_skin', name + '_jaw_lip_c_skin', name + '_downLip_jnt_*_skin', r=1))
                elif index == 9:
                    pm.catch(lambda : pm.select(name + '_l_cheek_jnt_2_skin', r=1))
                elif index == 10:
                    pm.catch(lambda : pm.select(name + '_l_cheek_jnt_3_skin', r=1))
                elif index == 11:
                    pm.catch(lambda : pm.select(name + '_l_cheek_jnt_4_skin', r=1))
                elif index == 12:
                    pm.catch(lambda : pm.select(name + '_l_cheek_jnt_1_skin', r=1))
                elif index == 13:
                    pm.catch(lambda : pm.select(name + '_nose_jnt_0_skin', r=1))
                elif index == 14:
                    pm.catch(lambda : pm.select(name + '_r_cheek_jnt_2_skin', r=1))
                elif index == 15:
                    pm.catch(lambda : pm.select(name + '_r_cheek_jnt_3_skin', r=1))
                elif index == 16:
                    pm.catch(lambda : pm.select(name + '_r_cheek_jnt_4_skin', r=1))
                elif index == 17:
                    pm.catch(lambda : pm.select(name + '_r_cheek_jnt_1_skin', r=1))
                elif index == 18:
                    pm.catch(lambda : pm.select(name + '_nose_jnt_0_skin', r=1))
                elif index == 19:
                    pm.catch(lambda : pm.select(name + '_nose_jnt_7_skin', r=1))
                elif index == 20:
                    pm.catch(lambda : pm.select(name + '_l_cheek_jnt_0_skin', r=1))
                elif index == 21:
                    pm.catch(lambda : pm.select(name + '_r_cheek_jnt_0_skin', r=1))
                elif index == 22:
                    pm.catch(lambda : pm.select(name + '_l_downEyeBorder_jnt_*_skin', r=1))
                elif index == 23:
                    pm.catch(lambda : pm.select(name + '_l_downEye_jnt_*_skin', r=1))
                elif index == 24:
                    pm.catch(lambda : pm.select(name + '_l_upEye_jnt_*_skin', r=1))
                elif index == 25:
                    pm.catch(lambda : pm.select(name + '_l_upEyeBorder_jnt_*_skin', r=1))
                elif index == 26:
                    pm.catch(lambda : pm.select(name + '_r_downEyeBorder_jnt_*_skin', r=1))
                elif index == 27:
                    pm.catch(lambda : pm.select(name + '_r_downEye_jnt_*_skin', r=1))
                elif index == 28:
                    pm.catch(lambda : pm.select(name + '_r_upEye_jnt_*_skin', r=1))
                elif index == 29:
                    pm.catch(lambda : pm.select(name + '_r_upEyeBorder_jnt_*_skin', r=1))
                elif index == 30:
                    pm.catch(lambda : pm.select(name + '_up_nose_jnt_0_skin', r=1))
                elif index == 31:
                    pm.catch(lambda : pm.select(name + '_l_brows_jnt_0_skin', r=1))
                elif index == 32:
                    pm.catch(lambda : pm.select(name + '_l_brows_jnt_1_skin', r=1))
                elif index == 33:
                    pm.catch(lambda : pm.select(name + '_l_brows_jnt_2_skin', r=1))
                elif index == 34:
                    pm.catch(lambda : pm.select(name + '_l_brows_jnt_3_skin', r=1))
                elif index == 35:
                    pm.catch(lambda : pm.select(name + '_c_brows_jnt_skin', r=1))
                elif index == 36:
                    pm.catch(lambda : pm.select(name + '_r_brows_jnt_0_skin', r=1))
                elif index == 37:
                    pm.catch(lambda : pm.select(name + '_r_brows_jnt_1_skin', r=1))
                elif index == 38:
                    pm.catch(lambda : pm.select(name + '_r_brows_jnt_2_skin', r=1))
                elif index == 39:
                    pm.catch(lambda : pm.select(name + '_r_brows_jnt_3_skin', r=1))
                elif index == 40:
                    pm.catch(lambda : pm.select(name + '_nose_jnt_down_skin', r=1))
                elif index == 41:
                    pm.catch(lambda : pm.select(name + '_l_cheek_jnt_5_skin', r=1))
                elif index == 42:
                    pm.catch(lambda : pm.select(name + '_r_cheek_jnt_5_skin', r=1))
                elif index == 43:
                    pm.catch(lambda : pm.select(name + '_downLip_jnt_*_skin', name + '_upLip_jnt_*_skin', r=1))
                elif index == 44:
                    pm.catch(lambda : pm.select(name + '_nose_jnt_*_skin', name + '_l_cheek_jnt_0_skin', name + '_r_cheek_jnt_0_skin', r=1))
                elif index == 45:
                    pm.catch(lambda : pm.select(name + '_l_downEye_jnt_*_skin', name + '_l_upEye_jnt_*_skin', name + '_l_upEyeBorder_jnt_*_skin', name + '_l_downEyeBorder_jnt_*_skin', r=1))
                elif index == 46:
                    pm.catch(lambda : pm.select(name + '_r_downEye_jnt_*_skin', name + '_r_upEye_jnt_*_skin', name + '_r_upEyeBorder_jnt_*_skin', name + '_r_downEyeBorder_jnt_*_skin', r=1))
                elif index == 47:
                    pm.catch(lambda : pm.select(name + '_l_brows_jnt_*_skin', r=1))
                elif index == 48:
                    pm.catch(lambda : pm.select(name + '_r_brows_jnt_*_skin', r=1))
                elif index == 49:
                    pm.catch(lambda : pm.select(name + '_up_teeth_jnt_skin', r=1))
                elif index == 50:
                    pm.catch(lambda : pm.select(name + '_down_teeth_jnt_skin', r=1))
                elif index == 51:
                    pm.catch(lambda : pm.select(name + '_upTongue_jnt_*_skin', r=1))
                elif index == 52:
                    pm.catch(lambda : pm.select(name + '_l_brows_jnt_4_skin', r=1))
                elif index == 53:
                    pm.catch(lambda : pm.select(name + '_r_brows_jnt_4_skin', r=1))
                infJooints = cmds.ls(sl=1)
                for objs in infJooints:
                    jntListSkin = '-tv ' + str(objs) + ' 0 '
                    pm.catch(lambda : pm.skinPercent(SkCluster, verListSkin, tv=(objs, 0)))

            pm.select(objects, r=1)

    def getSkinCluster(self, obj):
        """Get the skincluster of a given object
                Arguments:
                        obj (dagNode): The object to get skincluster
                Returns:
                        pyNode: The skin cluster pynode object
                """
        import pymel.all as pm
        skinCluster = None
        if isinstance(obj, basestring):
            obj = pm.PyNode(obj)
        try:
            if pm.nodeType(obj.getShape()) in ('mesh', 'nurbsSurface', 'nurbsCurve'):
                for shape in obj.getShapes():
                    try:
                        for skC in pm.listHistory(shape, type='skinCluster'):
                            try:
                                if skC.getGeometry()[0] == shape:
                                    skinCluster = skC
                            except Exception:
                                pass

                    except Exception:
                        pass

        except Exception:
            pm.displayWarning('%s: is not supported.' % obj.name())

        return skinCluster

    def skinCopy(self, sourceMesh=None, targetMesh=None, *args):
        if not sourceMesh or not targetMesh:
            if len(cmds.ls(sl=1)) >= 2:
                sourceMesh = pm.ls(sl=1)[0]
                targetMeshes = pm.ls(sl=1)[1:]
            else:
                pm.displayWarning('Please select target mesh/meshes and source mesh with skinCluster.')
                return
        else:
            targetMeshes = [
             targetMesh]
            if isinstance(sourceMesh, basestring):
                sourceMesh = pm.PyNode(sourceMesh)
            for targetMesh in targetMeshes:
                if isinstance(targetMesh, basestring):
                    sourceMesh = pm.PyNode(targetMesh)
                ss = self.getSkinCluster(sourceMesh)
                if ss:
                    oDef = pm.skinCluster(sourceMesh, query=True, influence=True)
                    skinCluster = pm.skinCluster(oDef, targetMesh, tsb=True, nw=1, n=targetMesh.name() + '_SkinCluster')
                    pm.copySkinWeights(ss=ss.stripNamespace(), ds=skinCluster.name(), noMirror=True, ia='oneToOne', sm=True, nr=True)
                else:
                    pm.displayError('Source Mesh :' + sourceMesh.name() + " Don't have skinCluster")

    def source_define(self):
        base = cmds.ls(sl=1)
        mel.eval('PolySelectConvert 3;')
        self.SourceDestinationSel('source')
        print(sourceVertexLs)
        cmds.select(base)

    def destination_define(self):
        base = cmds.ls(sl=1)
        mel.eval('PolySelectConvert 3;')
        self.SourceDestinationSel('destination')
        print(destinationVertexLs)
        cmds.select(base)

    def SourceDestinationSel(self, sdType):
        global destinationVertexLs
        global sourceVertexLs
        selectionList = pm.ls(sl=1, flatten=1)
        if selectionList:
            if pm.nodeType(selectionList[0]) == 'mesh':
                mel.eval('PolySelectConvert 3;')
                selectionList = pm.ls(sl=1, flatten=1)
                if sdType == 'destination':
                    destinationVertexLs = selectionList
                if sdType == 'source':
                    sourceVertexLs = selectionList

    def copySkinGlobal(self):
        global destinationVertexLs
        global sourceVertexLs
        base = cmds.ls(sl=1)
        self.copySkinMain()
        sourceVertexLs = []
        destinationVertexLs = []
        cmds.select(base)

    def hammerSkinGlobal(self):
        pm.mel.weightHammerVerts()

    def copySkinMain(self):
        self.settings_wdg.progress.setValue(0)
        sourceVer = sourceVertexLs
        destinationVer = destinationVertexLs
        i = 0.0
        if len(destinationVer) > 0:
            for x_dis in destinationVer:
                x_disPos = x_dis.getPosition()
                length = 20000
                closest_src = None
                for x_src in sourceVer:
                    newlength = (x_disPos - x_src.getPosition()).length()
                    if newlength < length:
                        length = newlength
                        closest_src = x_src

                if closest_src:
                    pm.select(closest_src)
                    mel.eval('artAttrSkinWeightCopy')
                    pm.select(x_dis)
                    mel.eval('artAttrSkinWeightPaste')
                    i += 10.0 / len(destinationVer)
                    self.skin_wdg.progress.setValue(i * 10)

        return

    def copyPivotF(self, source, dist):
        pivotTranslate = cmds.xform(dist, q=True, ws=True, rotatePivot=True)
        cmds.xform(source, ws=True, pivots=pivotTranslate)

    def connectBlendShape(self):
        objects = pm.ls(sl=1)
        objectTypeFace = pm.objectType(objects[0])
        if objectTypeFace != 'joint':
            objectShapeTypeFace = pm.objectType(objects[0].getShape())
            if objectShapeTypeFace == 'nurbsCurve':
                self.copyPivotF(str(objects[1]), str(objects[0]))
                pm.parentConstraint(objects[0], objects[1], n=objects[0] + '_Facial_pc', mo=1)
                pm.connectAttr(objects[0] + '.scale', objects[1] + '.scale')
        else:
            self.copyPivotF(str(objects[1]), str(objects[0]))
            pm.parentConstraint(objects[0], objects[1], n=objects[0] + '_Facial_pc', mo=1)
            pm.connectAttr(objects[0] + '.scale', objects[1] + '.scale')

    def connectBlendShapeB(self):
        objects = pm.ls(sl=1)
        if len(objects) == 2:
            nameRefObj = pm.selected()[0].namespace()
            objNoSpaceObj = objects[0].replace(nameRefObj, '')
            pm.blendShape(objects[0], objects[1], frontOfChain=1, tc=0, n=objects[0] + '_faceRig_bs')
            pm.setAttr(objects[0] + '_faceRig_bs.' + objNoSpaceObj, 1)
            print('// Result: BlendShape ->> {}').format(objects[0] + '_faceRig_bs')
        else:
            print('Please select source and target mesh to connect with BlendShape')

    def connectBlendShapeC(self):
        objects = pm.ls(sl=1)
        if len(objects) == 2:
            cmds.optionVar(fv=('exclusiveBind', 1), iv=[('autoWeightThreshold', 0), ('maxDistance', 0.01)])
            pm.select(objects[1], objects[0], r=1)
            cmds.CreateWrap(n=objects[0] + '_wrap', frontOfChain=1)
            print('// Result: Wrap deformer ')
        else:
            print('Please select source and target mesh to connect with BlendShape')

    def connectBlendShapeD(self):
        name = self.headGeo_wdg.nameField.text()
        chkPrefix = int(self.headGeo_wdg.chkPrefix.isChecked())
        if chkPrefix == 0:
            parentsDict = [
             [
              name + '_face_Ctrl_root', 'local']]
        else:
            parentsDict = [
             [
              'face_Ctrl_root', 'local']]
        objects = cmds.ls(sl=1)
        for obj in objects:
            parentsDict.append([obj, obj])

        if chkPrefix == 0:
            aimctl = pm.PyNode(name + '_eye_Target_ctrl')
            cns = name + '_eye_Target_ctrl_grp'
        else:
            aimctl = pm.PyNode('eye_Target_ctrl')
            cns = 'eye_Target_ctrl_grp'
        aimctl.addAttr('space', at='enum', en=(':').join([ it[1] for it in parentsDict ]), k=1)
        parCnst = pm.parentConstraint(mo=1, *([ it[0] for it in parentsDict ] + [cns]))
        i = 0
        for ctl, spcName in parentsDict:
            cnd = pm.createNode('condition')
            cnd.secondTerm.set(i)
            aimctl.space >> cnd.firstTerm
            cnd.colorIfTrueR.set(1)
            cnd.colorIfFalseR.set(0)
            cnd.outColorR >> parCnst.attr(ctl + 'W' + str(i))
            i += 1

    def detachSkinJntConnection(self):
        currentSel = cmds.ls(sl=1)
        cmds.select(hi=1)
        cmds.select(currentSel, d=1)
        skinJntList = cmds.ls(sl=1, type='joint')
        if len(skinJntList) > 0:
            for obj in skinJntList:
                try:
                    cmds.copyAttr(obj, obj + '_ghost', inConnections=True, values=True)
                except:
                    print('There is no ghost group for ' + obj)

        cmds.select(currentSel, r=1)

    def attachSkinJntConnection(self):
        currentSel = cmds.ls(sl=1)
        cmds.select(hi=1)
        cmds.select(currentSel, d=1)
        skinJntList = cmds.ls(sl=1, type='joint')
        if len(skinJntList) > 0:
            for obj in skinJntList:
                try:
                    cmds.copyAttr(obj + '_ghost', obj, inConnections=True, values=True)
                except:
                    print('There is no ghost group for ' + obj)

        cmds.select(currentSel, r=1)

    def SaveFacialSkinSet(self):
        global jntsFaceInf
        FirstObj = pm.selected()[0]
        orig = str(pm.selected()[0])
        jntsFaceInf = pm.skinCluster(orig, q=True, influence=True)
        if pm.objExists('setA_Perseus'):
            pm.select('setA_Perseus', r=1, ne=1)
            pm.mel.doDelete()
        pm.select(FirstObj, r=1)
        cmds.ConvertSelectionToVertices()
        createSetResult = cmds.sets(name='setA_Perseus')
        pm.select(FirstObj, r=1)

    def TransferFacialSkinSet(self):
        SecondObj = pm.selected()
        if pm.objExists('setB_Perseus'):
            pm.select('setB_Perseus', r=1, ne=1)
            pm.mel.doDelete()
        pm.select(SecondObj, r=1)
        cmds.ConvertSelectionToVertices()
        createSetResult = cmds.sets(name='setB_Perseus')
        vtx = pm.selected()[0]
        transforms = pm.listTransforms(vtx.node())
        pm.select(jntsFaceInf, transforms, r=1)
        pm.mel.skinClusterInfluence(1, '-ug -dr 4 -ps 0 -ns 10 -lw true -wt 0')
        pm.select('setA_Perseus', 'setB_Perseus', r=1)
        pm.copySkinWeights(surfaceAssociation='closestPoint', influenceAssociation='label', noMirror=1)
        if pm.objExists('setA_Perseus'):
            pm.select('setA_Perseus', r=1, ne=1)
            pm.mel.doDelete()
        if pm.objExists('setB_Perseus'):
            pm.select('setB_Perseus', r=1, ne=1)
            pm.mel.doDelete()
        pm.select(SecondObj, r=1)


def prExportSkin():
    newSel = pm.selected()
    if len(newSel) == 0:
        pm.displayWarning('Please Select Some Objects')
    else:
        prSkinExp()


def prSkinExp(packPath=None, objs=None, *args):
    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning('Please Select Some Objects')
            return
    packDic = {'objectsList': [], 'rootPath': []}
    startDir = pm.workspace(q=True, rootDirectory=True)
    packPath = pm.fileDialog2(dialogStyle=2, fileMode=0, startingDirectory=startDir, fileFilter='data list (*%s)' % PACK_EXT)
    if not packPath:
        return
    packPath = packPath[0]
    if not packPath.endswith(PACK_EXT):
        packPath += PACK_EXT
    packDic['Path'], packName = os.path.split(packPath)
    for obj in objs:
        fileName = obj.stripNamespace() + FILE_EXT
        filePath = os.path.join(packDic['Path'], fileName)
        if exportSkin(filePath, [obj]):
            packDic['objectsList'].append(fileName)
            pm.displayInfo(filePath)
        else:
            pm.displayWarning(obj.name() + ": Skipped because don't have Skin Cluster")

    if packDic['objectsList']:
        data_string = json.dumps(packDic, indent=4, sort_keys=True)
        f = open(packPath, 'w')
        f.write(data_string + '\n')
        f.close()
        pm.displayInfo('Skin Data exported: ' + packPath)
    else:
        pm.displayWarning('Any of the selected objects have Skin Cluster. Skin Pack export aborted.')


def exportSkin(filePath=None, objs=None, *args):
    if not objs:
        if pm.selected():
            objs = pm.selected()
        else:
            pm.displayWarning('Please Select One or more objects')
            return False
    packDic = {'objs': [], 'objDDic': [], 'bypassObj': []}
    if not filePath:
        startDir = pm.workspace(q=True, rootDirectory=True)
        filePath = pm.fileDialog2(dialogStyle=2, fileMode=0, startingDirectory=startDir, fileFilter='data data (*%s)' % FILE_EXT)
        filePath = filePath[0]
    if not filePath:
        return False
    if not filePath.endswith(FILE_EXT):
        filePath += FILE_EXT
    for obj in objs:
        skinCls = getSkinCluster(obj)
        if not skinCls:
            pm.displayWarning(obj.name() + ": Skipped because don't have Skin Cluster")
        else:
            listDic = {'weights': {}, 'blendWeights': [], 'skinClsName': '', 
               'objName': '', 
               'nameSpace': ''}
            listDic['objName'] = obj.name()
            listDic['nameSpace'] = obj.namespace()
            collectlist(skinCls, listDic)
            packDic['objs'].append(obj.name())
            packDic['objDDic'].append(listDic)
            pm.displayInfo('%s (%d influences, %d points) %s' % (
             skinCls.name(),
             len(listDic['weights'].keys()),
             len(listDic['blendWeights']),
             obj.name()))

    if packDic['objs']:
        fh = open(filePath, 'wb')
        pickle.dump(packDic, fh, pickle.HIGHEST_PROTOCOL)
        fh.close()
        return True


def getSkinCluster(obj):
    """Get the skincluster of a given object
        Arguments:
                obj (dagNode): The object to get skincluster
        Returns:
                pyNode: The skin cluster pynode object
        """
    skinCluster = None
    if isinstance(obj, basestring):
        obj = pm.PyNode(obj)
    try:
        if pm.nodeType(obj.getShape()) in ('mesh', 'nurbsSurface', 'nurbsCurve'):
            for shape in obj.getShapes():
                try:
                    for skC in pm.listHistory(shape, type='skinCluster'):
                        try:
                            if skC.getGeometry()[0] == shape:
                                skinCluster = skC
                        except Exception:
                            pass

                except Exception:
                    pass

    except Exception:
        pm.displayWarning('%s: is not supported.' % obj.name())

    return skinCluster


def prImpSkinAll(filePath=None, *args):
    import pymel.all as pm
    if not filePath:
        startDir = cmds.workspace(q=True, rootDirectory=True)
        filePath = cmds.fileDialog2(dialogStyle=2, fileMode=1, startingDirectory=startDir, fileFilter='data list (*%s)' % PACK_EXT)
    if not filePath:
        return
    if not isinstance(filePath, basestring):
        filePath = filePath[0]
    packDic = json.load(open(filePath))
    for pFile in packDic['objectsList']:
        filePath = os.path.join(os.path.split(filePath)[0], pFile)
        prImpSkin(filePath, True)


def prImpSkin(filePath=None, *args):
    if not filePath:
        startDir = pm.workspace(q=True, rootDirectory=True)
        filePath = pm.fileDialog2(dialogStyle=2, fileMode=1, startingDirectory=startDir, fileFilter='data data (*%s)' % FILE_EXT)
    if not filePath:
        return
    if not isinstance(filePath, basestring):
        filePath = filePath[0]
    fh = open(filePath, 'rb')
    listPack = pickle.load(fh)
    fh.close()
    for list in listPack['objDDic']:
        try:
            skinCluster = False
            objName = list['objName']
            objNode = pm.PyNode(objName)
            try:
                meshVertices = pm.polyEvaluate(objNode, vertex=True)
                importedVertices = len(list['blendWeights'])
                if meshVertices != importedVertices:
                    pm.displayWarning('Vertex counts do not match. %d != %d' % (
                     meshVertices, importedVertices))
                    continue
            except Exception:
                pass

            if getSkinCluster(objNode):
                skinCluster = getSkinCluster(objNode)
            else:
                try:
                    joints = list['weights'].keys()
                    skinCluster = pm.skinCluster(joints, objNode, tsb=True, nw=2, n=list['skinClsName'])
                except Exception:
                    notFound = list['weights'].keys()
                    sceneJoints = set([ pm.PyNode(x).name() for x in pm.ls(type='joint')
                                      ])
                    for j in notFound:
                        if j in sceneJoints:
                            notFound.remove(j)

                    pm.displayWarning('Object: ' + objName + " Skiped. Can't found corresponding deformer for the following joints: " + str(notFound))
                    continue

            if skinCluster:
                setlist(skinCluster, list)
                print('%s skin data loaded.' % objName)
        except Exception:
            pm.displayWarning('Object: ' + objName + ' Skiped. Can NOT be found in the scene')


def setlist(skinCls, listDic):
    import pymel.all as pm
    dagPath, components = getGeometryComponents(skinCls)
    setInfluenceWeights(skinCls, dagPath, components, listDic)
    setBlendWeights(skinCls, dagPath, components, listDic)
    for attr in ['skinningMethod', 'normalizeWeights']:
        cmds.setAttr('%s.%s' % (skinCls, attr), listDic[attr])


def getGeometryComponents(skinCls):
    import pymel.all as pm
    fnSet = OpenMaya.MFnSet(skinCls.__apimfn__().deformerSet())
    members = OpenMaya.MSelectionList()
    fnSet.getMembers(members, False)
    dagPath = OpenMaya.MDagPath()
    components = OpenMaya.MObject()
    members.getDagPath(0, dagPath, components)
    return (dagPath, components)


def setInfluenceWeights(skinCls, dagPath, components, listDic):
    import pymel.all as pm
    unusedImports = []
    weights = getCurrentWeights(skinCls, dagPath, components)
    influencePaths = OpenMaya.MDagPathArray()
    numInfluences = skinCls.__apimfn__().influenceObjects(influencePaths)
    numComponentsPerInfluence = weights.length() / numInfluences
    for importedInfluence, importedWeights in listDic['weights'].items():
        for ii in range(influencePaths.length()):
            influenceName = influencePaths[ii].partialPathName()
            nnspace = pm.PyNode(influenceName).stripNamespace()
            influenceWithoutNamespace = nnspace
            if influenceWithoutNamespace == importedInfluence:
                for jj in range(numComponentsPerInfluence):
                    weights.set(importedWeights[jj], jj * numInfluences + ii)

                break
        else:
            unusedImports.append(importedInfluence)

    influenceIndices = OpenMaya.MIntArray(numInfluences)
    for ii in range(numInfluences):
        influenceIndices.set(ii, ii)

    skinCls.__apimfn__().setWeights(dagPath, components, influenceIndices, weights, False)


def setBlendWeights(skinCls, dagPath, components, listDic):
    import pymel.all as pm
    blendWeights = OpenMaya.MDoubleArray(len(listDic['blendWeights']))
    for i, w in enumerate(listDic['blendWeights']):
        blendWeights.set(w, i)

    skinCls.__apimfn__().setBlendWeights(dagPath, components, blendWeights)


def collectlist(skinCls, listDic):
    import pymel.all as pm
    dagPath, components = getGeometryComponents(skinCls)
    collectInfluenceWeights(skinCls, dagPath, components, listDic)
    collectBlendWeights(skinCls, dagPath, components, listDic)
    for attr in ['skinningMethod', 'normalizeWeights']:
        listDic[attr] = cmds.getAttr('%s.%s' % (skinCls, attr))

    listDic['skinClsName'] = skinCls.name()


def collectInfluenceWeights(skinCls, dagPath, components, listDic):
    import pymel.all as pm
    weights = getCurrentWeights(skinCls, dagPath, components)
    influencePaths = OpenMaya.MDagPathArray()
    numInfluences = skinCls.__apimfn__().influenceObjects(influencePaths)
    numComponentsPerInfluence = weights.length() / numInfluences
    for ii in range(influencePaths.length()):
        influenceName = influencePaths[ii].partialPathName()
        influenceWithoutNamespace = pm.PyNode(influenceName).stripNamespace()
        inf_w = [ weights[(jj * numInfluences + ii)] for jj in range(numComponentsPerInfluence)
                ]
        listDic['weights'][influenceWithoutNamespace] = inf_w


def collectBlendWeights(skinCls, dagPath, components, listDic):
    import pymel.all as pm
    weights = OpenMaya.MDoubleArray()
    skinCls.__apimfn__().getBlendWeights(dagPath, components, weights)
    listDic['blendWeights'] = [ weights[i] for i in range(weights.length()) ]


def getCurrentWeights(skinCls, dagPath, components):
    import pymel.all as pm
    weights = OpenMaya.MDoubleArray()
    util = OpenMaya.MScriptUtil()
    util.createFromInt(0)
    pUInt = util.asUintPtr()
    skinCls.__apimfn__().getWeights(dagPath, components, weights, pUInt)
    return weights


def encode_data_to_attr(node, attr_name, data):
    """
        Dump data into a string attriubte
        Args:
                node (pm.nt.DagNode): node to get data 
                attr_name (str):  name of attribute
                data (python object): python data object
        """
    if not node.hasAttr(attr_name):
        node.addAttr(attr_name, dataType='string')
    pickled_data = pickle.dumps(data)
    node.attr(attr_name).unlock()
    node.attr(attr_name).set(pickled_data)
    node.attr(attr_name).lock()


def decode_data_from_attr(node, attr_name):
    """
        Return data from string attriute
        Args:
                node (pm.nt.DagNode): node to get data 
                attr_name (str):  name of attribute
        Returns:
                list or dict
        """
    if not node.hasAttr(attr_name):
        raise pm.MayaAttributeError(('Attribute does not exist:{}').format(attr_name))
    data = str(node.attr(attr_name).get())
    return pickle.loads(data)


def detach_bind_joints():
    """
        Detach bind joints from rig.
        Adds a custom compound attribute (connected_nodes) to what the node was connected to
        """
    SKIN_JNT_GRP = '*facialRig_skinJnt_grp'
    if not pm.objExists(SKIN_JNT_GRP):
        raise pm.MayaObjectError(('Missing node: {}').format(SKIN_JNT_GRP))
    pm.select(SKIN_JNT_GRP, replace=True)
    bind_joints = pm.selected()
    for joint in bind_joints:
        connected_plugs = joint.inputs(plugs=True, connections=True)
        ordered_plugs = []
        for i, (source, destination) in enumerate(connected_plugs):
            if i == 0:
                ordered_plugs.append((source, destination))
            else:
                ordered_plugs.append((destination, source))

        connection_data = []
        for incoming_plug, outgoing_plug in connected_plugs:
            incoming_node = incoming_plug.node()
            incoming_attr = incoming_plug.longName()
            outgoing_node = outgoing_plug.node()
            outgoing_attr = outgoing_plug.longName()
            incoming_uuid = cmds.ls(incoming_node.name(), uuid=True)[0]
            outgoing_uuid = cmds.ls(outgoing_node.name(), uuid=True)[0]
            outgoing_node_attr = (outgoing_uuid, outgoing_attr)
            incoming_node_attr = (incoming_uuid, incoming_attr)
            connection_data.append((incoming_node_attr, outgoing_node_attr))
            outgoing_plug.disconnect(incoming_plug)

        encode_data_to_attr(joint, 'connection_data', connection_data)

    logging.info('Bind joints detached!')


def attach_bind_joints():
    """ Attach bind joints to rig nodes """
    connection_attr_name = 'connection_data'
    all_joints = pm.ls(type=pm.nt.Joint)
    bind_joints = [ joint for joint in all_joints if joint.hasAttr(connection_attr_name) ]
    if not bind_joints:
        raise RuntimeError('No joints found to re-attach rig! Detach bind joints first!')
    for joint in bind_joints:
        connection_data = decode_data_from_attr(joint, connection_attr_name)
        for incoming_data, outgoing_data in connection_data:
            incoming_node = pm.ls(incoming_data[0])[0]
            incoming_attr = incoming_data[1]
            incoming_node_attr = incoming_node.attr(incoming_attr)
            outgoing_node = pm.ls(outgoing_data[0])[0]
            outgoing_attr = outgoing_data[1]
            destination_node_attr = outgoing_node.attr(outgoing_attr)
            if not destination_node_attr.isConnectedTo(incoming_node_attr):
                destination_node_attr.connect(incoming_node_attr)

        if joint.hasAttr(connection_attr_name):
            joint.attr(connection_attr_name).unlock()
            joint.deleteAttr(connection_attr_name)

    logging.info('Bind joints attached!')


def rename_transforms_by_position(transforms, search_name, center_tolerance=0.2, left_prefix='left', right_prefix='right', center_prefix='center', suffix=''):
    """
        Given a list of pm.nt.Transforms and a search name, rename objects based on the 
        X axis world position in order starting from lowest(0) to highest position(nth)
        The center tolerance is used to test if an object is close enough to the center origin
        to be named 'center'
        Args:
                transforms (list of pm.nt.Transforms): list of transforms to search and rename 
                search_name (str): name to parse for and use and the main object name 
                center_tolerance (float): amount to use for determining how close the object is to the origin in X world space
                left_prefix (str): left prefix name for the object
                right_prefix (str): right prefix name for the object
                center_prefix (str): center prefix name for the object
                suffix (str): optional suffix name
        
        Usage:
        all_joints = pm.ls(type=pm.nt.Joint)
        search_for = 'downLip'
        renamed_joints = rename_transforms_by_position(all_joints, search_for, suffix='joint') 
        Returns:
                list of renamed pm.nt.Transforms
        """
    transform_list = [ transform for transform in transforms if search_name in transform.name() ]
    position_dict = {}
    for transform in transform_list:
        pos = transform.getTranslation(space='world')
        position_dict[transform] = pos

    sorted_array = sorted(position_dict.items(), key=lambda i: i[1][0], reverse=True)
    left_array = []
    center_array = []
    right_array = []
    for transform, pos in sorted_array:
        if pos[0] <= 0.0:
            if abs(pos[0]) <= center_tolerance:
                center_array.append((transform, pos))
            else:
                right_array.append((transform, pos))
        if pos[0] >= 0.0:
            if abs(pos[0]) <= center_tolerance:
                center_array.append((transform, pos))
            else:
                left_array.append((transform, pos))

    renamed_transforms = []
    for i, (transform, position) in enumerate(reversed(left_array)):
        if suffix:
            transform.rename(('{}_{}_{}_{}').format(left_prefix, search_name, i, suffix))
        else:
            transform.rename(('{}_{}_{}').format(left_prefix, search_name, i))
        renamed_transforms.append(transform)

    for i, (transform, position) in enumerate(right_array):
        if suffix:
            transform.rename(('{}_{}_{}_{}').format(right_prefix, search_name, i, suffix))
        else:
            transform.rename(('{}_{}_{}').format(right_prefix, search_name, i))
        renamed_transforms.append(transform)

    for i, (transform, position) in enumerate(center_array):
        if suffix:
            transform.rename(('{}_{}_{}_{}').format(center_prefix, search_name, i, suffix))
        else:
            transform.rename(('{}_{}_{}').format(center_prefix, search_name, i))
        renamed_transforms.append(transform)

    return renamed_transforms