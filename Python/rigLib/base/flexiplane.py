import pymel.core as pm
import shaderLib.base.shader


def create_plane(name, width=10, lengthratio=0.2):
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


# si puo saltare
def create_lambret(geo, color=(0.5, 0.5, 0.5), transparency=(0.0, 0.0, 0.0)):
    """
    Create base lamber shader
    :param geo: list of geo to apply shader
    :param color: es: (0,1,0)
    :param transparency: es: (0,1,0)
    :return: none
    """
    name = 'flexiPlane_surface_material01'
    shader = shaderLib.base.shader.build_lambert(shaderType='lambert',
                                                 shaderName=name,
                                                 color=color,
                                                 transparency=transparency)
    shaderLib.base.shader.assign_shader(geo, shader)


# function to create control curves
def ctrl_square(name=None, pos=None):
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
    fp_cnt = pm.curve(d=1,
                      p=[(-1, 0, 1), (1, 0, 1), (1, 0, -1), (-1, 0, -1), (-1, 0, 1)],
                      k=[0, 1, 2, 3, 4],
                      n=name)
    fp_cnt.overrideEnabled.set(1)
    fp_cnt.overrideColor.set(17)
    pm.move(pos, rpr=True)
    pm.scale(0.5, 0.5, 0.5, r=True)
    pm.makeIdentity(t=1, r=1, s=1, a=True)
    pm.xform(roo='xzy')
    return fp_cnt


# function for creating and attaching follicles to flexiplane surface
def create_follicle(onurbs, name, upos=0.0, vpos=0.0):
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
def make_cluster(target,
                 name=None,
                 origin=0,
                 pos_x=0,
                 pos_y=0,
                 pos_z=0):
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


def cluster_curve(curve, name):
    """
    adds clusters to 3 cv curve
    :param curve: curve node to be affected
    :param name: string for cluster names
    :param settings: dictionary that holds node number
    :return: new clusters
    """
    cl_a = make_cluster(target=curve.cv[0:1],
                        name='%s_cl_a01' % name,
                        origin=-6,
                        pos_x=-5,
                        pos_z=-5)

    cl_b = make_cluster(target=curve.cv[1:2],
                        name='%s_cl_b01' % name,
                        origin=6,
                        pos_x=5,
                        pos_z=-5)

    cl_mid = make_cluster(target=curve.cv[1],
                          name='%s_cl_mid01' % name)

    # redistributes cluster weight
    pm.percent(cl_a[0], curve.cv[1], v=0.5)
    pm.percent(cl_b[0], curve.cv[1], v=0.5)
    return cl_a, cl_b, cl_mid


def flexiplane():
    """
    Build FlexiPlane
    :return: FlexiPlane group node
    """
    surface_suffix = '_surface'
    nurbs_plane = create_plane('flexiPlane' + surface_suffix)[0]

    # Assign Material
    create_lambret(nurbs_plane, color=(0.067, 0.737, 0.749), transparency=(0.75, 0.75, 0.75))

    # Create Follicles
    flc_name = 'flexiPlane'
    v = 0.1  # 1/width
    flcs = []
    how_many_flc = 5  # width/2
    for i in range(0, how_many_flc):
        ofoll = create_follicle(nurbs_plane, flc_name + str(i) + '_flc', v, 0.5)
        flcs.append(ofoll)
        v += 0.2  # (1/width)*2

    # Group Follicles
    grp_name = 'flexiPlane_flcs_grp'
    flc_grp = pm.group(flcs, name=grp_name)

    # creates flexiPlane controls curves at each end
    ctrl_a = ctrl_square(name='%s_a_ctrl' % flc_name, pos=[-5, 0, 0])
    ctrl_ashape = ctrl_a.getShape()
    pm.rename(ctrl_ashape, '%sShape' % ctrl_a)

    ctrl_b = ctrl_square(name='%s_b_ctrl' % flc_name, pos=[5, 0, 0])
    cnt_bshape = ctrl_b.getShape()
    pm.rename(cnt_bshape, '%sShape' % ctrl_b)

    pm.select(cl=True)

    # creates flexiPlane blendshape     #  blendshape suffix: _bShp_
    fp_bshp = pm.duplicate(nurbs_plane, n=nurbs_plane.name() + '_bShp')[0]
    pm.move(0, 0, -5, fp_bshp)

    fps_bshp_node = pm.blendShape(fp_bshp, nurbs_plane,
                                  n=nurbs_plane.name().replace(surface_suffix, '_bShpNode' + surface_suffix))[0]
    pm.setAttr('%s.%s' % (fps_bshp_node, fp_bshp), 1)
    pm.rename('tweak1', nurbs_plane.name().replace(surface_suffix, '_bShp' + surface_suffix + '_tweak01'))

    # creates curve for wire deformer
    fp_curve = pm.curve(d=2,
                        p=[(-5, 0, -5), (0, 0, -5), (5, 0, -5)],
                        k=[0, 0, 1, 1],
                        n=nurbs_plane.name().replace(surface_suffix, '_wire' + surface_suffix))
    cl_a, cl_b, cl_mid = cluster_curve(fp_curve, nurbs_plane.name())

    # skins wire to blendshape
    fp_wire = pm.wire(fp_bshp,
                      w=fp_curve,
                      gw=False,
                      en=1,
                      ce=0,
                      li=0,
                      n=nurbs_plane.name().replace(surface_suffix, '_wreAttrs' + surface_suffix))
    fp_wire[0].dropoffDistance[0].set(20)
    hist = pm.listHistory(nurbs_plane)
    tweaks = [t for t in hist if 'tweak' in t.nodeName()]
    pm.rename(tweaks[2], nurbs_plane.name().replace(surface_suffix, '_cl_cluster_tweak'))
    pm.rename(tweaks[0], nurbs_plane.name() + '_wreAttrs_tweak')
    pm.rename(tweaks[1], nurbs_plane.name() + '_extra_tweak')


if __name__ == "__main__":
    flexiplane()
