import numpy as np
cimport numpy as np

# see INSTALL

dtype = np.float64
ctypedef np.float64_t dtype_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)

def pyx_linear_interp_2D(np.ndarray[dtype_t, ndim=2] resampled_buffer not None,
                         np.ndarray[dtype_t, ndim=1] data not None,
                         np.ndarray[dtype_t, ndim=1] old_data not None,
                         dtype_t orig_index,
                         dtype_t resampled_index,
                         dtype_t resampling_ratio,
                         int n):
    cdef dtype_t a
    cdef np.int_t i, j
    cdef Py_ssize_t N = data.shape[0]

    for i in range(n):
        # linear interpolation
        resampled_index += resampling_ratio
        a = orig_index - resampled_index
        for j in range(N):
            resampled_buffer[j,i] = (1-a)*data[j] + a*old_data[j]

    return resampled_index
