from frontmatter_stdlib import parse_frontmatter
from pathlib import Path
import json, re, html, shutil, math
ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/'preview'
FAMILIES=json.loads((ROOT/'src/data/problem-families.json').read_text(encoding='utf-8'))
LAYOUT=json.loads((ROOT/'src/data/mosaic-layout.json').read_text(encoding='utf-8'))
SYSTEMS=json.loads((ROOT/'src/data/system-catalog.json').read_text(encoding='utf-8'))
REAL_CASES=json.loads((ROOT/'src/data/real-cases.json').read_text(encoding='utf-8'))
COMP_KEYS={'Kristal':'kristal','Konnaxion':'konnaxion','Orgo':'orgo','Smart Vote':'smart-vote','EkoH':'ekoh','SenTient':'sentient','SemantiK Architect':'semantik-architect','Kreative/Konservation':'kreative'}
UI={
'en':dict(title='Koali Scenario Mosaic',examples='canonical problems',explore='Explore 36 real-world problem patterns',intro='Select a problem to see its scale, urgency, failure mechanisms, real-world parallels, and the Koali response path.',search='Search a problem, sector, mechanism, or system…',family='Problem family',scale='Scale',urgency='Urgency',stakes='Stakes',allfam='All families',allscale='All scales',allurg='All urgencies',allstakes='All stakes',surprise='Surprise me',reset='Reset',scenarios='scenarios',inside='Inside Koali',path='System path',mechanisms='Failure mechanisms',gap='Coordination gap',koali='What Koali changes',open='Open the full scenario',back='Back to the full Mosaic',whatbreaks='What breaks',whoknows='Who holds part of the picture',response='Koali response',cases='Real-world parallels',success='What success looks like',evidence='Documented parallels show that the failure mechanism is real; they do not claim Koali would have changed a specific outcome.'),
'fr':dict(title='Mosaïque de scénarios Koali',examples='problèmes canoniques',explore='Explorez 36 problèmes sociotechniques récurrents',intro='Sélectionnez un problème pour voir son échelle, son urgence, ses mécanismes de défaillance, ses cas réels analogues et la réponse Koali.',search='Rechercher un problème, secteur, mécanisme ou système…',family='Famille de problème',scale='Échelle',urgency='Urgence',stakes='Enjeux',allfam='Toutes les familles',allscale='Toutes les échelles',allurg='Toutes les urgences',allstakes='Tous les enjeux',surprise='Au hasard',reset='Réinitialiser',scenarios='scénarios',inside='Dans Koali',path='Chemin système',mechanisms='Mécanismes de défaillance',gap='Déficit de coordination',koali='Ce que Koali change',open='Ouvrir le scénario complet',back='Retour à la mosaïque complète',whatbreaks='Ce qui casse',whoknows='Qui détient une partie du savoir',response='Réponse Koali',cases='Cas réels semblables',success='À quoi ressemble le succès',evidence='Les cas documentés montrent que le mécanisme de défaillance existe; ils ne prétendent pas que Koali aurait changé une issue particulière.')}
FR_SCALE={'individual':'Individu','team':'Équipe','organization':'Organisation','community':'Communauté','city':'Ville','regional':'Région','national':'Pays','global':'Monde','institution':'Institution','sector':'Secteur','network':'Réseau'}
FR_URGENCY={'low':'Faible','moderate':'Modérée','significant':'Importante','high':'Élevée','critical':'Critique','immediate':'Immédiate'}
FR_GAP={'low':'Faible','medium':'Modéré','high':'Élevé','extreme':'Extrême'}
FR_STAKES={'access':'Accès','continuity':'Continuité','culture':'Culture','dignity':'Dignité','education':'Éducation','environment':'Environnement','equity':'Équité','essential_service':'Services essentiels','health':'Santé','identity':'Identité','innovation':'Innovation','knowledge':'Savoir','life':'Vie humaine','money':'Coûts financiers','privacy':'Vie privée','public_policy':'Politiques publiques','public_safety':'Sécurité publique','public_value':'Intérêt public','research':'Recherche','rights':'Droits','safety':'Sécurité','security':'Sécurité','service_quality':'Qualité des services','sovereignty':'Souveraineté','trust':'Confiance'}
FR_MECH={'aggregation_bias':'Biais d’agrégation','anecdote_overweight':'Surpondération de l’anecdote','blame_distortion':'Distorsion du blâme','central_dependency':'Dépendance à un système central','citizen_signal_ignored':'Signal citoyen ignoré','conflict_of_interest':'Conflit d’intérêts','connectivity_failure':'Rupture de connectivité','content_silo':'Silo de contenu','context_loss':'Perte de contexte','continuity_gap':'Rupture de continuité','criterion_ambiguity':'Ambiguïté des critères','expertise_asymmetry':'Asymétrie d’expertise','expertise_isolation':'Isolement des expertises','expertise_mismatch':'Expertise inadaptée','false_balance':'Fausse équivalence','false_certainty':'Fausse certitude','fragmentation':'Fragmentation','handoff_failure':'Échec de transmission','hidden_tradeoff':'Compromis caché','hindsight_bias':'Biais rétrospectif','institutional_amnesia':'Amnésie institutionnelle','institutional_dependency':'Dépendance institutionnelle','interoperability_failure':'Défaillance d’interopérabilité','knowledge_attrition':'Érosion du savoir','legacy_dependency':'Dépendance aux systèmes patrimoniaux','legitimacy_gap':'Déficit de légitimité','lock_in':'Verrouillage','memory_failure':'Défaillance de mémoire institutionnelle','metric_fixation':'Fixation sur les indicateurs','missing_escalation':'Absence d’escalade','noise_amplification':'Amplification du bruit','opacity':'Opacité','opaque_decision':'Décision opaque','opaque_weighting':'Pondération opaque','organizational_silo':'Silo organisationnel','participation_without_power':'Participation sans pouvoir d’action','pattern_detection_failure':'Défaillance de détection des tendances','power_asymmetry':'Asymétrie de pouvoir','premature_conclusion':'Conclusion prématurée','provenance_loss':'Perte de provenance','publication_bias':'Biais de publication','recommendation_decay':'Déperdition des recommandations','resource_orchestration_failure':'Défaillance d’orchestration des ressources','reuse_failure':'Échec de réutilisation','rights_detachment':'Dissociation des droits','risk_distortion':'Distorsion du risque','routing_failure':'Échec d’orientation','scale_confusion':'Confusion d’échelle','semantic_mismatch':'Incompatibilité sémantique','signal_dilution':'Dilution du signal','single_point_of_failure':'Point de défaillance unique','tacit_knowledge_loss':'Perte de savoir tacite','training_gap':'Déficit de formation','unclosed_loop':'Boucle non bouclée','vendor_dependency':'Dépendance au fournisseur','visibility_failure':'Défaillance de visibilité'}

