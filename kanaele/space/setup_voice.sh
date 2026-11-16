#!/usr/bin/env bash
# George (Kokoro-82M, Apache-2.0) + word timings (faster-whisper) for the narrated videos. Idempotent, ~1-3 min on a fresh container.
set -e
command -v espeak-ng >/dev/null || (apt-get update -qq && apt-get install -y -qq espeak-ng)
python3 -c "import kokoro_onnx" 2>/dev/null || python3 -m pip install -q --disable-pip-version-check kokoro-onnx
python3 -c "import faster_whisper" 2>/dev/null || python3 -m pip install -q --disable-pip-version-check faster-whisper
python3 -c "import skia" 2>/dev/null || { apt-get install -y -qq libegl1 libgl1 || true; python3 -m pip install -q skia-python soundfile scipy pillow; }
mkdir -p ~/.cache/kokoro
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s ~/.cache/kokoro/$f ] || curl -sSL -o ~/.cache/kokoro/$f https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f
done
echo "voice setup OK"
