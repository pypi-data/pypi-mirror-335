"""
Line detector
"""

from typing import Tuple, List, Union
from ..utils import check_numpy_array

from ..pylena_cxx import scribo as cxx
from ..pylena_cxx.scribo import (
    e_segdet_preprocess,
    e_segdet_process_traversal_mode,
    e_segdet_process_tracking,
    e_segdet_process_extraction,
)
from ..pylena_cxx.scribo import SegDetParams
from ..pylena_cxx.scribo import LSuperposition, VSegment

import numpy as np


def get_params(kwargs) -> Tuple[int, SegDetParams]:
    """
    Get the parameters for the line detection from the input arguments

    Return
    ------
    Tuple[int, SegDetParams]
        The minimum length of a line and the parameters for the line detection
    """
    min_len: int = kwargs.get("min_len", 10)

    params: SegDetParams = SegDetParams()
    params.preprocess = kwargs.get("preprocess", e_segdet_preprocess.NONE)
    params.tracker = kwargs.get("tracker", e_segdet_process_tracking.KALMAN)
    params.traversal_mode = kwargs.get("traversal_mode", e_segdet_process_traversal_mode.HORIZONTAL_VERTICAL)
    params.extraction_type = kwargs.get("extraction_type", e_segdet_process_extraction.BINARY)
    params.negate_image = kwargs.get("negate_image", False)
    params.dyn = kwargs.get("dyn", 0.6)
    params.size_mask = kwargs.get("size_mask", 11)
    params.double_exponential_alpha = kwargs.get("double_exponential_alpha", 0.6)
    params.simple_moving_average_memory = kwargs.get("simple_moving_average_memory", 30.0)
    params.exponential_moving_average_memory = kwargs.get("exponential_moving_average_memory", 16.0)
    params.one_euro_beta = kwargs.get("one_euro_beta", 0.007)
    params.one_euro_mincutoff = kwargs.get("one_euro_mincutoff", 1.0)
    params.one_euro_dcutoff = kwargs.get("one_euro_dcutoff", 1.0)
    params.bucket_size = kwargs.get("bucket_size", 32)
    params.nb_values_to_keep = kwargs.get("nb_values_to_keep", 30)
    params.discontinuity_relative = kwargs.get("discontinuity_relative", 0)
    params.discontinuity_absolute = kwargs.get("discontinuity_absolute", 0)
    params.minimum_for_fusion = kwargs.get("minimum_for_fusion", 15)
    params.default_sigma_position = kwargs.get("default_sigma_position", 2)
    params.default_sigma_thickness = kwargs.get("default_sigma_thickness", 2)
    params.default_sigma_luminosity = kwargs.get("default_sigma_luminosity", 57)
    params.min_nb_values_sigma = kwargs.get("min_nb_values_sigma", 10)
    params.sigma_pos_min = kwargs.get("sigma_pos_min", 1.0)
    params.sigma_thickness_min = kwargs.get("sigma_thickness_min", 0.64)
    params.sigma_luminosity_min = kwargs.get("sigma_luminosity_min", 13.0)
    params.gradient_threshold = kwargs.get("gradient_threshold", 30)
    params.llumi = kwargs.get("llumi", 225)
    params.blumi = kwargs.get("blumi", 225)
    params.ratio_lum = kwargs.get("ratio_lum", 1.0)
    params.max_thickness = kwargs.get("max_thickness", 100)
    params.threshold_intersection = kwargs.get("threshold_intersection", 0.8)
    params.remove_duplicates = kwargs.get("remove_duplicates", True)

    ret: Tuple[int, SegDetParams] = (min_len, params)

    return ret


