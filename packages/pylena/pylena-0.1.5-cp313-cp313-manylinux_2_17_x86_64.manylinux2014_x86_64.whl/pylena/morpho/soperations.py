from ..pylena_cxx import morpho as cxx
from ..pylena_cxx.morpho import structuring_element_2d
from ..utils import check_numpy_array, check_type

from typing import Union

import numpy as np


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
@check_type(ind=1, wanted_types=[structuring_element_2d, np.ndarray])
def erosion(
    img: np.ndarray,
    se: Union[np.ndarray, structuring_element_2d],
    padding_value: int = None,
):
    """
    Performs an erosion by a structuring element.

    Given a structuring element :math:`B`, the erosion :math:`\\varepsilon(f)` of the input image
    :math:`f` is defined as

    .. math::

        \\varepsilon(f)(x) = \\bigwedge \\{f(y), y \\in B_x\\}

    Args
    ----
    img: 2-D array (dtype=uint8)
        The image to be processed
    se: structuring_element_2d or 2-D array
        The structuring element

    Return
    ------
    2-D array
        The resulting image

    Example
    -------

    >>> img = ...  # Get an image
    >>> from pylena.morpho import make_structuring_element_2d, erosion
    >>> se = make_structring_element_2d("rect", 10, 10)
    >>> out = erosion(img, se)
    """
    if issubclass(type(se), np.ndarray):
        if se.ndim != 2:
            raise ValueError("Structuring element should be a 2D array")
        se = se.astype(bool)
        se = structuring_element_2d(se)
    return cxx.erosion(img, se, padding_value)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
@check_type(ind=1, wanted_types=[structuring_element_2d, np.ndarray])
def dilation(
    img: np.ndarray,
    se: Union[np.ndarray, structuring_element_2d],
    padding_value: int = None,
):
    """
    Performs an dilation by a structuring element.

    Given a structuring element :math:`B`, the dilation :math:`\\delta(f)` of the input image
    :math:`f` is defined as

    .. math::

        \\delta(f)(x) = \\bigvee \\{f(y), y \\in B_x\\}

    Args
    ----
    img: 2-D array (dtype=uint8)
        The image to be processed
    se: structuring_element_2d or 2-D array
        The structuring element

    Return
    ------
    2-D array
        The resulting image

    Example
    -------

    >>> img = ...  # Get an image
    >>> from pylena.morpho import make_structuring_element_2d, dilation
    >>> se = make_structring_element_2d("rect", 10, 10)
    >>> out = dilation(img, se)
    """
    if issubclass(type(se), np.ndarray):
        if se.ndim != 2:
            raise ValueError("Structuring element should be a 2D array")
        se = se.astype(bool)
        se = structuring_element_2d(se)
    if padding_value is not None:
        padding_value = int(padding_value)
    return cxx.dilation(img, se, padding_value)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
@check_type(ind=1, wanted_types=[structuring_element_2d, np.ndarray])
def opening(
    img: np.ndarray,
    se: Union[np.ndarray, structuring_element_2d],
    padding_value: int = None,
):
    """
    Performs an opening by a structuring element.

    Given a structuring element :math:`B`, the dilation :math:`\\gamma(f)` of the input image
    :math:`f` is defined as

    .. math::

        \\gamma(f) = \\delta_{B}(\\varepsilon_{B}(f))

    Args
    ----
    img: 2-D array (dtype=uint8)
        The image to be processed
    se: structuring_element_2d or 2-D array
        The structuring element

    Return
    ------
    2-D array
        The resulting image

    Example
    -------

    >>> img = ...  # Get an image
    >>> from pylena.morpho import make_structuring_element_2d, opening
    >>> se = make_structring_element_2d("rect", 10, 10)
    >>> out = opening(img, se)
    """
    if issubclass(type(se), np.ndarray):
        if se.ndim != 2:
            raise ValueError("Structuring element should be a 2D array")
        se = se.astype(bool)
        se = structuring_element_2d(se)
    if padding_value is not None:
        padding_value = int(padding_value)
    return cxx.opening(img, se, padding_value)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
@check_type(ind=1, wanted_types=[structuring_element_2d, np.ndarray])
def closing(
    img: np.ndarray,
    se: Union[np.ndarray, structuring_element_2d],
    padding_value: int = None,
):
    """
    Performs an closing by a structuring element.

    Given a structuring element :math:`B`, the dilation :math:`\\gamma(f)` of the input image
    :math:`f` is defined as

    .. math::

        \\gamma(f) = \\varepsilon_{B}(\\delta_{B}(f))

    Args
    ----
    img: 2-D array (dtype=uint8)
        The image to be processed
    se: structuring_element_2d or 2-D array
        The structuring element

    Return
    ------
    2-D array
        The resulting image

    Example
    -------

    >>> img = ...  # Get an image
    >>> from pylena.morpho import make_structuring_element_2d, closing
    >>> se = make_structring_element_2d("rect", 10, 10)
    >>> out = closing(img, se)
    """
    if issubclass(type(se), np.ndarray):
        if se.ndim != 2:
            raise ValueError("Structuring element should be a 2D array")
        se = se.astype(bool)
        se = structuring_element_2d(se)
    if padding_value is not None:
        padding_value = int(padding_value)
    return cxx.closing(img, se, padding_value)


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
@check_type(ind=1, wanted_types=[structuring_element_2d, np.ndarray])
def gradient(
    img: np.ndarray,
    se: Union[np.ndarray, structuring_element_2d],
    padding_value: int = None,
):
    """
    Performs a morphological gradient, also called **Beucher** gradient.

    Given a structuring element :math:`B` and an image :math:`f`, the morphological gradient is defined as

    .. math::

        \\rho_B = \\delta_B - \\varepsilon_B

    Args
    ----
    img: 2-D array (dtype=uint8)
        The image to be processed
    se: structuring_element_2d or 2-D array
        The structuring element

    Return
    ------
    2-D array
        The resulting image

    Example
    -------

    >>> img = ...  # Get an image
    >>> from pylena.morpho import make_structuring_element_2d, gradient
    >>> se = make_structring_element_2d("rect", 10, 10)
    >>> out = gradient(img, se)
    """
    if issubclass(type(se), np.ndarray):
        if se.ndim != 2:
            raise ValueError("Structuring element should be a 2D array")
        se = se.astype(bool)
        se = structuring_element_2d(se)
    if padding_value is not None:
        padding_value = int(padding_value)  # coverage: disable
    return cxx.gradient(img, se, padding_value)
