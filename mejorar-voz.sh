#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v node >/dev/null || ! command -v npm >/dev/null; then
  echo 'Falta Node.js/NPM. Usa nvm use --lts.' >&2
  exit 1
fi
if ! command -v ffmpeg >/dev/null; then
  if command -v brew >/dev/null; then brew install ffmpeg
  else echo 'Falta ffmpeg y Homebrew no está instalado.' >&2; exit 1; fi
fi
if [ ! -f package.json ]; then
  printf '{"name":"km-hyperframes","private":true,"type":"module"}\n' > package.json
fi
npm install --save-dev --no-audit --no-fund node-edge-tts@1.2.12
if [ -f .gitignore ]; then
  grep -qxF 'assets/audio/voice-robotica.bak.wav' .gitignore || printf '\nassets/audio/voice-robotica.bak.wav\n' >> .gitignore
fi
node mejorar-voz.mjs
if [ -f 'renders/contrucciones-pepe-y-manuel-voz-natural.mp4' ]; then
  open 'renders/contrucciones-pepe-y-manuel-voz-natural.mp4'
fi
