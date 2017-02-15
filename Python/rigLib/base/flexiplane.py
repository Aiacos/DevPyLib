import pymel.core as pm
from string import letters
from shaderLib.base import shader
from rigLib.utils import util


class Flexiplane():
    """Manage flexiplane"""

    # creates static variable containing default name
    SETTINGS_DEFAULT = {
        'prefix': 'M_',  # char
        'num': 0,
    }

    def __init__(self, prefix=''):
        self.fp = 'flexiPlane_'
        self.sur = 'surface_'
        self.YELLOW = 17

        Flexiplane.SETTINGS_DEFAULT['prefix'] = prefix
        Flexiplane.SETTINGS_DEFAULT['num'] += 1
        self.flexiplane(settings=Flexiplane.SETTINGS_DEFAULT)

    def __del__(self):
        print self.safe_delete()

    def safe_delete(self):
        """
        deletes curve info node then flexiplane group node
        :param : global control curve of flexiplane to be deleted
        """
        # filter out nodes that aren't a flexiplane global control
        selection = pm.selected()
        flex = [f for f in selection if '_flexiPlane_ctrl_global' in f.nodeName()]

        # get the flexiplane curve info node
        curve_name = [f.replace('ctrl_global', 'curveInfo') for f in flex]

        # delete curve info node
        delete_curve = [pm.delete(c) for c in curve_name]
        # delete the flexiplane
        delete_flex = [pm.delete(f.getParent()) for f in flex]
        return flex, curve_name

    def test(self):
        print Flexiplane.SETTINGS_DEFAULT['prefix']
        print Flexiplane.SETTINGS_DEFAULT['num']

    def create_plane(self, name, width=10, lengthratio=0.2):
        """
        Create NURBS plane
        :param name: string
        :param width:
        :param lengthratio:
        :return:
        """
        nurbs_plane = pm.nurbsPlane(name=name,
                                    width=width,
                                    lengthRatio=lengthratio,
                                    patchesU=width / 2,
                                    degree=3,
                                    axis=[0, 1, 0],
                                    constructionHistory=False)
        return nurbs_plane

    def create_lambret(self, geo, color=(0.5, 0.5, 0.5), transparency=(0.0, 0.0, 0.0)):
        """
        Create base lamber shader
        :param geo: list of geo to apply shader
        :param color: es: (0,1,0)
        :param transparency: es: (0,1,0)
        :return: none
        """
        name = 'flexiPlane_lambert_material01'
        my_shader = shader.build_lambert(shaderType='lambert',
                                         shaderName=name,
                                         color=color,
                                         transparency=transparency)
        shader.assign_shader(geo, my_shader)

    def create_surfaceshader(self, geo, color=(0.5, 0.5, 0.5)):
        """
        Create base lamber shader
        :param geo: list of geo to apply shader
        :param color: es: (0,1,0)
        :return: none
        """
        name = 'flexiPlane_surface_material01'
        my_shader = shader.build_surfaceshader(shaderType='surfaceShader',
                                               shaderName=name,
                                               color=color)
        shader.assign_shader(geo, my_shader)

    # function to create control curves
    def ctrl_square(self, name=None, pos=None):
        """
        create square control curve
        :param name: control curve name
        :param pos: control curves final position
        :return: control curve
        """
        if not name:
            name = 'flexiPlane_ctrl'
        if not pos:
            pos = [0, 0, 0]
        fp_ctrl = pm.curve(d=1,
                           p=[(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1)],
                           k=[0, 1, 2, 3, 4],
                           n=name)
        fp_ctrl.overrideEnabled.set(1)
        fp_ctrl.overrideColor.set(17)
        pm.move(pos, rpr=True)
        pm.scale(0.5, 0.5, 0.5, r=True)
        pm.makeIdentity(t=1, r=1, s=1, a=True)
        fp_ctrl.rotateOrder.set('xzy')
        return fp_ctrl

    # function for creating and attaching follicles to flexiplane surface
    def create_follicle(self, onurbs, name, upos=0.0, vpos=0.0):
        """
        Create follicle
        :param onurbs: node object
        :param name: string
        :param upos: real
        :param vpos: real
        :return:
        """
        # manually place and connect a follicle onto a nurbs surface.
        if onurbs.type() == 'transform':
            onurbs = onurbs.getShape()
        elif onurbs.type() == 'nurbsSurface':
            pass
        else:
            'Warning: Input must be a nurbs surface.'
            return False

        # create a name with frame padding
        pname = '%sShape' % name

        ofoll = pm.createNode('follicle', name=pname)
        onurbs.local.connect(ofoll.inputSurface)
        # if using a polygon mesh, use this line instead.
        # (The polygons will need to have UVs in order to work.)
        # oMesh.outMesh.connect(oFoll.inMesh)

        onurbs.worldMatrix[0].connect(ofoll.inputWorldMatrix)
        ofoll.outRotate.connect(ofoll.getParent().rotate)
        ofoll.outTranslate.connect(ofoll.getParent().translate)
        ofoll.parameterU.set(upos)
        ofoll.parameterV.set(vpos)
        ofoll.getParent().t.lock()
        ofoll.getParent().r.lock()

        return ofoll

    # funtion to create cluster
    def make_cluster(self, target, name=None, origin=0, pos_x=0, pos_y=0, pos_z=0):
        """
        creates a cluster on targeted cvs
        :param target: affect cvs
        :param name: name for cluster
        :param origin: integer value for cluster originX
        :param pos_x: integer for x value for move
        :param pos_y: integer for y value for move
        :param pos_z: integer for z value for move
        :return: new cluster
        """
        cl = pm.cluster(target,
                        rel=1,
                        en=1.0,
                        n=name)
        if origin != 0:
            cl[1].originX.set(origin)
            pm.move(pos_x, pos_y, pos_z, cl[1].scalePivot, cl[1].rotatePivot)
        else:
            pass
        return cl

    def cluster_curve(self, curve, name):
        """
        adds clusters to 3 cv curve
        :param curve: curve node to be affected
        :param name: string for cluster names
        :return: new clusters
        """
        cl_a = self.make_cluster(target=curve.cv[0:1],
                                 name='%s_cl_a01' % name,
                                 origin=-6,
                                 pos_x=-5,
                                 pos_z=-5)

        cl_b = self.make_cluster(target=curve.cv[1:2],
                                 name='%s_cl_b01' % name,
                                 origin=6,
                                 pos_x=5,
                                 pos_z=-5)

        cl_mid = self.make_cluster(target=curve.cv[1],
                                   name='%s_cl_mid01' % name)

        # redistributes cluster weight
        pm.percent(cl_a[0], curve.cv[1], v=0.5)
        pm.percent(cl_b[0], curve.cv[1], v=0.5)
        return cl_a, cl_b, cl_mid

    def flexiplane_mid_ctrl(self, name=None):
        """
        Create Mid Control
        :param name:
        :return:
        """
        if not name:
            name = '_mid_ctrl'

        mid_ctrl = pm.polySphere(n=name, r=0.3, sx=8, sy=8, ax=(0.0, 1.0, 0.0), ch=False)[0]
        # cc_shp = cc.getShape()
        # cc_shp.overrideEnabled.set(1)
        # cc_shp.overrideColor.set(color)
        self.create_surfaceshader(mid_ctrl, color=(1.0, 1.0, 0.0))

        return mid_ctrl

    # function to create global move control curve
    def global_ctrl(self, name='ctrl', settings=SETTINGS_DEFAULT):
        """
        create global control curve
        :param name: string for control curve name
        :param settings: dictionary holding node number
        :return: control curve
        """
        # creates primary global control curve
        glb_ctrl = pm.circle(c=[0, 0, -2],
                             sw=360,
                             r=0.3,
                             nr=[0, 1, 0],
                             ch=0,
                             n='%sglobal_%i' % (name, settings['num']))[0]
        # grab its shape and recolors it

        glb_ctrlshape = glb_ctrl.getShape()
        glb_ctrlshape.overrideEnabled.set(1)
        glb_ctrlshape.overrideColor.set(17)
        # adds the volume label and an enable attribute
        pm.addAttr(ln='_',
                   at='enum',
                   en='volume:')
        glb_ctrl._.set(e=True,
                       cb=True)
        pm.addAttr(ln='enable',
                   sn='en',
                   at='bool',
                   k=True,
                   h=False)
        # create secondary control curve
        glb_ctrl_b = pm.circle(c=[0, 0, 2],
                               sw=360,
                               r=0.3,
                               nr=[0, 1, 0],
                               ch=0,
                               n='%sglobal_b_%i' % (name, settings['num']))[0]
        # grabs it's shape recolors it
        glb_ctrl_bshape = glb_ctrl_b.getShape()
        glb_ctrl_bshape.overrideEnabled.set(1)
        glb_ctrl_bshape.overrideColor.set(17)
        # parents the shapeNode of secondary curve the primary curve
        pm.parent(glb_ctrl_bshape,
                  glb_ctrl,
                  r=True,
                  s=True)
        # deletes empty transformNode
        pm.delete(glb_ctrl_b)
        # return primary control transformNode
        pm.select(glb_ctrl,
                  r=True)
        return glb_ctrl

    def flexiplane(self, settings=SETTINGS_DEFAULT):
        """
        Build FlexiPlane
        :param index: number of flexiplane in scene (auto managed by maya)
        :return: FlexiPlane group node
        """

        fp_name = '%sflexiPlane_' % settings['prefix']

        fp_surf = self.create_plane('%s%s_%i' % (fp_name, self.sur, settings['num']))[0]

        # Assign Material
        self.create_lambret(fp_surf, color=(0.067, 0.737, 0.749), transparency=(0.75, 0.75, 0.75))

        # Create Follicles
        flc_name = 'flexiPlane'
        v = 0.1  # 1/width
        flcs = []
        how_many_flc = 5  # width/2
        for i in range(0, how_many_flc):
            ofoll = self.create_follicle(fp_surf, '%sflc_%s_%i' % (fp_name, letters[i + 26], settings['num']), v, 0.5)
            flcs.append(ofoll)
            v += 0.2  # (1/width)*2

        # Group Follicles
        flc_grp = pm.group(flcs, name='%sflcs_%i' % (fp_name, settings['num']))

        # creates flexiPlane controls curves at each end
        ctrl_a = self.ctrl_square(name='%sctrl_a_%i' % (fp_name, settings['num']), pos=[-5, 0, 0])
        ctrl_ashape = ctrl_a.getShape()
        pm.rename(ctrl_ashape, '%sShape' % ctrl_a)

        ctrl_b = self.ctrl_square(name='%sctrl_b_%i' % (fp_name, settings['num']), pos=[5, 0, 0])
        ctrl_bshape = ctrl_b.getShape()
        pm.rename(ctrl_bshape, '%sShape' % ctrl_b)

        pm.select(cl=True)

        # creates flexiPlane blendshape     #  blendshape suffix: _bShp_
        fp_bshp = pm.duplicate(fp_surf, n='%sbshp_%s_%i' % (fp_name, self.sur, settings['num']))[0]
        pm.move(0, 0, -5, fp_bshp)

        fps_bshp_node = pm.blendShape(fp_bshp, fp_surf, n='%sbshpNode_%s%i' % (fp_name, self.sur, settings['num']))[0]
        pm.setAttr('%s.%s' % (fps_bshp_node, fp_bshp), 1)
        # pm.rename('tweak1', '%sbshp_%stweak_01' % (fp_name, sur))

        # creates curve for wire deformer
        fp_curve = pm.curve(d=2,
                            p=[(-5, 0, -5), (0, 0, -5), (5, 0, -5)],
                            k=[0, 0, 1, 1],
                            n='%swire_%s%i' % (fp_name, self.sur, settings['num']))
        cl_a, cl_b, cl_mid = self.cluster_curve(fp_curve, fp_name)

        # create and place twist deformer
        pm.select(fp_bshp)
        fp_twist = pm.nonLinear(type='twist', lowBound=-1, highBound=1)
        # displays warning: pymel.core.general : could not create desired mfn. Defaulting MfnDependencyNode.
        # doesn't seem to affect anything though
        pm.rename(fp_twist[0], '%stwistAttr_surface_%i' % (fp_name, settings['num']))
        pm.rename(fp_twist[1], '%stwist_%i_Handle' % (fp_name, settings['num']))
        fp_twist[1].rz.set(90)
        # connect start and end angle to their respective control
        connect = ctrl_b.rx >> fp_twist[0].startAngle
        connect = ctrl_a.rx >> fp_twist[0].endAngle

        # skins wire to blendshape
        fp_wire = pm.wire(fp_bshp, w=fp_curve, gw=False, en=1, ce=0, li=0,  # dds=(0, 20),
                          n='%swireAttrs_%s%i' % (fp_name, self.sur, settings['num']))
        fp_wire[0].dropoffDistance[0].set(20)
        hist = pm.listHistory(fp_surf)
        tweaks = [t for t in hist if 'tweak' in t.nodeName()]
        pm.rename(tweaks[2], '%scl_cluster_tweak_%i' % (fp_name, settings['num']))
        pm.rename(tweaks[0], '%swireAttrs_%stweak_%i' % (fp_name, self.sur, settings['num']))
        pm.rename(tweaks[1], '%sextra_%stweak_%i' % (fp_name, self.sur, settings['num']))

        # group clusters
        cl_grp = pm.group(cl_a[1], cl_b[1], cl_mid[1], n='%scls_%i' % (fp_name, settings['num']))
        util.lock_and_hide_all(cl_grp)

        # creates mid control
        ctrl_mid = self.flexiplane_mid_ctrl(name='%sctrl_mid_%i' % (fp_name, settings['num']))
        ctrl_mid_grp = pm.group(ctrl_mid, n='%sgrp_midBend_%i' % (fp_name, settings['num']))
        pm.pointConstraint(ctrl_a, ctrl_b, ctrl_mid_grp, o=[0, 0, 0], w=1)

        # groups controls together and locks and hides group attributes
        ctrl_grp = pm.group(ctrl_a, ctrl_b, ctrl_mid_grp, n='%sctrl_%i' % (fp_name, settings['num']))
        util.lock_and_hide_all(ctrl_grp)

        # connecting translate attrs of control curves for to the clusters
        connect = []
        connect.append(ctrl_a.t >> cl_a[1].t)
        connect.append(ctrl_b.t >> cl_b[1].t)
        connect.append(ctrl_mid.t >> cl_mid[1].t)

        # makes mid_ctrl, flexiPlane and blendShape surfaces non renderable
        util.no_render(fp_surf)
        util.no_render(fp_bshp)
        util.no_render(ctrl_mid)

        # groups everything under 1 group then locks and hides the transform attrs of that group #flexiPlane_wire_surface0101BaseWire
        fp_grp = pm.group(fp_surf, flc_grp, fp_bshp, fp_wire,
                          '%swire_%s%iBaseWire' % (fp_name, self.sur, settings['num']),
                          cl_grp, ctrl_grp, n='%s%i' % (fp_name, settings['num']))
        util.lock_and_hide_all(fp_grp)

        # creates global move group and extraNodes
        fp_gm_grp = pm.group(fp_surf, ctrl_grp, n='%sglobalMove_%i' % (fp_name, settings['num']))
        fp_xnodes_grp = pm.group(flc_grp, fp_bshp, fp_wire,
                                 '%swire_%s%iBaseWire' % (fp_name, self.sur, settings['num']),
                                 cl_grp, n='%sextraNodes_%i' % (fp_name, settings['num']))
        pm.parent(fp_twist, fp_xnodes_grp)

        # scale constrains follicles to global move group
        for follicle in flcs:
            mparent = follicle.getParent()
            pm.scaleConstraint(fp_gm_grp, mparent)

        # creates global move control
        fp_gm_ctrl = self.global_ctrl(name='%sctrl_' % fp_name, settings=settings)

        # moves global control into flexiPlane group then parent global move group to global move control.
        pm.parent(fp_gm_ctrl, fp_grp)
        pm.parent(fp_gm_grp, fp_gm_ctrl)

        # joints placement
        jnts = []
        for i in range(0, len(flcs)):
            posx = round(flcs[i].getParent().translateX.get(), 4)
            jnt = pm.joint(p=(posx, 0, 0), rad=0.5, n='%sbind_%s_%i' % (fp_name, letters[i + 26], settings['num']))
            jnts.append(jnt)
            # parent joint under follicle
            pm.parent(jnt, flcs[i].getParent())

        # locks and hides transformNodes flexiPlane surface
        util.lock_and_hide_all(fp_surf)
        # hides blendShape, clusters and twist Deformer
        fp_twist[1].visibility.set(0)
        cl_grp.visibility.set(0)
        fp_bshp.visibility.set(0)
        fp_curve.visibility.set(0)

        # selects the wire deformer and creates a curve info node...
        # ...to get the wire deformers length
        pm.select(fp_curve, r=True)
        length = pm.arclen(ch=1)
        length.rename('%scurveInfo_%i' % (fp_name, settings['num']))

        # creates a multiplyDivideNode for squashStretch length...
        # ...and sets it operation to divide
        fp_div = pm.createNode('multiplyDivide', n='%sdiv_squashStretch_length_%i' % (fp_name, settings['num']))
        fp_div.operation.set(2)

        # secondary multDivNode for volume, sets input1X to 1
        fp_div_vol = pm.createNode('multiplyDivide', n='%sdiv_volume_%i' % (fp_name, settings['num']))
        fp_div_vol.operation.set(2)
        fp_div_vol.input1X.set(1)

        # creates a conditionNode for global_ctrl enable attr
        fp_cond = pm.createNode('condition', n='%scond_volume_%i' % (fp_name, settings['num']))
        fp_cond.secondTerm.set(1)

        # connects curve all the nodes
        connect = length.arcLength >> fp_div.input1.input1X
        fp_div.input2.input2X.set(10)
        connect = fp_div.outputX >> fp_div_vol.input2.input2X
        connect = fp_gm_ctrl.enable >> fp_cond.firstTerm
        connect = fp_div_vol.outputX >> fp_cond.colorIfTrueR
        fp_ctrl_global = fp_gm_ctrl.getShape()

        for i in range(0, len(flcs)):
            connect = fp_cond.outColorR >> jnts[i].sy
            connect = fp_cond.outColorR >> jnts[i].sz
            flcs[i].visibility.set(0)

        # hides blendShape, clusters and twist Deformer
        fp_twist[1].visibility.set(0)
        cl_grp.visibility.set(0)
        fp_bshp.visibility.set(0)
        fp_curve.visibility.set(0)

        pm.select(fp_gm_ctrl, r=True)
        return fp_gm_ctrl


if __name__ == "__main__":
    fp1 = Flexiplane()
    fp1.test()
    fp2 = Flexiplane('L_')
    fp2.test()
    fp2.safe_delete()
    fp3 = Flexiplane('R_')
    fp3.test()
