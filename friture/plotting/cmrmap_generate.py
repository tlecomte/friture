#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015, Timothée Lecomte
# Copyright (c) 2012, Christopher Hummersone
# Copyright (c) 2002, Carey Rappaport
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in
#       the documentation and/or other materials provided with the distribution
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import numpy as np
from scipy.interpolate.fitpack import splrep, splev

#   Returns a colour map CMAP (varying black -
#   purple - red - yellow - white) that is monochrome-
#   compatible, i.e. it produces a monotonic greyscale
#   colour map.
#
#   The map is a slight modification to that suggested in
#   [1].
#
#   Reference:
#
#   [1] Rappaport, C. 2002: "A Color Map for Effective
#   Black-and-White Rendering of Color Scale Images", IEEE
#   Antenna's and Propagation Magazine, Vol.44, No.3,
#   pp.94-96 (June).
#
# http://stackoverflow.com/questions/7251872/is-there-a-better-color-scale-than-the-rainbow-colormap
# http://matplotlib.org/users/colormaps.html
# http://www.mathworks.com/matlabcentral/fileexchange/39552-modified-cmrmap

# reference colour map
# adapted from article to produce more linear luminance
CMRref = np.array([[0, 0, 0],
                   [0.1, 0.1, 0.35],
                   [0.3, 0.15, 0.65],
                   [0.6, 0.2, 0.50],
                   [1, 0.25, 0.15],
                   [0.9, 0.55, 0],
                   [0.9, 0.75, 0.1],
                   [0.9, 0.9, 0.5],
                   [1, 1, 1]])


def compute_colors(N):
    xref = np.linspace(0, 1, CMRref.shape[0])
    x = np.linspace(0, 1, N)
    cmap = np.zeros((N, 3))

    for i in range(3):
        tck = splrep(xref, CMRref[:, i], s=0)  # cubic spline (default) without smoothing
        cmap[:, i] = splev(x, tck)

    # Limit to range [0,1]
    cmap -= np.min(cmap)
    cmap /= np.max(cmap)

    return cmap


def generate_cmrmap():
    import os
    import json

    cmap = compute_colors(256)

    out = """\
# CMRMAP generated from cmrmap_generate.py

#   Returns a colour map CMAP (varying black -
#   purple - red - yellow - white) that is monochrome-
#   compatible, i.e. it produces a monotonic greyscale
#   colour map.
#
#   The map is a slight modification to that suggested in
#   [1].
#
#   Reference:
#
#   [1] Rappaport, C. 2002: "A Color Map for Effective
#   Black-and-White Rendering of Color Scale Images", IEEE
#   Antenna's and Propagation Magazine, Vol.44, No.3,
#   pp.94-96 (June).
#
# http://stackoverflow.com/questions/7251872/is-there-a-better-color-scale-than-the-rainbow-colormap
# http://matplotlib.org/users/colormaps.html
# http://www.mathworks.com/matlabcentral/fileexchange/39552-modified-cmrmap

import json
import numpy

JSON_CMAP = \"\"\"
%s
\"\"\"

CMAP = numpy.array(json.loads(JSON_CMAP))
""" % json.dumps(cmap.tolist(), indent=4, sort_keys=True)

    path = os.path.dirname(__file__)
    fname = os.path.join(path, 'generated_cmrmap.py')
    with open(fname, 'w') as output:
        output.write(out)


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    N = 256

    generate_cmrmap()

    cmap = compute_colors(N)

    xref = np.linspace(0, 1, CMRref.shape[0])
    x = np.linspace(0, 1, N)

    plt.figure()
    plt.plot(xref, CMRref[:, 0], 'xr', x, cmap[:, 0], 'r')
    plt.plot(xref, CMRref[:, 1], 'xg', x, cmap[:, 1], 'g')
    plt.plot(xref, CMRref[:, 2], 'xb', x, cmap[:, 2], 'b')
    plt.legend(['Linear', 'Cubic Spline'])
    plt.show()
