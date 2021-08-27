import pymel.core as pm


def ak_rope():
    """:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::://
      Script:     ak_rope                                                                         //
      Version:    12.0                                                                            //
      Date:       21.05.2013                                                                      //
      Author:     Andrey Kanin                                                                    //
    :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::://"""

    win = "ROPE"
    if pm.window(win, exists=1):
        pm.deleteUI(win)

    pm.window(win, h=100, mb=1, t="ak       ROPE", w=100, tlb=1)
    pm.columnLayout(w=101)
    pm.rowLayout(nc=2)
    pm.button(h=15, c=lambda *args: pm.mel.rp_curve(), bgc=(0.3, 0.3, 0.3), l="curve", w=48)
    pm.button(h=15, c=lambda *args: pm.mel.rp_bezier(), bgc=(0.3, 0.3, 0.3), l="bezier", w=48)
    pm.setParent('..')
    pm.separator(h=5, w=100, st="in")
    pm.rowLayout(nc=4, cw4=(5, 15, 50, 15))
    pm.text(" ")
    pm.checkBoxGrp('CTJ', cc=lambda *args: pm.mel.eval(
        "if(`checkBoxGrp -q -v1 CTJ`){checkBoxGrp -e -vis 1 CTJP;}else{checkBoxGrp -e -vis 0 CTJP;}"),
                   v1=1, ncb=1,
                   ann="add circle contollers CT",
                   w=15)
    pm.text("   add CT")
    pm.checkBoxGrp('CTJP', cc=lambda *args: pm.mel.eval(
        "if(`checkBoxGrp -q -v1 CTJP`){text -e -en 0 TXTCT;}else{text -e -en 1 TXTCT;}"),
                   v1=0, ncb=1, ann="add bezier CT contollers", w=15)
    pm.setParent('..')
    pm.separator(h=5, w=100, st="in")
    pm.button(c=lambda *args: pm.mel.rp_cr(), bgc=(0.8, 0.8, 0.1), h=20, ann="riging curve", l="riging curve", w=99)
    pm.separator(h=5, w=100, st="in")
    pm.rowLayout(nc=4, cw4=(5, 15, 50, 15))
    pm.text(" ")
    pm.checkBoxGrp('MRL', cc=lambda *args: pm.mel.eval("if(`checkBoxGrp -q -v1 MRL`){checkBoxGrp -e -v1 0 VRL;}"),
                   v1=1, ncb=1,
                   ann="nodes sistem",
                   w=15)
    pm.button(c=lambda *args: [pm.mel.rp_mixTwist(), pm.mel.rp_Twist()], bgc=(0.3, 0.3, 0.3), h=20, ann="resistems",
              l="twist", w=50)
    pm.checkBoxGrp('VRL', cc=lambda *args: pm.mel.eval("if(`checkBoxGrp -q -v1 VRL`){checkBoxGrp -e -v1 0 MRL;}"),
                   v1=0, ncb=1,
                   ann="vectors sistem",
                   w=15)
    pm.setParent('..')
    pm.separator(h=5, w=100, st="in")
    pm.rowLayout(nc=2, cw2=(60, 30))
    pm.text('TXTCT', l="   controls")
    pm.intField('NCJ', bgc=(0.15, 0.15, 0.15), min=2, max=100, ann="how many contols", w=37, v=3)
    pm.setParent('..')
    pm.rowLayout(nc=2, cw2=(60, 30))
    pm.text("   segment")
    pm.intField('PCJ', bgc=(0.15, 0.15, 0.15), min=1, max=100, ann="how many segments", w=37, v=5)
    pm.setParent('..')
    pm.rowLayout(nc=2, cw2=(60, 30))
    pm.text("   ==>")
    pm.intField('NJ', bgc=(0.3, 0.3, 0.3), min=1, max=100, ann="total segments", w=37, v=10)
    pm.setParent('..')
    pm.separator(h=5, w=100, st="in")
    pm.rowLayout(nc=2, cw2=(60, 30))
    pm.text("   orient")
    pm.intField('OJ', bgc=(0.2, 0.2, 0.2), min=0, max=360, ann="orient ik sistem", w=37, v=0)
    pm.setParent('..')
    pm.separator(h=5, w=100, st="in")
    pm.rowLayout(nc=2)
    pm.button(c=lambda *args: pm.mel.rp_surface(), bgc=(0.0, 0.6, 0.4), h=20, ann="convert to surface", l="surface",
              w=60)
    pm.optionMenuGrp('AXES', bgc=(0.2, 0.2, 0.2), w=36)
    pm.menuItem(l="y")
    pm.menuItem(l="x")
    pm.menuItem(l="z")
    pm.setParent('..')
    pm.separator(h=5, w=100, st="in")
    pm.rowLayout(nc=2)
    pm.button(h=20, c=lambda *args: pm.mel.rp_grip(), bgc=(0.2, 0.2, 0.2), l="grip", w=60)
    pm.button(h=20, c=lambda *args: pm.mel.rp_del(), bgc=(0.2, 0.2, 0.2), l="del", w=36)
    pm.setParent('..')
    pm.setParent('..')
    pm.showWindow(win)


