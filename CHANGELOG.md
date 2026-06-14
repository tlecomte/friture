# Changelog

All notable changes to this project will be documented in this file.

## [0.59] - 2026-06-14

### Added
- **Per-device calibration:** SPL offset is now stored separately for each audio device. Switching between a Focusrite interface and a built-in mic no longer clobbers your calibration — each device remembers its own offset.
- **Calibration age display:** The Settings dialog now shows "Last calibrated: today / N days ago" so you know how fresh your calibration is without guessing.
- **Stale mic cal warning:** When a microphone calibration file has been moved or deleted from disk, a warning appears in Settings so you can reload it before measurements drift silently.
- **CAL button on dB Levels dock:** You can trigger a calibration pass directly from the Levels dock without opening Settings — click CAL, play a 94 dB reference tone, enter the target level.

### Fixed
- Device switch during a session no longer silently resets calibration to 0 dB. The previous code stored a stale QSettings reference that read from the wrong path after the `AudioBackend` group closed.
- QSettings group stack can no longer become permanently unbalanced if corrupted mic-cal data raises an exception during device profile restore.
- Calibration age display no longer shows negative days if the system clock skews backward.
- Input capture now restarts correctly after a device switch even if settings loading throws an exception.
- Timezone-aware ISO timestamps in calibration age display no longer crash with a TypeError.
- Stale mic cal warning now clears the summary text (previously showed stale + default prompt simultaneously).
- Calibration timestamp is now set before emitting the `changed` signal (previously listeners saw the old value on the first update).

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
