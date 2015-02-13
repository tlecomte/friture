import numpy as np
from friture.ringbuffer import RingBuffer
import matplotlib.pyplot as plt

Ns = int(1e4)

x = np.arange(Ns)
x.shape = (1,Ns)

l = 1024
Nb = int(Ns/l)
print("Nb =", Nb)

rb = RingBuffer()
rb.data(Ns) # grow the buffer as needed

# split in two to test zero-length insertions
Nb0 = Nb/2

print("Nb0 =", Nb0, "Nb1 =", Nb - Nb0)

print("pushing first parts")
for i in range(Nb0):
	rb.push(x[:,i*l:(i+1)*l])

print("pushing an empty array", x[:,0:0].shape)
rb.push(x[:,0:0])

print("pushing second parts")
for i in range(Nb0,Nb):
	rb.push(x[:,i*l:(i+1)*l])

print("pushing leftovers")
rb.push(x[:,Nb*l:])

print("retrieving")
y = rb.data(Ns)

print(x.shape, y.shape)

print("correct values in the ringbuffer ? =", np.all(x == y))

print("plotting")
plt.figure()
plt.subplot(2,1,1)
plt.plot(x[0,:])
plt.subplot(2,1,2)
plt.plot(y[0,:])

print("finished")
plt.show()
