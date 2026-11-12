#!/usr/bin/env python3
"""Lightweight checks using Python stdlib and ffprobe, no app deps."""
from pathlib import Path
from html.parser import HTMLParser
import subprocess,json,wave
P=Path(__file__).parent
class Extract(HTMLParser):
    def __init__(self): super().__init__();self.scenes=[];self.root=None;self.ids=set();self.audio=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs); i=d.get('id')
        if i:
            assert i not in self.ids, f'Duplicate id: {i}'
            self.ids.add(i)
        if d.get('data-composition-id')=='pepe-manuel':self.root=d
        if tag=='section' and 'clip' in d.get('class','').split():self.scenes.append(d)
        if tag=='audio':self.audio.append(d)
p=Extract();p.feed((P/'index.html').read_text())
assert p.root is not None
assert int(p.root['data-duration'])==69
assert len(p.scenes)==10
assert len(p.audio)==2
for idx,scene in enumerate(p.scenes):
    assert 'data-track-index' in scene
    a=float(scene['data-start']);d=float(scene['data-duration'])
    assert a == sum(float(x['data-duration']) for x in p.scenes[:idx]),f'Gap scene {idx}'
    assert d>0
assert sum(float(x['data-duration']) for x in p.scenes)==69
for f in ('assets/audio/music.wav','assets/audio/voice.wav'):
    with wave.open(str(P/f),'rb') as wf:
        assert abs(wf.getnframes()/wf.getframerate()-69)<.005
output=P/'renders'/'contrucciones-pepe-y-manuel.mp4'
if output.exists():
    x=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height','-of','json',str(output)]))
    assert abs(float(x['format']['duration'])-69)<.04
    assert any(s['codec_type']=='video' and s.get('width')==1280 and s.get('height')==720 for s in x['streams'])
    assert any(s['codec_type']=='audio' for s in x['streams'])
print('PASS: 10 scenes, contiguous 69 s timeline, narration & music, video metadata')
