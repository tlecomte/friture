#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2016 Timothée Lecomte

# This file is part of Friture.
#
# Friture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as published by
# the Free Software Foundation.
#
# Friture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Friture.  If not, see <http://www.gnu.org/licenses/>.

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from cmrmap import compute_colors

    N = 256

    cmap = compute_colors(N)

    xref = np.linspace(0, 1, CMRref.shape[0])
    x = np.linspace(0, 1, N)

    plt.figure()
    plt.plot(xref, CMRref[:, 0], 'xr', x, cmap[:, 0], 'r')
    plt.plot(xref, CMRref[:, 1], 'xg', x, cmap[:, 1], 'g')
    plt.plot(xref, CMRref[:, 2], 'xb', x, cmap[:, 2], 'b')
    plt.legend(['Linear', 'Cubic Spline'])
    plt.show()
