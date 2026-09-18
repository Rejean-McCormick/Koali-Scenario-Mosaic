const root=document.querySelector<HTMLElement>('[data-mosaic-root]');
if(root){
  const data=JSON.parse(root.querySelector<HTMLScriptElement>('[data-mosaic-data]')?.textContent ?? '{}');
  const i18n=JSON.parse(root.querySelector<HTMLScriptElement>('[data-mosaic-i18n]')?.textContent ?? '{}');
  const cells=[...root.querySelectorAll<SVGAElement>('[data-scenario-id]')];
  const search=root.querySelector<HTMLInputElement>('[data-mosaic-search]');
  const count=root.querySelector<HTMLOutputElement>('[data-mosaic-result-count]');
  const canvas=root.querySelector<HTMLElement>('[data-mosaic-canvas]');
  const preview=root.querySelector<HTMLElement>('.scenario-preview');
  const filters=[...root.querySelectorAll<HTMLSelectElement>('[data-mosaic-filter]')];
  const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');
  const touchPreviewMode=window.matchMedia('(hover: none), (pointer: coarse)').matches;

  const setText=(query:string,value:string)=>{const el=root.querySelector<HTMLElement>(query);if(el){el.textContent=value;el.title=value;}};
  const setLevel=(query:string, level:number|string)=>{const el=root.querySelector<HTMLElement>(query);if(el)el.dataset.level=String(level);};
  const humanList=(items:string[],limit=3)=>items?.length?(items.length>limit?`${items.slice(0,limit).join(' · ')} +${items.length-limit}`:items.join(' · ')):'—';

  function renderSystems(systems:Array<{key:string;label:string;description:string}> = []){
    const list=root.querySelector<HTMLElement>('[data-preview-system-list]'); if(!list)return; list.replaceChildren();
    systems.forEach(system=>{const item=document.createElement('span');item.className='system-route';item.dataset.systemKey=system.key;item.title=system.description;
      const strong=document.createElement('strong');strong.textContent=system.label;const small=document.createElement('small');small.textContent=system.description;item.append(strong,small);list.append(item);});
  }
  function renderMechanisms(items:string[]=[]){
    const box=root.querySelector<HTMLElement>('[data-preview-mechanisms]');if(!box)return;box.replaceChildren();
    items.slice(0,4).forEach(m=>{const tag=document.createElement('span');tag.textContent=m;box.append(tag);});
  }
  function selectOnly(id:string){cells.forEach(cell=>cell.classList.toggle('is-active',cell.dataset.scenarioId===id));}
  function show(id:string){
    const s=data[id]; if(!s)return; selectOnly(id); if(preview)preview.dataset.previewSelected='true'; if(canvas)canvas.dataset.activeTerritory=s.familyId;
    setText('[data-preview-id]',s.id);setText('[data-preview-category]',s.family);setText('[data-preview-title]',s.title);setText('[data-preview-summary]',s.hook);setText('[data-preview-koali]',s.summary);
    const kw=root.querySelector<HTMLElement>('[data-preview-koali-wrap]');if(kw)kw.hidden=false;
    setText('[data-preview-scale]',s.scale);setText('[data-preview-urgency]',s.urgency);setText('[data-preview-gap]',s.coordinationGap);setText('[data-preview-stakes]',humanList(s.stakes,3));
    setLevel('[data-preview-scale-visual]', s.scaleLevel ?? 0);setLevel('[data-preview-urgency-visual]', s.urgencyLevel ?? 0);setLevel('[data-preview-gap-visual]', s.gapLevel ?? 0);
    const image=root.querySelector<HTMLImageElement>('[data-preview-image]');if(image){image.src=s.image.src;image.srcset=s.image.srcset??'';image.sizes=s.image.sizes??'';image.alt=s.title;image.dataset.imageState='scenario';}
    const metricsRow=root.querySelector<HTMLElement>('[data-preview-metrics-row]');if(metricsRow)metricsRow.hidden=false;
    setText('[data-preview-mechanism-summary]',humanList(s.mechanisms,3));setText('[data-preview-stakes-profile]',humanList(s.stakes,4));setText('[data-preview-scale-profile]',s.scalePath);
    const urgency=root.querySelector<HTMLElement>('[data-preview-urgency-wrap]');if(urgency)urgency.dataset.urgency=s.urgencyKey;
    renderMechanisms(s.mechanisms);renderSystems(s.systems);
    const link=root.querySelector<HTMLAnchorElement>('[data-preview-link]');if(link){link.href=s.href;link.hidden=false;}
    preview?.dispatchEvent(new CustomEvent('preview:contentchange'));
  }

  let hoverTimer:number|undefined; let pending:string|null=null;
  const cancel=(id?:string)=>{if(id&&pending!==id)return;if(hoverTimer!==undefined)clearTimeout(hoverTimer);hoverTimer=undefined;pending=null;};
  const schedule=(id:string)=>{cancel();pending=id;hoverTimer=window.setTimeout(()=>{pending=null;hoverTimer=undefined;show(id);},140);};
  const available=()=>cells.filter(c=>!c.classList.contains('is-filtered-out')).sort((a,b)=>(a.dataset.scenarioId??'').localeCompare(b.dataset.scenarioId??'',undefined,{numeric:true}));
  const step=(dir:-1|1)=>{const list=available();if(!list.length)return;const active=cells.find(c=>c.classList.contains('is-active'))?.dataset.scenarioId;let ix=list.findIndex(c=>c.dataset.scenarioId===active);if(ix<0)ix=dir>0?-1:0;const next=list[(ix+dir+list.length)%list.length]?.dataset.scenarioId;if(next)show(next);};

  if(touchPreviewMode&&preview){let start:{x:number;y:number;t:number}|null=null;preview.addEventListener('touchstart',e=>{if(e.touches.length!==1){start=null;return;}const t=e.touches[0];start={x:t.clientX,y:t.clientY,t:performance.now()};},{passive:true});preview.addEventListener('touchend',e=>{if(!start||e.changedTouches.length!==1){start=null;return;}const t=e.changedTouches[0],dx=t.clientX-start.x,dy=t.clientY-start.y,dur=performance.now()-start.t;start=null;if(dur<=900&&Math.abs(dx)>=48&&Math.abs(dx)>Math.abs(dy)*1.2)step(dx<0?1:-1);},{passive:true});preview.addEventListener('touchcancel',()=>{start=null;},{passive:true});}

  cells.forEach(cell=>{const id=cell.dataset.scenarioId!;cell.addEventListener('pointerenter',e=>{if(!touchPreviewMode&&e.pointerType!=='touch')schedule(id);});cell.addEventListener('pointerleave',()=>cancel(id));cell.addEventListener('focus',()=>{cancel();show(id);});cell.addEventListener('click',e=>{if(!touchPreviewMode)return;e.preventDefault();cancel();show(id);preview?.scrollIntoView({behavior:reducedMotion.matches?'auto':'smooth',block:'start'});});});

  function applyFilters(){
    const q=search?.value.trim().toLowerCase() ?? ''; const active=Object.fromEntries(filters.map(f=>[f.dataset.mosaicFilter!,f.value])); let visible=0;
    cells.forEach(cell=>{const s=data[cell.dataset.scenarioId!];const hitSearch=!q||s.search.includes(q);const hitFamily=!active.family||s.familyId===active.family;const hitScale=!active.scale||s.scaleKey===active.scale;const hitUrgency=!active.urgency||s.urgencyKey===active.urgency;const hitStakes=!active.stakes||s.stakesKeys.includes(active.stakes);const hit=hitSearch&&hitFamily&&hitScale&&hitUrgency&&hitStakes;cell.classList.toggle('is-filtered-out',!hit);if(hit)visible++;});
    if(count)count.value=`${visible} ${visible===1?i18n.scenarioSingular:i18n.scenarios}`;
  }
  search?.addEventListener('input',applyFilters);filters.forEach(f=>f.addEventListener('change',applyFilters));
  root.querySelector('[data-mosaic-surprise]')?.addEventListener('click',()=>{cancel();const list=available();if(list.length){const cell=list[Math.floor(Math.random()*list.length)];show(cell.dataset.scenarioId!);cell.focus({preventScroll:true});}});
  root.querySelector('[data-mosaic-reset]')?.addEventListener('click',()=>{cancel();if(search)search.value='';filters.forEach(f=>f.value='');cells.forEach(c=>c.classList.remove('is-filtered-out','is-active'));if(canvas)delete canvas.dataset.activeTerritory;if(count)count.value=`${cells.length} ${i18n.scenarios}`;});
}
export {};
