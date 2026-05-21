"""treecrown-nz: tools for measuring tree canopy and shaded walks."""

from .loader import (
    load_canopy,
    load_suburbs,
    canopy_coverage,
    route_shade,
)

__version__ = "0.1.0"

__all__ = [
    "load_canopy",
    "load_suburbs",
    "canopy_coverage",
    "route_shade",
]