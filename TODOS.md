# TODOs


## Per-device input calibration

**What:** Associate calibration offset (and optionally mic cal file) with a specific audio input device identity, not just globally.

**Why:** Today the global calibration follows the app to any interface. An engineer who calibrated with Interface A and then plugs in Interface B gets the wrong SPL reading silently.

**Context:** `GlobalCalibrationService` stores `offset_db` and `mic_cal_file_path` in QSettings with no device identity. Use a composite `(sanitized_name, host_api_name)` key for stability across USB re-enumeration. Schema: `GlobalCalibration/profiles/{device_key}/offsetDb` (profiles-compatible for future named profiles). Read device identity from the live `InputDeviceCatalog` at save time, not from QSettings, to avoid selected-vs-active mismatch. Fall back to global flat keys for legacy user configs (no deletion of old keys for at least 2 releases).

**Depends on:** feature/global-calibration landing first. ✓ (merged)


## Stale mic cal file UX warning

**What:** When the app restarts and the configured mic cal file path no longer exists on disk, display a visible warning in the Settings calibration group rather than silently falling back to the cached arrays.

**Why:** Silent fallback means the engineer could be running stale frequency correction without knowing it. A yellow warning label ("Mic cal file not found — using cached data") makes this transparent.

**Context:** `GlobalCalibrationService.restoreState` already handles this with a try/except that falls back to `_mic_cal_from_settings_cache`. Warning condition: `os.path.exists(mic_cal_file_path)` is False (not just `mic_cal is None` — file-missing and corrupt-file are both covered this way). Fix in `Settings_Dialog._sync_mic_cal_form`.

**Depends on:** feature/global-calibration landing first. ✓ (merged)


## Guided calibration wizard

**What:** A modal/inline wizard that shows a live SPL reading and walks the user through calibration (plug in calibrator → hold to mic → click Calibrate → done) in under 60 seconds.

**Why:** The design doc's primary success criterion is "under 2 minutes from first launch to calibrated data." The current UI (dB offset text box) requires the engineer to already know their offset. The wizard eliminates that expertise requirement.

**Context:** `GlobalCalibrationService.calibrate_from_live_reading()` (landing in the calibration polish sprint) is the seed. The wizard wraps it with a live SPL display and guided copy. Quick-recalibrate button on the dB Levels dock is the entry point. Full design needed before implementation — mock in Figma or paper first and time-test against Smaart's calibration flow.

**Priority:** P1 for product vision.
**Depends on:** Calibration polish sprint (per-device cal + quick-recalibrate button).


## Platform stability sprint

**What:** Fix crashes and platform compatibility: PyQt6 migration (#415 — scoped enum errors), AppImage on Arch Linux (#412), GUI freeze on Linux (#409), segfault (#410), UnicodeDecodeError on Windows (#360).

**Why:** PyQt6 unlocks macOS arm64 packaging (#417) — Apple Silicon is the target FOH engineer's primary laptop. Crashes block adoption before users ever reach the calibration features.

**Context:** PyQt6 migration is the largest item — scoped enums (`Qt.AlignmentFlag.AlignLeft` instead of `Qt.AlignLeft`) permeate the codebase. The GUI freeze (#409) is likely a thread/GIL issue in the audio → Qt signal path. AppImage issues may be distribution-level and separate from the freeze. Tackle PyQt6 first (unlocks macOS), then crashes.

**Priority:** P2 for sequencing (calibration polish ships first), P1 for reach (Apple Silicon users).
**Depends on:** nothing.


## Dual-channel TF / live room EQ

**What:** Magnitude-only transfer function between two channels (reference signal + measurement mic). Display ratio spectrum showing how the room modifies the source signal.

**Why:** This is the feature that makes friture a real Smaart alternative for PA alignment. A working FOH engineer can align subs, mains, and fills with a magnitude TF in under 10 minutes. Phase/coherence deferred to v2 per design doc.

**Context:** No TF infrastructure exists today. Issue #302 describes the user workflow. friture already supports dual-channel input (stereo). The key DSP: compute FFT of both channels, divide, display in dB. The hard UX problem is delay compensation (reference delay) — v1 can skip it and document the limitation. Reference: SATlive and OSM both have magnitude TF; Smaart's advantage is speed + coherence.

**Priority:** P1 for product vision.
**Depends on:** Calibration polish sprint (dual-channel calibration must be solid first).
