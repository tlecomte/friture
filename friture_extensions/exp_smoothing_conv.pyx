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
	cdef double a = (1.-alpha)**N
	
	# as we disable the cython bounds checking, do it by ourselves
	# it is absolutely needed as the kernel is not of infinite size !!
	if N > Nk:
		N = Nk
		a = 0.
	
	if N == 0:
		value = previous

	conv = 0.
	
	for i in range(0, N):
		conv = conv + kernel[Nk - N + i]*data[i]
	
	value = alpha * conv + previous*a
	
	return value


def pyx_exp_smoothed_value_numpy(np.ndarray[dtype_t, ndim=1] kernel, dtype_t alpha, np.ndarray[dtype_t, ndim=2] data, np.ndarray[dtype_t, ndim=1] previous):
	"""
	Compute exponential filtering of data with given kernel and alpha.
	The filter is applied on the 2nd axis (axis=1), independently for each row (axis=0).

	This is equivalent to applying the following IIR filter on each row of data:
	y_i = alpha*x_i + (1-alpha)*y_{i-1}
	where x_i is the input data, y_i the filtered data, and y_{i-1} the previous filtered value.

	We can unroll the recurrence a bit:
    y_{i+1} = a*x_{i+1} + (1-a)*y_i
            = a*x_{i+1} + (1-a)*a*x_i + (1-a)^2*y_{i-1}
    y_{i+2} = a*x_{i+2} + (1-a)*y_{i+1}
            = a*x_{i+2} + (1-a)*a*x_{i+1} + (1-a)^2*a*x_i + (1-a)^3*y_{i-1}
    ...

	This unrolling can be implemented with a convolution of a precomputed kernel.         
	
	By using a precomputed kernel, this function is optimized to process a large number of samples at once.

	Parameters:
	-----------
	kernel : 1D array
		the pre-computed convolution kernel for the exponential smoothing
	alpha : float
		the exponential smoothing factor, between 0 and 1
	data : 2D array
		the input data to filter
	previous : 1D array
		the previous filtered value
	Returns:
	--------
	1D array
		the filtered value"""
	cdef Py_ssize_t Nf = data.shape[0]
	cdef Py_ssize_t Nt = data.shape[1]
	cdef Py_ssize_t Nk = kernel.shape[0]
	cdef Py_ssize_t i, j
	cdef np.ndarray[dtype_t, ndim=1] value, conv
	cdef double a = (1.-alpha)**Nt

	# as we disable the cython bounds checking, do it by ourselves
	# it is absolutely needed as the kernel is not of infinite size !!
	if Nt > Nk:
		Nt = Nk
		a = 0.
	
	if Nt == 0:
		return previous

	conv = np.zeros(Nf, dtype=dtype)
	value = np.zeros(Nf, dtype=dtype)
	
	for i in range(0, Nt):
		for j in range(Nf):
			conv[j] = conv[j] + kernel[Nk - Nt + i]*data[j, i]
	
	for j in range(Nf):
		value[j] = alpha * conv[j] + previous[j]*a

	return value
