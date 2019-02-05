import numpy as np
cimport numpy as np

# see INSTALL

dtype = np.float64
ctypedef np.float64_t dtype_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)

def pyx_lfilter_float64_1D(
    np.ndarray[np.float64_t, ndim=1] b not None,
    np.ndarray[np.float64_t, ndim=1] a not None,
    np.ndarray[np.float64_t, ndim=1] x not None,
    np.ndarray[np.float64_t, ndim=1] zi not None):

    """
    Filter data along one-dimension with an IIR or FIR filter.

    Filter a data sequence, x, using a digital filter.  This works for many
    fundamental data types (including Object type).  The filter is a direct
    form II transposed implementation of the standard difference equation
    (see Notes).

    Parameters
    ----------
    b : array_like
        The numerator coefficient vector in a 1-D sequence.
    a : array_like
        The denominator coefficient vector in a 1-D sequence.  If a[0]
        is not 1, then both a and b are normalized by a[0].
    x : array_like
        An N-dimensional input array.
    axis : int
        The axis of the input data array along which to apply the
        linear filter. The filter is applied to each subarray along
        this axis (*Default* = -1)
    zi : array_like (optional)
        Initial conditions for the filter delays.  It is a vector
        (or array of vectors for an N-dimensional input) of length
        max(len(a),len(b))-1.  If zi=None or is not given then initial
        rest is assumed.  SEE signal.lfiltic for more information.

    Returns
    -------
    y : array
        The output of the digital filter.
    zf : array (optional)
        If zi is None, this is not returned, otherwise, zf holds the
        final filter delay values.

    Notes
    -----
    The filter function is implemented as a direct II transposed structure.
    This means that the filter implements

    ::

       a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
                               - a[1]*y[n-1] - ... - a[na]*y[n-na]

    using the following difference equations::

         y[m] = b[0]*x[m] + z[0,m-1]
         z[0,m] = b[1]*x[m] + z[1,m-1] - a[1]*y[m]
         ...
         z[n-3,m] = b[n-2]*x[m] + z[n-2,m-1] - a[n-2]*y[m]
         z[n-2,m] = b[n-1]*x[m] - a[n-1]*y[m]

    where m is the output sample number and n=max(len(a),len(b)) is the
    model order.

    The rational transfer function describing this filter in the
    z-transform domain is::

                             -1               -nb
                 b[0] + b[1]z  + ... + b[nb] z
         Y(z) = ---------------------------------- X(z)
                             -1               -na
                 a[0] + a[1]z  + ... + a[na] z

    """


    assert b.shape[0] == a.shape[0], "a and b must be of the same shape"
    assert zi.shape[0] == b.shape[0]-1

    cdef Py_ssize_t len_x = x.shape[0]
    cdef Py_ssize_t len_b = b.shape[0]
    cdef np.int_t n
    cdef np.uint_t k

    cdef np.ndarray[np.float64_t, ndim=1] y = np.empty(x.shape[0])
    cdef np.ndarray[np.float64_t, ndim=1] z = np.array(zi, copy=True)

    if len_b > 1:
        for k in range(len_x):
            y[k] = z[0] + b[0] * x[k] # Calculate first delay (output)

            # Fill in middle delays
            for n in range(len_b - 2):
                z[n] = z[1+n] + x[k] * b[1+n] - y[k] * a[1+n]

            # Calculate last delay
            z[len_b - 2] = x[k] * b[len_b - 1] - y[k] * a[len_b - 1]
    else:
        for k in range(len_x):
            y[k] = x[k] * b[0]



    return y, z