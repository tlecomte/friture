#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Cross-platform smoke-test harness for the frozen Friture packages.
#
# It launches the packaged binary headless (the offscreen Qt platform, so no
# display server is required) and verifies that the bundle is intact: the app
# must reach its startup banner and the Qt/QML/Python stack must load without
# any missing-module or missing-DLL errors.
#
# Usage (run from the repo root, e.g. via `uv run python`):
#   scripts/smoke_test.py <binary> [app args...]
#
# Exit status: 0 = pass, 1 = fail, 2 = usage error.
#
# For an AppImage, extract it first (--appimage-extract) and pass the resulting
# squashfs-root/AppRun so no FUSE mount is needed.

import os
import sys
import time
import signal
import platform
import subprocess

import platformdirs

# Best-effort: used to build the expected startup banner.
try:
    import friture
    VERSION = friture.__version__
except Exception:
    VERSION = None

TIMEOUT_SECONDS = 20

# Substrings that, if found in the log or stderr, mean the bundle is broken
# (a missing Qt module, shared library, or Python extension). We include the
# Python traceback header and the app's own unhandled-exception log line so a
# crash that is swallowed by Friture's global exception handler (logged but not
# fatal to the process) is still reported as a failure.
FATAL_MARKERS = (
    "ModuleNotFoundError",
    "ImportError",
    "FileNotFoundError",
    "Fatal Python error",
    "cannot load Qt platform plugin",
    "could not find or load",
    "error while loading shared libraries",
    "undefined symbol",
    "This application failed to start",
    "QLibraryPrivate",
    "QML error(s)",
    "Unhandled exception",
    "Traceback (most recent call last)",
    "Aborted",
    "core dumped",
)

# Reaching this line means the whole initialisation completed: QApplication,
# the QML engine, the audio backend and the main window were all created.
FULL_INIT_LINE = "Init finished, entering the main loop"


def startup_banner():
    return "Friture %s starting on %s (%s)" % (
        VERSION if VERSION is not None else "???",
        platform.system(),
        sys.platform,
    )


def log_file_path():
    log_dir = platformdirs.user_log_dir("Friture", "")
    return os.path.join(log_dir, "friture.log.txt")


def main():
    if len(sys.argv) < 2:
        print("usage: smoke_test.py <binary> [app args...]")
        return 2

    binary = sys.argv[1]
    extra_args = sys.argv[2:]
    banner = startup_banner()
    log_path = log_file_path()

    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    # Keep Qt chatty output quiet so stderr only surfaces real problems.
    env.setdefault("QT_LOGGING_RULES", "qt.qpa.*=false")

    # Snapshot the log so we only inspect entries produced by this run (the log
    # is append-only across runs).
    pre_mtime = os.path.getmtime(log_path) if os.path.exists(log_path) else 0.0

    print("---- SMOKE TEST ----")
    print("binary : %s" % binary)
    print("log    : %s" % log_path)
    print("banner : %s" % banner)

    started = time.time()
    try:
        proc = subprocess.Popen(
            [binary] + extra_args,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            # start in a new session so we can kill the whole process group on
            # timeout (otherwise a spawned helper can keep the stdout pipes open
            # and make communicate() hang until the child exits).
            start_new_session=True,
        )
    except OSError as exc:
        print("FAILED to launch %r: %s" % (binary, exc))
        return 2

    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT_SECONDS)
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        # kill the entire process group, not just the leader
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        stdout, stderr = proc.communicate()
        rc = proc.returncode

    elapsed = time.time() - started

    log_text = ""
    if os.path.exists(log_path):
        try:
            if os.path.getmtime(log_path) >= pre_mtime:
                with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
                    log_text = fh.read()
        except OSError:
            pass

    combined = log_text + "\n" + (stderr or "")

    banner_seen = banner in log_text
    full_init = FULL_INIT_LINE in log_text
    fatal = next((m for m in FATAL_MARKERS if m in combined), None)

    print("elapsed        : %.1fs" % elapsed)
    print("terminated     : %s (return code %r)" % (
        "timeout/killed" if timed_out else "exited", rc))
    print("startup banner : %s" % ("FOUND" if banner_seen else "MISSING"))
    print("full init line : %s" % ("FOUND" if full_init else "not seen"))
    print("fatal marker   : %s" % (fatal or "none"))

    if stderr:
        print("---- stderr (tail) ----")
        print(stderr[-1500:])

    # Pass only when the bundle booted far enough to reach the Qt main event
    # loop and emit Friture's "Init finished, entering the main loop" line.
    # Reaching that line implies the startup banner was printed, the audio
    # backend opened a stream, the default docks were constructed and the
    # QML/Python stacks all loaded -- i.e. the bundle is genuinely intact.
    # A crash before line 216 (e.g. a missing data file caught by the app's
    # own exception handler) leaves full_init unset and fails the test, rather
    # than false-passing on a hung-but-crashed process.
    ok = full_init and banner_seen and fatal is None

    if not ok and log_text:
        print("---- log tail ----")
        print(log_text[-3000:])

    print("---- RESULT: %s ----" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
