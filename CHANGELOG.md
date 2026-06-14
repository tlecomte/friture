# Changelog

All notable changes to this project will be documented in this file.

## [0.58] - 2026-06-13

### Added
- Reference curve overlays on FFT Spectrum and Octave Spectrum docks. Choose from Flat, Pink noise, A-weighting, or House curve targets with an adjustable dB offset. The overlay appears as a gray line on the spectrum display so you can compare your measurement against a reference response.

### Fixed
- Pink noise FFT reference now correctly falls at −10 dB/decade (previously rose with frequency, which was wrong).
- Reference overlay now renders on top of the spectrum fill rather than behind it.

## [0.57] - 2026-06-12

### Added
- Global input calibration with SPL offset and microphone calibration file support (.cal / factory .txt formats).
- Per-dock calibration override: each analysis dock can use the global calibration or its own local offset.
- Frequency-dependent mic correction applied to Spectrum, Octave Spectrum, and Spectrogram displays.
- Calibrated dB Levels dock with A/B/C-weighting and configurable response time.
- Reference curve overlays on FFT and octave spectrum (shipped as feature/reference-curves).
