"""
Test package for varana.trim module.

"""
import unittest
from os.path import realpath, split

import numpy as np

from varana.trim import cutoff, filter_lightcurve, get_data, sigma_clipping, split_filename, trim, x_domain


class TrimTest(unittest.TestCase):
    def setUp(self):
        path = split(realpath(__file__))[0]
        self.lc_filename = path + r"/test_data/synthetic_lc.dat"
        self.lc_trim_inverse_filename = path + r"/test_data/synthetic_lc_sigma_clipping_inverse.dat"
        self.lc_manual_trim_filename = path + r"/test_data/synthetic_lc_manual_trim.dat"
        self.data = np.genfromtxt(self.lc_filename)
        self.inverse_trim_data = np.genfromtxt(self.lc_trim_inverse_filename)
        self.manual_trim_data = np.genfromtxt(self.lc_manual_trim_filename)
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

    def test_get_data(self):
        data = get_data(self.lc_filename)
        self.assertTrue(np.array_equal(data, self.data))

    def test_sigma_clipping(self):
        array = sigma_clipping(self.data)
        array = np.array(array[array.mask])
        self.assertTrue(np.allclose(self.inverse_trim_data.flatten(), array))

    def test_cutoff(self):
        array = cutoff(self.data, -2.0, 2.0)
        array = np.array(array[array.mask])
        self.assertTrue(np.allclose(self.manual_trim_data.flatten(), array))

    def test_trim(self):
        array = trim(self.data)
        array = np.array(array[array.mask])
        self.assertTrue(np.allclose(self.inverse_trim_data.flatten(), array))
        array = trim(self.data, -2.0, 2.0)
        array = np.array(array[array.mask])
        self.assertTrue(np.allclose(self.manual_trim_data.flatten(), array))

    def test_x_domain(self):
        x_dom = x_domain(np.ma.array(self.data[:, 0]))
        self.assertTrue(np.allclose(self.x_domain, x_dom[:10]))

    def test_split_filename(self):
        filenames = ["example_file.txt", "example.file.txt"]
        file_tuples = [("example_file", ".txt"), ("example.file", ".txt")]

        for filename, file_tuple in zip(filenames, file_tuples):
            self.assertEqual(split_filename(filename), file_tuple)

    def test_filter_lightcurve(self):
        array = np.ma.array(
            [
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                [10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                [30, 31, 32, 33, 34, 35, 36, 37, 38, 39],
                [40, 41, 42, 43, 44, 45, 46, 47, 48, 49],
                [70, 71, 72, 73, 74, 75, 76, 77, 78, 79],
                [80, 81, 82, 83, 84, 85, 86, 87, 88, 89],
                [90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
            ]
        )
        data = np.ma.arange(100).reshape(10, 10)
        data.mask = [False]
        data.mask[2, :] = data.mask[5:7, :] = True
        self.assertTrue(np.allclose(array, filter_lightcurve(data)))

    def tearDown(self):
        self.lc_filename = None
        self.lc_trim_inverse_filename = None
        self.lc_manual_trim_filename = None
        self.data = None
        self.inverse_trim_data = None
        self.manual_trim_data = None
        self.x_domain = None
