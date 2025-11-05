"""Deformer creation and weight painting utilities for Maya.

Provides tools for creating and manipulating various Maya deformers including
proximity wrap, blend shapes, shrink wrap, delta mush, wrap, soft mod, tension map,
and cMuscle systems. Also includes utilities for painting deformer weights,
inverting shapes, and managing deformer hierarchies.
"""

__author__ = "Lorenzo Argentieri"

from pathlib import Path

import maya.cmds as cmds
import maya.internal.nodes.proximitywrap.node_interface as node_interface
import pymel.core as pm
from maya import mel


def remove_shape_deformed():
    """
    Remove the suffix "Deformed" from all deformed geometry shape nodes.
    """
    # Get all deformed geometry shape nodes
    shape_deformed_node_list = pm.ls("*ShapeDeformed", "*:*ShapeDeformed")

    # Rename each shape node to remove the suffix
    for shape in shape_deformed_node_list:
        shape_old_name = str(shape.name())
        new_name = shape_old_name.replace("Deformed", "")
        pm.rename(shape, new_name)


def reorder_deformer(node, geo_list, search_type="skincluster"):
    """
    Reorder deformers on a list of geometry.

    Args:
        node (PyNode): The deformer node to reorder.
        geo_list (list): List of geometry to reorder deformers on.
        search_type (str): Type of deformer to search for. Defaults to "skincluster".

    """
    for geo in geo_list:
        # Get history of deformers on the geometry
        deformer_history_list = pm.listHistory(geo, type="ffd")
        # Reorder the last deformer in the history with the specified node
        pm.reorderDeformers(deformer_history_list[-1], node, geo)


def paint_deformer_weights(channel, vtx_list, value, smooth_iteration=1):
    """
    Paint deformer weights on selected vertices.

    Args:
        channel (str): Channel to paint weights on.
        vtx_list (list): List of vertices to paint weights on.
        value (float): Value to set weights to.
        smooth_iteration (int): Number of iterations to smooth the weights. Defaults to 1.

    Returns:
        None
    """
    # Set the channel to paint weights on
    mel.eval('artSetToolAndSelectAttr("artAttrCtx", "ffd.ffd1.weights");')

    # Select the vertices to paint weights on
    pm.select(vtx_list)

    # Set the value of the weights
    mel.eval("artAttrCtx -e -value " + str(value) + " `currentCtx`;")

    # Replace the weights with the set value
    mel.eval("artAttrPaintOperation artAttrCtx Replace;")

    # Clear the weights
    mel.eval("artAttrCtx -e -clear `currentCtx`;")

    # Smooth the weights
    for i in range(0, smooth_iteration):
        mel.eval("artAttrPaintOperation artAttrCtx Smooth;")
        mel.eval("artAttrCtx -e -clear `currentCtx`;")

    # Clear the selection
    pm.select(cl=True)


