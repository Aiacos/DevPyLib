__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import rigLib
#from qtshim import QtGui, QtCore, Signal


def createPV(ikHandle_selection=pm.ls(sl=True)):
    '''
    Create a Locator in a correct plane to usa as Pole Vector
    :param ikHandle_selection: select an ikHandle
    :return: grupped locator
    '''
    ## Put all three joints in a variable based on a selected ikHandle

    # string $ikHandleSel[] = (`ls -sl`);
    # ikHandle_selection = pm.ls(sl=True)
    ikHandle_name = ikHandle_selection
    # string $selJoints[] = `ikHandle -q -jointList $ikHandleSel`;
    selJoints = ikHandle_selection.getJointList()
    # select $selJoints;
    pm.select(selJoints[-1])
    # pickWalk -d down;
    pm.pickWalk(d='down')
    # string $newJoints[] = `ls -sl`;
    newJoints = pm.ls(sl=True)
    # appendStringArray ($newJoints, $selJoints, 1);
    selJoints.append(newJoints[0])

    ## Create a locator and group it twice

    # spaceLocator -name ("poleVector"+"_#");
    poleVector_locator = pm.spaceLocator(n=ikHandle_name + '_pv' + '_loc')
    # string $locatorItself1[] = `ls -sl`;
    pm.select(poleVector_locator)
    # group -w -name ($locatorItself1[0]+"_grp");
    # group -w -name ($locatorItself1[0]+"_off");
    ## Cast the vector group into a variable
    # string $vectorGroup111 = ($locatorItself1[0]+"_off");
    poleVector_group = pm.group(n=ikHandle_name + '_pv' + '_loc' + '_grp')

    ## Point constrain it between the three joints

    # pointConstraint -name "myVerySpecialPointConstraint" $newJoints $vectorGroup111;
    pointConstraint = pm.pointConstraint(selJoints, poleVector_group)

    ## Delete the point constraint

    # delete "myVerySpecialPointConstraint";
    pm.delete(pointConstraint)

    ## Create an aim constraint for the locator to aim at the middle joint

    # aimConstraint -name "myVerySpecialAimConstraint" $newJoints[0] $vectorGroup111;
    aimConstraint = pm.aimConstraint(selJoints[1], poleVector_group)

    ## Delete the aim constraint

    # delete "myVerySpecialAimConstraint";
    pm.delete(aimConstraint)

    ##Snap grupLocator to middle joint
    # snap = pm.pointConstraint( selJoints[1], poleVector_group, skip=('y','z'))

    return poleVector_group

def getJointDistance(ikHandle_selection=pm.ls(sl=True)):
    '''
    Return the lenght of ikHandle
    :param ikHandle_selection: select an ikHandle
    :return: Return the lenght og ikHandle
    '''
    ## Put all three joints in a variable based on a selected ikHandle
    selJoints = ikHandle_selection.getJointList()
    pm.select(selJoints[-1])
    pm.pickWalk(d='down')
    newJoints = pm.ls(sl=True)
    selJoints.append(newJoints[0])
    loc0 = pm.spaceLocator()
    loc1 = pm.spaceLocator()
    constraint0 = pm.pointConstraint(selJoints[0],loc0)
    constraint1 = pm.pointConstraint(selJoints[2],loc1)
    def ctr_dist( objA, objB ):
        Ax, Ay, Az = objA.getTranslation(space="world")
        Bx, By, Bz = objB.getTranslation(space="world")
        return (  (Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2  )**0.5

    distance = ctr_dist(loc0, loc1)
    #distance = pm.distanceDimension(loc0, loc1)
    pm.delete(constraint0, constraint1, loc0, loc1)
    return distance

def connect_poleVector(ikHandle):
    # string $testObject[] = `ls -sl`;
    # if (`objectType $testObject[0]` != "ikHandle")
    # confirmDialog -title "Seriously?" -message "This is not an IK Handle!" -button "Sorry, I'm Kinda High";

    if ikHandle:
        if ikHandle.type() != 'ikHandle':
            print "Seriously? This is not an IK Handle!"
            return 'no ikHandle Exit'
    else:
        return "Nothing selected!"



    poleVector_locator_grp = createPV(ikHandle)

    ## Calculate ikHandle lenght to set as pv -X axis
    distance = int(getJointDistance(ikHandle)/2)
    ## Move the Locator Group in the -X axis (Object Space)
    pm.move(distance, 0, 0, poleVector_locator_grp, objectSpace=True, relative=True)

    ## Connect PoleVector
    pm.select(poleVector_locator_grp)
    poleVector_loc = pm.pickWalk(d='down')
    pm.poleVectorConstraint(poleVector_loc, ikHandle)

    return 'PoleVector ' + poleVector_loc[0] + ' successfully created!'

def main_poleVector():
    selectedObj = pm.ls(sl=True)
    for ikHandle in selectedObj:
        print connect_poleVector(ikHandle)

if __name__ == "__main__":
    main_poleVector()
    rigLib.base.colorControl.color_control(controls=pm.ls('*_pv*'))
## instance a GUI
#app = QtGui.QApplication.instance()
#poleVector_form = qtMainWindow_poleVector()
#poleVector_form.show()
#app.exec_()
