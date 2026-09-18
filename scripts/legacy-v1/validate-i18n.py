from pathlib import Path
import json, re, sys

R=Path(__file__).resolve().parents[1]
errors=[]
meta=json.loads((R/'src/data/scenarios.json').read_text(encoding='utf-8'))
fr_tags=json.loads((R/'src/i18n/fr-tags.json').read_text(encoding='utf-8'))
public_values=set()
for item in meta.values():
    for key in ('palette','scales','settings','properties','domains','transfer_domains'):
        public_values.update(item.get(key,[]) or [])
missing_tags=sorted(public_values-set(fr_tags))
if missing_tags: errors.append('French public-tag labels missing: '+', '.join(missing_tags))
if len(meta)!=120: errors.append(f'shared metadata expected 120 scenarios, found {len(meta)}')
for sid,d in meta.items():
    if d.get('id') and d.get('id')!=sid: errors.append(f'{sid}: shared metadata id mismatch')

localized_fields={'title','category_label','pattern_label','pattern','continuity_gap','preview_summary','preview_image_alt'}
common_fields={'primary_category','pattern_family','palette','components','entry_trigger','scales','settings','properties','domains','signature_patterns','canon_refs','transfer_domains','derivation','runtime_evidence','preview_image'}
for locale in ('en','fr'):
    files=sorted((R/f'src/content/scenarios/{locale}').glob('SCN-*.md'))
    if len(files)!=120: errors.append(f'{locale}: expected 120 localized files')
    for p in files:
        fm=p.read_text(encoding='utf-8').split('---',2)[1]
        for key in common_fields:
            if re.search(rf'(?m)^{re.escape(key)}:',fm): errors.append(f'{p.relative_to(R)} duplicates shared field {key}')
        for key in localized_fields|{'id','locale'}:
            if not re.search(rf'(?m)^{re.escape(key)}:',fm): errors.append(f'{p.relative_to(R)} missing localized field {key}')

required=[
 ('src/pages/[lang]/uses/index.astro','getLocalizedScenarios'),
 ('src/pages/[lang]/uses/[id].astro','getStaticPaths'),
 ('src/layouts/BaseLayout.astro','language-switcher'),
 ('src/layouts/BaseLayout.astro','hreflang'),
 ('src/pages/index.astro','navigator.languages'),
 ('src/components/ScenarioMosaic.astro','`/${locale}/uses/${entry.data.id}/`'),
 ('src/i18n/ui.ts','Mosaïque de scénarios'),
]
for file,token in required:
    p=R/file
    if not p.exists() or token not in p.read_text(encoding='utf-8'): errors.append(f'{file} missing bilingual contract token {token}')

for locale in ('en','fr'):
    preview=R/'preview'/locale/'index.html'
    if not preview.exists(): errors.append(f'preview/{locale}/index.html missing'); continue
    t=preview.read_text(encoding='utf-8')
    if 'language-switcher' not in t: errors.append(f'preview/{locale} missing language switcher')
    if locale=='fr':
        for token in ('Mosaïque de scénarios','Dans Koali','Rechercher un besoin, un système ou un exemple…','Conditions particulières'):
            if token not in t: errors.append(f'French preview missing {token}')
        for stale in ('Scenario profile','Search the mosaic…','Special conditions'):
            if stale in t: errors.append(f'French preview leaks English UI: {stale}')
    else:
        for token in ('Scenario Mosaic','Inside Koali','Search a need, system, or example…'):
            if token not in t: errors.append(f'English preview missing {token}')

fr_detail=R/'preview/fr/uses/SCN-061/index.html'
if not fr_detail.exists(): errors.append('French detailed scenario page missing')
else:
    t=fr_detail.read_text(encoding='utf-8')
    fr_source=R/'src/content/scenarios/fr/SCN-061.md'
    fr_title_match=re.search(r'(?m)^title:\s*(.+)$', fr_source.read_text(encoding='utf-8'))
    fr_title=fr_title_match.group(1).strip().strip("'\"") if fr_title_match else 'SCN-061'
    for token in (fr_title,'Part de','Ce qui se perd sans continuité','Chemin système','Comment ça circule','Aussi utile pour'):
        if token not in t: errors.append(f'French public scenario detail missing {token}')
    for stale in ('What can get lost','Ce qui peut se perdre','Koali keeps connected','Koali maintient le lien','PAT-','POS-','COMPOSED','UNVERIFIED'):
        if stale in t: errors.append(f'French public scenario detail leaks internal/English token: {stale}')

print('Bilingual contract: 120 shared identities + 120 EN + 120 FR editorial documents')
if errors:
    print('\nI18N VALIDATION FAILED')
    for e in errors[:100]: print(' -',e)
    sys.exit(1)
print('Bilingual routing, content separation, language switch, and offline previews validated.')