def en_label(v): return v.replace('_',' ').replace('-',' ').title()
def loc(group,lang,v):
    if lang=='en': return en_label(v)
    return {'scale':FR_SCALE,'urgency':FR_URGENCY,'gap':FR_GAP,'stakes':FR_STAKES,'mechanisms':FR_MECH}[group].get(v,en_label(v))
def parse_scale(v):
    p=[x.strip() for x in v.split('→')];return p[0],p[-1]
def split_file(p):
    t=p.read_text(encoding='utf-8');m=re.match(r'^---\r?\n(.*?)\r?\n---\r?\n([\s\S]*)$',t,re.S);return parse_frontmatter(m.group(1)),m.group(2)
def sec(body,head):
    m=re.search(rf'^## {re.escape(head)}\s*$([\s\S]*?)(?=^## |\Z)',body,re.M);return m.group(1).strip() if m else ''
def bullets(raw): return [re.sub(r'[`*_]','',x[2:].strip()) for x in raw.splitlines() if x.strip().startswith('- ')]
def clean(s): return re.sub(r'\s+',' ',re.sub(r'[`*_]','',s)).strip()
def details(body,lang):
    h={'en':('With Koali','Who holds part of the picture','What success looks like'),'fr':('Avec Koali','Qui détient une partie du savoir','À quoi ressemble le succès')}[lang]
    return dict(koali=clean(sec(body,h[0])),holders=bullets(sec(body,h[1])),success=bullets(sec(body,h[2])))
