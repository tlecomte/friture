import numpy as np
import matplotlib.pyplot as plt

from friture import generated_filters
from friture.audiobackend import SAMPLING_RATE
from friture.delay_estimator import subsampler, subsampler_filtic

Ns = int(1e4)
#y = np.random.rand(Ns)

f = 2e1
t = np.linspace(0, float(Ns)/SAMPLING_RATE, Ns)
y = np.cos(2.*np.pi*f*t)

Ndec = 2
subsampled_sampling_rate = SAMPLING_RATE/2**(Ndec)
[bdec, adec] = generated_filters.PARAMS['dec']
zfs0 = subsampler_filtic(Ndec, bdec, adec)

Nb = 10
l = int(Ns/Nb)

Nb0 = Nb/2
print("Nb0 =", Nb0, "Nb1 =", Nb - Nb0)

print("subsample first parts")
for i in range(Nb0):
    ydec, zfs0 = subsampler(Ndec, bdec, adec, y[i*l:(i+1)*l], zfs0)
    if i == 0:
        y_dec = ydec
    else:
        y_dec = np.append(y_dec, ydec)

print("push an empty array to the subsampler", y[i*l:i*l].shape, y[i*l:i*l].size)
ydec, zfs0 = subsampler(Ndec, bdec, adec, y[i*l:i*l], zfs0)
y_dec = np.append(y_dec, ydec)

print("subsample last parts")
for i in range(Nb0, Nb):
    ydec, zfs0 = subsampler(Ndec, bdec, adec, y[i*l:(i+1)*l], zfs0)
    y_dec = np.append(y_dec, ydec)

print("plot")
plt.figure()
plt.subplot(2,1,1)
plt.plot(y)
plt.subplot(2,1,2)
plt.plot(y_dec)

plt.show()
