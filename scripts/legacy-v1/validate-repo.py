from pathlib import Path
import json, sys, re
R=Path(__file__).resolve().parents[1]
errors=[]

def read_frontmatter_scalar(raw, key):
    """Read one simple top-level YAML frontmatter scalar without PyYAML."""
    parts = raw.split('---', 2)
    if len(parts) < 3:
        return ''
    match = re.search(rf'(?m)^{re.escape(key)}:\s*(.*?)\s*$', parts[1])
    if not match:
        return ''
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value

js=(R/'src/scripts/mosaic.ts').read_text(encoding='utf-8')
preview_layout=(R/'src/scripts/preview-layout.ts').read_text(encoding='utf-8')
css=(R/'src/styles/mosaic.css').read_text(encoding='utf-8')
component=(R/'src/components/ScenarioMosaic.astro').read_text(encoding='utf-8')
layout=json.loads((R/'src/data/mosaic-layout.json').read_text(encoding='utf-8'))
package=json.loads((R/'package.json').read_text(encoding='utf-8'))
netlify=(R/'netlify.toml').read_text(encoding='utf-8') if (R/'netlify.toml').exists() else ''
meta=json.loads((R/'src/data/scenarios.json').read_text(encoding='utf-8'))
if len(meta)!=120: errors.append('shared scenario metadata count')
system_catalog=json.loads((R/'src/data/system-catalog.json').read_text(encoding='utf-8'))
system_routes=json.loads((R/'src/data/scenario-system-routes.json').read_text(encoding='utf-8'))
capability_titles=json.loads((R/'src/data/scenario-capability-titles.json').read_text(encoding='utf-8'))
if set(capability_titles)!=set(meta): errors.append('specific capability-title coverage')
for locale in ('en','fr'):
    localized=[]
    for sid in sorted(meta):
        title=(capability_titles.get(sid,{}) or {}).get(locale,'').strip()
        if not title: errors.append(f'{sid}: missing {locale} specific capability title'); continue
        localized.append(title.casefold())
        source=R/f'src/content/scenarios/{locale}/{sid}.md'
        if source.exists():
            raw=source.read_text(encoding='utf-8')
            pattern_label=read_frontmatter_scalar(raw, 'pattern_label')
            if not pattern_label:
                errors.append(f'{sid}: cannot read {locale} pattern_label for title validation')
            elif title.casefold()==pattern_label.strip().casefold():
                errors.append(f'{sid}: {locale} public title repeats pattern family')
    if len(localized)!=120 or len(set(localized))!=120: errors.append(f'{locale} specific capability titles must be 120 unique values')
if set(system_routes)!=set(meta): errors.append('scenario system-route coverage')
for sid, routes in system_routes.items():
    if not 1 <= len(routes) <= 3: errors.append(f'{sid}: expected 1–3 system routes')
    if len(routes)!=len(set(routes)): errors.append(f'{sid}: duplicate system routes')
    for route in routes:
        if route not in system_catalog: errors.append(f'{sid}: unknown system route {route}')
    secondary=set(meta.get(sid,{}).get('secondary_components',[]) or [])
    for specialized in ('smart-vote','ekoh','semantik'):
        if specialized in secondary and specialized not in routes: errors.append(f'{sid}: missing specialized route {specialized}')
for locale in ('en','fr'):
    if len(list((R/f'src/content/scenarios/{locale}').glob('SCN-*.md')))!=120: errors.append(f'{locale} scenario count')
