"""
Structuring element
"""

from ..pylena_cxx.morpho import structuring_element_2d

from warnings import warn


def make_structuring_element_2d(kind, *args):
    """
    Compute a predifined structuring element. The morphological operations for
    these structuring elements have been optimized for their use.

    Three kinds of structuring element can be computed using this method:

    * 2-D rectangle
    * Disc
    * 2-D periodic line

    For these structuring elements, argument taken by the function are different.

    * 2-D rectangle

    The supplementary arguments are the width and the height

    >>> se = make_structuring_element_2d("rect", width, height)

    * Disc

    The supplementary argument is the radius of the disc

    >>> se = make_structuring_element_2d("disc", radius)

    * 2-D periodic line

    The supplementary argument are the period (represented by a tuple of int of size 2 corresponding to a point)
    and the half number of pixel in the line

    >>> se = make_structuring_element_2d("periodic_line", (2, 5), 10)

    Args
    ----
    kind:
        The structuring element to be computed.
    args:
        The parameters for the computation of a structuring element

    Return
    ------
    structuring_element_2d
        A structuring element

    Raise
    -----
    ValueError
        If the `kind` argument is incorrect or if the argument for the structuring element computation is incorrect.

    Example
    -------

    The following code sample show how to compute a rectangle structuring element

    >>> se = make_structuring_element_2d("rect", 10, 5)  # width=10 and height=5

    """
    if kind == "disc":
        if len(args) < 1:
            raise ValueError("Disc needs one argument (the radius)")
        if len(args) > 1:
            warn("The arguments after the radius will not be taken into account")
        return structuring_element_2d(float(args[0]))
    elif kind == "rect":
        if len(args) < 2:
            raise ValueError("Rect needs two arguments (the width and the height)")
        if len(args) > 2:
            warn("The arguments after the width and the height will not be taken into account")
        return structuring_element_2d(int(args[0]), int(args[1]))
    elif kind == "periodic_line":
        if len(args) < 2:
            raise ValueError("Periodic line: invalid number of argument")
        if (
            not isinstance(args[0], tuple)
            or len(args[0]) != 2
            or not isinstance(args[0][0], int)
            or not isinstance(args[0][1], int)
        ):
            raise ValueError("First argument for periodic line is a tuple of int of size 2")
        if len(args) > 2:
            warn("The arguments after the arguments will not be taken into account")
        return structuring_element_2d(args[0], int(args[1]))
    else:
        raise ValueError("Structuring element `{}` unknown".format(kind))
