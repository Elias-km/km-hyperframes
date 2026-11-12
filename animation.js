/** Deterministic seekable timeline shared by browser previews and frame renderers. */
(function(){
  'use strict';
  const duration=69, scenes=[...document.querySelectorAll('.scene')];
  const root=document.querySelector('#film');
  const flash=document.querySelector('#flash');
  const clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));
  const ease=t=>1-Math.pow(1-clamp(t),3);
  const lerp=(a,b,v)=>a+(b-a)*v;
  let current=0;
  const animItems={
    s0:['.headline','.money','.subtitle','.floating-stamp'],
    s1:['.headline','.skills','.corner-note'],
    s2:['.headline','.computer','.metric'],
    s3:['.stack-msg','.big-bottom'],
    s4:['.not-again','.fake-chat','.tagline'],
    s5:['.builder-icon','.brand-over','.brand-main','.brand-name','.brand-bar'],
    s6:['.course-title','.course','.degree'],
    s7:['.salary-title','.salary-middle','.salary-sub'],
    s8:['.final-main','.call-to-action','.final-brand'],
    s9:['.tg-eyebrow','.tg-flight','.tg-kicker','.tg-headline','.tg-target','.tg-bonus']
  };
  function setFrame(time){
    const t=clamp(Number(time)||0,0,duration-0.001); current=t;
    for(const s of scenes){
      const start=Number(s.dataset.start), dur=Number(s.dataset.duration), local=t-start;
      const active=local>=0&&local<dur;
      s.style.display=active?'block':'none';
      if(!active)continue;
      const fadeIn=ease(local/.47),fadeOut=clamp((dur-local)/.28);
      s.style.opacity=String(fadeIn*fadeOut);
      const zoom=s.id==='s5'?1.025:1.012;
      s.style.transform=`scale(${lerp(zoom,1,clamp(local/dur))})`;
      const selector=animItems[s.id]??[];
      let index=0;
      for(const group of selector){
        for(const el of s.querySelectorAll(group)){
          const p=ease((local-.12-index*.135)/.56);
          el.style.opacity=String(p);
          const sign=s.id==='s3'?-1:1;
          const drift=(1-p)*sign*46;
          if(el.classList.contains('floating-stamp'))el.style.transform=`rotate(${13+10*(1-p)}deg) translateY(${drift}px)`;
          else if(el.classList.contains('call-to-action'))el.style.transform=`rotate(-5deg) translateY(${drift}px) scale(${lerp(.85,1,p)})`;
          else el.style.transform=`translateY(${drift}px)`;
          index++;
        }
      }
      if(s.id==='s0'){
        const m=s.querySelector('#money');
        m.style.filter=`brightness(${1+.07*Math.sin(local*7)})`;
      }
      if(s.id==='s5'){
        const logo=s.querySelector('.builder-icon');
        logo.style.transform=`translateY(${(1-ease(local/.7))*90+Math.sin(local*4)*3}px) rotate(${(1-ease(local/.7))*-9}deg)`;
      }
      if(s.id==='s2'){
        const robot=s.querySelector('.robot'); robot.style.transform=`rotate(${Math.sin(local*3)*12}deg)`;
      }
    }
    // White flash on the brand reveal, and short flash for each act transition.
    const reveal=Math.abs(t-31);const cuts=[6,12,19,24,39,48,55,63];
    const c=Math.min(...cuts.map(x=>Math.abs(t-x)));
    flash.style.opacity=String(reveal<.20?clamp((.20-reveal)/.20)*.98:c<.07?clamp((.07-c)/.07)*.35:0);
    root.dataset.currentTime=t.toFixed(3);
    return t;
  }
  // HyperFrames registers one paused, seekable timeline for its root composition.
  const timeline={paused:true,duration:()=>duration,seek(v){setFrame(v);return timeline;},time(v){if(v===undefined)return current;setFrame(v);return timeline;},totalDuration:()=>duration,progress(v){if(v===undefined)return current/duration;setFrame(v*duration);return timeline;},pause(){return timeline;}};
  window.__timelines=window.__timelines||{};window.__timelines['pepe-manuel']=timeline;
  window.setFrame=setFrame;
  setFrame(0);
  // Scrub with ?t=... for an easy still-frame review; ?preview=1 plays the film.
  const params=new URLSearchParams(location.search);
  if(params.has('t'))setFrame(Number(params.get('t')));
  if(params.get('preview')==='1'){
    const started=performance.now();
    function tick(){setFrame((performance.now()-started)/1000%duration);requestAnimationFrame(tick);}requestAnimationFrame(tick);
    document.querySelectorAll('audio').forEach(a=>a.play().catch(()=>{}));
  }
})();