class PaintDeformer(object):
    def __init__(self, geo, channel):
        """Initialize the PaintDeformer tool on a specific geometry and channel.

        This sets up the painting tool for the specified geometry and channel
        by executing several MEL commands to configure the painting context.

        Args:
            geo (PyNode or str): The geometry to apply the painting tool on.
            channel (str): The attribute channel to paint weights on.
        """

        # Select the geometry to work with
        pm.select(geo)

        # Set the painting tool and select the attribute channel
        mel.eval('artSetToolAndSelectAttr("artAttrCtx", "' + channel + '");')

        # Initialize the paintable attributes
        mel.eval("artAttrInitPaintableAttr;")

        # Display the paint menu for attribute selection
        mel.eval('artAttrPaintMenu( "artAttrListPopupMenu" );')

        # Initialize attribute values in the paint context
        mel.eval("artAttrValues artAttrContext;")

        # Show tool properties
        mel.eval("toolPropertyShow;")

        # Trigger a context change for refresh
        mel.eval("dR_contextChanged;")

        # Set the current context
        mel.eval("currentCtx;")

        # mel.eval('changeSelectMode -component;')

    def select(self, vtx_list):
        """Selects the specified vertices.

        Args:
            vtx_list (list): List of vertices to select.
        """
        # Use pymel to select the vertices
        pm.select(vtx_list)

    def select_all(self):
        """Selects all vertices on the current geometry.

        Calls the Maya MEL command "SelectAll" to select all vertices on the
        current geometry.
        """
        mel.eval("SelectAll;")

    def invert_selection(self):
        """Invert the current selection.

        This method will invert the selection of components or objects
        in the scene using the Maya MEL command 'invertSelection'.
        """
        # Execute the MEL command to invert the current selection
        mel.eval("invertSelection;")

    def grow_selection(self, grow_selection):
        """Expand the current selection in the scene.

        This method grows the current selection by traversing
        the mesh components a specified number of times.

        Args:
            grow_selection (int): Number of times to grow the selection.
        """
        for _ in range(grow_selection):
            # Traverse and expand the current selection by one level
            mel.eval("select `ls -sl`;PolySelectTraverse 1;select `ls -sl`;")

    def replace(self, vtx_list, value):
        """Replace weights on selected vertices with a specified value.

        This method selects the given list of vertices and replaces their
        weights with the specified value using the Maya paint tool.

        Args:
            vtx_list (list): List of vertices to replace weights on.
            value (float): Value to set weights to.
        """
        # Select the vertices to modify
        pm.select(vtx_list)

        # Set the value for the current painting context
        mel.eval("artAttrCtx -e -value " + str(value) + " `currentCtx`;")

        mel.eval("artAttrPaintOperation artAttrCtx Replace;")
        mel.eval("artAttrCtx -e -clear `currentCtx`;")

    def smooth(self, smooth_iteration=1):
        """Smooths the weights of the selected vertices.

        Iterates the Maya paint tool's smooth operation a specified number of
        times to smooth the weights of the selected vertices.

        Args:
            smooth_iteration (int): Number of times to smooth the weights.
        """
        for _ in range(0, smooth_iteration):
            # Smooth the weights of the selected vertices
            mel.eval("artAttrPaintOperation artAttrCtx Smooth;")
            # Clear the current painting context
            mel.eval("artAttrCtx -e -clear `currentCtx`;")

    def __del__(self):
        """Clean up when the object is deleted."""
        # Clean up paint context
        mel.eval("setToolTo $gMove;")
        # Clean up selection
        pm.select(cl=True)


def add_meshes_to_deformer(obj_list, deformer):
    """
    Adds the given list of objects to the given deformer.

    Args:
        obj_list (list): List of objects (meshes) to add to the deformer.
        deformer (pm.nodetypes.Deformer): Deformer to add meshes to.
    """
    obj_list = pm.ls(obj_list)
    deformer = pm.ls(deformer)[-1]

    for obj in obj_list:
        pm.deformer(deformer, e=True, g=obj)


def add_meshes_to_wrap(obj_list, wrap_target):
    """
    Adds the specified list of objects to a wrap deformer with the given wrap target.

    This function selects the wrap target and the provided list of objects,
    and then executes a MEL command to add the objects as influences to the
    wrap deformer.

    Args:
        obj_list (list): List of objects to add to the wrap deformer.
        wrap_target (str): The wrap target object that the wrap deformer is applied to.

    Returns:
        None
    """

    for obj in obj_list:
        pm.select(wrap_target, r=True)
        pm.select(obj, add=True)
        mel.eval("AddWrapInfluence();")

        pm.select(cl=True)


def create_proximity_wrap(source, target_list):
    """
    Creates a proximity with the given source and target transforms.

    Args:
        source (pm.nodetypes.Transform): Transform with skinned mesh that will drive given target.
        target (pm.nodetypes.Transform): Transform with mesh shape that will be driven by given source.

    Returns:
        (pm.nodetypes.ProximityWrap): Proximity wrap node created.
    """
    # implementing with maya.cmds since PyMel raises the following warning for every attribute set.
    # Warning: pymel.core.general : Could not create desired MFn. Defaulting to MFnDependencyNode.
    target_names_list = [geo.name() for geo in pm.ls(target_list)]
    deformer = cmds.deformer(
        target_names_list,
        type="proximityWrap",
        name=pm.ls(target_list)[0].name(stripNamespace=True) + "_pWrap",
    )[0]

    proximity_interface = node_interface.NodeInterface(deformer)
    proximity_interface.addDriver(
        source.getShapes()[-1].name()
    )  # last shape should be the deformed shape

    return deformer


