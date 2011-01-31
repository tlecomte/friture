import numpy as np
cimport numpy as np

# to build the module on linux:
#cython array_of_dots4.pyx
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I/usr/include/python2.6 -o array_of_dots4.so array_of_dots4.c

dtype = np.float64
ctypedef np.float64_t dtype_t

cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)

# Note: b and a must have the same length !!
# Note: b must be of length > 1
# Note : a[0] must be equal to 1 !!
def pyx_double_filt(np.ndarray[dtype_t, ndim=1] b, np.ndarray[dtype_t, ndim=1] a, np.ndarray[dtype_t, ndim=1] x, np.ndarray[dtype_t, ndim=1] Z):
	#The filter function is implemented as a direct II transposed structure.
	#This means that the filter implements:

	#a[0]*y[n] = b[0]*x[n] + b[1]*x[n-1] + ... + b[nb]*x[n-nb]
			#- a[1]*y[n-1] - ... - a[na]*y[n-na]

	#using the following difference equations::

	#y[m] = b[0]*x[m] + z[0,m-1]
	#z[0,m] = b[1]*x[m] + z[1,m-1] - a[1]*y[m]
	#...
	#z[n-3,m] = b[n-2]*x[m] + z[n-2,m-1] - a[n-2]*y[m]
	#z[n-2,m] = b[n-1]*x[m] - a[n-1]*y[m]
	
	cdef Py_ssize_t lb, lx, k, i, j
	cdef np.ndarray[dtype_t, ndim=1] y = np.zeros(x.shape[0], dtype=dtype)
	cdef dtype_t xn, yk
	
	lb = b.shape[0]
	lx = x.shape[0]
	
	for k in range(0, lx):
		xn = x[k]
		# Calculate first delay (output)
		yk = Z[0] + b[0]*xn
		y[k] = yk
		# Fill in middle delays
		for i in range(0, lb-2):
			j = i + 1
			Z[i] = Z[j] + xn*b[j] - yk*a[j]
		# Calculate last delay
		Z[lb - 2] = xn*b[lb - 1] - yk*a[lb - 1]

	return y, Z

def pyx_exp_smoothed_value(np.ndarray[dtype_t, ndim=1] kernel, dtype_t alpha, np.ndarray[dtype_t, ndim=1] data, dtype_t previous):
	cdef Py_ssize_t N = data.shape[0]
	cdef Py_ssize_t Nk = kernel.shape[0]
	cdef Py_ssize_t i
	cdef dtype_t value, conv
	
	if N == 0:
		value = previous
	else:
		conv = 0.
		
		for i in range(0, N):
			conv = conv + kernel[Nk - N + i]*data[i]
		
		value = alpha * conv + previous*(1.-alpha)**N
	
	return value
