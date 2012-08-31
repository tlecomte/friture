import numpy as np
cimport numpy as np

# see INSTALL

dtype = np.float64
ctypedef np.float64_t dtype_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)

def pyx_norm_square(np.ndarray[np.complex128_t, ndim=1] fft not None, np.float64_t factor):
    cdef np.int_t i
    cdef Py_ssize_t N = fft.shape[0]
    cdef np.ndarray[np.float64_t, ndim=1] out = np.zeros([N], dtype=np.float64)

    for i in range(N):
        out[i] = factor*(fft[i].real**2 + fft[i].imag**2)
    
    return out