def rp_curve():
    """..............................................................................................//"""

    s = pm.ls(sl=1)
    if len(s) == 0:
        pm.EPCurveTool()


    else:
        pm.mel.rp_convert_curve(s)


def rp_bezier():
    s = pm.ls(sl=1)
    if len(s) == 0:
        pm.CreateBezierCurveTool()


    else:
        pm.mel.rp_convert_curve(s)


def rp_convert_curve(s):
    ss = pm.listRelatives(s[0], s=1)
    tss = str(pm.objectType(ss[0]))
    if pm.mel.gmatch(tss, "nurbsCurve"):
        pm.nurbsCurveToBezier()

    if pm.mel.gmatch(tss, "bezierCurve"):
        pm.bezierCurveToNurbs()


def rp_check(s):
    """..............................................................................................//"""

    if pm.mel.gmatch(s[0], "*CT*"):
        pm.pm.mel.error(" :( > this is not a rope curve")

    if len(s) == 0:
        pm.pm.mel.error(" :( > nothing is selected")

    ss = pm.listRelatives(s[0], s=1)
    # > selection shape
    if len(ss) == 0:
        pm.pm.mel.error(" :( > this is not a curve")

    tss = str(pm.objectType(ss[0]))
    # > type selection shape
    typ = 0
    if pm.mel.gmatch(tss, "nurbsCurve") or pm.mel.gmatch(tss, "bezierCurve"):
        typ = 1

    if typ == 0:
        pm.pm.mel.error(" :( > this is not a curve")


def rp_del():
    """..............................................................................................//"""

    s = pm.ls(sl=1)
    rp_check(s)
    if pm.objExists(s[0] + "_rig"):
        pm.parent(s[0], w=1)
        pm.delete(s[0] + "_rig")


def rp_info(s):
    """..............................................................................................//"""

    if pm.objExists(s[0] + "_info"):
        pm.delete(s[0] + "_info")

    ss = pm.listRelatives(s[0], s=1)
    is_ = str(pm.createNode('curveInfo', n=(s[0] + "_info")))
    pm.connectAttr((ss[0] + ".ws[0]"), (is_ + ".ic"),
                   f=1)
    return is_


def rp_create_control(s, i):
    """..............................................................................................//"""

    ct = []
    cct = pm.circle(ch=0, nr=(1, 0, 0), r=1, d=3, n=(s[0] + "_" + str((i + 1)) + "_CT"))
    ct[0] = cct[0]
    print(ct)
    ct[1] = str(pm.group(ct[0], n=("ctGrp_" + s[0] + "_" + str((i + 1)))))
    pm.setAttr((ct[0] + "Shape.ove"),
               1)
    pm.setAttr((ct[0] + "Shape.ovc"),
               17)
    pm.setAttr((ct[0] + ".sx"),
               k=0, l=1)
    pm.setAttr((ct[0] + ".sy"),
               k=0, l=1)
    pm.setAttr((ct[0] + ".sz"),
               k=0, l=1)
    pm.setAttr((ct[0] + ".v"),
               k=0)
    pm.setAttr((ct[0] + ".ro"),
               3)
    pm.addAttr(ct[0], ln="bezier", k=1, at="bool")
    pm.setAttr((ct[0] + ".bezier"),
               cb=1, k=0)
    pm.setAttr((ct[0] + ".bezier"),
               1)
    pm.addAttr(ct[0], ln="change", dv=1, k=1, at="double", min=0)
    return ct


