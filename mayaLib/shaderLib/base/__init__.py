"""Base shader creation classes for different renderers.

Provides abstract base classes and concrete implementations for Arnold,
RenderMan, 3Delight, and texture management.
"""

from . import arnold
from . import renderman
from . import shader_base
from . import texture
