import numpy as np
cimport numpy as np

# see INSTALL

dtype = np.float64
ctypedef np.float64_t dtype_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)

def pyx_color_from_float(np.ndarray[np.uint32_t, ndim=1] lut not None,
                         np.ndarray[np.float64_t, ndim=1] values not None):
    cdef np.int_t i, j
    cdef Py_ssize_t N = values.shape[0]
    cdef np.ndarray[np.uint32_t, ndim=1] out = np.zeros([N], dtype=np.uint32)

    for i in range(N):
        j = (int)(values[i]*255)
        out[i] = lut[j]
    
    return out

def pyx_color_from_float_2D(np.ndarray[np.uint32_t, ndim=1] lut not None,
                            np.ndarray[np.float64_t, ndim=2] values not None):
    cdef np.int_t i, j, k
    cdef Py_ssize_t M = values.shape[0]
    cdef Py_ssize_t N = values.shape[1]
    cdef np.ndarray[np.uint32_t, ndim=2] out = np.zeros([M, N], dtype=np.uint32)

    for i in range(M):
        for j in range(N):
            k = (int)(values[i, j]*255)
            out[i, j] = lut[k]
    
    return out
