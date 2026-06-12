#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Timothée Lecomte

# Backward-compatible entry to the audio ingest seam.

from friture.audio_ingest import FRAMES_PER_BUFFER, SAMPLING_RATE, get_audio_ingest


def AudioBackend():
    return get_audio_ingest()