def blend_shape_deformer(
    base,
    blendshape_list,
    node_name,
    default_value=None,
    front_of_chain=False,
):
    """
    Create a blendshape deformer using the given parameters.

    Args:
        base: The base object.
        blendshape_list: A list of targets to add to the blendshape.
        node_name: The name of the blendshape deformer to create.
        default_value: The default weight values for the targets.
        front_of_chain: Whether to add the deformer to the front of the chain.

    Returns:
        The blendshape deformer created.
    """
    if default_value is None:
        default_value = [1.0]

    # Set the default weights
    w = (0, float(default_value[0]))
    if isinstance(blendshape_list, list):
        for i, df in zip(list(range(0, len(blendshape_list))), default_value):
            w = (i, float(df))

    # Create the blendshape deformer
    blendshape_node = pm.blendShape(
        blendshape_list, base, n=node_name, frontOfChain=front_of_chain, weight=w
    )

    return blendshape_node


def wrap_deformer(wrapped_objs, wrapper_obj):
    """
    Create a wrap deformer.

    Select all wrapped objects and the wrapper object.
    Then call the mel command to create a wrap deformer.

    Args:
        wrapped_objs (list): The objects to wrap.
        wrapper_obj (str): The wrapper object.

    Returns:
        The wrap deformer node.
    """
    # Select all wrapped objects and the wrapper object
    pm.select(wrapped_objs)
    pm.select(wrapper_obj, add=1)
    # Call the mel command to create a wrap deformer
    deformer_node = mel.eval(
        'doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" }'
    )
    return pm.ls(deformer_node)[0]


def delta_mush_deformer(geo, smoothing_iterations=10, smoothing_step=0.5):
    """Create a Delta Mush Deformer on the given geometry.

    Args:
        geo: The geometry to apply the deformer to.
        smoothing_iterations: Number of smoothing iterations.
        smoothing_step: Smoothing step.

    Returns:
        The deformer node.

    """
    deformer_node = pm.deltaMush(
        geo, smoothingIterations=smoothing_iterations, smoothingStep=smoothing_step
    )[0]
    return deformer_node


def shrink_wrap_deformer(wrapped_obj, wrapper_obj):
    """
    Apply Shrink Wrap Deformer to wrapped object. The deformer will deform the wrapped object
    to match the shape of the wrapper object.

    Args:
        wrapped_obj: The object to be wrapped.
        wrapper_obj: The object to wrap around.

    Returns:
        The deformer node.
    """
    shrink_wrap_node = pm.deformer(wrapped_obj, type="shrinkWrap")[0]
    # Set the target geometry of the deformer to the wrapper object
    pm.PyNode(wrapper_obj).worldMesh[0] >> shrink_wrap_node.targetGeom
    # Set the deformer to use the closest point on the wrapper object if no intersection is found
    shrink_wrap_node.closestIfNoIntersection.set(True)
    return shrink_wrap_node


def c_muscle_system_deformer(obj, relative_sticky=True):
    """Create a cMuscleSystem deformer on the given object.

    Args:
        obj: The geometry object to apply the deformer to.
        relative_sticky (bool): Whether to use a sticky muscle system.

    Returns:
        The deformer node.

    """
    deformer_node = None

    if relative_sticky:
        # Select the object and create a sticky muscle system
        pm.select(obj)
        d = mel.eval("cMuscle_makeMuscleSystem(1);")
        deformer_node = pm.ls(d)[0]
    else:
        # Create a regular cMuscleSystem deformer
        deformer_node = pm.deformer(obj, type="cMuscleSystem")[0]

    return deformer_node


