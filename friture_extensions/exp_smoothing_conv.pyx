import numpy as np
cimport numpy as np

# see INSTALL

dtype = np.float64
ctypedef np.float64_t dtype_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)

def pyx_exp_smoothed_value(np.ndarray[dtype_t, ndim=1] kernel, dtype_t alpha, np.ndarray[dtype_t, ndim=1] data, dtype_t previous):
	cdef Py_ssize_t N = data.shape[0]
	cdef Py_ssize_t Nk = kernel.shape[0]
	cdef Py_ssize_t i
	cdef dtype_t value, conv
	
	# as we disable the cython bounds checking, do it by ourselves
	# it is absolutely needed as the kernel is not of infinite size !!
	if N > Nk:
		N = Nk
	
	if N == 0:
		value = previous
	else:
		conv = 0.
		
		for i in range(0, N):
			conv = conv + kernel[Nk - N + i]*data[i]
		
		value = alpha * conv + previous*(1.-alpha)**N
	
	return value

def pyx_exp_smoothed_value_numpy(np.ndarray[dtype_t, ndim=1] kernel, dtype_t alpha, np.ndarray[dtype_t, ndim=2] data, np.ndarray[dtype_t, ndim=1] previous):
	cdef Py_ssize_t N = data.shape[1]
	cdef Py_ssize_t Nf = data.shape[0]
	cdef Py_ssize_t Nk = kernel.shape[0]
	cdef Py_ssize_t i, j
	cdef np.ndarray[dtype_t, ndim=1] value, conv
	cdef double a = (1.-alpha)**N

	# as we disable the cython bounds checking, do it by ourselves
	# it is absolutely needed as the kernel is not of infinite size !!
	if N > Nk:
		N = Nk
	
	if N == 0:
		return previous
	else:
		conv = np.zeros(Nf)
		value = np.zeros(Nf)
		
		for i in range(0, N):
			for j in range(Nf):
				conv[j] = conv[j] + kernel[Nk - N + i]*data[j, i]
		
		for j in range(Nf):
			value[j] = alpha * conv[j] + previous[j]*a
	
		return value
