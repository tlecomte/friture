# -*- coding: utf-8 -*-

import unittest
import numpy as np
import numpy.testing as npt

from friture.signal import exp_smoothing as esc

class ExpSmoothingTest(unittest.TestCase):
    def test_uniform_rows(self):
        # rows with identical time-series should produce identical filtered values
        alpha = 0.2
        Nt = 6
        Nk = 10
        kernel = (1. - alpha) ** np.arange(Nk - 1, -1, -1)

        Nf = 5
        # create data where each row has same time-series
        row = np.array([0., 0., 1., 2., 3., 4.])
        data = np.tile(row, (Nf, 1))
        previous = np.zeros(Nf)

        out = esc.exp_smoothed_value_2d(kernel, alpha, data, previous)
        # all outputs must be equal (within tolerance)
        npt.assert_allclose(out, out[0] * np.ones_like(out))

    def test_shifted_rows_consistency(self):
        # rows with time-shifted versions should have sensible monotonic relation
        alpha = 0.1
        Nt = 5
        Nk = 20
        kernel = (1. - alpha) ** np.arange(Nk - 1, -1, -1)

        Nf = 4
        base = np.array([0., 0., 0., 1., 2.])
        data = np.zeros((Nf, Nt))
        for i in range(Nf):
            # each row ramps more strongly
            data[i, :] = base * (i + 1)
        previous = np.zeros(Nf)

        out = esc.exp_smoothed_value_2d(kernel, alpha, data, previous)
        # outputs should be strictly increasing with the multiplier
        self.assertTrue((out[1:] > out[:-1]).all())


if __name__ == '__main__':
    unittest.main()