def rp_cr():
    """..............................................................................................//"""

    ncj = int(pm.intField('NCJ', q=1, v=1))
    # > input data
    # > control joints
    pcj = int(pm.intField('PCJ', q=1, v=1))
    # > pow control joints
    nj = ((ncj * pcj) - (pcj - 1))
    # > joints
    pm.intField('NJ', e=1, v=(nj - 1))
    oj = int(pm.intField('OJ', q=1, v=1))
    # > orient joint
    # > selection list
    s = pm.ls(sl=1)
    rp_check(s)
    ss = pm.listRelatives(s[0], s=1)
    # > selection shape
    tss = str(pm.objectType(ss[0]))
    # > type selection shape
    typ = 0
    if pm.mel.gmatch(tss, "nurbsCurve"):
        typ = 0

    if pm.mel.gmatch(tss, "bezierCurve"):
        typ = 1

    rp_del()
    pm.delete(s[0], ch=1)
    if typ == 0:
        pm.rebuildCurve(s[0], s=(nj - 1), kt=1, d=3, kep=1)

    pm.setAttr((s[0] + ".it"),
               0)
    # > curve info
    is_ = str(rp_info(s))
    iv = float(pm.getAttr(is_ + ".al"))
    # > group folders
    rg = str(pm.group(em=1, n=(s[0] + "_rig")))
    sg = str(pm.group(em=1, n=(s[0] + "_sistem")))
    # > twist joint
    sj = []
    ds = str(pm.curve(p=[(0, 0, 0), (iv, 0, 0)], k=[0, 1], d=1, n=(s[0] + "_tw")))
    pm.rebuildCurve(ds, s=(nj - 1), ch=0, d=1, kep=1)
    if nj == 3:
        pm.delete(ds + ".cv[1]")
        pm.delete(ds + ".cv[2]")

    for i in range(0, nj):
        t = (pm.xform((ds + ".cv[" + str(i) + "]"),
                            q=1, ws=1, t=1))
        sj[i] = str(pm.joint(p=((t.x), (t.y), (t.z)), rad=1, n=(s[0] + "_tw_" + str((i + 1)))))
        pm.setAttr((sj[i] + ".ro"),
                   3)

    pm.pm.cmds.rotate(oj, 0, 0, sj[0], r=1, os=1)
    pm.makeIdentity(sj[0], a=1, r=1)
    h = pm.ikHandle(c=s[0], ee=sj[nj], ccv=0,
                    sol="ikSplineSolver", n=(s[0] + "_tw_hl"),
                    sj=sj[0])
    pm.parent(sj[0], h[0], sg)
    pm.delete(ds)
    # > control joint
    pm.select(s[0], r=1)
    pm.mel.selectCurveCV("all")
    cv = pm.ls(fl=1, sl=1)
    p = (((len(cv)) + 2) / 3)
    pm.select(cl=1)
    cj = []
    if pm.checkBoxGrp('CTJP', q=1, v1=1):
        pm.setAttr((s[0] + ".it"),
                   1)
        # > create joints
        for i in range(0, (len(cv))):
            t = (pm.xform(cv[i], q=1, ws=1, t=1))
            pm.select(cl=1)
            cj[i] = str(pm.joint(p=((t.x), (t.y), (t.z)), rad=2, n=(s[0] + "_ctj_" + str((i + 1)))))
            pm.setAttr((cj[i] + ".ro"),
                       3)

        # > aim joints
        for i in range(0, ((len(cv)) - 1)):
            pm.aimConstraint(cj[i], cj[i + 1], w=1, o=(0, 180, 0))

        pm.aimConstraint(cj[1], cj[0], w=1, o=(0, 0, 0))
        pm.delete(cj, cn=1)
        pm.makeIdentity(cj, a=1, r=1)
        # > correct aim joints
        for i in range(0, (p - 1)):
            pm.aimConstraint(cj[i + (2 * i)], cj[i + 1 + (2 * i)], w=1, o=(0, 0, 0))

        for i in range(1, (p - 0)):
            pm.aimConstraint(cj[i + (2 * i)], cj[i - 1 + (2 * i)], w=1, o=(0, 0, 0))

        pm.delete(cj, cn=1)
        pm.makeIdentity(cj, a=1, r=1)


    else:
        for i in range(0, ncj):
            t = (pm.xform(sj[(i * pcj)], q=1, ws=1, t=1))
            pm.select(cl=1)
            cj[i] = str(pm.joint(p=((t.x), (t.y), (t.z)), rad=2, n=(s[0] + "_ctj_" + str((i + 1)))))
            pm.setAttr((cj[i] + ".ro"),
                       3)
            pm.parentConstraint(sj[(i * pcj)], cj[i], w=1)
            pm.delete(cj[i], cn=1)
            pm.makeIdentity(cj[i], a=1, r=1)

    pm.parent(cj, sg)
    pm.parent(sg, s[0], rg)
    # > connect scale
    sw = str(pm.createNode('multiplyDivide', n=(s[0] + "_s")))
    pm.setAttr((sw + ".op"),
               2)
    pm.connectAttr((is_ + ".al"), (sw + ".i1x"),
                   f=1)
    pm.connectAttr((rg + ".sx"), (sw + ".i2x"),
                   f=1)
    sx = str(pm.createNode('multiplyDivide', n=(s[0] + "_sx")))
    pm.setAttr((sx + ".op"),
               2)
    pm.connectAttr((sw + ".ox"), (sx + ".i1x"),
                   f=1)
    pm.setAttr((sx + ".i2x"),
               iv)
    for i in range(0, nj):
        pm.connectAttr((sx + ".ox"), (sj[i] + ".sx"),
                       f=1)

    if pm.checkBoxGrp('CTJ', q=1, v1=1):
        cg = str(pm.group(em=1, n=(s[0] + "_control")))
        # > add control
        if pm.checkBoxGrp('CTJP', q=1, v1=1):
            c = []
            t = []
            for i in range(0, (len(cv))):
                pm.connectAttr((cj[i] + ".t"), (ss[0] + ".cp[" + str(i) + "]"),
                               f=1)
                ct = rp_create_control(s, i)
                c[i] = ct[0]
                t[i] = ct[1]
                pm.parentConstraint(cj[i], ct[1], w=1)
                pm.delete(ct[1], cn=1)
                pm.makeIdentity(ct[1], a=1, t=1)
                pm.parentConstraint(ct[0], cj[i], mo=1, w=1)
                pm.parent(ct[1], cg)

            scg = []
            for i in range(0, p):
                scg[i] = str(pm.group(em=1, n=("scGrp_" + s[0] + "_" + str((i + 1)))))
                scgpc = pm.parentConstraint(c[i + (2 * i)], scg[i], w=1)
                pm.delete(scgpc[0])
                pm.makeIdentity(scg[i], a=1, t=1)
                pm.parent(scg[i], c[i + (2 * i)])
                pm.connectAttr((c[i + (2 * i)] + ".change"), (scg[i] + ".sx"),
                               f=1)
                pm.connectAttr((c[i + (2 * i)] + ".change"), (scg[i] + ".sy"),
                               f=1)
                pm.connectAttr((c[i + (2 * i)] + ".change"), (scg[i] + ".sz"),
                               f=1)

            for i in range(0, (p - 1)):
                pm.parent(t[i + 1 + (2 * i)], scg[i])
                pm.setAttr((t[i + 1 + (2 * i)] + ".sx"),
                           0.5)
                pm.setAttr((t[i + 1 + (2 * i)] + ".sy"),
                           0.5)
                pm.setAttr((t[i + 1 + (2 * i)] + ".sz"),
                           0.5)
                pm.setAttr((c[i + 1 + (2 * i)] + ".bezier"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i + 1 + (2 * i)] + ".change"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i + 1 + (2 * i)] + ".rx"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i + 1 + (2 * i)] + ".ry"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i + 1 + (2 * i)] + ".rz"),
                           cb=0, k=0, l=1)
                pm.connectAttr((c[i + (2 * i)] + ".bezier"), (t[i + 1 + (2 * i)] + ".v"),
                               f=1)

            for i in range(1, (p - 0)):
                pm.parent(t[i - 1 + (2 * i)], scg[i])
                pm.setAttr((t[i - 1 + (2 * i)] + ".sx"),
                           0.5)
                pm.setAttr((t[i - 1 + (2 * i)] + ".sy"),
                           0.5)
                pm.setAttr((t[i - 1 + (2 * i)] + ".sz"),
                           0.5)
                pm.setAttr((c[i - 1 + (2 * i)] + ".bezier"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i - 1 + (2 * i)] + ".change"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i - 1 + (2 * i)] + ".rx"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i - 1 + (2 * i)] + ".ry"),
                           cb=0, k=0, l=1)
                pm.setAttr((c[i - 1 + (2 * i)] + ".rz"),
                           cb=0, k=0, l=1)
                pm.connectAttr((c[i + (2 * i)] + ".bezier"), (t[i - 1 + (2 * i)] + ".v"),
                               f=1)



        else:
            for i in range(0, (len(cj))):
                ct = rp_create_control(s, i)
                pm.parentConstraint(cj[i], ct[1], w=1)
                pm.delete(ct[1], cn=1)
                pm.makeIdentity(ct[1], a=1, t=1)
                pm.parentConstraint(ct[0], cj[i], mo=1, w=1)
                pm.parent(ct[1], cg)
                pm.connectAttr((ct[0] + ".change"), (cj[i] + ".sx"),
                               f=1)
                pm.connectAttr((ct[0] + ".change"), (cj[i] + ".sy"),
                               f=1)
                pm.connectAttr((ct[0] + ".change"), (cj[i] + ".sz"),
                               f=1)

        pm.parent(cg, rg)

    if pm.checkBoxGrp('CTJP', q=1, v1=1) == 0:
        pm.skinCluster(cj, s[0], mi=2, rui=1, dr=2.0, n=(s[0] + "_skin"))
    # > connection control to curve

    pm.select(h[0])
    # > end
    pm.ToggleLocalRotationAxes()
    pm.select(s[0])
    pm.mel.rp_Twist()
    print(" :) > rope riging curve > " + s[0] + "\n")