def systems(data,lang):
    out=[]
    for label in data['koali_components']:
        key=COMP_KEYS.get(label,label.lower().replace(' ','-'));item=SYSTEMS.get(key,{'label':label,'description':{lang:''}})
        out.append({'key':key,'label':item['label'],'description':item['description'].get(lang,'')})
    return out
def esc(x): return html.escape(str(x),quote=True)
def polygon(x,y,size): return ' '.join(f'{x+size*math.cos(math.pi/3*i-math.pi/6):.2f},{y+size*math.sin(math.pi/3*i-math.pi/6):.2f}' for i in range(6))
def inline(s):
    s=esc(s);s=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s);s=re.sub(r'`(.+?)`',r'<code>\1</code>',s);s=re.sub(r'(https?://[^\s<]+)',r'<a href="\1">\1</a>',s);return s
def markdown_basic(body):
    body=re.sub(r'^# .+\n','',body,count=1,flags=re.M);body=re.sub(r'^> .+\n','',body,count=1,flags=re.M);out=[];in_list=False
    for line in body.splitlines():
        s=line.strip()
        if not s:
            if in_list: out.append('</ul>');in_list=False
        elif s.startswith('## '):
            if in_list: out.append('</ul>');in_list=False
            out.append(f'<h2>{esc(s[3:])}</h2>')
        elif s.startswith('### '):
            if in_list: out.append('</ul>');in_list=False
            out.append(f'<h3>{esc(s[4:])}</h3>')
        elif s.startswith('- '):
            if not in_list: out.append('<ul>');in_list=True
            out.append(f'<li>{inline(s[2:])}</li>')
        elif s=='---':
            if in_list: out.append('</ul>');in_list=False
            out.append('<hr>')
        else:
            if in_list: out.append('</ul>');in_list=False
            out.append(f'<p>{inline(s)}</p>')
    if in_list: out.append('</ul>')
    return ''.join(out)
def image_rel(d,detail=False):
    png=ROOT/'public/scenarios/images'/f"{d['id']}.png"
    base='../../../assets/scenarios' if detail else '../assets/scenarios'
    if png.exists(): return f"{base}/images/{d['id']}.png"
    return f"{base}/fallback/{d['problem_family']}.svg"
def load(lang):
    result=[]
    for p in sorted((ROOT/'src/content/scenarios'/lang).glob('SCN-*.md')):
        d,b=split_file(p);det=details(b,lang);origin,extent=parse_scale(d['scale'])
        d.update(_body=b,_koali=det['koali'],_holders=det['holders'],_success=det['success'],_origin=origin,_extent=extent,_systems=systems(d,lang))
        d['_cases']=[REAL_CASES.get(cid,{}).get(lang,cid) for cid in d['real_case_ids']]
        d['_search']=' '.join([d['title'],d['hook'],d['problem_family_label'],*d['failure_mechanisms'],*d['stakes'],*d['domains'],*d['koali_patterns'],*d['koali_components'],*d['_cases'],det['koali']]).lower();result.append(d)
    return result

def header(lang):
    u=UI[lang];return f'<header class="site-header"><a class="brand" href="./index.html"><img class="brand-mark" src="../assets/brand/koali-mark.svg" alt=""><span class="brand-copy"><span class="brand-product"><strong>Koali</strong><span>{u["title"]}</span></span><small>the Sociotechnical Operating System</small></span></a><nav class="language-switcher"><a class="{"active" if lang=="en" else ""}" href="../en/index.html">EN</a><span>/</span><a class="{"active" if lang=="fr" else ""}" href="../fr/index.html">FR</a></nav></header>'
