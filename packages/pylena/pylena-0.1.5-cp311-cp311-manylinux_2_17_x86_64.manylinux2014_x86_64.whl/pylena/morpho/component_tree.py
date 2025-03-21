from typing import Callable, Any, Tuple
from ..pylena_cxx import morpho as cxx
from ..utils import check_numpy_array
from dataclasses import dataclass

import numpy as np
from numba import jit


@jit(nopython=True)
def _compute_area(parent: np.ndarray, nodemap: np.ndarray):
    n = len(parent)
    A = np.zeros(n, dtype="int")
    for v in np.nditer(nodemap):
        A[v] += 1
    for i in range(n - 1, 0, -1):
        A[parent[i]] += A[i]
    return A


@jit(nopython=True)
def _filter(parent: np.ndarray, predicate: np.ndarray, values: np.ndarray, inplace):
    if not inplace:
        values = values.copy()
    n = len(parent)
    for i in range(1, n):
        if not predicate[i]:
            values[i] = values[parent[i]]
    return values


@jit(nopython=True)
def _compute_depth(parent: np.ndarray):
    n = len(parent)
    A = np.empty(n, dtype="int")
    A[0] = 0
    for i in range(1, n):
        A[i] = A[parent[i]] + 1
    return A


# @jit(nopython=False)
def _compute_attribute(parent: np.ndarray, nodemap: np.ndarray, fun: Callable, init_value):
    n = len(parent)
    A = np.empty(n, dtype=object)
    A.fill(init_value)
    it = np.nditer(nodemap, ["multi_index"])
    for v in it:
        A[v] = fun(A[v], it.multi_index)
    for i in range(n - 1, 0, -1):
        A[parent[i]] = fun(A[parent[i]], A[i])
    return A


