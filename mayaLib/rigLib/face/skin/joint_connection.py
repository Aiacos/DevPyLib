"""Joint connection utilities for facial rigging.

This module provides functions for managing bind joint connections in facial rigs.
It allows detaching bind joints from rig controls (storing connection data on the
joints) and reattaching them later, which is useful for skin weight editing and
export workflows.

The connection data is stored as a pickled string attribute on each joint,
using UUID-based node identification for robust reconnection even after
scene modifications.

Example:
    Detach bind joints for weight editing::

        from mayaLib.rigLib.face.skin import joint_connection
        joint_connection.detach_bind_joints()
        # Edit skin weights...
        joint_connection.attach_bind_joints()

    Store custom data on a node::

        joint_connection.encode_data_to_attr(node, "my_data", {"key": "value"})
        data = joint_connection.decode_data_from_attr(node, "my_data")
"""

import logging

try:
    import cPickle as Pickle
except (ImportError, ModuleNotFoundError):
    import _pickle as Pickle

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)

# Default skin joint group pattern
DEFAULT_SKIN_JNT_GRP = "*facialRig_skinJnt_grp"

# Connection data attribute name
CONNECTION_ATTR_NAME = "connection_data"


def encode_data_to_attr(node, attr_name, data):
    """Dump Python data into a string attribute using pickle.

    Creates a locked string attribute on the node and stores the pickled
    representation of the data. Useful for storing connection information,
    custom data, or any serializable Python object on Maya nodes.

    Args:
        node: PyMEL node to store data on (pm.nt.DagNode).
        attr_name: Name of the attribute to create/update (str).
        data: Python object to store (must be pickle-serializable).

    Note:
        The attribute is locked after setting to prevent accidental
        modification. Use decode_data_from_attr() to retrieve the data.

    Example:
        >>> encode_data_to_attr(joint, "connection_data", [("nodeA", "tx")])
    """
    if not node.hasAttr(attr_name):
        node.addAttr(attr_name, dataType="string")

    pickled_data = Pickle.dumps(data)
    node.attr(attr_name).unlock()
    node.attr(attr_name).set(pickled_data)
    node.attr(attr_name).lock()


def decode_data_from_attr(node, attr_name):
    """Return Python data from a pickled string attribute.

    Retrieves and unpickles data stored by encode_data_to_attr().

    Args:
        node: PyMEL node to get data from (pm.nt.DagNode).
        attr_name: Name of the attribute containing the data (str).

    Returns:
        The unpickled Python object (list, dict, etc.).

    Raises:
        pm.MayaAttributeError: If the attribute does not exist on the node.

    Example:
        >>> data = decode_data_from_attr(joint, "connection_data")
        >>> print(data)
        [("nodeA_uuid", "tx"), ("nodeB_uuid", "ty")]
    """
    import pymel.all as pm

    if not node.hasAttr(attr_name):
        raise pm.MayaAttributeError(f"Attribute does not exist: {attr_name}")

    data = str(node.attr(attr_name).get())
    return Pickle.loads(data)


def detach_bind_joints(skin_jnt_grp=None):
    """Detach bind joints from rig by disconnecting and storing connections.

    For each joint in the skin joint group, stores all incoming connections
    as a custom attribute (using node UUIDs for robust reconnection) and
    then disconnects them. This allows the bind joints to be moved freely
    for skin weight editing.

    Args:
        skin_jnt_grp: Optional skin joint group pattern (str). If None, uses
            the default pattern "*facialRig_skinJnt_grp".

    Raises:
        pm.MayaObjectError: If the skin joint group does not exist.

    Note:
        The connection data is stored using encode_data_to_attr() and can
        be restored using attach_bind_joints().

    Example:
        >>> detach_bind_joints()  # Uses default group
        >>> detach_bind_joints("custom_skinJnt_grp")  # Custom group
    """
    import maya.cmds as cmds
    import pymel.all as pm

    if skin_jnt_grp is None:
        skin_jnt_grp = DEFAULT_SKIN_JNT_GRP

    if not pm.objExists(skin_jnt_grp):
        raise pm.MayaObjectError(f"Missing node: {skin_jnt_grp}")

    pm.select(skin_jnt_grp, replace=True)
    bind_joints = pm.selected()

    for joint in bind_joints:
        connected_plugs = joint.inputs(plugs=True, connections=True)
        ordered_plugs = []

        for i, (source, destination) in enumerate(connected_plugs):
            if i == 0:
                ordered_plugs.append((source, destination))
            else:
                ordered_plugs.append((destination, source))

        connection_data = []
        for incoming_plug, outgoing_plug in connected_plugs:
            incoming_node = incoming_plug.node()
            incoming_attr = incoming_plug.longName()
            outgoing_node = outgoing_plug.node()
            outgoing_attr = outgoing_plug.longName()

            # Use UUIDs for robust reconnection
            incoming_uuid = cmds.ls(incoming_node.name(), uuid=True)[0]
            outgoing_uuid = cmds.ls(outgoing_node.name(), uuid=True)[0]

            outgoing_node_attr = (outgoing_uuid, outgoing_attr)
            incoming_node_attr = (incoming_uuid, incoming_attr)

            connection_data.append((incoming_node_attr, outgoing_node_attr))
            outgoing_plug.disconnect(incoming_plug)

        encode_data_to_attr(joint, CONNECTION_ATTR_NAME, connection_data)

    logger.info("Bind joints detached!")