def metric_row(lang,d=None):
    u=UI[lang]
    if not d:return f'<div class="preview-metrics-row" data-preview-metrics-row hidden><div class="preview-metric"><span>{u["scale"]}</span><strong data-preview-scale>—</strong></div><div class="preview-metric preview-metric-urgency" data-preview-urgency-wrap><span>{u["urgency"]}</span><strong data-preview-urgency>—</strong></div><div class="preview-metric"><span>{u["gap"]}</span><strong data-preview-gap>—</strong></div><div class="preview-metric"><span>{u["stakes"]}</span><strong data-preview-stakes>—</strong></div></div>'
    return f'<div class="preview-metrics-row"><div class="preview-metric"><span>{u["scale"]}</span><strong>{esc(loc("scale",lang,d["_extent"]))}</strong></div><div class="preview-metric preview-metric-urgency" data-urgency="{d["urgency"]}"><span>{u["urgency"]}</span><strong>{esc(loc("urgency",lang,d["urgency"]))}</strong></div><div class="preview-metric"><span>{u["gap"]}</span><strong>{esc(loc("gap",lang,d["coordination_gap"]))}</strong></div><div class="preview-metric"><span>{u["stakes"]}</span><strong>{esc(" · ".join(loc("stakes",lang,x) for x in d["stakes"][:3]))}</strong></div></div>'
def preview_empty(lang):
    u=UI[lang]
    return f'''<section class="scenario-preview" data-preview-selected="false" data-preview-swipe="true"><div class="preview-image-shell"><img data-preview-image data-image-state="cover" src="../assets/brand/koali-mark.svg" alt="Koali"></div><div class="preview-copy"><p class="preview-eyebrow"><span data-preview-id>{u['title']}</span> · <span data-preview-category>36 {u['examples']}</span></p><h1 data-preview-title>{u['explore']}</h1><p class="preview-summary" data-preview-summary>{u['intro']}</p>{metric_row(lang)}<div class="preview-mechanisms" data-preview-mechanisms></div><div class="preview-koali" data-preview-koali-wrap hidden><span>{u['koali']}</span><p data-preview-koali></p></div><a class="preview-cta" data-preview-link hidden>{u['open']} →</a></div><aside class="preview-profile" data-preview-profile><div class="profile-heading"><span class="profile-title">{u['inside']}</span><span class="profile-section-label">{u['path']}</span></div><div class="profile-systems"><div class="system-route-list" data-preview-system-list></div></div><div class="profile-context"><div><span>{u['mechanisms']}</span><strong data-preview-mechanism-summary>—</strong></div><div><span>{u['scale']}</span><strong data-preview-scale-profile>—</strong></div></div></aside></section>'''
