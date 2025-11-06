"""Ziva VFX integration tools for tissue and muscle simulation.

Provides utilities for working with Ziva VFX dynamics including fiber
creation, attachment tools, and general Ziva workflow helpers.
Maya 2022+ only.
"""

import pymel.core as pm

if pm.about(version=True) == "2022":
    from . import ziva_attachments_tools, ziva_fiber_tools, ziva_tools
