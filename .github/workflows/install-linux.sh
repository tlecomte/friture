#!/bin/bash

set -x

uv run python -c 'import sys; print(sys.version)'

sudo apt-get update
sudo apt-get install -y fuse # AppImages require FUSE to run

# when PyInstaller collect libraries, it ignores libraries that are not found on the host.
# Those missing libs prevent proper startup.
# For example, PyQt6 bundles Qt6 libs that depend on libxcb-xinerama.so.0
# which would not be bundled unless explicitly installed.
sudo apt-get install libxcb-xinerama0
sudo apt-get install libxkbcommon-x11-0
# The Qt6/PyQt6 GUI stack links against the Mesa EGL/GL/X11/dbus/fontconfig
# stack. PyInstaller only bundles libs it can resolve with ldd at build time,
# so install them here too -- otherwise the bundled .so files emit
# "libEGL.so.1: cannot open shared object file" at import time.
sudo apt-get install -y libegl1 libgl1 libglx-mesa0 libgl1-mesa-dri

# dependencies to build PortAudio
sudo apt-get install -y libasound-dev
sudo apt-get install -y libjack-dev

# Provide a virtual audio device so the headless smoke test (and the frozen app)
# can fully start: PortAudio needs a default output device to enumerate, and
# Friture's audio backend raises (hanging in an error dialog) otherwise.
sudo apt-get install -y pulseaudio pulseaudio-utils libasound2-plugins
pulseaudio --start --exit-idle-time=-1 2>/dev/null || true
pactl load-module module-null-sink sink_name=friture_smoke sink_properties=device.description="Friture+smoke+test" 2>/dev/null || true

# build PortAudio 19.7.0 from scratch (required for Jack fixes on distributions using PipeWire)
wget https://github.com/PortAudio/portaudio/archive/refs/tags/v19.7.0.tar.gz
tar -xvf v19.7.0.tar.gz
cd portaudio-19.7.0
./configure --prefix=$PWD/portaudio-install
make
make install
ls -laR portaudio-install
cd ..

uv run pyinstaller friture.spec -y --log-level=DEBUG

# ---- AppDir assembly ----
# Friture is frozen with PyInstaller, so dist/friture/ is already a self-contained
# bundle (Python + Qt6 + PortAudio). We lay it into a standard AppDir and let
# appimagetool turn it into an AppImage (+ .zsync for AppImageUpdate).

# zsyncmake (from the zsync package) lets appimagetool emit the .zsync delta
# file that powers in-App AppImageUpdate.
sudo apt-get install -y zsync

APPDIR=AppDir
rm -rf $APPDIR
mkdir -p $APPDIR/usr/bin $APPDIR/usr/lib/x86_64-linux-gnu