@dataclass
class ComponentTree:
    """Tree representation of the inclusion of some connected components of an image (max-tree, min-tree, or tree of shapes)"""

    parent: np.ndarray
    values: np.ndarray
    nodemap: np.ndarray

    def compute_area(self) -> np.ndarray:
        """Compute the area attribute map of an image.

        Returns
        -------
        np.ndarray
            A mapping :math:`n \\to \\text{area}` which return the area of a node :math:`n`.

        Example
        -------
        >>> t = pln.morpho.tos(img)  # img is a (10, 10) image
        >>> area = t.compute_area()
        >>> area[0]  # 0 is the index of the root of the tree
        100
        """
        return _compute_area(self.parent, self.nodemap)

    def compute_depth(self) -> np.ndarray:
        """Compute the depth attribute map of an image.

        Returns
        -------
        np.ndarray
            A mapping :math:`n \\to \\text{depth}` which return the depth of a node :math:`n`.

        Example
        -------
        >>> t = pln.morpho.tos(img)
        >>> depth = t.compute_depth()
        >>> depth[0]  # 0 is the root, so its depth is 0
        0
        """
        return _compute_depth(self.parent)

    def compute_attribute(self, fun: Callable, init_value: Any) -> np.ndarray:
        """Compute an attribute using the callable object ``fun``

        Args
        ----
        fun: Callable
            A function ``fun(cur, arg)`` where ``cur`` is the value of the attribute of the current node and ``arg`` is the value taken for the current node.
        init_value: Any
            The value used to initialize the attribute

        Returns
        -------
        np.ndarray
            A mapping :math:`n \\to \\text{attr}` which return the attribute computed by ``fun`` for a node :math:`n`.

        Example
        -------
        >>> t = pln.morpho.tos(img)  # img is a (10, 10) image
        >>> def area_acc(cur: int, arg):
        ...     if isinstance(arg, tuple):  # Arg is a point of the nodemap
        ...         return cur + 1
        ...     return cur + arg  # Arg is the value of the mapping (here a child)
        >>> area = t.compute_attribute(area_acc, 0)  # area_acc is an accumulator function to compute the area
        >>> area[0]
        100
        """
        return _compute_attribute(self.parent, self.nodemap, fun, init_value)

    def filter(self, predicate: np.ndarray, values: np.ndarray = None, inplace=True) -> np.ndarray:
        """Filter (direct filtering rule) the tree based on a boolean predicate for each node.
        If **inplace**, the values array is modified inplace (a copy is returned otherwise).


        Args
        ----
        predicate: np.ndarray
            A boolean array that tells if a node as to be preserved or not.
        values: np.ndarray, optional
            The node values to filter. Defaults to ``self.values``.
        inplace: bool, optional
            Modify the values array or return a copy. Defaults to ``True``.

        Returns
        -------
        np.ndarray
            The filtered value array.

        Example
        -------
        >>> t = pln.morpho.tos(img)
        >>> area = t.compute_area()
        >>> t.filter(area >= 100)  # Remove all the nodes whose area is smaller than 100
        """
        if values is None:
            values = self.values
        return _filter(self.parent, predicate, values, inplace)

    def reconstruct(self, values: np.ndarray = None) -> np.ndarray:
        """Reconstruct an image from the values array.

        Args
        ----
        values: np.ndarray, optional
            Values of the nodes. Defaults is self.values.

        Returns
        -------
        np.ndarray
            The reconstructed image

        Example
        -------
        >>> t = pln.morpho.tos(img)
        >>> area = t.compute_area()
        >>> new_values = t.filter(area >= 100, inplace=False)
        >>> rec = t.reconstruct(new_values)
        """
        if values is None:
            values = self.values
        return values[self.nodemap]


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
def maxtree(img: np.ndarray, connectivity: int) -> ComponentTree:
    """Compute the max-tree :cite:p:`salembier.98.tip` of a 2D 8-bit image.

    Args
    ----
    img: np.ndarray
        The input image
    connectivity: int
        Input connectivity used to compute the maxt-tree (4 for 4-neighborhood or 8 for 8-neighborhood)

    Raises
    ------
    ValueError
        If the input connectivity is incorrect

    Returns
    -------
    ComponentTree
        The computed max-tree

    Example
    -------
    >>> import pylena as pln
    >>> t = pln.morpho.maxtree(img, 4)  # Compute the maxtree of an image using 4 connectivity.
    """
    if connectivity not in [4, 8]:
        raise ValueError(f"Connectivity should be 4 or 8 (not {connectivity})")
    tree, nodemap = cxx.maxtree(img, connectivity)
    return ComponentTree(tree.parent, tree.values, nodemap)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[3])
def maxtree3d(img: np.ndarray, connectivity: int) -> ComponentTree:
    """Compute the max-tree :cite:p:`salembier.98.tip` of a 3D 8-bit image.

    Args
    ----
    img: np.ndarray
        The input image
    connectivity: int
        Input connectivity used to compute the maxt-tree (6 for 6-neighborhood or 26 for 26-neighborhood)

    Raises
    ------
    ValueError
        If the input connectivity is incorrect

    Returns
    -------
    ComponentTree
        The computed max-tree

    Example
    -------
    >>> import pylena as pln
    >>> t = pln.morpho.maxtree3d(img, 6)  # Compute the maxtree of an image using 6 connectivity.
    """
    if connectivity not in [6, 26]:
        raise ValueError(f"Connectivity should be 6 or 26 (not {connectivity})")
    tree, nodemap = cxx.maxtree(img, connectivity)
    return ComponentTree(tree.parent, tree.values, nodemap)


def add_border_median(f: np.ndarray):
    if f.ndim == 2:
        m = np.median(np.concatenate([f[0, :], f[-1, :], f[:, 0], f[:, -1]]))
        return np.pad(f, [(1, 1), (1, 1)], mode="constant", constant_values=m)
    else:
        m = np.median(
            np.concatenate(
                [
                    f[0, :, :],
                    f[-1, :, :],
                    f[:, 0, :],
                    f[:, -1, :],
                    f[:, :, 0],
                    f[:, :, -1],
                ]
            )
        )
        return np.pad(f, [(1, 1), (1, 1), (1, 1)], mode="constant", constant_values=m)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
