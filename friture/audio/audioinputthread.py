import random
import sys
import threading
import time
from PyQt5 import QtCore
from numpy import ndarray
import logging

class AudioInputThread(QtCore.QObject):

    """Thread that reads from the audio input in a loop"""

    data_available = QtCore.pyqtSignal(ndarray)

    def __init__(self, microphone, samplerate, channels=None, blocksize=None):
        QtCore.QObject.__init__(self)

        self.microphone = microphone
        self.samplerate = samplerate
        self.channels = channels
        self.blocksize = blocksize

        self.logger = logging.getLogger(__name__)

    def start(self):
        self._stopRequest = threading.Event()
        self._thread = threading.Thread(target=self.run)
        self._thread.start()

    def run(self):
        self.logger.info("starting thread")
        with self.microphone.recorder(self.samplerate, self.channels, self.blocksize) as recorder:
            while not self._stopRequest.isSet():
                data = recorder.record(numframes=4096)
                self.data_available.emit(data)

    def stop(self, timeout=None):
        self._stopRequest.set()
        self._thread.join(timeout)