# drop the PyInstaller bundle into usr/bin/ (preserves the bundled libs' layout)
cp -R dist/friture/* $APPDIR/usr/bin/

# bundle the source-built PortAudio so sounddevice's ctypes.find_library() resolves it
cp portaudio-19.7.0/portaudio-install/lib/libportaudio.so* $APPDIR/usr/lib/x86_64-linux-gnu/

# PortAudio is loaded via ctypes.CDLL (not an ELF NEEDED of the binary), so the
# recursive ldd closure below cannot reach its own ALSA/JACK deps -- bundle them
# explicitly, the same way the legacy pkg2appimage recipe's audio ingredients did.
ldd portaudio-19.7.0/portaudio-install/lib/libportaudio.so.2 2>/dev/null \
  | grep '=>' | awk '{print $3}' | while read -r dep; do
    case "$dep" in
      *libasound*|*libjack*|*libportaudio*) cp -nL "$dep" $APPDIR/usr/lib/x86_64-linux-gnu/ 2>/dev/null ;;
    esac
  done

# The frozen Qt6/PyQt6 GUI stack pulls in a large transitive set of system libs
# (EGL, GL, X11, dbus, fontconfig, freetype...) that PyInstaller may skip if they
# are not installed at build time. Build the full ldd closure of the bundle and
# ship any system libraries we still don't provide, so the AppImage is
# self-contained on a minimal host.
gather_runtime_libs() {
  local libdir="$1"
  local -a queue=("$APPDIR/usr/bin/friture")
  local -A seen=()
  # seed with every shared object the freeze shipped
  while IFS= read -r -d '' so; do queue+=("$so"); done \
    < <(find "$APPDIR/usr/bin" -type f -name '*.so*' -print0 2>/dev/null)
  local idx=0
  while [ "$idx" -lt "${#queue[@]}" ]; do
    local f="${queue[$((idx++))]}"
    [ -e "$f" ] || continue
    [ -n "${seen[$f]:-}" ] && continue
    seen[$f]=1
    # field 3 of `ldd` is the resolved path when the dep was found (-> "/...")
    while IFS= read -r dep; do
      case "$dep" in
        /lib*/ld-linux*) continue ;;   # never bundle the ELF loader
        /*) cp -nL "$dep" "$libdir"/ 2>/dev/null || true
            queue+=("$dep") ;;
      esac
    done < <(ldd "$f" 2>/dev/null | awk '$3 ~ /^\// {print $3}')
  done
}
gather_runtime_libs "$APPDIR/usr/lib/x86_64-linux-gnu"

# desktop entry + icon
cp appimage/friture.desktop $APPDIR/friture.desktop
cp resources/images-src/window-icon.svg $APPDIR/friture.svg

# AppRun shim: expose the bundled PortAudio to the dynamic loader.
# (Only the PortAudio dir is added to LD_LIBRARY_PATH; the frozen binary finds
#  Qt/Python via its $ORIGIN rpath, so validation must not touch that lookup.)
cat > $APPDIR/AppRun <<'EOF'
#!/bin/sh
HERE="$(dirname "$(readlink -f "${0}")")"
export LD_LIBRARY_PATH="$HERE/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
exec "$HERE/usr/bin/friture" "$@"
EOF
chmod +x $APPDIR/AppRun

# ---- Build the AppImage (+ .zsync for AppImageUpdate) with appimagetool ----
# appimagetool is the canonical AppImage packager: it turns this AppDir into an
# AppImage, validates the desktop file, creates the .DirIcon, and embeds update
# info (generating the .zsync when zsyncmake is available).
wget -q -O appimagetool https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod a+x appimagetool

export ARTIFACT_FILENAME=friture-$(uv run python -c 'import friture; print(friture.__version__)')-$(date +'%Y%m%d').AppImage
echo $ARTIFACT_FILENAME

# update information lets AppImageUpdate do binary delta updates.
# Format must be a recognized zsync-style scheme (appimagetool validates it).
# For GitHub releases, gh-releases-zsync lets AppImageUpdate find the latest
# release asset automatically; for non-release builds we embed a no-update
# placeholder so the .zsync file is still produced for CI inspection.
if [[ "$GITHUB_REF" == refs/tags/* ]]; then
  UPDATE_INFO="gh-releases-zsync|tlecomte|friture|latest|friture*.AppImage.zsync"
else
  UPDATE_INFO="zsync|https://example.invalid/never"
fi

./appimagetool -u "$UPDATE_INFO" $APPDIR $ARTIFACT_FILENAME
ls -la $ARTIFACT_FILENAME $ARTIFACT_FILENAME.zsync 2>/dev/null
du -hs $ARTIFACT_FILENAME

# sanity check: a sane Friture AppImage is well under 200 MB.
# A much larger result usually means a packaging step duplicated the Qt/Python
# libs, so fail loudly rather than ship a bloated artifact.
SIZE_BYTES=$(stat -c%s "$ARTIFACT_FILENAME")
echo "AppImage size: $SIZE_BYTES bytes"
if [ "$SIZE_BYTES" -gt 200000000 ]; then
  echo "ERROR: AppImage is unexpectedly large (>200MB); aborting."
  exit 1
fi
