import pyfftw
import numpy as np
import scipy.fftpack as scifft
import time
import anfft
import fftw3

# initial data
N = 256
a0 = np.random.rand(N)

Ntest = 1000

# Create 3 16-byte aligned arays using the aligned array creation functions
# They are cleared during the object creation, so there is no point filling them.
a = pyfftw.n_byte_align_empty(a0.shape, 16, dtype=np.complex128)
b = pyfftw.n_byte_align_empty(a.shape, 16, dtype=a.dtype)
c = pyfftw.n_byte_align_empty(a.shape, 16, dtype=a.dtype)

# Create the DFT and inverse DFT objects
fft = pyfftw.FFTW(a, b)
ifft = pyfftw.FFTW(b, c, direction='FFTW_BACKWARD')

# Fill a with data
a[:] = a0
#print a

t0 = time.time()

for i in range(Ntest):
	# perform the fft
	#fft.execute()
	fft()
	#print b

	# perform the inverse fft
	#ifft.execute()
	ifft() #calling the class instance will normalize
	#print c/a.size
	#c[:] /= a.size

t0b = time.time()

print(np.sum(c))

t1 = time.time()

for i in range(Ntest):
	b2 = scifft.fft(a0)
	a1 = scifft.ifft(b2)

t1b = time.time()

print(np.sum(a1))

t2 = time.time()

for i in range(Ntest):
	b3 = anfft.fft(a0)
	a2 = anfft.ifft(b3)

t2b = time.time()

print(np.sum(a2))

t3 = time.time()

# create a forward and backward fft plan
a = fftw3.create_aligned_array(a0.shape, np.complex128, 16)
b = fftw3.create_aligned_array(a0.shape, np.complex128, 16)
c = fftw3.create_aligned_array(a0.shape, np.complex128, 16)
a[:] = a0
ft3fft = fftw3.Plan(a, b, direction='forward', flags=['measure'])
ft3ifft = fftw3.Plan(b, c, direction='backward', flags=['measure'])

t4 = time.time()

for i in range(Ntest):
	#perform a forward transformation
	ft3fft() # alternatively fft.execute() or fftw.execute(fft)

	#perform a backward transformation
	ft3ifft() 

t4b = time.time()

print(np.sum(c))

t5 = time.time()

for i in range(Ntest):
	b2 = np.fft.fft(a0)
	a1 = np.fft.ifft(b2)

t5b = time.time()

print(np.sum(a1))

t_pyfftw = t0b - t0
t_scipy = t1b - t1
t_anfft = t2b - t2
t_pyfftw3 = t4b - t4
t_numfft = t5b - t5

print("pyfftw:", t_pyfftw)
print("scipy fftpack:", t_scipy)
print("anfft", t_anfft)
print("pyfftw3:", t_pyfftw3)
print("numpy fft:", t_numfft)
