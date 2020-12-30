"""
Test package for varana.detrend module.

"""
from os.path import realpath, split

import numpy as np
import pytest

from varana.detrend import set_interval, validate_nodes_number, load_data

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


@pytest.mark.parametrize(
    "start, stop, node_numbers, result",
    [(242.91, 1039.82, 10, 79.8), (1.23, 10.61, 20, 0.5), (981.35, 1121.20, 10, 14.1)],
)
def test_set_interval(start, stop, node_numbers, result):
    assert pytest.approx(set_interval(start, stop, node_numbers)) == result
