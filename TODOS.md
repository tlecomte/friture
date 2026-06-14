# TODOs




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


## Completed

### Per-device input calibration
**Completed:** v0.59 (2026-06-14)
SPL offset stored per device in `GlobalCalibration/profiles/{key}/offsetDb`. Device key = sanitized `name__host_api`. Falls back to legacy flat key.

### Stale mic cal file UX warning
**Completed:** v0.59 (2026-06-14)
Yellow warning label in Settings when mic cal file path exists but file is missing from disk.
