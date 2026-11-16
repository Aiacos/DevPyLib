"""
Facial rig components module.

Each component represents a specific facial region that can be
built independently or as part of the complete facial rig.

Components:
    EyeComponent: Eye aim and tracking
    EyeLidComponent: Eyelid deformation and blink
    EyeBrowComponent: Eyebrow controls and deformation
    LipComponent: Lip ribbon setup and controls
    JawComponent: Jaw rotation and sliding
    CheekComponent: Cheek deformation
    NoseComponent: Nose and nostril controls
    TongueComponent: Tongue FK chain
    ForeheadComponent: Forehead deformation
    ARKitComponent: Apple ARKit 52 blendshape support
"""

from .arkit import ARKitComponent, connect_arkit_source, create_arkit_blendshapes
from .cheek import CheekComponent
from .eye import EyeComponent
from .eyebrow import EyeBrowComponent
from .eyelid import EyeLidComponent
from .forehead import ForeheadComponent
from .jaw import JawComponent
from .lip import LipComponent
from .nose import NoseComponent
from .tongue import TongueComponent

__all__ = [
    "EyeLidComponent",
    "LipComponent",
    "EyeBrowComponent",
    "EyeComponent",
    "JawComponent",
    "CheekComponent",
    "NoseComponent",
    "TongueComponent",
    "ForeheadComponent",
    "ARKitComponent",
    "create_arkit_blendshapes",
    "connect_arkit_source",
]
