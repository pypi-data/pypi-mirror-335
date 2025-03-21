import numpy as np

import pytest

from pylena import check_numpy_array, check_type


@check_type(ind=0, wanted_types=[float, int, np.ndarray])
def _func_check_type(a):
    return a + 1


@check_type(ind=1)
def _func2_check_type(a):
    return "error"


@check_numpy_array(ind=0, dtypes=[np.uint8, np.int16], ndims=[2, 3])
def _func_check_numpy_array(tab):
    return


@check_numpy_array(ind=1, dtypes=[np.uint8, np.uint16], ndims=[2])
def _func2_check_numpy_array(tab):
    return


def test_check_type():
    _func_check_type(float(1))
    _func_check_type(10)
    _func_check_type(np.ones((5,)))
    with pytest.raises(ValueError):
        _func_check_type((1, 2))
    with pytest.raises(ValueError):
        _func2_check_type(10)
    assert True


def test_check_numpy_array():
    _func_check_numpy_array(np.zeros((3, 3), dtype=np.uint8))
    _func_check_numpy_array(np.zeros((3, 3), dtype=np.int16))
    _func_check_numpy_array(np.zeros((3, 3, 3), dtype=np.uint8))
    _func_check_numpy_array(np.zeros((3, 3, 3), dtype=np.int16))
    with pytest.raises(ValueError):
        _func_check_numpy_array(np.zeros((3, 3), dtype=np.uint16))
    with pytest.raises(ValueError):
        _func_check_numpy_array(np.zeros((3, 3, 3, 3), dtype=np.uint8))
    with pytest.raises(ValueError):
        _func_check_numpy_array(np.zeros((3,), dtype=np.int16))
    with pytest.raises(ValueError):
        _func2_check_numpy_array(np.zeros((3, 3), dtype=np.uint8))
    with pytest.raises(ValueError):
        _func_check_numpy_array("tata")
    assert True