def rp_mixTwist():
    """..............................................................................................//"""

    if pm.checkBoxGrp('MRL', q=1, v1=1):
        pm.checkBoxGrp('MRL', v1=0, e=1)


    else:
        pm.checkBoxGrp('MRL', v1=1, e=1)

    if pm.checkBoxGrp('VRL', q=1, v1=1):
        pm.checkBoxGrp('VRL', v1=0, e=1)


    else:
        pm.checkBoxGrp('VRL', v1=1, e=1)


def rp_Twist():
    """..............................................................................................//"""

    ncj = int(pm.intField('NCJ', q=1, v=1))
    # > control joints
    # > selection list
    s = pm.ls(sl=1)
    rp_check(s)
    cj = pm.ls((s[0] + "_ctj_*"),
               typ="joint")
    # > twist and roll
    if pm.checkBoxGrp('MRL', q=1, v1=1):
        if pm.getAttr(s[0] + "_tw_hl.dtce") == 1:
            pm.setAttr((s[0] + "_tw_hl.dtce"),
                       0)
            pm.disconnectAttr((cj[0] + ".wm[0]"), (s[0] + "_tw_hl.dwum"))
            pm.disconnectAttr((cj[(ncj - 1)] + ".wm[0]"), (s[0] + "_tw_hl.dwue"))

        rl = str(pm.createNode('multiplyDivide', n=(s[0] + "_roll")))
        pm.connectAttr((cj[0] + ".rx"), (rl + ".i1x"),
                       f=1)
        pm.setAttr((rl + ".i2x"), (-1))
        pm.connectAttr((cj[0] + ".rx"), (s[0] + "_tw_hl" + ".rol"),
                       f=1)
        tw = str(pm.createNode('plusMinusAverage', n=(s[0] + "_twist")))
        pm.connectAttr((rl + ".ox"), (tw + ".i1[0]"),
                       f=1)
        pm.connectAttr((cj[(ncj - 1)] + ".rx"), (tw + ".i1[1]"),
                       f=1)
        pm.connectAttr((tw + ".o1"), (s[0] + "_tw_hl" + ".twi"),
                       f=1)


    # > advanced twist
    elif pm.objExists(s[0] + "_twist"):
        pm.delete((s[0] + "_twist"), (s[0] + "_roll"))
        pm.disconnectAttr((cj[0] + ".rx"), (s[0] + "_tw_hl" + ".rol"))

    pm.setAttr((s[0] + "_tw_hl.dtce"),
               1)
    pm.setAttr((s[0] + "_tw_hl.dwut"),
               4)
    pm.setAttr((s[0] + "_tw_hl.dwua"),
               0)
    pm.connectAttr((cj[0] + ".wm[0]"), (s[0] + "_tw_hl.dwum"))
    pm.connectAttr((cj[(ncj - 1)] + ".wm[0]"), (s[0] + "_tw_hl.dwue"))
    pm.setAttr((s[0] + "_tw_hl.dwuy"),
               1)
    pm.setAttr((s[0] + "_tw_hl.dwvy"),
               1)
    pm.setAttr((s[0] + "_tw_hl.dwuz"),
               0)
    pm.setAttr((s[0] + "_tw_hl.dwvz"),
               0)
    pm.setAttr((s[0] + "_tw_hl" + ".rol"),
               0)
    pm.setAttr((s[0] + "_tw_hl" + ".twi"),
               0)
    pm.select(s[0])


