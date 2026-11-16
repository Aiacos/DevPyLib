"""
Core module containing base classes and configuration.
"""

from .base import FacialComponent
from .config import ColorScheme, FacialRigConfig, FitData
from .fitting import FacialFitting, FitRegion, FittingUI, FitType
from .hierarchy import HierarchyManager
from .naming import NamingConvention, Side
