"""
Mathematical morphology
"""

from .se import make_structuring_element_2d
from .soperations import gradient, erosion, dilation, opening, closing
from .component_tree import maxtree, maxtree3d, tos, tos3d, ComponentTree
from .watershed import watershed
from ._dahu import dahu_distance, dahu_distance_map

__all__ = [
    "make_structuring_element_2d",
    "erosion",
    "dilation",
    "opening",
    "closing",
    "gradient",
    "maxtree",
    "maxtree3d",
    "ComponentTree",
    "tos",
    "tos3d",
    "watershed",
    "dahu_distance",
    "dahu_distance_map",
]
