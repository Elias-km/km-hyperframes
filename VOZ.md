# Sustitución de locución — solo Node.js

- Ejecutar `bash mejorar-voz.sh` desde el proyecto, con acceso a Internet.
- La voz es **es-ES-AlvaroNeural** (Microsoft Edge TTS mediante la biblioteca `node-edge-tts`).
- El guion de las diez escenas y sus tiempos viven en `mejorar-voz.mjs`.
- El script instala su dependencia npm y FFmpeg si falta y existe Homebrew.
- Se guarda una copia de la locución anterior en `assets/audio/voice-robotica.bak.wav`.
- Se actualiza `assets/audio/voice.wav`, utilizado por la composición HTML/HyperFrames.
- Se crea `renders/contrucciones-pepe-y-manuel-voz-natural.mp4` **sin volver a renderizar las imágenes**; el MP4 anterior no se modifica.
- El servicio de TTS necesita Internet, puede cambiar sus condiciones o fallar temporalmente.
- No ejecutes `make_audio.py` después: es un generador legado que repondría la voz robótica. Esta actualización no utiliza Python; el pipeline antiguo de renderizado en GitHub Actions no se modifica.