def c_muscle_connect_muscle(muscle_main_obj, muscle_obj_list):
    """Connects the given muscle objects to the muscle system of the main muscle object.

    Selects the muscle objects and the main muscle object, then calls the mel command
    to connect them to the same muscle system.

    Args:
        muscle_main_obj (str): The name of the main muscle object.
        muscle_obj_list (list[str]): The list of muscle objects to connect to the main
            muscle object.
    """
    pm.select(muscle_obj_list)
    pm.select(muscle_main_obj, add=1)
    mel.eval("cMuscle_connectToSystem();")


def soft_mod_deformer(vertex):
    """Creates a softMod deformer on the given vertex.

    Selects the given vertex and creates a softMod deformer on it. The falloff
    masking attribute is set to 0.

    Args:
        vertex: The vertex object to create the deformer on.

    Returns:
        The deformer node.
    """
    # Select the vertex
    pm.select(vertex)

    # Create the softMod deformer
    deformer_node = pm.softMod(vertex)[0]

    # Set the falloff masking to 0
    deformer_node.falloffMasking.set(0)

    return deformer_node


def mesh_collision(deformer, deformed):
    """Create a Mesh Collision deformer on the given deformer object and apply it to the given deformed object.

    Selects the given deformer and deformed objects, then calls the mel command to create a mesh collision deformer.

    Args:
        deformer: The object to be deformed by the mesh collision deformer.
        deformed: The object to be deformed by the mesh collision deformer.

    Returns:
        The deformer node.
    """
    # Select the deformer and deformed objects
    deformer = pm.ls(deformer)[0]
    deformed = pm.ls(deformed)[0]

    pm.select(deformer)
    pm.select(deformed, add=1)

    # Call the mel command to create a mesh collision deformer
    mel.eval("collisionDeformer()")

    # Get the deformer node
    deformer_node = pm.listConnections(deformer.worldMesh[0], c=True, p=False)[-1][1]

    # Clear the selection
    pm.select(cl=True)

    return deformer_node


def tension_map(obj):
    """
    Create a Tension Map node to relax the input geometry of a mesh.

    The Tension Map node is connected to the original geometry of the mesh
    and the deformed geometry of the mesh. The output of the node is then
    connected to the input geometry of the mesh.

    Args:
        obj: The geometry object to apply the Tension Map to.

    Returns:
        The created Tension Map node.
    """

    # Check if the tensionMap plugin is loaded and active
    plugin_name = "tensionMap"
    if not pm.pluginInfo(plugin_name, q=True, loaded=True):
        try:
            # Attempt to load the plugin
            pm.loadPlugin("plugin/tensionMap.py")
            print(f"Plugin '{plugin_name}' loaded successfully.")
        except (RuntimeError, IOError) as e:
            print(f"Failed to load plugin '{plugin_name}': {e}")
            return None
    else:
        print(f"Plugin '{plugin_name}' is already loaded.")

    obj = pm.ls(obj)[-1]
    shape = obj.getShape()
    # Get the original geometry of the mesh
    shape_orig = pm.ls(str(shape.name()) + "Orig")[-1]
    # Get the deformed geometry of the mesh
    shape_input = pm.listConnections(
        shape.inMesh, source=True, destination=False, plugs=True
    )[-1]

    # Create Tension Map node
    tensionmap_node = pm.createNode("tensionMap")

    # Connect the original geometry to the input of the Tension Map node
    pm.connectAttr(shapeOrig.worldMesh[0], tensionmap_node.orig, f=True)
    # Connect the deformed geometry to the deform input of the Tension Map node
    pm.connectAttr(shape_input, tensionmap_node.deform, f=True)
    # Connect the output of the Tension Map node to the input geometry of the mesh
    pm.connectAttr(tensionmap_node.out, shape.inMesh, f=True)

    return tensionmap_node


def save_deformer_weights():
    """Save deformer weights for character geometry objects.

    Note:
        This function is incomplete. The JSON serialization is not implemented.
        Use mayaLib.utility.b_skin_saver module for skin weight operations instead.
    """
    # TODO: Implement JSON serialization of deformer weight data or deprecate this function
    geo_list = pm.ls(sl=True)
    if not geo_list:
        pm.warning("No objects selected!")
        return

    # weights folders
    directory = Path(cmds.file(q=True, sn=True)).parent / "weights/deformer"
    if not directory.exists():
        directory.mkdir(parents=True)

    for geo in geo_list:
        wt_file = directory / (geo.name() + ".json")
        wt_data = {}
        for deformer in pm.findDeformers(geo):
            wt_data[str(deformer)] = pm.getAttr(deformer + ".weightList")
        with wt_file.open("w"):
            pass
            # json.dump(wtData, f, indent=4)


