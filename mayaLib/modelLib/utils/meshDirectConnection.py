import pymel.core as pm


def meshDirectConnection(source, destination):
    source = pm.ls(source)[0].getShape()
    destination = pm.ls(destination)[0].getShape()

    inBackUp = pm.listConnections(destination.inMesh, source=True, plugs=True)

    pm.connectAttr(source.outMesh, destination.inMesh, f=True)
    # pm.disconnectAttr(source.outMesh, destination.inMesh)

    if (len(inBackUp) > 0):
        # pass
        pm.connectAttr(inBackUp[0], destination.inMesh, f=True)


if __name__ == "__main__":
    meshDirectConnection(pm.ls(sl=True)[0], pm.ls(sl=True)[1])
