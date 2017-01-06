import maya.cmds as cmds

## Var ##
pointsNumber = 5

curve = cmds.ls(sl=True)
#nameBuilder_locator = curve[0] + "_loc"  #in function, lacal variables
#nameBuilder_joint = curve[0] + "_jnt"  #in function, local variables

spacing = 1.0/(pointsNumber-1)

## Main --wip

def deleteConnection(plug):
    #""" Equivalent of MEL: CBdeleteConnection """
    
	if cmds.connectionInfo(plug, isDestination=True):
		plug = cmds.connectionInfo(plug, getExactDestination=True)
		readOnly = cmds.ls(plug, ro=True)
		#delete -icn doesn't work if destination attr is readOnly 
		if readOnly:
			source = cmds.connectionInfo(plug, sourceFromDestination=True)
			cmds.disconnectAttr(source, plug)
		else:
			cmds.delete(plug, icn=True)

        
def pathMode(path,follow=False,sphereSize=0.1,offsetActive=False,locSize=0.1,jointRadius=0.1):
    nameBuilder_locator = path + "_loc"
    nameBuilder_offset = path + "_offset_jnt"
    nameBuilder_joint = path + "_jnt_ctrl"
    locatorList = []
    for p in range(0,pointsNumber):
        # place locator
        locator = cmds.spaceLocator(n=nameBuilder_locator+str(p+1))
        cmds.setAttr(locator[0]+'.localScaleX',locSize)
        cmds.setAttr(locator[0]+'.localScaleY',locSize)
        cmds.setAttr(locator[0]+'.localScaleZ',locSize)
        motionPath = cmds.pathAnimation( locator[0], c=path, f=follow)
        deleteConnection(motionPath+'.u')
        cmds.setAttr(motionPath+'.uValue', spacing*p)
        locatorList.append(locator[0])
        # place joint
        #- crea joint con il nome
        #- imparentalo al locator e freza le trasfmormazioni
        if offsetActive:
            jointOffset = cmds.joint(n=nameBuilder_offset, r=jointRadius)
            cmds.setAttr(jointOffset+'.radius', jointRadius)
        #- altro joint (con nome) imparentato al primo sempre freezato (o duplica il primo)
        joint = cmds.joint(n=nameBuilder_joint, r=jointRadius)
        cmds.setAttr(joint+'.radius', jointRadius)
        #- crea sfera e imparenta il nodo di shape al secondo joint
        sphereObj = cmds.sphere(r=sphereSize,axis=(0,1,0))#color based on L/R
        sphereShape = cmds.listRelatives(sphereObj, children=True, shapes=True)
        cmds.parent(sphereShape,joint,r=True,s=True)
        cmds.delete(sphereObj)
    return locatorList


locList = []
for cv in curve:
    #print cv
    locList.extend(pathMode(cv))
cmds.group(locList, n='locator_grp')

## --ToDo

# gui
# object oriented
# multithreading --probabilmente si puo evitare

# docstring not working. why?