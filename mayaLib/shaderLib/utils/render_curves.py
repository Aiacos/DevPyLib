import maya.mel as mel
import pymel.core as pm
from mayaLib.shaderLib.base import shader_base


def add_sweep(cv_list, size=0.05):
    pm.sweepMeshFromCurve(cv_list, oneNodePerCurve=False)
    sweep_deformer = pm.ls(sl=True)[-1]

    sweep_deformer.scaleProfileX.set(size)
    sweep_deformer.interpolationPrecision.set(100)
    sweep_deformer.interpolationOptimize.set(1)

    source_list = pm.listConnections(sweep_deformer.inCurveArray)
    destination_list = pm.listConnections(sweep_deformer.outMeshArray)

    for source, destination in zip(source_list, destination_list):
        pm.rename(destination, str(source.name()) + '_sweep_geo')

    pm.group(destination_list, n='ctrl_curve_geo_grp')

    return destination_list


def ctrl_paintEffect(cv_list):
    cv_list = pm.ls(cv_list)

    pm.select(cv_list)
    mel.eval('AttachBrushToCurves;')

    stroke_list = []
    for cv in cv_list:
        cv_shape_list = cv.getShapes()
        for cv_shape in cv_shape_list:
            stroke = pm.listConnections(cv_shape.worldSpace)[-1]
            stroke_list.append(stroke)
            pm.rename(stroke, str(cv.name()) + '_stroke')

    ctrl_geo_list = []
    empty_grp_list = []
    pm.select(stroke_list)
    mel.eval('doPaintEffectsToPoly( 1,0,0,1,100000);')
    for ctrl_geo_shape in pm.ls(sl=True):
        stroke = pm.listConnections(ctrl_geo_shape.inMesh)[-1]
        ctrl_geo = ctrl_geo_shape.getParent()
        ctrl_geo_list.append(ctrl_geo)

        empty_grp_list.append(ctrl_geo.getParent())
        pm.rename(ctrl_geo, str(stroke).replace('_stroke', '_stroke_geo'))

    ctrl_geo_grp = pm.group(em=True, n='ctrl_geo_grp')
    stroke_grp = pm.group(stroke_list, n='stroke_grp', p=ctrl_geo_grp)
    cv_geo_grp = pm.group(ctrl_geo_list, n='ctrl_geo_grp', p=ctrl_geo_grp)

    pm.hide(stroke_grp)

    pm.delete(empty_grp_list)

    return ctrl_geo_list


def add_ctrl_shader(ctrl_list):
    ctrl_list = pm.ls(ctrl_list)
    sweep_geo_list = ctrl_paintEffect(ctrl_list)

    for cv in ctrl_list:
        cv_shape_list = cv.getShapes()
        for cv_shape in cv_shape_list:
            stroke = pm.listConnections(cv_shape.worldSpace)[-1]
            ctrl_geo = pm.listConnections(stroke.worldMainMesh)[-1]

            try:
                rgb_color = pm.colorIndex(cv.overrideColor.get(), q=True)
            except:
                if cv.getShape().overrideEnabled.get() == 0:
                    cv.getShape().overrideEnabled.set(1)
                    cv.getShape().ovc.set(1)

                rgb = ('R', 'G', 'B')
                color = []
                for channel in rgb:
                    color_channel = pm.getAttr(str(cv.getShape().name()) + ".overrideColor%s" % channel)
                    color.append(color_channel)
                rgb_color = color#pm.colorIndex(cv.getShape().overrideColor.get(), q=True)

            shader_name = str(ctrl_geo.name()).replace('geo', 'mat')
            surface_shader = shader_base.build_surfaceshader(shaderName=shader_name,
                                                             color=(rgb_color[0], rgb_color[1], rgb_color[2]))
            shader_base.assign_shader(ctrl_geo, surface_shader)
