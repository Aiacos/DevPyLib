"""Character rigging framework for Maya.

Provides a comprehensive rigging system including base modules for limbs,
spine, neck, and face, as well as specialized systems for Ziva VFX,
AdonisFX, cloth simulation, and a rich collection of rigging utilities.
"""

from . import (
    Ziva,
    base,
    cloth,
    core,
    facial_rig,
    matrix,
    orient_ctrl,
    set_muscle_weight,
    utils,
)
