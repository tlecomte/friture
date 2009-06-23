# -*- coding: utf-8 -*-

import numpy
import audiodata
import audioproc

class ProcClass():
	def __init__(self, parent=None):
		self.adatabuffer = None

	def process(self, adata, fft_size):
		if adata.nframes < fft_size:
			self.adatabuffer = audiodata.concatenate(self.adatabuffer, adata)
			if self.adatabuffer.nframes < fft_size:
				return
			else:
				self.adata = self.adatabuffer
			self.adatabuffer = None
		else:
			self.adata = adata

		spectrograms = None
		# FIXME use linspace here
		for point in numpy.arange(0, self.adata.nframes/fft_size)*fft_size:
			spe = audioproc.analyzelive(self.adata, point, fft_size)
			if spectrograms == None:
				spectrograms = spe
			else:
				spectrograms = numpy.vstack((spectrograms,spe))

		return spectrograms