import pymel.core as pm

def listAllDisplayLayer():
    """Lists all display layers in the Maya scene, excluding the default layer.

    Returns:
        list: A list of display layer objects.
    """
    layerList = pm.ls(type='displayLayer')[1:]
    return layerList

def getObjectsInDisplayLayer(layer):
    """Retrieves objects contained within a specific display layer.

    Args:
        layer (str): The name of the display layer.

    Returns:
        list: A list of objects within the specified display layer.
    """
    return pm.ls(pm.editDisplayLayerMembers(layer, query=True))

if __name__ == "__main__":
    # Iterate over all display layers, set their color to 3, and print the objects they contain.
    for layer in listAllDisplayLayer():
        print(('Layer: ', layer.color.set(3)))
        print((getObjectsInDisplayLayer(layer)))