if 'is-related' in js or 'is-related' in css: errors.append('related highlight')
if '.mosaic-cell:hover' in css: errors.append('css hover state')
if '.mosaic-cell:focus-visible' in css: errors.append('independent focus highlight')
if 'selectOnly' not in js: errors.append('single select')
title_rule = re.search(r'\.preview-copy h1\{([^}]*)\}', css)
title_css = title_rule.group(1) if title_rule else ''
if 'line-height:1.08' not in title_css or 'height:auto' not in title_css or 'height:6.7rem' in title_css: errors.append('adaptive title flow')
if '-webkit-line-clamp:2' not in title_css: errors.append('two-line title clamp')
if '--preview-title-min' not in title_css or 'FIT_ITERATIONS' not in preview_layout: errors.append('bounded title auto-fit')
if 'titleDensity' in js or 'data-title-density' in css: errors.append('obsolete title-density heuristic')
if 'scrollHeight' not in preview_layout or 'MAX_TITLE_LINES = 2' not in preview_layout: errors.append('measured two-line title fit')
if 'ResizeObserver' not in preview_layout or 'document.fonts?.ready' not in preview_layout: errors.append('preview layout resize and font reflow')
if 'fitPaletteRows' in js or '--preview-palette-fit' not in css: errors.append('shared palette fitting')
if 'height:286px' not in css or 'height:clamp(180px,24vh,220px)' not in css: errors.append('one-viewport compact sizing')
if 'territory-legend' not in css or 'MosaicLegend' not in component: errors.append('color legend')
if package.get('scripts',{}).get('build')!='npm run validate && astro build': errors.append('Netlify-safe production build')
if 'preview:offline' in package.get('scripts',{}).get('build',''): errors.append('offline preview leaked into production build')
if 'NODE_VERSION = "24.20.0"' not in netlify or 'publish = "dist"' not in netlify: errors.append('Netlify configuration')
if 'align-items:end' not in css or '.profile-context span{line-height:1.12}' not in css: errors.append('profile context bottom alignment')
if layout['geometry']['rows']!=6 or layout['geometry']['columns']!=20: errors.append('panorama geometry')
if layout['geometry'].get('territories')!=8: errors.append('territory count')

# Responsive preview contract: no horizontal spill and no branded cover crop.
if 'container-name:scenario-layout' not in css: errors.append('preview container query root')
if '@container scenario-layout (min-width:1120px)' not in css: errors.append('wide preview container contract')
if 'minmax(250px,292px) minmax(480px,1fr) minmax(300px,340px)' not in css: errors.append('wide preview column contract')
if '@container scenario-layout (min-width:721px) and (max-width:1119px)' not in css: errors.append('tablet preview container contract')
if '@container scenario-layout (max-width:720px)' not in css or 'grid-template-columns:1fr' not in css: errors.append('narrow preview stack contract')
if 'img[data-image-state="cover"]{object-fit:contain' not in css: errors.append('cover contain contract')
if 'img[data-image-state="scenario"]{object-fit:cover' not in css: errors.append('scenario image cover contract')
if "dataset.imageState = 'scenario'" not in js: errors.append('scenario image state switch')
cover=(R/'public/mosaic-cover.svg').read_text(encoding='utf-8')
if '<text ' in cover: errors.append('initial cover repeats product text')
if not (R/'src/pages/[lang]/uses/index.astro').exists(): errors.append('localized mosaic route')
if not (R/'src/pages/[lang]/uses/[id].astro').exists(): errors.append('localized scenario route')
if not (R/'preview/en/index.html').exists() or not (R/'preview/fr/index.html').exists(): errors.append('bilingual offline preview')

# Public scenario page contract: same preview shell, supplemental public hexes, no internal Markdown dump.
scenario_route=(R/'src/pages/[lang]/uses/[id].astro').read_text(encoding='utf-8')
preview_component=(R/'src/components/ScenarioPreview.astro').read_text(encoding='utf-8')
detail_component=(R/'src/components/ScenarioInfoMosaic.astro').read_text(encoding='utf-8')
portal_source=(R/'src/lib/scenario-portal.ts').read_text(encoding='utf-8')
offline_builder=(R/'scripts/build-offline-preview.py').read_text(encoding='utf-8')
scenario_css=(R/'src/styles/scenario.css').read_text(encoding='utf-8')
if 'ScenarioPreview' not in scenario_route or 'ScenarioInfoMosaic' not in scenario_route: errors.append('scenario selected-state composition')
if 'render(' in scenario_route or '<Content' in scenario_route or 'scenario-body' in scenario_route: errors.append('public scenario still renders internal markdown')
for token in ('detailStartsWith','detailWhatGetsLost','detailKoaliContinuity','detailFlow','detailTransferable'):
    if token not in detail_component: errors.append(f'missing public detail token {token}')
