"""
Directly connect two meshes together without using an intermediate mesh.

This is useful when you want to directly connect a mesh to another mesh
without having to create a new mesh in between.

Example:
    meshDirectConnection(pm.ls(sl=True)[0], pm.ls(sl=True)[1])

Args:
    source (str or pm.PyNode): The source mesh.
    destination (str or pm.PyNode): The destination mesh.

Returns:
    None
"""
import pymel.core as pm

def meshDirectConnection(source, destination):
    """
    Connects the outMesh attribute of the source mesh directly to the inMesh attribute
    of the destination mesh, bypassing any intermediate meshes.

    This function is useful for directly connecting one mesh to another without creating
    a new mesh in between. It first backs up any existing connections to the destination's
    inMesh attribute. After making the direct connection, it restores any original connections
    if they exist.

    Args:
        source (str or pm.PyNode): The source mesh or its name.
        destination (str or pm.PyNode): The destination mesh or its name.

    Returns:
        None
    """
    source = pm.ls(source)[0].getShape()
    destination = pm.ls(destination)[0].getShape()

    # Store the original connections
    inBackUp = pm.listConnections(destination.inMesh, source=True, plugs=True)

    # Connect the source mesh to the destination mesh
    pm.connectAttr(source.outMesh, destination.inMesh, f=True)
    # pm.disconnectAttr(source.outMesh, destination.inMesh)

    # If there are any original connections, reconnect them
    if (len(inBackUp) > 0):
        # pass
        pm.connectAttr(inBackUp[0], destination.inMesh, f=True)


if __name__ == "__main__":
    meshDirectConnection(pm.ls(sl=True)[0], pm.ls(sl=True)[1])