def attach_bind_joints():
    """Attach bind joints back to rig nodes using stored connection data.

    Finds all joints with stored connection data (from detach_bind_joints())
    and reconnects them to their original rig nodes using UUID-based node
    lookup for robust matching.

    Raises:
        RuntimeError: If no joints with connection data are found.

    Note:
        After successful reconnection, the connection_data attribute is
        removed from each joint.

    Example:
        >>> detach_bind_joints()
        >>> # ... edit skin weights ...
        >>> attach_bind_joints()
    """
    import pymel.all as pm

    all_joints = pm.ls(type=pm.nt.Joint)
    bind_joints = [
        joint for joint in all_joints if joint.hasAttr(CONNECTION_ATTR_NAME)
    ]

    if not bind_joints:
        raise RuntimeError(
            "No joints found to re-attach rig! Detach bind joints first!"
        )

    for joint in bind_joints:
        connection_data = decode_data_from_attr(joint, CONNECTION_ATTR_NAME)

        for incoming_data, outgoing_data in connection_data:
            # Look up nodes by UUID
            incoming_node = pm.ls(incoming_data[0])[0]
            incoming_attr = incoming_data[1]
            incoming_node_attr = incoming_node.attr(incoming_attr)

            outgoing_node = pm.ls(outgoing_data[0])[0]
            outgoing_attr = outgoing_data[1]
            destination_node_attr = outgoing_node.attr(outgoing_attr)

            # Only connect if not already connected
            if not destination_node_attr.isConnectedTo(incoming_node_attr):
                destination_node_attr.connect(incoming_node_attr)

        # Clean up the connection data attribute
        if joint.hasAttr(CONNECTION_ATTR_NAME):
            joint.attr(CONNECTION_ATTR_NAME).unlock()
            joint.deleteAttr(CONNECTION_ATTR_NAME)

    logger.info("Bind joints attached!")


def has_detached_connections():
    """Check if any joints have detached connection data.

    Returns:
        bool: True if any joints have stored connection data.
    """
    import pymel.all as pm

    all_joints = pm.ls(type=pm.nt.Joint)
    return any(joint.hasAttr(CONNECTION_ATTR_NAME) for joint in all_joints)


def get_detached_joints():
    """Get all joints that have stored connection data.

    Returns:
        list: List of PyNode joints with detached connections.
    """
    import pymel.all as pm

    all_joints = pm.ls(type=pm.nt.Joint)
    return [joint for joint in all_joints if joint.hasAttr(CONNECTION_ATTR_NAME)]


def get_connection_data(joint):
    """Get the stored connection data from a joint.

    Args:
        joint: PyMEL joint node.

    Returns:
        list: List of connection tuples, or None if no data exists.
    """
    import pymel.all as pm

    if isinstance(joint, str):
        joint = pm.PyNode(joint)

    if not joint.hasAttr(CONNECTION_ATTR_NAME):
        return None

    return decode_data_from_attr(joint, CONNECTION_ATTR_NAME)


def clear_connection_data(joint):
    """Clear stored connection data from a joint without reconnecting.

    Args:
        joint: PyMEL joint node.

    Returns:
        bool: True if data was cleared, False if no data existed.
    """
    import pymel.all as pm

    if isinstance(joint, str):
        joint = pm.PyNode(joint)

    if not joint.hasAttr(CONNECTION_ATTR_NAME):
        return False

    joint.attr(CONNECTION_ATTR_NAME).unlock()
    joint.deleteAttr(CONNECTION_ATTR_NAME)
    return True


def clear_all_connection_data():
    """Clear stored connection data from all joints without reconnecting.

    Returns:
        int: Number of joints cleared.
    """
    joints = get_detached_joints()
    count = 0

    for joint in joints:
        if clear_connection_data(joint):
            count += 1

    if count:
        logger.info("Cleared connection data from %d joints", count)

    return count


# Legacy function aliases for backward compatibility
# These maintain the original camelCase naming from facial3.py
detach_bind_joints_func = detach_bind_joints  # Direct reference
attach_bind_joints_func = attach_bind_joints  # Direct reference
encodeDataToAttr = encode_data_to_attr  # noqa: N816 - backward compat
decodeDataFromAttr = decode_data_from_attr  # noqa: N816 - backward compat
hasDetachedConnections = has_detached_connections  # noqa: N816 - backward compat
getDetachedJoints = get_detached_joints  # noqa: N816 - backward compat
getConnectionData = get_connection_data  # noqa: N816 - backward compat
clearConnectionData = clear_connection_data  # noqa: N816 - backward compat
clearAllConnectionData = clear_all_connection_data  # noqa: N816 - backward compat

# Module-level exports
__all__ = [
    # Constants
    "DEFAULT_SKIN_JNT_GRP",
    "CONNECTION_ATTR_NAME",
    # Primary API (snake_case)
    "encode_data_to_attr",
    "decode_data_from_attr",
    "detach_bind_joints",
    "attach_bind_joints",
    "has_detached_connections",
    "get_detached_joints",
    "get_connection_data",
    "clear_connection_data",
    "clear_all_connection_data",
    # Legacy API (camelCase) for backward compatibility
    "encodeDataToAttr",
    "decodeDataFromAttr",
    "hasDetachedConnections",
    "getDetachedJoints",
    "getConnectionData",
    "clearConnectionData",
    "clearAllConnectionData",
]