def load_deformer_weights(
    geo_list,
    project_path=Path("/".join(cmds.file(q=True, sn=True).split("/")[:-1])),
    skin_weights_dir="weights/deformer",
):
    """
    load deformer weights for character geometry objects
    """
    # check folder
    directory = project_path / skin_weights_dir
    if not directory.exists():
        print("Path to load Deformer Weights not found!")
        return

    if not isinstance(geo_list, list):
        geo_list = pm.ls(geo_list)

    # weights folders
    wt_files = (project_path / skin_weights_dir).glob("*.json")

    # load skin weights
    for wt_file in wt_files:
        # check geometry list
        if geo_list and str(wt_file.stem) not in geo_list:
            continue

        # check if objects exist
        if not pm.objExists(str(wt_file.stem)):
            continue


def invert_shape(original_shape, targhet_shape, suffix="invertShape_"):
    """
    Inverts the shape of an object.

    This function will load the "invertShape" plugin if it is not already loaded.
    It will then use the invertShape command to invert the shape of the given
    object. The result will be a new shape node with the same name as the original
    shape node but with the given suffix added.

    Args:
        original_shape (str or pm.PyNode): The shape node to be inverted.
        targhet_shape (str or pm.PyNode): The shape node that the inverting shape
            will be subtracted from.
        suffix (str, optional): The suffix to add to the name of the result shape
            node. Defaults to "invertShape_".

    Returns:
        pm.PyNode: The resulting shape node.
    """
    plugin_name = "invertShape"

    # Check if the plugin is loaded
    if not pm.pluginInfo(plugin_name, query=True, loaded=True):
        try:
            # Attempt to load the plugin
            pm.loadPlugin(plugin_name)
            print(f"Plugin '{plugin_name}' loaded successfully.")
        except (RuntimeError, IOError) as e:
            print(f"Failed to load plugin '{plugin_name}': {e}")
            return None
    else:
        pass
        # print(f"Plugin '{plugin_name}' is already loaded.")

    original_shape = pm.PyNode(original_shape)
    targhet_shape = pm.PyNode(targhet_shape)
    shape_result = pm.invertShape(original_shape, targhet_shape)

    pm.sets("initialShadingGroup", e=True, forceElement=shape_result)

    pm.rename(shape_result, suffix + str(targhet_shape.name()).split("|")[-1])

    return suffix + str(targhet_shape.name()).split("|")[-1]


def generate_new_blendshspae(
    original, blendhspae_original_list, blendhspae_target, bs_name="reconstruction_BS"
):
    """
    Function to generate a new blendshape that combines the original shape with the
    other shapes in the blendhspae_original_list.

    Args:
        original (str or pm.PyNode): The original shape node.
        blendhspae_original_list (str or pm.PyNode): The list of original shapes to be
            combined in the new blendshape.
        blendhspae_target (str or pm.PyNode): The target shape to be deformed by the
            new blendshape.
        bs_name (str, optional): The name of the new blendshape node. Defaults to
            "reconstruction_BS".

    Returns:
        pm.PyNode: The new blendshape node.
    """
    original = pm.ls(original)[-1]
    blendhspae_original_list = pm.ls(blendhspae_original_list)
    blendhspae_target = pm.ls(blendhspae_target)[-1]

    bs_list = [original] + blendhspae_original_list

    out_bs = blend_shape_deformer(
        blendhspae_target,
        bs_list,
        bs_name,
        defaultValue=[-1] + [1 for _ in range(len(blendhspae_original_list) - 1)],
    )

    # The new blendshape will deform the target shape with the original shape
    # and the other shapes in the blendhspae_original_list.
    return out_bs


if __name__ == "__main__":
    pass
