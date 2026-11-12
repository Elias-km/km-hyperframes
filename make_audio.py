#!/usr/bin/env python3
"""Fully offline original soundtrack, foley and comic Spanish eSpeak demo VO."""
from pathlib import Path
import subprocess, tempfile, wave
import numpy as np

SR=22050
DURATION=69
OUT=Path(__file__).parent/'assets'/'audio'
OUT.mkdir(parents=True,exist_ok=True)
SEGS=[
(0.40,6.00,'¿Quieres ganar seis mil euros al mes? ¡Sin experiencia, sin riesgo, y sin saber de qué estamos hablando!'),
(6.22,5.6,'Basta con dos habilidades: abrir Linkedin... y escribir hazlo en un prompt.'),
(12.25,6.6,'Pero tu consultora acaba de descubrir la inteligencia artificial. Diez desarrolladores... ahora son un prompt.'),
(19.22,4.6,'Te dijeron que eras estratégico. Que erais una gran familia. Y ahora el bot te hace la daily.'),
(24.20,6.50,'¿Otro curso de trading? ¡No! La inteligencia artificial te dibuja un muro... pero no te lo levanta.'),
(31.30,7.2,'¡Presentamos Contrucciones Pepe y Manuel! El primer bootcamp full stack... ¡de ladrillo!'),
(39.22,8.5,'Frontend: fachadas. Backend: tabiques. Devops: la hormigonera. ¡Por fin, un trabajo con cimentación continua!'),
(48.25,6.5,'¡Salario de por vida! Bueno... hasta que haya goteras. ¡Aquí los tickets nunca se acaban!'),
(55.25,7.5,'Apúntate ya. De senior developer... ¡a señor de la obra! Contrucciones Pepe y Manuel.'),
(63.25,5.55,'¡Pide tu código de descuento en el canal Inversiones Cripto de Telegram!')
]

def save_pcm(path, arr, sr=SR):
    arr=(np.clip(arr,-1,1)*32767).astype('<i2')
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(arr.tobytes())

def interp_audio(data,old_rate,new_rate=SR):
    return np.interp(np.arange(int(len(data)*new_rate/old_rate))*old_rate/new_rate,np.arange(len(data)),data).astype(np.float32)

