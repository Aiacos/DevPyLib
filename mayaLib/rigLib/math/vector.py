import pymel.core as pm


def add(v1, v2, output, name=""):
    """Add two vectors using a plusMinusAverage node.

    Computes output = v1 + v2 using the translate attributes of the given transforms.

    Args:
        v1: First transform node.
        v2: Second transform node.
        output: Transform node to receive the resulting translation.
        name (str): Prefix for created node names.

    Returns:
        The plusMinusAverage node.
    """
    node = pm.shadingNode(
        "plusMinusAverage", asUtility=True, n=f"{name}_add_plusMinusAverage"
    )
    pm.setAttr(node.operation, 1)  # Sum

    pm.connectAttr(v1.translate, node.input3D[0], f=True)
    pm.connectAttr(v2.translate, node.input3D[1], f=True)
    pm.connectAttr(node.output3D, output.translate, f=True)

    return node


def subtract(v1, v2, output, name=""):
    """Subtract two vectors using a plusMinusAverage node.

    Computes output = v1 - v2 using the translate attributes of the given transforms.

    Args:
        v1: First transform node (minuend).
        v2: Second transform node (subtrahend).
        output: Transform node to receive the resulting translation.
        name (str): Prefix for created node names.

    Returns:
        The plusMinusAverage node.
    """
    node = pm.shadingNode(
        "plusMinusAverage", asUtility=True, n=f"{name}_sub_plusMinusAverage"
    )
    pm.setAttr(node.operation, 2)  # Subtract

    pm.connectAttr(v1.translate, node.input3D[0], f=True)
    pm.connectAttr(v2.translate, node.input3D[1], f=True)
    pm.connectAttr(node.output3D, output.translate, f=True)

    return node


def multiply(v1, v2, output, name=""):
    """Multiply two vectors component-wise using a multiplyDivide node.

    Computes output = (v1.x*v2.x, v1.y*v2.y, v1.z*v2.z).

    Args:
        v1: First transform node.
        v2: Second transform node.
        output: Transform node to receive the resulting translation.
        name (str): Prefix for created node names.

    Returns:
        The multiplyDivide node.
    """
    node = pm.shadingNode(
        "multiplyDivide", asUtility=True, n=f"{name}_mul_multiplyDivide"
    )
    pm.setAttr(node.operation, 1)  # Multiply

    pm.connectAttr(v1.translate, node.input1, f=True)
    pm.connectAttr(v2.translate, node.input2, f=True)
    pm.connectAttr(node.output, output.translate, f=True)

    return node


def midpoint(v1, v2, output, scale=0.5, name=""):
    """Compute a weighted midpoint between two transforms using Maya nodes.

    Builds a node network: result = v1 + (v2 - v1) * scale.
    When scale=0.5 (default), produces the exact midpoint.

    Args:
        v1: First transform node (start point).
        v2: Second transform node (end point).
        output: Transform node to receive the resulting translation.
        scale (float): Blend factor between v1 and v2. 0.0 = v1, 1.0 = v2.
        name (str): Prefix for created node names.
    """
    delta_node = pm.shadingNode(
        "plusMinusAverage", asUtility=True, n=f"{name}_delta_plusMinusAverage"
    )
    pm.setAttr(delta_node.operation, 2)  # Subtract: v2 - v1

    final_node = pm.shadingNode(
        "plusMinusAverage", asUtility=True, n=f"{name}_final_plusMinusAverage"
    )

    envelope_node = pm.shadingNode(
        "multiplyDivide", asUtility=True, n=f"{name}_envelope_multiplyDivide"
    )
    pm.setAttr(envelope_node.input2X, scale)
    pm.setAttr(envelope_node.input2Y, scale)
    pm.setAttr(envelope_node.input2Z, scale)

    # Delta: v2 - v1
    pm.connectAttr(v2.translate, delta_node.input3D[0], f=True)
    pm.connectAttr(v1.translate, delta_node.input3D[1], f=True)

    # Envelope: (v2 - v1) * scale
    pm.connectAttr(delta_node.output3D, envelope_node.input1, f=True)

    # Final: v1 + (v2 - v1) * scale
    pm.connectAttr(v1.translate, final_node.input3D[0], f=True)
    pm.connectAttr(envelope_node.output, final_node.input3D[1], f=True)

    pm.connectAttr(final_node.output3D, output.translate, f=True)


def length(v1, name=""):
    """Compute the length of a translation vector using a distanceBetween node.

    Measures the distance from the origin to v1.translate, which equals the
    vector length |v1|.

    Args:
        v1: Transform node whose translate represents the vector.
        name (str): Prefix for created node names.

    Returns:
        The distanceBetween node. Access the scalar result via node.distance.
    """
    node = pm.shadingNode(
        "distanceBetween", asUtility=True, n=f"{name}_len_distanceBetween"
    )

    # point1 defaults to (0,0,0) — distance from origin = vector length
    pm.connectAttr(v1.translate, node.point2, f=True)

    return node


def normalize(v1, output, name=""):
    """Normalize a vector using a vectorProduct node.

    Uses vectorProduct with operation=0 (No Operation) and normalizeOutput=True,
    which passes the input through and normalizes the result.

    Args:
        v1: Transform node whose translate represents the vector.
        output: Transform node to receive the normalized vector.
        name (str): Prefix for created node names.

    Returns:
        The vectorProduct node.
    """
    node = pm.shadingNode(
        "vectorProduct", asUtility=True, n=f"{name}_norm_vectorProduct"
    )
    pm.setAttr(node.operation, 0)  # No Operation (pass-through)
    pm.setAttr(node.normalizeOutput, True)

    pm.connectAttr(v1.translate, node.input1, f=True)
    pm.connectAttr(node.output, output.translate, f=True)

    return node


def dot_product(v1, v2, name=""):
    """Compute the dot product of two vectors using a vectorProduct node.

    The result is a scalar value accessible via node.outputX.

    Args:
        v1: First transform node.
        v2: Second transform node.
        name (str): Prefix for created node names.

    Returns:
        The vectorProduct node. Access the scalar result via node.outputX.
    """
    node = pm.shadingNode(
        "vectorProduct", asUtility=True, n=f"{name}_dot_vectorProduct"
    )
    pm.setAttr(node.operation, 1)  # Dot Product

    pm.connectAttr(v1.translate, node.input1, f=True)
    pm.connectAttr(v2.translate, node.input2, f=True)

    return node


def cross_product(v1, v2, output, name=""):
    """Compute the cross product of two vectors using a vectorProduct node.

    Computes output = v1 × v2, a vector perpendicular to both inputs.

    Args:
        v1: First transform node.
        v2: Second transform node.
        output: Transform node to receive the resulting vector.
        name (str): Prefix for created node names.

    Returns:
        The vectorProduct node.
    """
    node = pm.shadingNode(
        "vectorProduct", asUtility=True, n=f"{name}_cross_vectorProduct"
    )
    pm.setAttr(node.operation, 2)  # Cross Product

    pm.connectAttr(v1.translate, node.input1, f=True)
    pm.connectAttr(v2.translate, node.input2, f=True)
    pm.connectAttr(node.output, output.translate, f=True)

    return node