def main_html(lang,items):
    u=UI[lang];families=[];seen=set()
    for d in items:
        if d['problem_family'] not in seen:seen.add(d['problem_family']);families.append((d['problem_family'],d['problem_family_label']))
    scales=sorted({d['_extent'] for d in items});urg=[x for x in ['low','significant','moderate','high','critical','immediate'] if any(d['urgency']==x for d in items)];stakes=sorted({x for d in items for x in d['stakes']})
    ctrls=f'''<div class="mosaic-controls"><label class="search-box"><input data-mosaic-search type="search" placeholder="{esc(u['search'])}"></label><label class="filter-box"><span>{u['family']}</span><select data-mosaic-filter="family"><option value="">{u['allfam']}</option>{''.join(f'<option value="{esc(k)}">{esc(v)}</option>' for k,v in families)}</select></label><label class="filter-box"><span>{u['scale']}</span><select data-mosaic-filter="scale"><option value="">{u['allscale']}</option>{''.join(f'<option value="{esc(x)}">{esc(loc("scale",lang,x))}</option>' for x in scales)}</select></label><label class="filter-box"><span>{u['urgency']}</span><select data-mosaic-filter="urgency"><option value="">{u['allurg']}</option>{''.join(f'<option value="{esc(x)}">{esc(loc("urgency",lang,x))}</option>' for x in urg)}</select></label><label class="filter-box"><span>{u['stakes']}</span><select data-mosaic-filter="stakes"><option value="">{u['allstakes']}</option>{''.join(f'<option value="{esc(x)}">{esc(loc("stakes",lang,x))}</option>' for x in stakes)}</select></label><button class="ghost-button" data-mosaic-surprise>{u['surprise']}</button><button class="ghost-button" data-mosaic-reset>{u['reset']}</button><output data-mosaic-result-count>36 {u['scenarios']}</output></div>'''
    by={d['id']:d for d in items};cells='';pdata={}
    for sid,pos in LAYOUT['positions'].items():
        d=by[sid];cells+=f'<a class="mosaic-cell family-{d["problem_family"]}" data-scenario-id="{sid}" href="./uses/{sid}/index.html" tabindex="0"><polygon points="{polygon(pos["x"],pos["y"],pos["size"])}"></polygon><text x="{pos["x"]}" y="{pos["y"]+3}" text-anchor="middle">{sid[-3:]}</text></a>'
        pdata[sid]=dict(id=sid,title=d['title'],family=d['problem_family_label'],familyId=d['problem_family'],hook=d['hook'],summary=d['_koali'],systems=d['_systems'],mechanisms=[loc('mechanisms',lang,x) for x in d['failure_mechanisms']],scale=loc('scale',lang,d['_extent']),scaleKey=d['_extent'],scalePath=f"{loc('scale',lang,d['_origin'])} → {loc('scale',lang,d['_extent'])}",urgency=loc('urgency',lang,d['urgency']),urgencyKey=d['urgency'],stakes=[loc('stakes',lang,x) for x in d['stakes']],stakesKeys=d['stakes'],coordinationGap=loc('gap',lang,d['coordination_gap']),href=f'./uses/{sid}/index.html',search=d['_search'],image={'src':image_rel(d,False)})
    labels=''.join(f'<div class="territory-label" data-territory-id="{fid}" style="--territory-x:{meta["x"]*100}%;--territory-y:{meta["y"]*100}%;--territory-w:{meta.get("width",.16)*100}%"><span>{esc(next((d["problem_family_label"] for d in items if d["problem_family"]==fid),fid))}</span></div>' for fid,meta in LAYOUT['territoryLabels'].items())
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="../assets/styles.css"><title>{u['title']}</title></head><body>{header(lang)}<main><div class="mosaic-experience" data-mosaic-root>{preview_empty(lang)}{ctrls}<div class="mosaic-stage"><div class="mosaic-scroll"><div class="mosaic-canvas" data-mosaic-canvas><svg class="mosaic" viewBox="{' '.join(map(str,LAYOUT['viewBox']))}">{cells}</svg><div class="territory-label-layer">{labels}</div></div></div></div><script type="application/json" data-mosaic-data>{html.escape(json.dumps(pdata,ensure_ascii=False))}</script><script type="application/json" data-mosaic-i18n>{json.dumps({'scenarios':u['scenarios'],'scenarioSingular':'scenario' if lang=='en' else 'scénario'})}</script></div></main><script src="../assets/app.js"></script><script src="../assets/preview-layout.js"></script></body></html>'''
def selected_preview(lang,d):
    u=UI[lang];mech=[loc('mechanisms',lang,x) for x in d['failure_mechanisms']];system_html=''.join(f'<span class="system-route"><strong>{esc(x["label"])}</strong><small>{esc(x["description"])}</small></span>' for x in d['_systems'])
    return f'''<section class="scenario-preview" data-preview-selected="true"><div class="preview-image-shell"><img data-image-state="scenario" src="{image_rel(d,True)}" alt="{esc(d['title'])}"></div><div class="preview-copy"><p class="preview-eyebrow">{d['id']} · {esc(d['problem_family_label'])}</p><h1>{esc(d['title'])}</h1><p class="preview-summary">{esc(d['hook'])}</p>{metric_row(lang,d)}<div class="preview-mechanisms">{''.join(f'<span>{esc(x)}</span>' for x in mech[:4])}</div><div class="preview-koali"><span>{u['koali']}</span><p>{esc(d['_koali'])}</p></div><a class="preview-cta" href="../../index.html">← {u['back']}</a></div><aside class="preview-profile" data-family="{d['problem_family']}"><div class="profile-heading"><span class="profile-title">{u['inside']}</span><span class="profile-section-label">{u['path']}</span></div><div class="profile-systems"><div class="system-route-list">{system_html}</div></div><div class="profile-context"><div><span>{u['mechanisms']}</span><strong>{' · '.join(mech[:3])}</strong></div><div><span>{u['scale']}</span><strong>{loc('scale',lang,d['_origin'])} → {loc('scale',lang,d['_extent'])}</strong></div></div></aside></section>'''
def detail_html(lang,d):
    u=UI[lang];mech=' · '.join(loc('mechanisms',lang,x) for x in d['failure_mechanisms'][:4]);holders=' • '.join(d['_holders'][:3]);success=' • '.join(d['_success'][:2]);cases=d['_cases'][:3]
    case_list=''.join(f'<li>{esc(x)}</li>' for x in cases)
    info=f'''<section class="scenario-info-mosaic" data-family="{d['problem_family']}"><article class="detail-hex detail-hex--trigger"><div class="detail-hex-inner"><span>{u['whatbreaks']}</span><strong>{esc(mech)}</strong></div></article><article class="detail-hex detail-hex--mechanism"><div class="detail-hex-inner"><span>{u['whoknows']}</span><p>{esc(holders)}</p></div></article><article class="detail-hex detail-hex--flow"><div class="detail-hex-inner"><span>{u['response']}</span><p>{esc(d['_koali'])}</p></div></article><article class="detail-hex detail-hex--systems"><div class="detail-hex-inner"><span>{u['cases']}</span><ul class="detail-case-list">{case_list}</ul></div></article><article class="detail-hex detail-hex--transfer"><div class="detail-hex-inner"><span>{u['success']}</span><p>{esc(success)}</p></div></article></section><p class="evidence-note">{u['evidence']}</p>'''
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><link rel="stylesheet" href="../../../assets/styles.css"><title>{esc(d['title'])} | {u['title']}</title></head><body><header class="site-header"><a class="brand" href="../../index.html"><img class="brand-mark" src="../../../assets/brand/koali-mark.svg" alt=""><span class="brand-copy"><span class="brand-product"><strong>Koali</strong><span>{u['title']}</span></span><small>the Sociotechnical Operating System</small></span></a><nav class="language-switcher"><a class="{'active' if lang=='en' else ''}" href="{'index.html' if lang=='en' else '../../../en/uses/'+d['id']+'/index.html'}">EN</a><span>/</span><a class="{'active' if lang=='fr' else ''}" href="{'index.html' if lang=='fr' else '../../../fr/uses/'+d['id']+'/index.html'}">FR</a></nav></header><main><div class="mosaic-experience scenario-detail-experience">{selected_preview(lang,d)}{info}<article class="scenario-article">{markdown_basic(d['_body'])}</article></div></main><script src="../../../assets/preview-layout.js"></script></body></html>'''
def write():
    if PREVIEW.exists():shutil.rmtree(PREVIEW)
    (PREVIEW/'assets/brand').mkdir(parents=True);shutil.copy2(ROOT/'public/brand/koali-mark.svg',PREVIEW/'assets/brand/koali-mark.svg')
    if (ROOT/'public/scenarios').exists():shutil.copytree(ROOT/'public/scenarios',PREVIEW/'assets/scenarios')
    css='\n'.join((ROOT/x).read_text(encoding='utf-8') for x in ['src/styles/global.css','src/styles/mosaic.css','src/styles/scenario.css']);(PREVIEW/'assets/styles.css').write_text(css,encoding='utf-8')
    shutil.copy2(ROOT/'src/scripts/preview-layout.ts',PREVIEW/'assets/preview-layout.js')
    app=r'''(() => {
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
})();'''
    (PREVIEW/'assets/app.js').write_text(app,encoding='utf-8')
    (PREVIEW/'index.html').write_text('''<!doctype html><meta charset="utf-8"><script>const l=(navigator.languages||[navigator.language||'en']).some(x=>String(x).toLowerCase().startsWith('fr'))?'fr':'en';location.replace(`./${l}/index.html`)</script><p><a href="./en/index.html">English</a> · <a href="./fr/index.html">Français</a></p>''',encoding='utf-8')
    for lang in ['en','fr']:
        items=load(lang);(PREVIEW/lang/'uses').mkdir(parents=True,exist_ok=True);(PREVIEW/lang/'index.html').write_text(main_html(lang,items),encoding='utf-8')
        for d in items:
            out=PREVIEW/lang/'uses'/d['id'];out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text(detail_html(lang,d),encoding='utf-8')
    print('Offline preview generated: 2 mosaic pages + 72 scenario pages.')
if __name__=='__main__':write()
