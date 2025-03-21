import functools

import numpy as np


def check_type(func=None, ind=0, wanted_types=[]):
    """
    Decorator to check the type of an argument

    Args
    ----
    func
        The function to be decorated
    ind
        The index of the argument to be checked in the function
    wanted_types
        The accepted type for the argument

    Raise
    -----
    ValueError
        If `ind` is superior or equal to the number of argument or if the type is not accepted by the function

    Example
    -------
    .. code-block:: python

        @check_type(ind=0, wanted_types=[str])
        def foo(name):
            return "My name is {}".format(name)

    """

    def decorator(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            if ind >= len(args):
                raise ValueError("Missing argument in the function `{}`".format(func.__name__))
            input_type = type(args[ind])
            ok = False
            for wanted_type in wanted_types:
                if issubclass(input_type, wanted_type):
                    ok = True
            if not ok:
                raise ValueError(
                    "Function `{}`: argument at index {} should be of type `{}` (Got `{}`)".format(
                        func.__name__,
                        ind,
                        [wanted_type.__name__ for wanted_type in wanted_types],
                        input_type.__name__,
                    )
                )
            return func(*args, **kwargs)

        return wrap

    if func is None:
        return decorator
    return decorator(func)  # coverage: disable


def check_numpy_array(func=None, ind=0, dtypes=[], ndims=[]):
    """
    Decorator to check that the input numpy array dtype is accepted by a
    function

    Args
    ----
    func
        The function to be decorated
    ind
        The index of the argument in the function
    dtypes
        The list of accepted dtypes
    ndims
        The list of accepted number of dimensions

    Raise
    -----
    ValueError
        If `ind` is superior or equal to the number of argument, the
        argument pointed by `ind` is not a numpy array, if the dtype is not accepted
        or if the number of dimensions is incorrect.

    Example
    -------

    .. code-block:: python

        @check_numpy_array(ind=0, dtypes=[np.uint8], ndims=[2])
        def transpose_uint8(a):
            return a.T
    """

    def decorator(func):
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            if ind >= len(args):
                raise ValueError("Missing argument in the function `{}`".format(func.__name__))
            if not issubclass(type(args[ind]), np.ndarray):
                raise ValueError(
                    "Function `{}`: argument at index {} should be a `ndarray` (Got `{}`)".format(
                        func.__name__, ind, type(args[ind]).__name__
                    )
                )
            if args[ind].dtype not in dtypes:
                raise ValueError(
                    "Function `{}`: argument at index {} has invalid numpy dtype (Got {}, expected in {})".format(
                        func.__name__,
                        ind,
                        args[ind].dtype,
                        [d.__name__ for d in dtypes],
                    )
                )
            if args[ind].ndim not in ndims:
                raise ValueError(
                    "Function `{}`: argument at index {} has invalid number of dimension (Got {}, expected in {})".format(
                        func.__name__, ind, args[ind].ndim, ndims
                    )
                )
            return func(*args, **kwargs)

        return wrap

    if func is None:
        return decorator
    return decorator(func)  # coverage: disable
