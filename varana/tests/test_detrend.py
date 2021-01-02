"""
Test package for varana.detrend module.

"""
from os.path import realpath, split

import numpy as np
import pytest

from varana.detrend import (
    validate_nodes_number,
    load_data,
    sigma_clipping_magnitude,
    too_many_points_rejected,
)

test_data_dir_path = split(realpath(__file__))[0]
synthetic_lc_path = test_data_dir_path + r"/test_data/synthetic_lc.dat"


def test_load_data():
    time, brightness, errors = load_data(synthetic_lc_path)
    time_result = np.array([165.445448, 166.264696, 166.947026, 167.665380, 168.527654])
    brightness_result = np.array([-0.37832, 1.71500, 0.52351, -0.45549, 1.35745])
    errors_result = np.array([0.00067, 0.00072, 0.00051, 0.00108, 0.00085])

    for i in (time, brightness, errors):
        assert i.shape == (1000,)
    np.testing.assert_allclose(time[:5], time_result)
    np.testing.assert_allclose(brightness[:5], brightness_result)
    np.testing.assert_allclose(errors[:5], errors_result)


@pytest.mark.parametrize("nodes_number", [2, 3, 4, 12, 95])
def test_validate_nodes_number(nodes_number):
    assert validate_nodes_number(nodes_number) == nodes_number


@pytest.mark.parametrize("nodes_number", [-1, 0, 1])
def test_validate_nodes_number_exception(nodes_number):
    with pytest.raises(ValueError, match="At least 2 nodes are required to detrend data"):
        validate_nodes_number(nodes_number)


def test_sigma_clipping_magnitude():
    data = load_data(synthetic_lc_path)
    out_mag = np.array([-3.67704, 3.33428])
    out_idx = np.where(np.in1d(data[1], out_mag) == True)

    trim_data = sigma_clipping_magnitude(data)

    for i in range(3):
        np.testing.assert_allclose(np.delete(data[i], out_idx), trim_data[i])


@pytest.mark.parametrize("value", [96, 97, 98, 99, 100])
def test_too_many_points_rejected(value):
    too_many_points_rejected("object.dat", 100, value)


@pytest.mark.parametrize("value", [0, 1, 50, 90, 94, 95])
def test_too_many_points_rejected_exception(value):
    filename = "object.dat"
    with pytest.raises(ValueError, match=f"Rejected too many points from {filename}"):
        too_many_points_rejected(filename, 100, value)
