# -*- coding: utf-8 -*-

import unittest
import numpy as np

from friture.octavefilters import Octave_Filters, NOCTAVE
from friture.filter import (
    octave_filter_bank_decimation,
    octave_filter_bank_decimation_filtic,
)


class OctaveFilterTest(unittest.TestCase):
    """Verify that the all-FFT octave filter bank matches the pure-IIR
    reference within the expected FIR-approximation tolerance."""

    bands_per_octave_list = [1, 6, 12, 24]
    block_size = 1024
    n_blocks = 8

    def _run_reference(self, ofs, x):
        """Run the pure-IIR octave filter bank with state continuity."""
        zis = octave_filter_bank_decimation_filtic(
            ofs.bdec, ofs.adec, ofs.boct, ofs.aoct
        )
        nb = len(x) // self.block_size
        y = [np.zeros(0)] * (NOCTAVE * ofs.bandsperoctave)
        for b in range(nb):
            xb = x[b * self.block_size:(b + 1) * self.block_size]
            yb, dec, zis = octave_filter_bank_decimation(
                ofs.bdec, ofs.adec, ofs.boct, ofs.aoct, xb, zis
            )
            for i in range(len(yb)):
                y[i] = np.concatenate([y[i], yb[i]])
        return y

    def test_all_fft_matches_iir(self):
        rng = np.random.default_rng(42)
        x = rng.standard_normal(self.block_size * self.n_blocks)

        for bpo in self.bands_per_octave_list:
            ofs_ref = Octave_Filters(bpo)
            y_ref = self._run_reference(ofs_ref, x)

            ofs = Octave_Filters(bpo)
            y_fft = [np.zeros(0)] * (NOCTAVE * bpo)
            for b in range(self.n_blocks):
                xb = x[b * self.block_size:(b + 1) * self.block_size]
                yb, _ = ofs.filter(xb)
                for i in range(len(yb)):
                    y_fft[i] = np.concatenate([y_fft[i], yb[i]])

            for i in range(NOCTAVE * bpo):
                e_ref = np.sum(y_ref[i] ** 2)
                e_fft = np.sum(y_fft[i] ** 2)
                if e_ref > 1e-12:
                    ratio = e_fft / e_ref
                    self.assertAlmostEqual(
                        ratio, 1.0, delta=0.05,
                        msg=f"bpo={bpo} band {i}: energy ratio {ratio:.4f}"
                    )

    def test_decimation_factors(self):
        """Decimation factors should be [1, 2, 4, ..., 256] repeated
        for each band within a stage, in reverse band order."""
        for bpo in self.bands_per_octave_list:
            ofs = Octave_Filters(bpo)
            x = np.zeros(1024)
            _, dec = ofs.filter(x)
            expected = [2 ** j for j in range(NOCTAVE) for _ in range(bpo)]
            expected.reverse()
            self.assertEqual(dec, expected, f"dec mismatch for bpo={bpo}")

    def test_single_block_correctness(self):
        """Single-block FFT output should match IIR within tolerance."""
        rng = np.random.default_rng(123)
        for bpo in self.bands_per_octave_list:
            ofs_ref = Octave_Filters(bpo)
            x = rng.standard_normal(self.block_size)

            zis = octave_filter_bank_decimation_filtic(
                ofs_ref.bdec, ofs_ref.adec, ofs_ref.boct, ofs_ref.aoct
            )
            y_ref, _, _ = octave_filter_bank_decimation(
                ofs_ref.bdec, ofs_ref.adec, ofs_ref.boct, ofs_ref.aoct, x, zis
            )

            ofs = Octave_Filters(bpo)
            y_fft, _ = ofs.filter(x)

            for i in range(NOCTAVE * bpo):
                e_ref = np.sum(y_ref[i] ** 2)
                if e_ref > 1e-10:
                    err = np.max(np.abs(y_ref[i] - y_fft[i]))
                    rel_err = err / (np.max(np.abs(y_ref[i])) + 1e-30)
                    energy_ratio = np.sum(y_fft[i] ** 2) / e_ref
                    self.assertTrue(
                        rel_err < 0.10 and abs(energy_ratio - 1.0) < 0.05,
                        msg=f"bpo={bpo} band {i}: rel_err={rel_err:.4f}, energy_ratio={energy_ratio:.4f}"
                    )


if __name__ == "__main__":
    unittest.main()
