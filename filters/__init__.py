"""
Filters Package
"""

from .base_filters import FILTER_MAP as BASE_FILTERS
from .edge_filters import FILTER_MAP as EDGE_FILTERS
from .convolution_filters import FILTER_MAP as CONV_FILTERS
from .photogrammetry import FILTER_MAP as PHOTO_FILTERS
from .creative_filters import FILTER_MAP as CREATIVE_FILTERS
from .color_filters import FILTER_MAP as COLOR_FILTERS
from .transformation_filters import FILTER_MAP as TRANSFORM_FILTERS

__all__ = [
    "BASE_FILTERS",
    "EDGE_FILTERS",
    "CONV_FILTERS",
    "PHOTO_FILTERS",
    "CREATIVE_FILTERS",
    "COLOR_FILTERS",
    "TRANSFORM_FILTERS",
]