# > end



def rp_grip():
    """..............................................................................................//"""

    s = pm.ls(sl=1)
    if pm.mel.gmatch(s[0], "*_grip*"):
        ps = pm.listRelatives(s[0], p=1)
        pm.delete(ps[0])


    else:
        rp_check(s)
        cj = pm.ls((s[0] + "_tw_*"),
                   typ="joint")
        for y in range(0, (len(cj))):
            if pm.objExists("ctgrp_" + s[0] + "_grip" + str((y + 1))) == 0:
                ct = pm.circle(ch=0, nr=(1, 0, 0), r=0.8, d=3, n=("CT_" + s[0] + "_grip" + str((y + 1))))
                ctg = str(pm.group(ct[0], n=("ctgrp_" + s[0] + "_grip" + str((y + 1)))))
                pm.parent(ctg,
                          (s[0] + "_rig"))
                pm.setAttr((ct[0] + ".tx"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".ty"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".tz"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".rx"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".ry"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".rz"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".sx"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".sy"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".sz"),
                           k=0, l=1)
                pm.setAttr((ct[0] + ".v"),
                           k=0)
                pm.setAttr((ct[0] + "Shape.ove"),
                           1)
                pm.setAttr((ct[0] + "Shape.ovc"),
                           13)
                pm.addAttr(ct[0], min=0, ln="move", max=(len(cj)), k=1, at="long", dv=0)
                pm.parentConstraint(cj, ctg, w=1)
                for i in range(0, (len(cj))):
                    pm.setAttr((ct[0] + ".move"),
                               i)
                    for x in range(0, (len(cj))):
                        pm.setAttr((ctg + "_parentConstraint1." + cj[x] + "W" + str(x)),
                                   0)
                        pm.setAttr((ctg + "_parentConstraint1." + cj[i] + "W" + str(i)),
                                   1)
                        pm.setDrivenKeyframe((ctg + "_parentConstraint1." + cj[x] + "W" + str(x)),
                                             cd=(ct[0] + ".move"))

                pm.setAttr((ct[0] + ".move"), (y + 1))
                pm.select(s[0])
                break


