"""
# query scene unit:
maya_query_unit = cmds.currentUnit(query=True, linear=True)
# Result: 'cm'

# query scene unit (full name):
maya_query_unit = cmds.currentUnit(query=True, linear=True, fullName=True)
# Result: 'centimeter'


# set scene unit (full name):
maya_set_unit = cmds.currentUnit(linear="meter")
# Result: 'meter'
# or:
maya_set_unit = cmds.currentUnit(linear="m")
# Result: 'meter'


# get option var string value for 'workingUnitLinear':
maya_option_var_get_unit = cmds.optionVar(query="workingUnitLinear")
# Result: 'cm'

# set option var string value for 'workingUnitLinear':
cmds.optionVar(category="Settings", stringValue=("workingUnitLinear", "m"))

# and seved in pref file userPref.mel (-general: Save the general prefs to disk (optionVars)):
cmds.savePrefs(general=True)
# // Result: 1
# Saving preferences to : C:/Users/UserName/Documents/maya/2025/prefs/userPrefs.mel

# Result in file userPref.mel:
# ...
# // Settings
# optionVar -cat "Settings"
# -fv "positionalTolerance" 1e-08
# -sv "workingUnitLinear" "m"
# ;
# ...
"""

import maya.cmds as cmds


def get_scene_unit():
    """Returns the scene unit.

    Returns:
        str: The unit of length used in the scene.
    """
    return cmds.currentUnit(query=True, linear=True, fullName=True)


def set_scene_unit(unit="cm"):
    """Sets the scene unit.

    Args:
        unit (str): The unit of length to set in the scene.
    """
    # Set the current unit of length used in the scene.
    # This will affect all length parameters in the scene.
    # The unit must be one of the available units in Maya.
    # See the Maya documentation for the available units.
    cmds.currentUnit(linear=unit)


def get_option_var_unit():
    """Gets the option variable unit.

    Returns:
        str: The unit of length stored in the option variable 'workingUnitLinear'.
    """
    # Query the option variable 'workingUnitLinear' to get the current unit setting.
    return cmds.optionVar(query="workingUnitLinear")


def set_option_var_unit(unit="cm"):
    """Sets the option variable unit.

    This function sets the value of the Maya option variable
    'workingUnitLinear' to the given unit. The unit must be one of the
    available units in Maya. See the Maya documentation for the available
    units.

    Args:
        unit (str): The unit of length to set in the scene. Defaults to 'cm'.

    Returns:
        None
    """
    # Set the option variable 'workingUnitLinear' to the given unit.
    # This will affect the default unit used in the scene.
    # The unit must be one of the available units in Maya.
    # See the Maya documentation for the available units.
    cmds.optionVar(category="Settings", stringValue=("workingUnitLinear", unit))

    # Save the preferences so that the change is persistent.
    cmds.savePrefs(general=True)


def set_to_meter():
    """Sets the Maya scene unit and option variable unit to meters.

    This is a convenience function that sets the Maya scene unit to meters
    and the option variable 'workingUnitLinear' to 'm'. This is useful for
    setting the scene up to use meters as the unit of length.

    Returns:
        None
    """
    set_scene_unit("m")
    set_option_var_unit("m")


def set_to_cm():
    """Sets the Maya scene unit and option variable unit to centimeters.

    This is a convenience function that sets the Maya scene unit to
    centimeters and the option variable 'workingUnitLinear' to 'cm'.
    This is useful for setting the scene up to use centimeters as the unit
    of length.

    Returns:
        None
    """
    set_scene_unit("cm")
    set_option_var_unit("cm")