@check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
def line_detector(
    img: np.ndarray, mode: str = "full", verbose: bool = False, **kwargs
) -> Union[
    List[VSegment],
    Tuple[np.ndarray, List[LSuperposition]],
    Tuple[np.ndarray, List[LSuperposition], List[VSegment]],
]:
    """
    Perform a line detection in a greyscale document image from :cite:p:`bernet.23.icdar`

    Args
    ----
    img: 2-D array (dtype=uint8)
        The image to be processed
    mode: str
        The mode of the line detection. Should be one of 'full', 'pixel' or 'vector'
    verbose: bool
        Whether to print information about the line detection
    **kwargs: Additional keyword arguments.

    Keyword Arguments:
        min_len (int, optional): The minimum length of a line.
            Default is 10.
        preprocess (e_segdet_preprocess, optional): Preprocess applied.
            Default is e_segdet_preprocess.NONE.
        tracker (e_segdet_process_tracking, optional): Tracker used.
            Default is e_segdet_process_tracking.KALMAN.
        traversal_mode (e_segdet_process_traversal_mode, optional): Traversal performed.
            Default is e_segdet_process_traversal_mode.HORIZONTAL_VERTICAL.
        extraction_type (e_segdet_process_extraction, optional): Extraction type for observations.
            Default is e_segdet_process_extraction.BINARY.
        negate_image (bool, optional): Specify if the image has to be reversed before processing.
            Default is False.
        dyn (float, optional): Dynamic when Black-Top-Hat preprocess is applied.
            Default is 0.6.
        size_mask (int, optional): Filter size when Black-Top-Hat preprocess is applied.
            Default is 11.
        double_exponential_alpha (float, optional): Alpha used in double exponential tracker if chosen.
            Default is 0.6.
        simple_moving_average_memory (float, optional): Memory used in simple moving average tracker if chosen.
            Default is 30.0.
        exponential_moving_average_memory (float, optional): Memory used in exponential moving average tracker if chosen.
            Default is 16.0.
        one_euro_beta (float, optional): Beta used in one euro tracker if chosen.
            Default is 0.007.
        one_euro_mincutoff (float, optional): Min cutoff used in one euro tracker if chosen.
            Default is 1.0.
        one_euro_dcutoff (float, optional): Dcutoff used in one euro tracker if chosen.
            Default is 1.0.
        bucket_size (int, optional): Bucket size during traversal.
            Default is 32.
        nb_values_to_keep (int, optional): Memory of tracker to compute variances for the matching.
            Default is 30.
        discontinuity_relative (int, optional): Percentage. Discontinuity = discontinuity_absolute +
            discontinuity_relative * current_segment_size.
            Default is 0.
        discontinuity_absolute (int, optional): Discontinuity = discontinuity_absolute +
            discontinuity_relative * current_segment_size.
            Default is 0.
        minimum_for_fusion (int, optional): Threshold to merge trackers following the same observation.
            Default is 15.
        default_sigma_position (int, optional): Position default variance value.
            Default is 2.
        default_sigma_thickness (int, optional): Thickness default variance value.
            Default is 2.
        default_sigma_luminosity (int, optional): Luminosity default variance value.
            Default is 57.
        min_nb_values_sigma (int, optional): Threshold to compute variance and not use default values.
            Default is 10.
        sigma_pos_min (float, optional): Minimum position variance value.
            Default is 1.0.
        sigma_thickness_min (float, optional): Minimum thickness variance value.
            Default is 0.64.
        sigma_luminosity_min (float, optional): Minimum luminosity variance value.
            Default is 13.0.
        gradient_threshold (int, optional): Gradient threshold when gradient preprocess is applied.
            Default is 30.
        llumi (int, optional): First threshold for observation ternary extraction.
            Default is 225.
        blumi (int, optional): Second threshold for observation ternary extraction.
            Default is 225.
        ratio_lum (float, optional): Ratio of kept luminosity in observation extraction.
            Default is 1.0.
        max_thickness (int, optional): Max allowed (vertical|horizontal) thickness of segment to detect.
            Default is 100.
        threshold_intersection (float, optional): Threshold for duplication removal.
            Default is 0.8.
        remove_duplicates (bool, optional): Specify if duplication removal has to be computed.
            Default is True.

    Return
    ------
    List[VSegment] or Tuple[np.ndarray, List[LSuperposition]] or Tuple[np.ndarray, List[LSuperposition], List[VSegment]]
        The detected lines in the image or the label map, the superpositions and the segments of the detected lines depending on the mode of the line detection (see `mode`).

    Example
    -------
    >>> from pylena.scribo import line_detector
    >>> img = ...  # Get an image
    >>> img_label, superpositions, lines = pln.scribo.line_detector(
    ...     img, "full", min_len=100, blumi=110, llumi=110, discontinuity_relative=5
    ... )
    """
    min_len: int
    params: SegDetParams

    min_len, params = get_params(kwargs)
    if verbose:
        print("min_len = {}".format(min_len))
        print("params = {}".format(params))

    if mode == "full":
        return cxx.line_detector_full(img, min_len, params)
    elif mode == "pixel":
        return cxx.line_detector_pixel(img, min_len, params)
    elif mode == "vector":
        return cxx.line_detector_vector(img, min_len, params)
    else:
        raise ValueError("Invalid mode. Should be one of 'full', 'pixel' or 'vector'")
