# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 16:12:12 2012

@author: timothee
"""

import numpy as np

from .scipy_resample import resample
from friture_extensions.linear_interp import pyx_linear_interp_2D


class Online_Linear_2D_resampler:

    def __init__(self, interp_factor_L=1, decim_factor_M=1, height=1):
        self.interp_factor_L = interp_factor_L
        self.decim_factor_M = decim_factor_M
        self.resampling_ratio = float(interp_factor_L) / decim_factor_M

        self.height = height

        self.orig_index = 0.
        self.resampled_index = 0.

        self.old_data = np.zeros((self.height))

        self.resampled_data = np.zeros((self.height, 1))

    def set_ratio(self, interp_factor_L, decim_factor_M):
        if self.interp_factor_L != interp_factor_L or self.decim_factor_M != decim_factor_M:
            self.interp_factor_L = interp_factor_L
            self.decim_factor_M = decim_factor_M
            self.resampling_ratio = float(interp_factor_L) / decim_factor_M

            self.orig_index = 0.
            self.resampled_index = 0.

    def set_height(self, height):
        if self.height != height:
            self.height = height

            self.orig_index = 0.
            self.resampled_index = 0.

            # we resample here instead of just restarting with zeros to avoid black vertical lines
            # in the spectrogram
            self.old_data = resample(self.old_data, self.height)
            self.resampled_data = resample(self.resampled_data, self.height)  # resample on the first axis

    def processable(self, m):
        return int(np.ceil((self.orig_index + m - (self.resampled_index + self.resampling_ratio)) / self.resampling_ratio))

    # will return as much resampled data as possible
    def process(self, data):
        self.orig_index += 1.
        n = int(np.ceil((self.orig_index - (self.resampled_index + self.resampling_ratio)) / self.resampling_ratio))

        if self.resampled_data.shape[1] < n:
            self.resampled_data = np.zeros((self.height, n))

        self.resampled_index = pyx_linear_interp_2D(self.resampled_data, data, self.old_data, self.orig_index, self.resampled_index, self.resampling_ratio, n)

        # shift
        self.old_data = data

        return self.resampled_data[:, :n]
