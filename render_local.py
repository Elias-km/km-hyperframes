#!/usr/bin/env python3
"""Headless, deterministic Chromium -> FFmpeg render, no npm packages needed.

The source remains an editable HyperFrames-style HTML composition.
Use --review to write scene contact sheet PNGs without rendering the entire film.
"""
import argparse
import asyncio
from pathlib import Path
import subprocess
import sys
import shutil
from playwright.async_api import async_playwright

ROOT=Path(__file__).parent.resolve()
TARGET=ROOT/'renders'/'contrucciones-pepe-y-manuel.mp4'

async def run(review=False, capture_fps=12):
    async with async_playwright() as p:
        exe=shutil.which('chromium') or shutil.which('google-chrome') or shutil.which('chromium-browser')
        kw={'executable_path':exe} if exe else {}
        browser=await p.chromium.launch(headless=True,args=['--no-sandbox'],**kw)
        page=await browser.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
        # Avoid navigation restrictions in managed Chromium environments.
        html=(ROOT/'index.html').read_text()
        html=html.replace('<link rel="stylesheet" href="styles.css">','').replace('<script src="animation.js"></script>','')
        await page.set_content(html,wait_until='domcontentloaded')
        await page.add_style_tag(content=(ROOT/'styles.css').read_text())
        await page.add_script_tag(content=(ROOT/'animation.js').read_text())
        await page.evaluate('document.fonts.ready')
        # Some environments need one repaint after opening the file.
        if review:
            from PIL import Image,ImageDraw,ImageFont
            times=[1.8,8,14.5,20.5,27,33.5,42,51,58,66]
            thumbs=[]
            for i,t in enumerate(times):
                await page.evaluate('(t) => window.setFrame(t)',t)
                path=ROOT/'renders'/f'review-{i+1:02d}.png'
                await page.screenshot(path=str(path),type='png',animations='disabled')
                im=Image.open(path).convert('RGB').resize((480,270))
                thumbs.append(im)
            sheet=Image.new('RGB',(480*5,270*2))
            for i,im in enumerate(thumbs):sheet.paste(im,((i%5)*480,(i//5)*270))
            sheet.save(ROOT/'renders'/'storyboard-contact-sheet.jpg',quality=92)
            await browser.close()
            return
        TARGET.parent.mkdir(parents=True,exist_ok=True)
        frames=69*capture_fps
        command=['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(capture_fps),'-f','image2pipe','-vcodec','mjpeg','-i','pipe:0','-i',str(ROOT/'assets/audio/music.wav'),'-i',str(ROOT/'assets/audio/voice.wav'),'-filter_complex','[1:a][2:a]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.96[aout]','-map','0:v','-map','[aout]','-vf','fps=24,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','21','-c:a','aac','-b:a','160k','-ar','44100','-t','69','-movflags','+faststart',str(TARGET)]
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        try:
            for i in range(frames):
                await page.evaluate('(t) => window.setFrame(t)',i/capture_fps)
                data=await page.screenshot(type='jpeg',quality=88,animations='disabled')
                process.stdin.write(data)
                if i%120==0: print(f'{i}/{frames} frames ({round(100*i/frames)}%)',flush=True)
            process.stdin.close()
            err=process.stderr.read().decode('utf-8',errors='replace')
            rc=process.wait()
            if rc: raise RuntimeError(f'ffmpeg status {rc}: {err}')
        except BaseException:
            process.kill();raise
        finally:
            await browser.close()
        print('RENDER FINISHED',TARGET, TARGET.stat().st_size)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--review',action='store_true');ap.add_argument('--fps',type=int,default=12)
    ns=ap.parse_args()
    asyncio.run(run(review=ns.review,capture_fps=ns.fps))
