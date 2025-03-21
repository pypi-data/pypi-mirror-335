"""
Dahu pseudo-distance based on the Tree of Shapes
"""

from numba import njit
import numpy as np

from typing import Optional, Iterable

from . import ComponentTree


@njit
def _dahu_distance_jit(parent: np.ndarray, values: np.ndarray, depth: np.ndarray, n1: int, n2: int) -> int:
    min_v = values[n1]
    max_v = values[n1]
    while depth[n1] < depth[n2]:
        max_v = max(max_v, values[n2])
        min_v = min(min_v, values[n2])
        n2 = parent[n2]
    while depth[n1] > depth[n2]:
        max_v = max(max_v, values[n1])
        min_v = min(min_v, values[n1])
        n1 = parent[n1]
    while n1 != n2:
        max_v = max(max_v, values[n1])
        min_v = min(min_v, values[n1])
        max_v = max(max_v, values[n2])
        min_v = min(min_v, values[n2])
        n1 = parent[n1]
        n2 = parent[n2]
    max_v = max(max_v, values[n1])
    min_v = min(min_v, values[n1])
    return max_v - min_v


def dahu_distance(t: ComponentTree, n1: int, n2: int, depth: Optional[np.ndarray] = None) -> np.number:
    """Compute the Dahu pseudo-distance :cite:p:`geraud.17.ismm` based on the Tree of Shapes (ToS)
    between two nodes `n1` and `n2`.

    For two nodes :math:`n_1` and :math:`n_2` belonging to a ToS :math:`\\mathfrak{G}`, the Dahu
    pseudo-distance :math:`d_{\\mathfrak{G}}^{DAHU}` is defined by:

    .. math::

        d_{\\mathfrak{G}}^{DAHU} = \\underset{n \\in \\widehat{\\pi}(n_1, n_2)}{\\text{max}} \\nu(n) - \\underset{n \\in \\widehat{\\pi}(n_1, n_2)}{\\text{min}} \\nu(n)

    with :math:`\\nu : \\mathfrak{G} \\rightarrow \\mathcal{V}` the mapping from a node of the ToS to its associated value
    and :math:`\\widehat{\\pi}(n_1, n_2) = (n_1, ..., \\text{lca}(n_1, n_2), ..., n_2)` the path in the ToS :math:`\\mathfrak{G}`
    between the nodes :math:`n_1` and :math:`n_2`.

    Args
    ----
    t: ComponentTree
        The input Tree of Shapes
    n1: int
        A node of the Tree of Shapes.
    n2: int
        A second node of the Tree of Shapes.
    depth: Optional[np.ndarray]
        The depth attribute of each node of the Tree of Shapes. This argument is
        optional and is computed if missing. However, for performance purposes,
        it is advised to compute it before computing the Dahu pseudo-distance
        several times.

    Returns
    -------
    np.ndarray
        The Dahu pseudo-distance between the two nodes `n1` and `n2`.

    Example
    -------
    >>> t = pln.morpho.tos(img)
    >>> depth = t.compute_depth()
    >>> d = dahu_distance(t, n1, n2, depth)
    """
    if depth is None:
        depth = t.compute_depth()
    return _dahu_distance_jit(t.parent, t.values, depth, n1, n2)


def _dahu_distance_map_jit(
    parent: np.ndarray, values: np.ndarray, depth: np.ndarray, seed_nodes: Iterable[int]
) -> np.ndarray:
    res = np.zeros_like(values)
    for n in range(parent.shape[0]):
        min_v = np.iinfo(values.dtype).max
        for n2 in seed_nodes:
            min_v = min(min_v, _dahu_distance_jit(parent, values, depth, n, n2))
        res[n] = min_v
    return res


def dahu_distance_map(
    t: ComponentTree,
    seed_nodes: Optional[Iterable[int]] = None,
    depth: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compute the distance map based on the Dahu pseudo-distance.

    For a set of seed nodes :math:`N` whose elements belong to a ToS :math:`\\mathfrak{G}`, the distance map
    :math:`D_{\\mathfrak{G}}^{DAHU}` computed using the Dahu pseudo-distance :math:`d_{\\mathfrak{G}}^{DAHU}`
    is defined by:

    .. math::

        D_{\\mathfrak{G}}^{DAHU}(n, N) = \\underset{n' \\in N}{\\text{min}}\\ d_{\\mathfrak{G}}^{DAHU}(n, n')

    for each node :math:`n \\in \\mathfrak{G}`. This function takes by default a set only containing the root node
    of the tree as described in :cite:p:`movn.20.cviu` to compute visual saliency detection.

    Args
    ----
    t: ComponentTree
        The input Tree of Shapes.
    seed_nodes: Optional[Iterable[int]]
        The set of seed nodes. If not provided, this set is initialized with the
        root.
    depth: Optional[np.ndarray]
        The depth attribute of the ToS.

    Returns
    -------
    np.ndarray
        The Dahu distance map.
    """
    if seed_nodes is None:
        seed_nodes = {0}
    if depth is None:
        depth = t.compute_depth()
    return _dahu_distance_map_jit(t.parent, t.values, depth, seed_nodes)
