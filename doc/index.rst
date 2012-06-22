.. Friture documentation master file, created by
   sphinx-quickstart on Thu May 17 16:53:22 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. Commented-out lines start with '..'

.. Build the doc using 'sphinx-build -b html doc doc/_build'

Welcome to Friture documentation!
===================================

This document contains some notes to help you use Friture to perform various
tasks.

.. Contents:

.. toctree::
   :maxdepth: 2

Identify a feedback frequency (Larsen effect)
---------------------------------------------

The FFT Spectrum is the best tool to identify a feedback frequency. It provides the high frequency
resolution that you need to precisely pinpoint the position of the feedbacks in the spectrum.

Instructions:
    1. Plug the output of your mixing console, or a measurement microphone,
       to the Left input channel
    2. In Friture, add a new dock, and choose the FFT Spectrum in the widget list.
    3. Raise the volume of the microphone of interest.
    4. As soon as you reach the feedback threshold and produce a Larsen effect,
       hit the spacebar or click on "pause" in Friture to freeze the display, and lower
       the microphone volume to stop the Larsen effect (to protect the audio system and
       your ears !).
    5. The feedback will appear as a sharp peak in the FFT Spectrum. Pinpoint
       them with the mouse cursor and left-click to display the frequency.
    6. Use a parametric equalizer to place a notch filter at that precise
       frequency.
    7. Repeat the procedure to identify and filter-out more feedback frequencies.

Equalize the response of a hall
-------------------------------

The human ear system has approximately a resolution one third of an octave. To
equalize the audio response of a hall, the Octave Spectrum with three bands per
octave (one third octave resolution) is the best tool that you can use.

Instructions:
    1. Plug a measurement microphone to the Left input channel.
    2. In Friture, add a new dock, and choose the Octave Spectrum in the widget list.
    3. In the dock settings, ask for 3 bands per octave.
    4. Play pink noise to your sound system (using Friture pink noise generator
       if you will).
    5. The ideal spectrum should be flat. Use an equalizer to raise the dips and
       lower the peaks in the spectrum.

Measure a delay, align audio sources
------------------------------------

The Delay Estimator can identify and measure a delay between two audio streams.
It works by computing how much the audio signals look like each other depending
on the relative delay, and looking for the maximum of similarity
(mathematically, the "similarity" function is a generalized cross-correlation
with a PHAT-transform weighting, time-smoothed by an exponential filter).

Instructions:
    1. Plug the reference signal (the output of the mixing console) to the Left
       channel.
    2. Plug the delayed channel (the measurement microphone) to the Right channel.
    3. Enable the two-channel mode in Friture settings, and make sure that the
       First channel is the Left channel, and the Second channel is the Right channel.
    4. Add a new dock, and choose the Delay Estimator in the widget list.
    5. Play a Burst signal in your system (using Friture burst generator if you
       will), with a period of one second.
    6. The delay will be displayed in milliseconds and, equivalently, in meters.
       If a meaningless delay is displayed, a low confidence is probably
       displayed too, and it means that the signal is either too weak, or
       saturated in one or both of the input channels, or the signal is
       masked by the ambiant noise in the measurement microphone channel, or the
       room is too reverberant.

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
