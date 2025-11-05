"""Adds a gamma correct node to the selected file node.

This script is meant to be used in Maya as a Python script. It adds a gamma
correct node to the selected file node and connects it to the output of the
file node and the input of the shader.

"""

__author__ = 'Lorenzo Argentieri'

import maya.cmds as cmds
import pymel.core as pmc


def gamma_node():
    """Creates a gamma correct node.

    Returns:
        str: The name of the created node.
    """
    gamma = cmds.shadingNode("gammaCorrect", asUtility=True)
    cmds.setAttr(gamma + '.gammaX', 0.454)
    cmds.setAttr(gamma + '.gammaY', 0.454)
    cmds.setAttr(gamma + '.gammaZ', 0.454)
    return gamma


def gamma_node_pm():
    """Creates a gamma correct node using Pymel.

    Returns:
        Node: The created node.
    """
    gamma = pmc.shadingNode("gammaCorrect", asUtility=True)
    gamma.gammaX.set(0.454)
    gamma.gammaY.set(0.454)
    gamma.gammaZ.set(0.454)
    return gamma


def connect_gamma_pm(selection):
    """Connects the selected file node to a gamma correct node using Pymel.

    Args:
        selection (list[Node]): The selected file node.
    """
    # Find the source and destination
    source, destination = selection.connections(c=True, p=True)
    # Create the gamma node
    gamma = gamma_node_pm()
    # Connect the selected file node to the gamma node
    gamma.inColor >> source.outColor
    # Disconnect the file node from the shader
    destination.inColor // source.outColor
    # Connect the gamma node to the shader
    gamma.outColor >> destination.inColor


def connect_gamma(selection):
    """Connects the selected file node to a gamma correct node.

    Args:
        selection (str): The selected file node.
    """
    # Find where it is connected
    connection = cmds.listConnections('%s.outColor' % selection, p=True, d=True)
    # Create the gamma node
    gamma = gamma_node()
    # Connect the selected file node to the gamma node
    cmds.connectAttr('%s.outColor' % selection, '%s.value' % gamma)
    # Disconnect the file node from the shader
    cmds.disconnectAttr('%s.outColor' % selection, connection[0])
    # Connect the gamma node to the shader
    cmds.connectAttr('%s.value' % gamma, connection[0])


def add_gamma_correct():
    """Adds a gamma correct node to the selected file node."""
    # Select the file node to gamma correct
    selection = pmc.ls(sl=True)
    for node in selection:
        # Connect the gamma node
        connect_gamma_pm(node)


if __name__ == "__main__":
    add_gamma_correct()