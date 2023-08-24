import maya.cmds
import maya.mel
from functools import partial
import re

def UI():
    if maya.cmds.window("makeCenterLine", ex=True):
        maya.cmds.deleteUI("makeCenterLine")
    window = maya.cmds.window("makeCenterLine", t="Make Center Line", w=300, h=50)
    form = maya.cmds.formLayout("formA", parent=window)
    chkA = maya.cmds.checkBox("curve",  l="curve", v=True, p=form)
    chkB = maya.cmds.checkBox("joints",  l="joints", v=False, p=form)
    execute = maya.cmds.button("OK", l="OK", p=form, w=50)
    help = maya.cmds.button("help", l="help", p=form, w=50)
    maya.cmds.showWindow(window)
    maya.cmds.formLayout(form, edit=True, af=[(chkA, "top", 5),
                                            (chkA, "left", 5),
                                            (chkB, "top", 5),
                                            (help, "bottom", 5),
                                            (execute, "bottom", 5),
                                            (execute, "right", 5)],
                                        ac=[(chkB, "left", 5, chkA),(help, "right", 5, execute)])

    maya.cmds.button(execute, e=True, c=partial(uiRun, chkA, chkB))
    maya.cmds.button(help, e=True, c=partial(mclHelp))

def uiRun(chkA, chkB, *ignore):
    c = maya.cmds.checkBox(chkA, q=True, v=True)
    j = maya.cmds.checkBox(chkB, q=True, v=True)
    run(c=c, j=j)

def mclHelp(*ignore):
    maya.cmds.confirmDialog(t="Help", m="If you select one edge and hit OK,\
it will generate a curve down the cente of the object using all edge loops. \n Select two edges,\
and it will generate a curve BETWEEN those two edge loops. \n Select three or more edges, and it \
will generate a curve only using those selected edge loops (Good for heavy, redundant geo")


def run(c=1, j=1):
    #track selection order must be ON for this to work
    points = 'curve -d 3 '
    sel = maya.cmds.ls(os=True, fl = True)
    ob = maya.cmds.ls(o=True, sl=True)
    num = []
    out = []
    edges = []
    joints = []
    for one in sel:
        strip = re.search(r"\[([0-9]+)\]", one)
        num.append(strip.group(1))
    edgeCount = len(num)
    if (edgeCount is not 0):
        if edgeCount == 1:
            edges = maya.cmds.polySelect(edgeRing=(int(num[0])), ns=True) or []
        elif edgeCount == 2:
            edges = maya.cmds.polySelect(edgeRingPath=(int(num[0]), int(num[1])), ns=True)
            if edges is None:
                print("You must select two edges in the same edge ring for that.")
                return False
        elif edgeCount > 2:
            edges = num

        for one in edges:
            maya.cmds.select(ob)
            maya.cmds.polySelect(elb=int(one))
            clust = maya.cmds.cluster(n = 'poo#')
            maya.cmds.select(clear=True)
            posi = maya.cmds.getAttr(clust[0]+'HandleShape.origin')
            if c:
                points = points + ('-p %s %s %s ' %(posi[0][0], posi[0][1], posi[0][2]))
            if j:
                joints.append(maya.cmds.joint(p = (posi[0][0], posi[0][1], posi[0][2])))
            maya.cmds.delete (clust[0])
        if c:
            out.append(maya.mel.eval(points))
        if j:
            for i in reversed(range(1, len(edges))):
                maya.cmds.parent(joints[i], joints[i-1])
            maya.cmds.joint(joints[0], e=True, oj = 'xyz', sao= 'zup', ch=True, zso=True)
            maya.cmds.joint(joints[-1],e=True, o =(0,0,0))
            out.append(joints[0])
        maya.cmds.select(out)
    else:
        print("Nothing is selected")




