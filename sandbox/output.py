# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 23:59:48 2011

@author: timothee
"""

""" Plays random data. """

import pyaudio
import numpy

SAMPLING_RATE = 44100
FRAMES_PER_BUFFER = 1024

chunk = 1024

p = pyaudio.PyAudio()

# open stream
stream = p.open(format = pyaudio.paInt16,
                channels = 1,
                rate = SAMPLING_RATE,
                output = True)

# play
i = 0
while i < 100:
    floatdata = numpy.random.standard_normal(FRAMES_PER_BUFFER)
    intdata = (floatdata*(2.**(16-1))).astype(numpy.int16)
    chardata = intdata.tostring()
    stream.write(chardata)
    i += 1

stream.close()
p.terminate()
