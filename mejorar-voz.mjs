import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { setTimeout as sleep } from 'node:timers/promises';
import { copyFileSync, existsSync, mkdirSync, mkdtempSync, renameSync, rmSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const root = process.cwd();
const totalSeconds = 69;
const voice = 'es-ES-AlvaroNeural';
const speech = [
  [0.40, 6.00, '¿Quieres ganar seis mil euros al mes? ¡Sin experiencia, sin riesgo, y sin saber de qué estamos hablando!'],
  [6.22, 5.60, 'Basta con dos habilidades: abrir LinkedIn... y escribir hazlo en un prompt.'],
  [12.25, 6.60, 'Pero tu consultora acaba de descubrir la inteligencia artificial. Diez desarrolladores... ahora son un prompt.'],
  [19.22, 4.60, 'Te dijeron que eras estratégico. Que erais una gran familia. Y ahora el bot te hace la daily.'],
  [24.20, 6.50, '¿Otro curso de trading? ¡No! La inteligencia artificial te dibuja un muro... pero no te lo levanta.'],
  [31.30, 7.20, '¡Presentamos Contrucciones Pepe y Manuel! El primer bootcamp full stack... ¡de ladrillo!'],
  [39.22, 8.50, 'Frontend: fachadas. Backend: tabiques. DevOps: la hormigonera. ¡Por fin, un trabajo con cimentación continua!'],
  [48.25, 6.50, '¡Salario de por vida! Bueno... hasta que haya goteras. ¡Aquí los tickets nunca se acaban!'],
  [55.25, 7.50, 'Apúntate ya. De senior developer... ¡a señor de la obra! Contrucciones Pepe y Manuel.'],
  [63.25, 5.55, '¡Pide tu código de descuento en el canal Inversiones Cripto de Telegram!']
];
const run = (program, args, options = {}) => execFileSync(program, args, { stdio: 'inherit', ...options });
const read = (program, args) => execFileSync(program, args, { encoding: 'utf8' }).trim();
// km-voice-cache-v2
const tmp = join(root, '.voice-cache');
mkdirSync(tmp, { recursive: true });
const audioDir = join(root, 'assets', 'audio');
const outputDir = join(root, 'renders');
mkdirSync(audioDir, { recursive: true });
mkdirSync(outputDir, { recursive: true });

try {
  const inputs = [];
  const filters = [];
  const streams = [];
  for (const [i, [start, slot, text]] of speech.entries()) {
    const hash = createHash('sha256').update(voice + ':' + text).digest('hex').slice(0, 12);
    const file = join(tmp, `${i}-${hash}.mp3`);
    console.log(`Locución ${i + 1}/${speech.length}`);
    if (process.env.SKIP_TTS !== '1') {
      if (!existsSync(file) || statSync(file).size < 500) {
        const cli = join(root, 'node_modules', '.bin', 'node-edge-tts');
        const args = ['-t', text, '-f', file, '-v', voice, '-l', 'es-ES', '-r', '+10%'];
        let completed = false;

        for (let attempt = 1; attempt <= 4; attempt++) {
          const result = spawnSync(cli, args, {
            encoding: 'utf8',
            timeout: 45000
          });

          if (result.status === 0 && existsSync(file) && statSync(file).size >= 500) {
            completed = true;
            break;
          }

          const details = [
            result.stdout,
            result.stderr,
            result.error?.message
          ].filter(Boolean).join('\n');

          if (attempt < 4 && /429|too many requests|rate.?limit/i.test(details)) {
            const pause = [15, 30, 60][attempt - 1];
            console.warn('Servicio saturado (429). Reintento en ' + pause + ' segundos...');
            await sleep(pause * 1000);
          } else {
            throw new Error('Fallo en locución ' + (i + 1) + ': ' + details.slice(-800));
          }
        }

        if (!completed) throw new Error('No se pudo generar la locución ' + (i + 1));
        await sleep(6000);
      } else {
        console.log('  Recuperada de caché');
      }
    } else {
      run('ffmpeg', ['-v', 'error', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3', '-q:a', '7', file]);
    }
    if (!existsSync(file) || statSync(file).size < 500) throw new Error(`La escena ${i + 1} no tiene audio válido`);
    const seconds = Number(read('ffprobe', [
      '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file
    ]));
    if (!Number.isFinite(seconds) || seconds <= 0) throw new Error(`Audio inválido en escena ${i + 1}`);
    const usable = slot - 0.15;
    const speed = Math.max(1, seconds / usable);
    if (speed > 1.3) console.warn(`Aviso: la frase ${i + 1} se acelera x${speed.toFixed(2)} para encajar.`);
    inputs.push('-i', file);
    filters.push(`[${i}:a]aresample=44100,atempo=${speed.toFixed(5)},atrim=duration=${usable.toFixed(3)},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.035,adelay=${Math.round(start * 1000)}:all=1[v${i}]`);
    streams.push(`[v${i}]`);
  }
  const voicePath = join(audioDir, 'voice.wav');
  const staging = join(audioDir, 'voice-neural.tmp.wav');
  const backup = join(audioDir, 'voice-robotica.bak.wav');
  filters.push(`${streams.join('')}amix=inputs=${speech.length}:duration=longest:normalize=0,alimiter=limit=0.93,apad=whole_dur=${totalSeconds},atrim=duration=${totalSeconds}[aout]`);
  run('ffmpeg', [
    '-v', 'error', '-y', ...inputs, '-filter_complex', filters.join(';'), '-map', '[aout]',
    '-ac', '1', '-ar', '44100', '-c:a', 'pcm_s16le', staging
  ]);
  if (existsSync(voicePath) && !existsSync(backup)) copyFileSync(voicePath, backup);
  renameSync(staging, voicePath);
  const video = join(outputDir, 'contrucciones-pepe-y-manuel.mp4');
  const newVideo = join(outputDir, 'contrucciones-pepe-y-manuel-voz-natural.mp4');
  if (existsSync(video) && existsSync(join(audioDir, 'music.wav'))) {
    run('ffmpeg', [
      '-v', 'error', '-y', '-i', video, '-i', join(audioDir, 'music.wav'), '-i', voicePath,
      '-filter_complex', '[1:a]volume=0.72[m];[2:a]volume=1.1[v];[m][v]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]',
      '-map', '0:v:0', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
      '-t', String(totalSeconds), '-movflags', '+faststart', newVideo
    ]);
    console.log(`✅ Vídeo listo: ${newVideo}`);
  } else {
    console.log('✅ Voz lista para HyperFrames:', voicePath);
    console.log('Falta el vídeo original o music.wav; no se ha mezclado el MP4.');
  }
} finally {
  // Conservar audios para futuras ejecuciones.
}
