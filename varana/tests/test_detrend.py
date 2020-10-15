"""
Test package for varana.detrend module

"""
import unittest
from os.path import realpath, split

import numpy as np

from varana.detrend import (
    calculate_kmeans,
    detrend_data,
    get_data,
    sigma_clipping_magnitude,
    sorted_centers,
    spline_function,
    spline_order,
    split_filename,
    too_much_points_rejected,
    unpack_data,
    valid_seasons_amount,
    x_domain_spline,
    y_domain_spline,
)


class DetrendTest(unittest.TestCase):
    def setUp(self):
        path = split(realpath(__file__))[0]
        self.lc_filename = path + r"/test_data/synthetic_lc.dat"
        self.lc_trim_filename = path + r"/test_data/synthetic_lc_sigma_clipping.dat"
        self.data = np.genfromtxt(self.lc_filename)
        self.trim_data = np.genfromtxt(self.lc_trim_filename)
        self.x_domain = np.array(
            [
                165.445448,
                166.71958418,
                167.99372036,
                169.26785654,
                170.54199272,
                171.8161289,
                173.09026508,
                174.36440126,
                175.63853744,
                176.91267362,
            ]
        )

    def test_valid_seasons_amount(self):
        self.assertRaises(ValueError, valid_seasons_amount, 1)
        self.seasons_amount = 9
        seasons_amount = valid_seasons_amount(self.seasons_amount)
        self.assertEqual(seasons_amount, seasons_amount)

    def test_get_data(self):
        data = get_data(self.lc_filename)
        self.assertTrue(np.array_equal(data, self.data))

    def test_sigma_clipping_magnitude(self):
        data = sigma_clipping_magnitude(self.data)
        self.assertTrue(np.array_equal(data, self.trim_data))

    def test_too_much_points_rejected(self):
        self.assertFalse(too_much_points_rejected(100, 98))
        self.assertTrue(too_much_points_rejected(100, 91))

    def test_unpack_data(self):
        tuple_data = self.data[:, 0], self.data[:, 1], self.data[:, 2]
        self.assertTrue(np.array_equal(tuple_data, unpack_data(self.data)))

    def test_calculate_kmeans(self):
        clusters_centers = np.array(
            [
                [9.95274508e02, -9.85392445e-02],
                [2.67177517e02, 2.65203604e-01],
                [1.35113653e03, 6.14042550e-02],
                [6.29255809e02, -6.68374040e-02],
            ]
        )
        kmeans = calculate_kmeans(*unpack_data(self.data), clusters_number=4)
        self.assertTrue(np.allclose(kmeans.cluster_centers_, clusters_centers))

    def test_sorted_centers(self):
        update_centers = np.array(
            [
                [2.67177517e02, 2.65203604e-01],
                [6.29255809e02, -6.68374040e-02],
                [9.95274508e02, -9.85392445e-02],
                [1.35113653e03, 6.14042550e-02],
            ]
        )
        kmeans = calculate_kmeans(*unpack_data(self.data), clusters_number=4)
        self.assertTrue(np.allclose(sorted_centers(kmeans), update_centers))

    def test_spline_order(self):
        seasons = [2, 3, 4, 9]
        orders = [1, 2, 3, 3]

        for season, order in zip(seasons, orders):
            self.assertEqual(order, spline_order(season))

    def test_spline_function(self):
        spline_coeffs = np.array(
            [
                -0.37832,
                2.81363646,
                1.25721844,
                -1.46388609,
                3.21396524,
                -2.60229307,
                4.20855241,
                -0.65726299,
                1.93272306,
                -1.44624978,
            ]
        )
        func = spline_function(self.data[:, :2])
        self.assertTrue(np.allclose(spline_coeffs, func.get_coeffs()[:10]))

    def test_x_domain_spline(self):
        self.assertTrue(np.allclose(self.x_domain, x_domain_spline(self.data[:, 0])[:10]))

    def test_y_domain_spline(self):
        def _func(x):
            return 0.02 * x ** 3 + 0.01 * x ** 2 - 3.2 * x - 1.76

        self.assertTrue(np.allclose(_func(self.x_domain), y_domain_spline(_func, self.x_domain)))

    def test_split_filename(self):
        filenames = ["example_file.txt", "example.file.txt"]
        file_tuples = [("example_file", ".txt"), ("example.file", ".txt")]

        for filename, file_tuple in zip(filenames, file_tuples):
            self.assertEqual(split_filename(filename), file_tuple)

    def test_detrend_data(self):
        results = np.array(
            [
                [1.65445448e02, 2.21650434e01, 6.70000000e-04],
                [1.66264696e02, 2.42829409e01, 7.20000000e-04],
                [1.66947026e02, 2.31119208e01, 5.10000000e-04],
                [1.67665380e02, 2.21544714e01, 1.08000000e-03],
                [1.68527654e02, 2.39932796e01, 8.50000000e-04],
                [1.69521903e02, 2.24496271e01, 8.40000000e-04],
                [1.70285055e02, 2.52439317e01, 9.80000000e-04],
                [1.70848836e02, 2.35367251e01, 8.20000000e-04],
                [1.71769190e02, 2.35426657e01, 5.20000000e-04],
                [1.72479518e02, 2.17447055e01, 5.90000000e-04],
            ]
        )

        def _func(x):
            return -0.03 * x

        self.assertTrue(np.allclose(results, detrend_data(self.data[:10], _func, 17.58)))

    def tearDown(self):
        self.lc_filename = None
        self.lc_trim_filename = None
        self.data = None
        self.trim_data = None
        self.x_domain = None
