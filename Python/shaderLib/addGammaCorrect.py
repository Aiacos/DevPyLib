import pymel.core as pmc
import maya.cmds as cmds

def gammaNode():
    gamma = cmds.shadingNode("gammaCorrect", asUtility=True)
    cmds.setAttr(gamma+'.gammaX', 0.454)
    cmds.setAttr(gamma+'.gammaY', 0.454)
    cmds.setAttr(gamma+'.gammaZ', 0.454)
    return gamma

def gammaNodePM():
    gamma = pmc.shadingNode("gammaCorrect", asUtility=True)
    gamma.gammaX.set(0.454)
    gamma.gammaY.set(0.454)
    gamma.gammaZ.set(0.454)
    return gamma

def connectGammaPM(selection):##toDo in pymel
    print selection.outputs(c=1)
    #find source and destination
    #source, destination = selection.connections(c=True, p=True)
    #create gamma node
    #gamma = gammaNodePM()
    #for source, destination in selection.connections(c=1, p=1):
    #print source, destination

def connectGamma(selection):
    #find where is connected
    connection = cmds.listConnections('%s.outColor' %selection, p=True, d=True)
    #create gamma node
    gamma = gammaNode()
    #connect selected file node to gamma node
    cmds.connectAttr('%s.outColor' %selection, '%s.value' %gamma)
    #disconnect file node from shader
    cmds.disconnectAttr('%s.outColor' %selection, connection[0])
    #connect gamma node to shader
    cmds.connectAttr('%s.value' %gamma, connection[0])

def addGammaCorrect():
    #selct file node to gamma correct
    selection = pmc.ls(sl=True)
    for node in selection:
        #connectGamma(node)
        connectGammaPM(node)

addGammaCorrect()