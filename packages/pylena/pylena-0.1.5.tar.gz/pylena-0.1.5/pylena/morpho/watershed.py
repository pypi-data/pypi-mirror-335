import numpy as np

from typing import Tuple, Optional

from ..pylena_cxx import morpho as cxx
from ..utils import check_numpy_array


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
def watershed(
    img: np.ndarray,
    connectivity: int,
    waterline: bool = True,
    markers: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, int]:
    """
    Performs a Watershed segmentation using the Meyer's Watershed algorithm :cite:p:`meyer.91.rfia` on an image ``img``
    using the neighborhood relationship ``connectivity``.

    Args
    ----
    img: 2-D array (dtype=uint8)
        The input image
    connectivity: int
        The connectivity used by the watershed. Should be 4 (for 4-connectivity) or 8 (for 8-connectivity)
    waterline: bool
        Boolean to either display the watershed lines or
    markers: Optional[np.ndarray]
        Optional image (dtype=int16) representing the input markers. In this case, the watershed is computed from
        markers and not from local minima and it returns the watershed segmentation from this markers with watershed
        lines (``waterline`` argument is ignored in this case)

    Returns
    -------
    Tuple[np.ndarray, int]
        The resulting segmentation

    Raises
    ------
    ValueError
        If the connectivity is invalid or the input image is not & 2-D array with values encoded as uint8 value
    """
    if connectivity not in (4, 8):
        raise ValueError(f"Input connectivity should be 4 or 8 (Got {connectivity}")

    if markers is None:
        return cxx.watershed(img, connectivity, waterline)
    else:
        if markers.shape != img.shape or markers.dtype != np.int16:
            raise ValueError(
                f"Markers image should be an image with the same shape as the input image with value encoded in int16 (Got markers shape: {markers.ndim}, dtype: {markers.dtype})"
            )
        return cxx.watershed_from_markers(img, markers, connectivity)
