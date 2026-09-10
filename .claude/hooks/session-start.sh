#!/bin/bash
# SessionStart hook: make the video-production scripts runnable in Claude Code on the web.
# Installs ffmpeg (static, via imageio-ffmpeg) and the optional extras, then runs doctor.py.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"
REQ="squads/video-production/scripts/requirements.txt"

if [ -f "$REQ" ]; then
  python3 -m pip install -q -r "$REQ" 2>&1 | grep -v "WARNING: Running pip" || true
fi

# faster-whisper models come from Hugging Face; keep them inside the cached container state.
mkdir -p "$CLAUDE_PROJECT_DIR/.cache/huggingface"
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export HF_HOME=\"$CLAUDE_PROJECT_DIR/.cache/huggingface\"" >> "$CLAUDE_ENV_FILE"
  echo "export PYTHONDONTWRITEBYTECODE=1" >> "$CLAUDE_ENV_FILE"
fi

python3 squads/video-production/scripts/doctor.py || true
