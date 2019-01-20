"""
Test package of the varana.phase module
"""
import unittest
from os.path import realpath, split
from varana.phase import *


class PhaseTest(unittest.TestCase):

    def setUp(self):
        path = split(realpath(__file__))[0]
        self.lc_filename = path + r'/test_data/synthetic_lc.dat'
        self.model_filename = path + r'/test_data/model.dat'

    def test_read_lightcurve(self):
        results = np.array([
            [1.65445448e+02, 1.66264696e+02, 1.66947026e+02],
            [-3.78320000e-01, 1.71500000e+00, 5.23510000e-01],
            [6.70000000e-04, 7.20000000e-04, 5.10000000e-04]
        ])
        self.assertTrue(np.allclose(read_lightcurve(self.lc_filename)[:3, :3],
                                    results))

    def test_read_model(self):
        y0 = np.array([15.16501947])
        results = np.array([
            [2.68867230e-03, 4.31896040e-03, 5.31110432e+00],
            [7.24615470e-03, 9.93555190e-01, 1.21593659e+00],
            [1.97919640e-03, 1.90625012e+02, 7.01483222e-02]
        ])
        intercept, parameters = read_model(self.model_filename)
        self.assertTrue(np.allclose(intercept, y0))
        self.assertTrue(np.allclose(parameters, results))

    def test_time_to_phase(self):
        time = np.arange(1000, 1263, 14)
        period = 0.767
        results = np.array([
            0.0, 0.25293351, 0.50586701, 0.75880052, 0.01173403,
            0.26466754, 0.51760104, 0.77053455, 0.02346806, 0.27640156,
            0.52933507, 0.78226858, 0.03520209, 0.28813559, 0.5410691,
            0.79400261, 0.04693611, 0.29986962, 0.55280313
        ])
        self.assertTrue(np.allclose(time_to_phase(time, period), results))

    def test_multiply_phase(self):
        n = 4
        time = np.arange(2430, 2706, 13)
        period = 2.31
        phase = time_to_phase(time, period)
        magnitude = np.arange(10, 32)
        pha, mag = multiply_phase(phase, magnitude, n)
        phase = np.append(np.append(np.append(phase, phase+1), phase+2),
                          phase+3)
        self.assertTrue(np.allclose(pha, phase))
        self.assertTrue(np.allclose(mag, np.tile(magnitude, n)))
