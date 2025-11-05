#!/usr/bin/env python

"""Maya muscle tool helpers, adapted for snake_case naming.

Original author: Toshi Kosaka (Gorioshi Scripts). The logic is preserved, and
function names follow PEP 8 snake_case conventions.
"""

from __future__ import annotations

from maya import cmds as mc
from maya import mel

# pylint: disable=too-many-lines,too-many-branches,too-many-statements
# pylint: disable=too-many-locals,too-many-arguments,missing-function-docstring
# pylint: disable=invalid-name,line-too-long,consider-using-with,unused-argument


def apply_collision_solve_values(arg=None):
    """Apply collision solve preset values to nCloth attributes.

    Sets predefined values for cloth simulation collision solving,
    including thickness, stretch resistance, rigidity, and pressure.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    mc.floatField('clothThickness', e=True, v=0.01)
    mc.intField('stretchResistance', e=True, v=20)
    mc.floatField('rigidity', e=True, v=0)
    mc.intField('pressure', e=True, v=0)
    mc.floatField('pushOut', e=True, v=1)
    n_cloth_list = mc.ls(type='nCloth', fl=True)
    for each in n_cloth_list:
        mc.setAttr(each + '.thickness', mc.floatField('clothThickness', q=True, v=True))
        mc.setAttr(each + '.stretchResistance', mc.intField('stretchResistance', q=True, v=True))
        mc.setAttr(each + '.rigidity', mc.floatField('rigidity', q=True, v=True))
        mc.setAttr(each + '.pressure', mc.intField('pressure', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOut', q=True, v=True))
        mc.setAttr(each + '.compressionResistance', 0)
        mc.setAttr(each + '.bendResistance', 0)
        mc.setAttr(each + '.lift', 0)
        mc.setAttr(each + '.drag', 2)
        mc.setAttr(each + '.tangentialDrag', 1)
        mc.setAttr(each + '.damp', 10)
        mc.setAttr(each + '.stretchDamp', 10)
        mc.setAttr(each + '.trappedCheck', 1)
        mc.setAttr(each + '.selfTrappedCheck', 1)
        mc.setAttr(each + '.crossoverPush', 1)
        mc.setAttr(each + '.selfCrossoverPush', 1)
        mc.setAttr(each + '.restLengthScale', 1)
    mc.checkBox('restLengthScale', e=True, en=False, v=False)


def apply_fill_values(arg=None):
    """Apply expand and fill preset values to nCloth attributes.

    Sets predefined values for cloth simulation with lower stretch resistance
    for expansion behavior.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    mc.floatField('clothThickness', e=True, v=0.01)
    mc.intField('stretchResistance', e=True, v=1)
    mc.floatField('rigidity', e=True, v=0)
    mc.intField('pressure', e=True, v=2)
    mc.floatField('pushOut', e=True, v=1)
    n_cloth_list = mc.ls(type='nCloth', fl=True)
    for each in n_cloth_list:
        mc.setAttr(each + '.thickness', mc.floatField('clothThickness', q=True, v=True))
        mc.setAttr(each + '.stretchResistance', mc.intField('stretchResistance', q=True, v=True))
        mc.setAttr(each + '.rigidity', mc.floatField('rigidity', q=True, v=True))
        mc.setAttr(each + '.pressure', mc.intField('pressure', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOut', q=True, v=True))
        mc.setAttr(each + '.compressionResistance', 0)
        mc.setAttr(each + '.bendResistance', 0)
        mc.setAttr(each + '.lift', 0)
        mc.setAttr(each + '.drag', 2)
        mc.setAttr(each + '.tangentialDrag', 1)
        mc.setAttr(each + '.damp', 10)
        mc.setAttr(each + '.stretchDamp', 10)
        mc.setAttr(each + '.trappedCheck', 1)
        mc.setAttr(each + '.selfTrappedCheck', 1)
        mc.setAttr(each + '.crossoverPush', 1)
        mc.setAttr(each + '.selfCrossoverPush', 1)
        mc.setAttr(each + '.restLengthScale', 1)
    mc.checkBox('restLengthScale', e=True, en=True, v=False)

def apply_values(arg=None):
    """Apply current UI values to all nCloth nodes in the scene.

    Reads values from UI fields (thickness, resistance, pressure, etc.) and
    applies them to all nCloth nodes. Handles rest length scale checkbox logic.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    n_cloth_list = mc.ls(type='nCloth', fl=True)
    for each in n_cloth_list:
        mc.setAttr(each + '.thickness', mc.floatField('clothThickness', q=True, v=True))
        mc.setAttr(each + '.stretchResistance', mc.intField('stretchResistance', q=True, v=True))
        mc.setAttr(each + '.rigidity', mc.floatField('rigidity', q=True, v=True))
        mc.setAttr(each + '.pressure', mc.intField('pressure', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOut', q=True, v=True))
        mc.setAttr(each + '.compressionResistance', 0)
        mc.setAttr(each + '.bendResistance', 0)
        mc.setAttr(each + '.lift', 0)
        mc.setAttr(each + '.drag', 2)
        mc.setAttr(each + '.tangentialDrag', 1)
        mc.setAttr(each + '.damp', 10)
        mc.setAttr(each + '.stretchDamp', 10)
        mc.setAttr(each + '.trappedCheck', 1)
        mc.setAttr(each + '.selfTrappedCheck', 1)
        mc.setAttr(each + '.crossoverPush', 1)
        mc.setAttr(each + '.selfCrossoverPush', 1)
        mc.setAttr(each + '.inputMotionDrag', 1)
        if mc.checkBox('restLengthScale', q=True, v=True):
            mc.setAttr(each + '.restLengthScale', 0)
        else:
            mc.setAttr(each + '.restLengthScale', 1)

        if mc.getAttr(each + '.pressure') > 0 and mc.getAttr(each + '.stretchResistance') < 2:
            mc.checkBox('restLengthScale', e=True, en=True)
        else:
            mc.checkBox('restLengthScale', e=True, en=False, v=False)
            mc.setAttr(each + '.restLengthScale', 1)

def apply_values_rigid(arg=None):
    """Apply current UI values to all nRigid nodes in the scene.

    Reads values from UI fields (thickness, push out, crossover push)
    and applies them to all nRigid nodes.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    n_rigid_list = mc.ls(type='nRigid', fl=True)
    for each in n_rigid_list:
        mc.setAttr(each + '.thickness', mc.floatField('rigidThickness', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOutRigid', q=True, v=True))
        mc.setAttr(each + '.crossoverPush', mc.intField('crossoverPushRigid', q=True, v=True))
        mc.setAttr(each + '.pushOutRadius', 1)

def clear_ncloth(arg=None):
    """Remove nCloth deformer from selected objects and clean up mesh history.

    Deletes nCloth nodes and intermediate mesh objects while preserving the
    original mesh geometry. Handles blendShape cleanup if present.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, fl=True)
    remove = []
    for each in sel:
        current_shapes = mc.listRelatives(each, type='mesh')
        if len(current_shapes) > 1 and not mc.getAttr(current_shapes[0] + '.intermediateObject'):
            mc.delete(mc.listConnections(current_shapes[0], type='nCloth'))
            mc.delete(current_shapes[1])
            remove.append(each)

    for each in remove:
        sel.remove(each)
    for each in sel:
        n_cloth_name = mc.listConnections(mc.listRelatives(each), type='nCloth')[0]
        input_mesh_name = mc.listRelatives(each)[0]

        if any('blendShape' in x for x in mc.listConnections(mc.listRelatives(each, c=True))):
            bs_delete = mc.listConnections(mc.listConnections(mc.listRelatives(each, c=True), type='blendShape')[0] +'.inputTarget')
            mc.delete(each, ch=True)
            mc.delete(bs_delete)
        else:
            mc.delete(each, ch=True)

        if mc.objExists(n_cloth_name):
            mc.delete(n_cloth_name)
            if mc.objExists(input_mesh_name):
                mc.delete(input_mesh_name)
            mc.rename(mc.listRelatives(each, c=True), input_mesh_name)
            mc.hyperShade(a='initialShadingGroup')
        else:
            mc.delete(input_mesh_name)
            mc.rename(mc.listRelatives(each, c=True), input_mesh_name)
            mc.hyperShade(a='initialShadingGroup')

def clear_nrigid(arg=None):
    """Remove nRigid passive collider from selected objects.

    Deletes nRigid nodes connected to selected objects and resets
    shading to initial shading group.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, fl=True)
    for each in sel:
        sel_children = mc.listRelatives(each, c=True)
        if len(sel_children) < 2:
            sel_connections = mc.listConnections(sel_children)
            for this in sel_connections:
                if 'nRigid' in this:
                    mc.delete(this)
                    mc.sets(sel, e=True, fe='initialShadingGroup')

def reset_ui(arg=None):
    """Refresh the muscle tool UI by recreating the window.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    muscle_tool()

def make_shaders():
    """Create muscle and rigid Lambert shaders for visualization.

    Creates two shaders: 'rigidLambert' (dark semi-transparent) and
    'muscleLambert' (pink) if they don't already exist.
    """
    shader_name = 'rigidLambert'
    if mc.objExists(shader_name) == 0:
        mc.shadingNode('lambert', asShader=True, n=shader_name)
        mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader_name + 'SG')
        mc.connectAttr(shader_name + '.outColor', shader_name + 'SG.surfaceShader', f=True)
    mc.setAttr(shader_name + '.color', 0.1, 0.1, 0.1)
    mc.setAttr(shader_name + '.transparency', 0.5, 0.5, 0.5)

    shader_name2 = 'muscleLambert'
    if mc.objExists(shader_name2) == 0:
        mc.shadingNode('lambert', asShader=True, n=shader_name2)
        mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader_name2 + 'SG')
        mc.connectAttr(shader_name2 + '.outColor', shader_name2 + 'SG.surfaceShader', f=True)
    mc.setAttr(shader_name2 + '.color', 1, .5, .5)

def make_rigid(arg=None):
    """Convert selected objects to nRigid passive colliders.

    Creates nRigid nodes for selected meshes with passive collider setup
    and applies rigid shader. Sets gravity to zero for simulation.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel_rigids = mc.ls(sl=True, fl=True)
    make_shaders()
    for this in sel_rigids:
        if len(mc.listRelatives(this)) > 1:
            sel_rigids.remove(this)
    make_passive_collider = 'makeCollideNCloth'
    nodes = mel.eval(make_passive_collider)
    for each in nodes:
        mc.setAttr('nRigid' + each.split('RigidShape')[1] + '.visibility', 0)
    nucleus_node = mc.ls(type='nucleus')
    if len(nucleus_node) > 1:
        mc.promptDialog(m='Use only one nucleus.  It\'s confusing...')
    mc.setAttr(nucleus_node[0] + '.gravity', 0)
    mc.select(sel_rigids)
    mc.sets(e=True, fe='rigidLambertSG')
    apply_values_rigid()

def make_muscle(arg=None):
    """Convert selected objects to nCloth muscle simulation objects.

    Creates nCloth nodes for selected meshes and applies muscle shader.
    Sets gravity to zero for simulation. Filters out objects with
    multiple connections.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel_muscles = mc.ls(sl=True, fl=True)
    make_shaders()
    for this in sel_muscles:
        if len(mc.listConnections(mc.listRelatives(this, c=True))) > 1:
            sel_muscles.remove(this)
    make_n_cloth = 'createNCloth 0;'
    nodes = mel.eval(make_n_cloth)
    for each in nodes:
        mc.setAttr('nCloth' + each.split('ClothShape')[1] + '.visibility', 0)
    nucleus_node = mc.ls(type='nucleus')
    if len(nucleus_node) > 1:
        mc.promptDialog(m='Use only one nucleus.  It\'s confusing...')
    mc.setAttr(nucleus_node[0] + '.gravity', 0)
    mc.select(sel_muscles)
    mc.sets(e=True, fe='muscleLambertSG')
    apply_values()

def reverse_normal(arg=None):
    """Reverse mesh normals for selected objects.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel_rigids = mc.ls(sl=True, fl=True)
    mc.polyNormal(sel_rigids, nm=0, unm=1, ch=0)

def select_nrigid(arg=None):
    """Select all mesh objects with nRigid deformers.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel_rigid = mc.ls(type='nRigid')
    sel = []
    for each in sel_rigid:
        con = mc.listConnections(each)
        sel.append(con[len(con)-1])
    mc.select(sel)

def select_ncloth(arg=None):
    """Select all mesh objects with nCloth deformers.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel_n_cloth = mc.ls(type='nCloth')
    sel = []
    for each in sel_n_cloth:
        con = mc.listConnections(each, type='mesh')
        sel.append(con[len(con)-2])
    mc.select(sel)

def relax_edges(arg=None):
    """Relax mesh edges on selected objects.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, o=True, fl=True)
    for each in sel:
        mc.polyMoveEdge(each, ch=0, ran=0, lc=0, lsx=0)
        mc.DeleteHistory()
    mc.select(sel)

def move_along_normal(arg=None):
    """Inflate mesh edges by moving vertices along surface normals.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, o=True, fl=True)
    for each in sel:
        mc.polyMoveVertex(each, ch=0, ran=0, ltz=.01)
        mc.DeleteHistory()
    mc.select(sel)

def time_reset(arg=None):
    """Reset timeline to frame 1.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    mc.currentTime(1)

def time_next(arg=None):
    """Advance timeline to next frame.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    mc.currentTime(mc.currentTime(q=True) +1)

def time_stop(arg=None):
    """Stop timeline playback.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    mc.play(st=False)

def time_play(arg=None):
    """Toggle timeline playback on/off.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    if mc.play(q=True, st=True):
        mc.play(st=False)
    else:
        mc.play(st=True)

def freeze_setup(arg=None):
    """Create blendShape weight painting setup for selected nCloth mesh.

    Creates a duplicate mesh with blendShape connection, enabling weight
    painting on cloth deformation.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    connections = mc.listConnections(mc.listRelatives(mc.ls(sl=True, fl=True)))

    if any('nCloth' in s for s in connections) and any('blendShape' not in k for k in connections):
        sel = mc.ls(sl=True, fl=True)
        for each in sel:
            bs = mc.duplicate(each)[0]
            mc.setAttr(bs + '.hiddenInOutliner', 1)
            mc.setAttr(bs + '.visibility', 0)
            bs_shapes = mc.listRelatives(bs, c=True)
            mc.delete(bs + '|' + bs_shapes[1])
            mc.setAttr(bs_shapes[0] + '.intermediateObject', 0)
            bs_node = mc.blendShape(bs, each)[0]
            mc.setAttr(bs_node + '.' + bs, 1)
        mc.select(sel)
        mc.ArtPaintBlendShapeWeightsTool(sel)

def paint_weight(arg=None):
    """Open blendShape weight painting tool for selected object.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    if mc.listConnections(mc.listRelatives(mc.ls(sl=True, fl=True))[0], type='blendShape') is not None:
        mc.ArtPaintBlendShapeWeightsTool()

def fix_shape_name(arg=None):
    """Rename mesh shape nodes to match their parent transform names.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, fl=True)
    for this in sel:
        shapes = mc.listRelatives(this, c=True)
        if len(shapes) >= 2:
            mc.warning('There are more than 1 shapes')
        else:
            for each in sel:
                mc.rename(mc.listRelatives(each, c=True)[0], each + 'Shape')

def toggle_io(arg=None):
    """Toggle intermediate object flag between two mesh shapes.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, fl=True)
    for each in sel:
        shapes = mc.listRelatives(each, c=True)
        if len(shapes) == 2:
            if mc.getAttr(shapes[0] + '.intermediateObject') == 1:
                mc.setAttr(shapes[0] + '.intermediateObject', 0)
                mc.setAttr(shapes[1] + '.intermediateObject', 1)
            else:
                mc.setAttr(shapes[0] + '.intermediateObject', 1)
                mc.setAttr(shapes[1] + '.intermediateObject', 0)

def delete_io(arg=None):
    """Delete intermediate object mesh shape from selected object.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, fl=True)[0]
    shapes = mc.listRelatives(sel, c=True)

    if len(shapes) == 2:
        if mc.getAttr(shapes[0] + '.intermediateObject') == 1:
            if mc.listConnections(shapes[0], type='nCloth') is not None:
                mc.delete(mc.listConnections(shapes[0], type='nCloth'))
                mc.delete(shapes[0])
            else:
                mc.delete(shapes[0])
        else:
            if mc.listConnections(shapes[0], type='nCloth') is not None:
                mc.delete(mc.listConnections(shapes[0], type='nCloth'))
                mc.delete(shapes[1])
            else:
                mc.delete(shapes[1])
        mc.rename(mc.listRelatives(sel, c=True)[0], sel + 'Shape')

def transform_constraint(arg=None):
    """Apply nConstraint transform to selected objects.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.ls(sl=True, o=True)
    mc.nConstraintTransform()
    mc.select(mc.listRelatives(sel, p=True))

def remove_constraint(arg=None):
    """Remove nConstraint components from selected objects.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    sel = mc.listRelatives(mc.ls(sl=True, fl=True), c=True, type='mesh')
    for each in sel:
        if not mc.getAttr(each + '.intermediateObject'):
            sel.remove(each)
    all_n_components = mc.ls(type='nComponent')
    for this in sel:
        for each in all_n_components:
            if mc.objExists(each):
                if this in mc.listHistory(each):
                    mc.delete(each)

def rest_length_scale_box(arg=None):
    """Update rest length scale value based on checkbox state.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    if mc.checkBox('restLengthScale', q=True, v=True):
        n_cloth_list = mc.ls(type='nCloth', fl=True)
        for each in n_cloth_list:
            mc.setAttr(each + '.restLengthScale', 0)
    else:
        n_cloth_list = mc.ls(type='nCloth', fl=True)
        for each in n_cloth_list:
            mc.setAttr(each + '.restLengthScale', 1)
    apply_values()

def muscle_tool(arg=None):
    """Create and display the muscle tool UI window.

    Creates a comprehensive muscle tool interface with nCloth, nRigid, skin,
    freeze, time, and shape management controls.

    Args:
        arg (None): Unused callback argument (optional for MEL button callbacks).
    """
    window_name = "Muscle_Tool"
    window_size = (310, 360)
    if mc.window(window_name, exists=True):
        mc.deleteUI(window_name)
    mc.window(window_name, title=window_name, widthHeight=(window_size[0], window_size[1]))

    mc.columnLayout( "mainColumn", adjustableColumn=True)

    mc.rowLayout(nc=3)
    mc.button(l='Make Rigid', w=100, bgc=(0,.3,0.2), c=make_rigid)
    mc.button(l='Remove nRigid', w=100, bgc=(.3,0,0), c=clear_nrigid)
    mc.button(l='Select Rigids', w=100, c=select_nrigid)
    mc.setParent('..')
    mc.rowLayout(nc=3)
    mc.button(l='Make Muscle', w=100, bgc=(0,.3,0.2), c=make_muscle)
    mc.button(l='Remove nCloth', w=100, bgc=(.3,0,0), c=clear_ncloth)
    mc.button(l='Select Cloths', w=100, c=select_ncloth)
    mc.setParent('..')

    mc.rowLayout(w=350, nc=2, rowAttach=(2, 'top', 0))
    mc.columnLayout()
    mc.text(l='---------------nCloth-----------')
    mc.button(l='Collision Solve Preset', c=apply_collision_solve_values)
    mc.button(l='Expand and Fill Preset', c=apply_fill_values)

    mc.rowLayout(nc=2)
    mc.floatField('clothThickness', v=.01, w=40, pre=3, min=0, cc=apply_values)
    mc.text(l='Thickness')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.intField('stretchResistance', v=20, w=40, min=0, cc=apply_values)
    mc.text(l='Stretch Resistance')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('rigidity', v=0, w=40, pre=1, min=0, cc=apply_values)
    mc.text(l='Rigidity')
    mc.setParent('..')

    mc.rowLayout(nc=3)
    mc.intField('pressure', v=0, w=40, cc=apply_values)
    mc.text(l='Pressure     ')
    mc.checkBox('restLengthScale', l='Alt', cc=rest_length_scale_box)
    if not mc.checkBox('restLengthScale', q=True, v=True):
        mc.checkBox('restLengthScale', e=True, en=False)
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('pushOut', v=1, w=40, pre=1, min=0, cc=apply_values)
    mc.text(l='Push Out')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.text(l='---------------nRigid------------')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('rigidThickness', v=.01, w=40, pre=3, min=0, cc=apply_values_rigid)
    mc.text(l='Rigid Thickness')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('pushOutRigid', v=1, w=40, pre=1, min=0, cc=apply_values_rigid)
    mc.text(l='Push Out')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.intField('crossoverPushRigid', v=1, w=40, min=0, cc=apply_values_rigid)
    mc.text(l='Crossover Push')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.text(l='------------------------------------')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.button(l='Relax Edges', c=relax_edges)
    mc.button(l='Inflate Edges', c=move_along_normal)
    mc.setParent('..')
    mc.setParent('..')


    mc.columnLayout()
    mc.text(l='---------------Skin-------------')
    mc.rowLayout(nc=1)
    mc.button(l='Reverse Normal', w=100, c=reverse_normal)
    mc.setParent('..')

    mc.columnLayout()
    mc.text(l='-------------Freeze-------------')
    mc.rowLayout(nc=2)
    mc.button(l=' BlendShape ', bgc=(.1,.4,.4), c=freeze_setup)
    mc.button(l=' Paint Weight ', bgc=(.1,.3,.3), c=paint_weight)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l=' Transform Constraint', bgc=(0,.3,0.2), c=transform_constraint)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l=' Remove Constraint', bgc=(.3,0,0), c=remove_constraint)
    mc.setParent('..')

    mc.columnLayout()
    mc.text(l='---------------Time-------------')
    mc.rowLayout(nc=2)
    mc.button(l='<<- RESET', c=time_reset)
    mc.button(l='NEXT FRAME >', bgc=(0,.5,0.3), c=time_next)
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button('playButton', l=' PLAY >> ', bgc=(0,.3,0.2), c=time_play)
    mc.button(l=' > STOP < ', bgc=(.3,0,0), c=time_stop)
    mc.setParent('..')

    mc.columnLayout()
    mc.text(l='-------------Shapes-------------')
    mc.rowLayout(nc=1)
    mc.button(l='Toggle Input/nCloth Mesh', bgc=(.1,.3,0.3), c=toggle_io)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l='Delete Intermediate Object', bgc=(.3,0,0), c=delete_io)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l='Fix Shape Name', bgc=(.2,.2,0.2), c=fix_shape_name)
    mc.setParent('..')

    mc.showWindow(window_name)
    mel.eval('$tmpVar=$gMainWindow')
    mc.window(window_name, edit=True, widthHeight=(window_size[0], window_size[1]))


muscle_tool()
