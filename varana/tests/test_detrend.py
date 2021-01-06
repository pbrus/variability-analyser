"""
Test package for varana.detrend module.

"""
from os.path import realpath, split

import numpy as np
import pytest

from varana.detrend import (
    _calculate_intervals_for_nodes,
    calculate_nodes_positions,
    load_data,
    sigma_clipping_magnitude,
    split_filename,
    too_many_points_rejected,
    validate_nodes_number,
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


@pytest.mark.parametrize(
    "start, stop, nodes, result",
    [
        (1.0, 10.0, 3, [1.0, 4.0, 7.0, 10.0]),
        (1.0, 10.0, 2, [1.0, 5.5, 10.0]),
        (0.0, 20.0, 4, [0.0, 5.0, 10.0, 15.0, 20.0]),
        (20.0, 29.0, 3, [20.0, 23.0, 26.0, 29.0]),
        (49.5, 51.5, 5, [49.5, 49.9, 50.3, 50.7, 51.1, 51.5]),
        (1.0, 4.0, 5, [1.0, 1.6, 2.2, 2.8, 3.4, 4.0]),
    ],
)
def test_calculate_intervals_for_nodes(start, stop, nodes, result):
    intervals = _calculate_intervals_for_nodes(start, stop, nodes)
    np.testing.assert_allclose(intervals, np.array(result))


@pytest.mark.parametrize(
    "nodes, result_x, result_y",
    [(2, np.array([3.0, 8.0]), np.array([-0.8, -2.6])), (3, np.array([2.0, 5.0, 8.5]), np.array([-1.0, -2.0, -2.0]))],
)
def test_calculate_nodes_positions(nodes, result_x, result_y):
    x = np.linspace(1, 10, num=10)
    y = np.array([-2, -4, 3, -5, 4, -5, 2, -2, -5, -3])

    positions = calculate_nodes_positions(x, y, nodes)
    np.testing.assert_allclose(positions[:, 0], result_x)
    np.testing.assert_allclose(positions[:, 1], result_y)


@pytest.mark.parametrize(
    "nodes, result_x, result_y",
    [
        (
            5,
            np.array([1.7399999999999998, 4.35, 5.4799999999999995, 6.8, 9.080000000000002]),
            np.array([2.2, -4.5, 3.6, 5.0, 4.8]),
        ),
        (
            6,
            np.array([1.7399999999999998, 4.699999999999999, 6.0249999999999995, 9.080000000000002]),
            np.array([2.2, -3.25, 6.75, 4.8]),
        ),
    ],
)
def test_calculate_nodes_positions_with_gaps(nodes, result_x, result_y):
    x = np.array([1.2, 1.5, 1.7, 2.0, 2.3, 4.2, 4.5, 5.0, 5.1, 5.5, 5.7, 6.1, 6.8, 8.6, 8.8, 9.1, 9.2, 9.7])
    y = np.array([8.0, 5.0, 1.0, 5.0, -8.0, -6.0, -3.0, 5.0, -9.0, 7.0, 8.0, 7.0, 5.0, 8.0, 5.0, 4.0, -2.0, 9.0])

    positions = calculate_nodes_positions(x, y, nodes)
    np.testing.assert_allclose(positions[:, 0], result_x)
    np.testing.assert_allclose(positions[:, 1], result_y)


@pytest.mark.parametrize(
    "filename, name, extension",
    [("data.dat", "data", ".dat"), ("list.txt", "list", ".txt"), ("database.csv", "database", ".csv")],
)
def test_split_filename(filename, name, extension):
    base, ext = split_filename(filename)
    assert base == name
    assert ext == extension
