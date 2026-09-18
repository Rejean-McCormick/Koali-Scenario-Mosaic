// @ts-nocheck
(() => {
  const CONTENT_CHANGE_EVENT='preview:contentchange';
  const MAX_TITLE_LINES=2;
  const FIT_ITERATIONS=7;
  function initPreview(preview){
    const copy=preview.querySelector('.preview-copy');
    const title=preview.querySelector('[data-preview-title]');
    if(!copy||!title)return;
    let frame=0,lastCopyWidth=-1;
    const fits=()=>{const lh=Number.parseFloat(getComputedStyle(title).lineHeight);return Number.isFinite(lh)&&title.scrollHeight<=lh*MAX_TITLE_LINES+1;};
    const set=(n)=>title.style.setProperty('--preview-title-size',`${n}px`);
    function fitTitle(){
      title.title=title.textContent?.trim()||'';title.dataset.titleFitting='true';delete title.dataset.titleClamped;title.style.removeProperty('--preview-title-size');
      const max=Number.parseFloat(getComputedStyle(title).fontSize);title.style.setProperty('--preview-title-size','var(--preview-title-min)');const min=Number.parseFloat(getComputedStyle(title).fontSize);
      if(!Number.isFinite(max)||!Number.isFinite(min)){delete title.dataset.titleFitting;return;} set(max);
      if(!fits()){set(min);if(!fits())title.dataset.titleClamped='true';else{let lo=min,hi=max;for(let i=0;i<FIT_ITERATIONS;i++){const c=(lo+hi)/2;set(c);if(fits())lo=c;else hi=c;}set(Math.max(min,lo-.1));}}
      delete title.dataset.titleFitting;
    }
    function requestFit(){if(frame)cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{frame=0;fitTitle();});}
    preview.addEventListener(CONTENT_CHANGE_EVENT,requestFit);new MutationObserver(requestFit).observe(title,{childList:true,characterData:true,subtree:true});
    if('ResizeObserver'in window)new ResizeObserver(([entry])=>{const w=entry?.contentRect.width??copy.clientWidth;if(Math.abs(w-lastCopyWidth)<=.5)return;lastCopyWidth=w;requestFit();}).observe(copy);else window.addEventListener('resize',requestFit,{passive:true});
    document.fonts?.ready.then(requestFit);window.addEventListener('pageshow',requestFit,{passive:true});requestFit();
  }
  document.querySelectorAll('.scenario-preview').forEach(initPreview);
})();