def rp_surface():
    """..............................................................................................//"""

    ncj = int(pm.intField('NCJ', q=1, v=1))
    # > control joints
    rn = float(pm.intField('NJ', q=1, v=1))
    bz = int(pm.checkBoxGrp('CTJP', q=1, v1=1))
    s = pm.ls(sl=1)
    rp_check(s)
    if pm.objExists(s[0] + "_surface"):
        rp_del()
        rp_cr()

    cj = pm.ls((s[0] + "_ctj_*"),
               typ="joint")
    x = 0.0
    if pm.optionMenuGrp('AXES', q=1, v=1) == "x":
        x = float(1)

    y = 0.0
    if pm.optionMenuGrp('AXES', q=1, v=1) == "y":
        y = float(1)

    z = 0.0
    if pm.optionMenuGrp('AXES', q=1, v=1) == "z":
        z = float(1)

    su = pm.extrude(s[0], upn=0, dl=3, ch=bz, d=(x, y, z), n=(s[0] + "_surface"), et=0, rn=0, po=0)
    pm.pm.cmds.move(((-1) * (x / 2)), ((-1) * (y / 2)), ((-1) * (z / 2)),
                    su[0])
    pm.makeIdentity(su[0], a=1, t=1)
    sj = pm.ls((s[0] + "_tw_*"),
               typ="joint")
    # pivot move
    t = (pm.xform(cj[0], q=1, ws=1, t=1))
    pm.setAttr((su[0] + ".rpx"), (t.x))
    pm.setAttr((su[0] + ".rpy"), (t.y))
    pm.setAttr((su[0] + ".rpz"), (t.z))
    pm.setAttr((su[0] + ".spx"), (t.x))
    pm.setAttr((su[0] + ".spy"), (t.y))
    pm.setAttr((su[0] + ".spz"), (t.z))
    # hairs
    hsys = str(pm.createNode("hairSystem", n=(s[0] + "_position")))
    hsysg = pm.listRelatives(hsys, p=1)
    pm.rename(hsysg[0],
              (s[0] + "_surface_grp_"))
    pm.select(su[0], hsys)
    pm.mel.createHair((len(sj)), 1, 2, 0, 0, 1, 1, 1, 0, 2, 2, 1)
    pm.delete((s[0] + "_surface_grp_"), (s[0] + "_surface_grp_OutputCurves"))
    # joints
    sg = pm.listRelatives((s[0] + "_surface_grp_Follicles"),
                          c=1)
    pm.delete(s[0] + "_tw_hl")
    for i in range(0, (len(sj))):
        pm.parent(sj[i], sg[i])
        pm.makeIdentity(sj[i], a=1, r=1)
        pm.connectAttr((s[0] + "_rig.s"), (sg[i] + ".s"),
                       f=1)

    pm.parent(su[0],
              (s[0] + "_sistem"))
    pm.parent((s[0] + "_surface_grp_Follicles"), (s[0] + "_sistem"))
    # conection scale joints
    if bz == 0:
        if pm.checkBoxGrp('CTJ', q=1, v1=1):
            for i in range(0, (len(cj))):
                pm.disconnectAttr((s[0] + "_" + str((i + 1)) + "_CT.change"), (cj[i] + ".sy"))
                pm.disconnectAttr((s[0] + "_" + str((i + 1)) + "_CT.change"), (cj[i] + ".sz"))

        pm.delete((s[0] + "_sx"), (s[0] + "_s"))

    sx = str(pm.createNode('multiplyDivide', n=(s[0] + "_pow")))
    # pow scale
    pm.setAttr((sx + ".op"),
               2)
    pm.connectAttr((s[0] + "_rig.s"), (sx + ".i2"),
                   f=1)
    pm.setAttr((sx + ".i1x"),
               1)
    pm.setAttr((sx + ".i1y"),
               1)
    pm.setAttr((sx + ".i1z"),
               1)
    pm.connectAttr((sx + ".o"), (s[0] + "_surface_grp_Follicles.s"),
                   f=1)
    # > skin
    fol = pm.ls((s[0] + "_surfaceFollicle*"),
                typ="transform")
    for i in range(0, (len(fol))):
        pm.setAttr((fol[i] + ".it"),
                   0)

    if bz == 0:
        pm.rebuildSurface(su[0], dv=1, du=3, sv=0, su=rn)
        pm.intField('NJ', e=1, v=rn)
        pm.skinCluster(cj, su[0], mi=2, rui=1, dr=2.0, n=(s[0] + "_skin_surface"))

    pm.setAttr((su[0] + ".it"),
               0)
    pm.setAttr((su[0] + ".tmp"),
               1)
    # > end
    pm.select(s[0])


ak_rope()
# ..............................................................................................//
