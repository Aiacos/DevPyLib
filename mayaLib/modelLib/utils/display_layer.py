"""Display layer management utilities.

Provides functions for creating and managing Maya display
layers for model organization.
"""

import pymel.core as pm


def list_all_display_layer():
    """Lists all display layers in the Maya scene, excluding the default layer.

    Returns:
        list: A list of display layer objects.
    """
    layer_list = pm.ls(type="displayLayer")[1:]
    return layer_list


def get_objects_in_display_layer(layer):
    """Retrieves objects contained within a specific display layer.

    Args:
        layer (str): The name of the display layer.

    Returns:
        list: A list of objects within the specified display layer.
    """
    return pm.ls(pm.editDisplayLayerMembers(layer, query=True))


if __name__ == "__main__":
    # Iterate over all display layers, set their color to 3, and print the objects they contain.
    for layer in list_all_display_layer():
        print(("Layer: ", layer.color.set(3)))
        print(get_objects_in_display_layer(layer))
