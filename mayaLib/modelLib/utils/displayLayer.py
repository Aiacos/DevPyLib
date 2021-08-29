import pymel.core as pm


def listAllDisplayLayer():
    layerList = pm.ls(type='displayLayer')[1:]
    return layerList


def getObjectsInDisplayLayer(layer):
    return pm.ls(pm.editDisplayLayerMembers(layer, query=True))


if __name__ == "__main__":
    # layerEditorSelectObjects layer1;
    for layer in listAllDisplayLayer():
        print('Layer: ', layer.color.set(3))
        print(getObjectsInDisplayLayer(layer))