def tos(
    img: np.ndarray,
    root: Tuple = None,
    padding: str = None,
    subsampling: str = "original",
) -> ComponentTree:
    """Compute the tree of shapes :cite:p:`monasse.00.tip` of a 2D image in linear complexity :cite:p:`carlinet.18.icip`

    Args
    ----
    input: np.ndarray
        An 2D image with values encoded as 8 bits unsigned integer.
    root: Tuple, optional
        The root point of the tree (in the form ``(row, column)``) used as a starting point in the propagation. Defaults to None.
    padding: str, optional
        Add an extra border if not None. Defaults to None.
        Options available:

        * \"median\": Border with the median value of the original border

    subsampling: str, optional
        The size of the returned nodemap. Defaults to "original".
        Options available:

        * \"original\": The nodemap is returned with the same dimension as the original image.
        * \"full\": The nodemap is returned with the same dimension as in the Khalimsky space
        * \"full-no-border\": The nodemap is returned with the same dimension as in the Khalimsky space without border.

    Raises
    ------
    ValueError
        If an argument is invalid.

    Returns
    -------
    ComponentTree
        The component tree.

    Example
    -------
    >>> import pylena as pln
    >>> t = pln.morpho.tos(img, root=(0, 0), padding="median")
    """
    if padding is not None and padding not in ("median"):
        raise ValueError(f"Invalid argument {padding}")
    subsampling_mode = ["original", "full", "full-no-border"]
    if subsampling not in subsampling_mode:
        raise ValueError(f"Invalid argument {subsampling}. Not in {subsampling_mode}")

    if padding == "median":
        img = add_border_median(img)
        if root:
            root = (root[0] + 1, root[1] + 1)

    if root:
        if not isinstance(root, tuple) or len(root) != 2:
            raise ValueError("Invalid root point")
        root = (int(root[0]), int(root[1]))
    else:
        root = (0, 0)

    tree, nodemap = cxx.tos(img, root)
    if subsampling == "original":
        nodemap = nodemap[::2, ::2]
    if padding is not None and subsampling != "full":
        nodemap = nodemap[1:-1, 1:-1]
    return ComponentTree(tree.parent, tree.values, nodemap)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[3])
def tos3d(
    img: np.ndarray,
    root: Tuple = None,
    padding: str = None,
    subsampling: str = "original",
) -> ComponentTree:
    """Compute the tree of shapes :cite:p:`monasse.00.tip` of a 3D image in linear complexity :cite:p:`carlinet.18.icip`

    Args
    ----
    input: np.ndarray
        An 3D image with values encoded as 8 bits unsigned integer.
    root: Tuple, optional
        The root point of the tree (in the form ``(row, column, depth)``) used as a starting point in the propagation. Defaults to None.
    padding: str, optional
        Add an extra border if not None. Defaults to None.
        Options available:

        * \"median\": Border with the median value of the original border

    subsampling: str, optional
        The size of the returned nodemap. Defaults to "original".

    Raises
    ------
    ValueError
        If an argument is invalid.

    Returns
    -------
    ComponentTree
        The component tree.

    Example
    -------
    >>> import pylena as pln
    >>> t = pln.morpho.tos3d(img, root=(0, 0, 0), padding="median")
    """
    if padding is not None and padding not in ("median"):
        raise ValueError(f"Invalid argument {padding}")
    subsampling_mode = ["original", "full", "full-no-border"]
    if subsampling not in subsampling_mode:
        raise ValueError(f"Invalid argument {subsampling}. Not in {subsampling_mode}")

    if padding == "median":
        img = add_border_median(img)
        if root:
            root = (root[0] + 1, root[1] + 1, root[2] + 1)

    if root:
        if not isinstance(root, tuple) or len(root) != 3:
            raise ValueError("Invalid root point")
        root = (int(root[0]), int(root[1]), int(root[2]))
    else:
        root = (0, 0, 0)

    tree, nodemap = cxx.tos(img, root)
    if subsampling == "original":
        nodemap = nodemap[::2, ::2, ::2]
    if padding is not None and subsampling != "full":
        nodemap = nodemap[1:-1, 1:-1, 1:-1]
    return ComponentTree(tree.parent, tree.values, nodemap)
