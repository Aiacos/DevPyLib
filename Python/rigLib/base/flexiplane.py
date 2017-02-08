import pymel.core as pm
import shaderLib.base.shader


def create_plane(width=10, lengthratio=0.2):
    """
    Create NURBS plane
    :param width:
    :param lengthratio:
    :return:
    """
    nurbs_plane = pm.nurbsPlane(name='flexiPlane_surface',
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


def flexiplane():
    """
    Build FlexiPlane
    :return: FlexiPlane group node
    """
    nurbs_plane = create_plane()[0]

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


if __name__ == "__main__":
    flexiplane()
