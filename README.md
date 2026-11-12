# Contrucciones Pepe y Manuel — el último bootcamp

Vídeo de parodia de los anuncios «gana dinero con este bootcamp» y de la sustitución de trabajadores técnicos por IA. Proyecto **independiente**. La empresa y la promesa salarial son ficticias.

## Archivo listo para compartir

`renders/contrucciones-pepe-y-manuel.mp4` (puede entregarse fuera del repositorio, pues los MP4 están ignorados por Git).

## Edición en HyperFrames

El archivo raíz `index.html` contiene la composición `pepe-manuel` de 69 s. Cada escena tiene atributos temporales (`class="clip"`, `data-start`, `data-duration` y `data-track-index`). El movimiento está definido como una línea de tiempo **determinista y seekable** en `animation.js`, registrada en `window.__timelines`, con CSS en `styles.css`. Audio y voz en `assets/audio/`.

HyperFrames es un proyecto Apache-2.0 de HeyGen: https://github.com/heygen-com/hyperframes

Cuando tengas Internet y Node.js 22+:

```sh
npx hyperframes skills update
npx hyperframes check --json
npx hyperframes preview
npx hyperframes render
```

El render reproducible de esta entrega se ha generado por un capturador local (`render_local.py`) y FFmpeg, porque este entorno no permite instalar la CLI desde npm. **No se ha podido verificar aquí la ejecución del CLI oficial de HyperFrames**. Se entrega el HTML editable con atributos de composición y una línea de tiempo adaptada; si el CLI requiriese ajustes, habría que revisarlos tras instalarlo.

## Render local sin dependencias npm

Requiere Python, `playwright` + Chromium y FFmpeg:

```sh
python render_local.py
```

Para reproducir/inspeccionar el HTML sin compilar:

```sh
python -m http.server 8080
# abrir http://localhost:8080/?preview=1 o http://localhost:8080/?t=34
```

## Archivos

- `index.html`: montaje de escenas, capas y audio.
- `styles.css`: estilo de anuncio estafa-tech y el cambio a obra.
- `animation.js`: animaciones deterministas, temporización y `setFrame(t)`.
- `assets/audio/voice.wav`: voz de maqueta en español.
- `assets/audio/music.wav`: música y efectos originales sintetizados.
- `render_local.py`: exportación local MP4 usando Chromium + FFmpeg.
- `BRIEF.md`, `STORYBOARD.md`, `SCRIPT.md`: documentación de dirección creativa.

## Repositorio y publicación

Repositorio **ya creado**: https://github.com/Elias-km/km-hyperframes (público).

El script `publicar-github.sh` sube esta carpeta al repositorio **existente** sin sobrescribir ni forzar cambios. Se ejecuta desde macOS con GitHub CLI (`brew install gh`, `gh auth login`) autenticado con una cuenta que tenga permisos de escritura en `Elias-km/km-hyperframes`:

```sh
./publicar-github.sh
```

Si GitHub rechaza el push porque el repositorio tiene commits previos, el script se detiene para protegerlos. En ese caso, clona el repositorio y copia estos archivos en la copia local antes de hacer commit/push.

Los ficheros `.wav` se incluyen en la versión completa del proyecto. Si tienes solo el paquete ligero de código fuente, regenera la música y la locución ejecutando `python make_audio.py` (requiere `numpy` y `espeak`). Para un render local necesitas también `playwright`, Chromium y FFmpeg, además de `Pillow` si quieres el storyboard.

### Descargar el vídeo sin generarlo en tu equipo

Tras subir el código a `main`, GitHub Actions ejecuta `.github/workflows/render.yml`, genera el audio y el MP4 y publica el resultado como artefacto `contrucciones-pepe-y-manuel-video`. Para descargarlo desde GitHub: pestaña **Actions** → flujo **Renderizar anuncio MP4** → ejecución finalizada → **Artifacts**. No es necesario instalar HyperFrames ni FFmpeg en tu Mac para obtener ese vídeo. La ejecución automática todavía no ha sido verificada en GitHub.

Este proyecto no utiliza marcas comerciales reales de consultoras ni materiales de terceros protegidos; la música original se sintetiza y la locución de maqueta usa eSpeak. Las promesas salariales son parte de una parodia.

## Remate de Telegram (v2)

La escena final (63–69 s) incorpora la frase «Pide tu código de descuento en el canal Inversiones Cripto de Telegram» con locución y rótulo. Es una parodia: **no se afirma que exista una promoción real**. Para modificarlo, edita la escena `s9` de `index.html` y el último texto en `make_audio.py`, luego regenera audio y vídeo.