voice=np.zeros(DURATION*SR,np.float32)
print('VOICE SEGMENTS:')
for idx,(start,available,txt) in enumerate(SEGS):
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'speech.wav'
        subprocess.run(['espeak','-v','es+m3','-s','190','-p','49','-a','180','-w',str(f),txt],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        with wave.open(str(f),'rb') as w:
            raw=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype('float32')/32768
            segment=interp_audio(raw,w.getframerate())
    # fit audio to scene without losing words; cap at 1.18x acceleration
    if len(segment)>int((available-.15)*SR):
        wanted=int((available-.15)*SR)
        segment=np.interp(np.linspace(0,len(segment)-1,wanted),np.arange(len(segment)),segment).astype(np.float32)
    fade=min(750,len(segment)//8)
    segment[:fade]*=np.linspace(0,1,fade)
    segment[-fade:]*=np.linspace(1,0,fade)
    a=int(start*SR);b=min(a+len(segment),len(voice))
    voice[a:b]+=segment[:b-a]*.85
    print(idx,round(len(segment)/SR,2),'sec', txt[:50])
# limiter + slight warm clipping
voice=np.tanh(voice*1.0)*.8
save_pcm(OUT/'voice.wav',voice)

# Original instrumental: two halves (tech techno, then cartoon construction rock).
rng=np.random.default_rng(271828)
n=DURATION*SR
music=np.zeros(n,dtype=np.float32)

# steady 120 BPM pulse
beat=.5
notes_tech=[(49,53,56),(46,49,53),(44,48,51),(47,51,54)]
notes_build=[(45,49,52),(43,47,50),(41,45,48),(44,48,51)]

def tone(freq,dur,kind='lead'):
    k=int(SR*dur);t=np.arange(k)/SR
    if kind=='bass':
        y=np.sin(2*np.pi*freq*t)+.27*np.sin(2*np.pi*freq*2*t)
        env=np.exp(-t*5)
    elif kind=='pluck':
        y=np.sin(2*np.pi*freq*t)+.28*np.sin(2*np.pi*2*freq*t)+.08*np.sin(2*np.pi*4*freq*t)
        env=np.exp(-t*7)
    else:
        y=np.sin(2*np.pi*freq*t)+.25*np.sin(2*np.pi*3*freq*t)
        env=(1-np.exp(-t*70))*np.exp(-t*1.2)
    return (y*env).astype('float32')

def put(at,data,gain=1):
    a=int(at*SR);b=min(len(music),a+len(data))
    if a<len(music) and b>a:music[a:b]+=data[:b-a]*gain

for j in range(int(DURATION/beat)*2):
    tm=j*beat/2
    if tm>=DURATION: break
    # Open and close hi-hats
    dur=.12 if j%2==0 else .07
    samples=int(dur*SR);tn=np.arange(samples)/SR
    noise=rng.normal(0,1,samples).astype('float32')
    hat=noise*np.exp(-tn*50)
    put(tm,hat,.025 if tm<31 else .019)
for j in range(int(DURATION/beat)+1):
    tm=j*beat
    if tm>=DURATION:break
    kick_t=np.arange(int(.27*SR))/SR
    phase=2*np.pi*(62*kick_t+36*.04*(1-np.exp(-kick_t/.04)))
    kick=np.sin(phase)*np.exp(-kick_t*17)
    put(tm,kick,.21 if tm<31 else .22)
    if j%2:
        clap_t=np.arange(int(.15*SR))/SR
        clap=rng.normal(0,1,len(clap_t))*np.exp(-clap_t*25)
        put(tm,clap,.070)
    bar=j//8
    chords=notes_tech if tm<31 else notes_build
    note=chords[bar%len(chords)][0]
    f=440*2**((note-69)/12)
    put(tm,tone(f/2,.45,'bass'),.085)
    if j%2==0:
        ar=chords[bar%len(chords)][(j//2)%3]
        f2=440*2**((ar+12-69)/12)
        put(tm+.13,tone(f2,.33,'pluck'),.050 if tm<31 else .055)
    if j%4==0:
        for chord_note in chords[bar%len(chords)]:
            f3=440*2**((chord_note+12-69)/12)
            put(tm,tone(f3,1.6,'pad'),.017)

# original sound design: swooshes / digital beeps / hammer impact
for cut in [6,12,19,24,31,39,48,55,63]:
    d=.32;ts=np.arange(int(d*SR))/SR
    s=rng.normal(0,1,len(ts))*.13*np.sin(np.pi*ts/d)**2
    put(cut-.19,s,1)
    if cut>=31:
        e=np.arange(int(.40*SR))/SR
        clang=(np.sin(2*np.pi*710*e)+.34*np.sin(2*np.pi*1214*e)+.20*np.sin(2*np.pi*1560*e))*np.exp(-e*13)
        put(cut+.03,clang,.075)
# sparkle at intro
for t0 in [0,.8,1.6,2.4]:
    tx=np.arange(int(.38*SR))/SR
    p=np.sin(2*np.pi*(850*tx+1000*tx**2))*np.exp(-tx*10)
    put(t0,p,.05)

# mix original music quieter while spoken to support intelligibility
voice_active=np.convolve((np.abs(voice)>0.018).astype('float32'),np.ones(551)/551,'same')
# Smooth ducking by 0.2s gaussian-ish moving average
voice_active=np.convolve(voice_active,np.ones(4411)/4411,'same')
reduction=1-.60*np.clip(voice_active,0,1)
# depth and limiting
music=np.tanh(music*1.5)*reduction*.60
# fade both ends
fa=np.minimum(1,np.arange(n)/(SR*.8));fb=np.minimum(1,(n-np.arange(n)-1)/(SR*1.3))
music*=np.maximum(0,np.minimum(fa,fb))
save_pcm(OUT/'music.wav',music)
print('AUDIO:',[(p.name,round(p.stat().st_size/1024/1024,1)) for p in OUT.glob('*.wav')])
