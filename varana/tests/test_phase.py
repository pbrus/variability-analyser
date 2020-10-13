"""
Test package for varana.phase module

"""
import unittest
from os.path import realpath, split

from varana.phase import *


class PhaseTest(unittest.TestCase):
    def setUp(self):
        path = split(realpath(__file__))[0]
        self.lc_filename = path + r"/test_data/synthetic_lc_1.dat"
        self.model_filename = path + r"/test_data/model.dat"

    def test_read_lightcurve(self):
        results = np.array(
            [
                [1.65623458e02, 1.65635605e02, 1.65651111e02],
                [-4.77400000e-02, -3.67720000e-01, 1.06210000e-01],
                [2.64800000e-02, 7.83000000e-03, 1.25400000e-02],
            ]
        )
        self.assertTrue(np.allclose(read_lightcurve(self.lc_filename)[:3, :3], results))

    def test_read_model(self):
        y0 = np.array([6.44061e-05])
        results = np.array(
            [
                [0.25020369, 15.24000048, 3.21754473],
                [0.0603818, 40.28999286, 2.76319565],
                [0.10977151, 30.48000096, 0.42031565],
            ]
        )
        intercept, parameters = read_model(self.model_filename)
        self.assertTrue(np.allclose(intercept, y0))
        self.assertTrue(np.allclose(parameters, results))

    def test_time_to_phase(self):
        time = np.arange(1000, 1263, 14)
        period = 0.767
        results = np.array(
            [
                0.0,
                0.25293351,
                0.50586701,
                0.75880052,
                0.01173403,
                0.26466754,
                0.51760104,
                0.77053455,
                0.02346806,
                0.27640156,
                0.52933507,
                0.78226858,
                0.03520209,
                0.28813559,
                0.5410691,
                0.79400261,
                0.04693611,
                0.29986962,
                0.55280313,
            ]
        )
        self.assertTrue(np.allclose(time_to_phase(time, period), results))

    def test_multiply_phase(self):
        n = 4
        time = np.arange(2430, 2706, 13)
        period = 2.31
        phase = time_to_phase(time, period)
        magnitude = np.arange(10, 32)
        pha, mag = multiply_phase(phase, magnitude, n)
        phase = np.append(np.append(np.append(phase, phase + 1), phase + 2), phase + 3)
        self.assertTrue(np.allclose(pha, phase))
        self.assertTrue(np.allclose(mag, np.tile(magnitude, n)))

    def test_prepare_data_get_model(self):
        phase = np.array(
            [
                0.0,
                0.18512029,
                0.42143173,
                0.01751698,
                0.28033702,
                0.76573414,
                0.19333808,
                0.97463194,
                0.65582669,
                0.39205587,
            ]
        )
        magnitude = np.array(
            [-0.04774, -0.36772, 0.10621, -0.15934, -0.28908, 0.02377, -0.38645, -0.06013, 0.26934, 0.07838]
        )
        xx = np.array(
            [
                0.0,
                0.01005025,
                0.0201005,
                0.03015075,
                0.04020101,
                0.05025126,
                0.06030151,
                0.07035176,
                0.08040201,
                0.09045226,
            ]
        )
        yy = np.array(
            [
                -0.11475255,
                -0.13069089,
                -0.14593987,
                -0.16038649,
                -0.17394149,
                -0.1865397,
                -0.19813953,
                -0.20872167,
                -0.21828688,
                -0.22685327,
            ]
        )
        pha, mag = prepare_data(self.lc_filename, 15.24, 2)
        x_model, y_model = get_model(self.model_filename, 15.24, pha, mag)
        self.assertTrue(np.allclose(pha[:10], phase))
        self.assertTrue(np.allclose(mag[:10], magnitude))
        self.assertTrue(np.allclose(x_model[:10], xx))
        self.assertTrue(np.allclose(y_model[:10], yy))

    def test_sines_sum(self):
        parameters = np.array(
            [
                [0.30295617, 0.07417896, 0.45916029],
                [0.61863813, 0.28488621, 0.63261926],
                [0.17235333, 0.65313209, 0.66983205],
            ]
        )
        x0, y0 = 4.319, 17.517
        frequency = 1.364
        results = np.array(
            [
                17.648670550049133,
                17.000776679204602,
                16.995637267938356,
                17.70303244205788,
                18.39903676848221,
                17.870908510716415,
                17.4000763292155,
                17.238202876538708,
                18.217723680624406,
            ]
        )

        for x, res in zip(range(1, 10), results):
            func = sines_sum(parameters, y0, frequency)
            self.assertTrue(np.allclose(func(x, x0), res))

    def test_split_filename(self):
        filenames = ["example_file.txt", "example.file.txt"]
        file_tuples = [("example_file", ".txt"), ("example.file", ".txt")]

        for filename, file_tuple in zip(filenames, file_tuples):
            self.assertEqual(split_filename(filename), file_tuple)

    def tearDown(self):
        self.lc_filename = None
        self.model_filename = None
