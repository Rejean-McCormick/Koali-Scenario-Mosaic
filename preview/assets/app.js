(() => {
  const root=document.querySelector('[data-mosaic-root]');
  if(!root)return;
  const raw=root.querySelector('[data-mosaic-data]').textContent;
  const data=JSON.parse(raw.replace(/&quot;/g,'\"').replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>'));
  const i18n=JSON.parse(root.querySelector('[data-mosaic-i18n]').textContent);
  const cells=[...root.querySelectorAll('[data-scenario-id]')];
  const search=root.querySelector('[data-mosaic-search]');
  const filters=[...root.querySelectorAll('[data-mosaic-filter]')];
  const count=root.querySelector('[data-mosaic-result-count]');
  const canvas=root.querySelector('[data-mosaic-canvas]');
  const preview=root.querySelector('.scenario-preview');
  const touchPreviewMode=matchMedia('(hover: none), (pointer: coarse)').matches;
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)');

  const txt=(q,v)=>{const e=root.querySelector(q);if(e){e.textContent=v;e.title=v}};
  const list=(a,n=3)=>!a?.length?'—':a.length>n?`${a.slice(0,n).join(' · ')} +${a.length-n}`:a.join(' · ');
  function systems(items=[]){
    const box=root.querySelector('[data-preview-system-list]');
    if(!box)return;
    box.replaceChildren();
    items.forEach(s=>{const e=document.createElement('span');e.className='system-route';e.innerHTML=`<strong>${s.label}</strong><small>${s.description}</small>`;box.append(e)});
  }
  function mechanisms(items=[]){
    const box=root.querySelector('[data-preview-mechanisms]');
    if(!box)return;
    box.replaceChildren();
    items.slice(0,4).forEach(x=>{const e=document.createElement('span');e.textContent=x;box.append(e)});
  }
  function selectOnly(id){cells.forEach(c=>c.classList.toggle('is-active',c.dataset.scenarioId===id))}
  function show(id){
    const s=data[id];if(!s)return;
    selectOnly(id);
    if(canvas)canvas.dataset.activeTerritory=s.familyId;
    if(preview)preview.dataset.previewSelected='true';
    txt('[data-preview-id]',s.id);txt('[data-preview-category]',s.family);txt('[data-preview-title]',s.title);txt('[data-preview-summary]',s.hook);txt('[data-preview-koali]',s.summary);
    const kw=root.querySelector('[data-preview-koali-wrap]');if(kw)kw.hidden=false;
    txt('[data-preview-scale]',s.scale);txt('[data-preview-urgency]',s.urgency);txt('[data-preview-gap]',s.coordinationGap);txt('[data-preview-stakes]',list(s.stakes));
    txt('[data-preview-mechanism-summary]',list(s.mechanisms));txt('[data-preview-scale-profile]',s.scalePath);
    const urgency=root.querySelector('[data-preview-urgency-wrap]');if(urgency)urgency.dataset.urgency=s.urgencyKey;
    const im=root.querySelector('[data-preview-image]');if(im){im.src=s.image.src;im.alt=s.title;im.dataset.imageState='scenario'}
    const metrics=root.querySelector('[data-preview-metrics-row]');if(metrics)metrics.hidden=false;
    mechanisms(s.mechanisms);systems(s.systems);
    const link=root.querySelector('[data-preview-link]');if(link){link.href=s.href;link.hidden=false}
    preview?.dispatchEvent(new CustomEvent('preview:contentchange'));
  }

  const available=()=>cells.filter(c=>!c.classList.contains('is-filtered-out')).sort((a,b)=>(a.dataset.scenarioId||'').localeCompare(b.dataset.scenarioId||'',undefined,{numeric:true}));
  const step=dir=>{const items=available();if(!items.length)return;const active=cells.find(c=>c.classList.contains('is-active'))?.dataset.scenarioId;let ix=items.findIndex(c=>c.dataset.scenarioId===active);if(ix<0)ix=dir>0?-1:0;const next=items[(ix+dir+items.length)%items.length]?.dataset.scenarioId;if(next)show(next)};

  let hoverTimer, pendingHoverId=null;
  function cancelScheduledPreview(id){if(id&&pendingHoverId!==id)return;if(hoverTimer!==undefined)clearTimeout(hoverTimer);hoverTimer=undefined;pendingHoverId=null}
  function schedulePreview(id){cancelScheduledPreview();pendingHoverId=id;hoverTimer=setTimeout(()=>{hoverTimer=undefined;pendingHoverId=null;show(id)},140)}

  if(touchPreviewMode&&preview){
    let start=null;
    preview.addEventListener('touchstart',e=>{if(e.touches.length!==1){start=null;return}const t=e.touches[0];start={x:t.clientX,y:t.clientY,time:performance.now()}},{passive:true});
    preview.addEventListener('touchend',e=>{if(!start||e.changedTouches.length!==1){start=null;return}const t=e.changedTouches[0],dx=t.clientX-start.x,dy=t.clientY-start.y,duration=performance.now()-start.time;start=null;if(duration>900||Math.abs(dx)<48||Math.abs(dx)<=Math.abs(dy)*1.2)return;step(dx<0?1:-1)},{passive:true});
    preview.addEventListener('touchcancel',()=>{start=null},{passive:true});
  }

  cells.forEach(c=>{
    const id=c.dataset.scenarioId;
    c.addEventListener('pointerenter',e=>{if(touchPreviewMode||e.pointerType==='touch')return;schedulePreview(id)});
    c.addEventListener('pointerleave',()=>cancelScheduledPreview(id));
    c.addEventListener('focus',()=>{cancelScheduledPreview();show(id)});
    c.addEventListener('click',e=>{if(!touchPreviewMode)return;e.preventDefault();cancelScheduledPreview();show(id);preview?.scrollIntoView({behavior:reducedMotion.matches?'auto':'smooth',block:'start'})});
  });

  function apply(){
    const q=(search?.value||'').trim().toLowerCase();
    const f=Object.fromEntries(filters.map(x=>[x.dataset.mosaicFilter,x.value]));
    let n=0;
    cells.forEach(c=>{const s=data[c.dataset.scenarioId],hit=(!q||s.search.includes(q))&&(!f.family||s.familyId===f.family)&&(!f.scale||s.scaleKey===f.scale)&&(!f.urgency||s.urgencyKey===f.urgency)&&(!f.stakes||s.stakesKeys.includes(f.stakes));c.classList.toggle('is-filtered-out',!hit);if(hit)n++});
    if(count)count.value=`${n} ${n===1?i18n.scenarioSingular:i18n.scenarios}`;
  }
  search?.addEventListener('input',apply);filters.forEach(f=>f.addEventListener('change',apply));

  root.querySelector('[data-mosaic-reset]')?.addEventListener('click',()=>{cancelScheduledPreview();if(search)search.value='';filters.forEach(f=>f.value='');cells.forEach(c=>c.classList.remove('is-filtered-out','is-active'));if(canvas)delete canvas.dataset.activeTerritory;if(count)count.value=`${cells.length} ${i18n.scenarios}`});
  root.querySelector('[data-mosaic-surprise]')?.addEventListener('click',()=>{cancelScheduledPreview();const v=available();if(v.length){const c=v[Math.floor(Math.random()*v.length)];show(c.dataset.scenarioId);c.focus({preventScroll:true})}});
})();