if 'scenario-info-mosaic' not in scenario_css or 'detail-hex--systems' not in scenario_css or 'detail-hex--mechanism' not in scenario_css: errors.append('capability-first public detail styling')
if 'buildKoaliContinuityCopy' not in portal_source: errors.append('Koali continuity fallback contract')
if 'publicSummary' not in portal_source or 'koaliHelp: publicSummary' not in portal_source: errors.append('authored public impact-copy contract')
if 'scenario.data.continuity_gap' not in detail_component: errors.append('public continuity-gap detail contract')
if 'build_koali_continuity_copy' not in offline_builder or "x['continuity_gap']" not in offline_builder: errors.append('offline Koali continuity fallback parity')
if "'summary':summary if summary" not in offline_builder or 'example_lead(summary)' not in offline_builder: errors.append('offline authored impact-copy parity')
if 'paletteBacklightGroups' not in preview_component or 'data-architecture' not in preview_component: errors.append('eight-tag architecture discovery contract')
if 'getScenarioPortal' not in preview_component or 'data-preview-example' not in preview_component or 'data-preview-system-list' not in preview_component: errors.append('capability-first system portal contract')
if "import '../scripts/preview-layout.ts'" not in preview_component: errors.append('shared preview layout controller')
if (
    'scenario = null' not in preview_component
    or "data-image-state={selected ? 'scenario' : 'empty'}" not in preview_component
    or 'data-preview-prompt' not in preview_component
    or 'hidden={!selected}' not in preview_component
): errors.append('shared preview selected-state contract')

# Generated public detail pages must not expose editorial/internal governance markers.
internal_markers=('PAT-','SIG-','POS-','COMPOSED','UNVERIFIED','PARTIALLY-VALIDATED','DOCUMENTED','KristALL')
for locale in ('en','fr'):
    pages=sorted((R/f'preview/{locale}/uses').glob('SCN-*/index.html'))
    if len(pages)!=120: errors.append(f'{locale} offline public scenario page count')
    for page in pages:
        html=page.read_text(encoding='utf-8')
        for marker in internal_markers:
            if marker in html: errors.append(f'internal marker leaked into {locale}/{page.parent.name}: {marker}')
        if 'scenario-info-mosaic' not in html: errors.append(f'{locale}/{page.parent.name} missing public detail honeycomb')
        if '../../../assets/preview-layout.js' not in html: errors.append(f'{locale}/{page.parent.name} missing shared preview layout')


# Magnetic territory-label contract: visual legend replaced by embedded, non-intercepting labels.
territory_component=(R/'src/components/MosaicTerritoryLabels.astro').read_text(encoding='utf-8') if (R/'src/components/MosaicTerritoryLabels.astro').exists() else ''
territory_script=(R/'src/scripts/territory-repulsion.ts').read_text(encoding='utf-8') if (R/'src/scripts/territory-repulsion.ts').exists() else ''
if 'MosaicTerritoryLabels' not in component or 'data-mosaic-canvas' not in component: errors.append('magnetic territory labels not integrated')
if 'sr-only' not in (R/'src/components/MosaicLegend.astro').read_text(encoding='utf-8'): errors.append('detached legend still visually exposed')
if 'data-territory-label-layer' not in territory_component or 'aria-hidden="true"' not in territory_component: errors.append('territory overlay accessibility')
if "from 'gsap/SplitText'" not in territory_script or 'maxOffset: 11' not in territory_script: errors.append('territory repulsion implementation')
if 'prefers-reduced-motion: reduce' not in territory_script or '(hover: hover) and (pointer: fine)' not in territory_script: errors.append('territory motion eligibility')
if len(layout.get('territoryLabels',{})) != 8: errors.append('territory label anchors')
for locale in ('en','fr'):
    t=(R/f'preview/{locale}/index.html').read_text(encoding='utf-8')
    if t.count('data-territory-id=') != 8: errors.append(f'{locale} offline territory labels')
    if 'territory-legend sr-only' not in t: errors.append(f'{locale} semantic legend fallback')

print('120 shared scenarios; 240 localized documents; 20 × 6 panoramic honeycomb; bilingual EN/FR routes')
if errors:
    print(errors); sys.exit(1)
