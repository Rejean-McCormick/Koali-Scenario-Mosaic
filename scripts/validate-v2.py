from frontmatter_stdlib import parse_frontmatter
from pathlib import Path
import re, sys, json
ROOT=Path(__file__).resolve().parents[1]
langs=['en','fr']
expected_families={
'coordination_breakdown','signal_context_loss','knowledge_attrition','distributed_intelligence',
'evidence_vs_noise','decision_traceability','action_learning_loops','capacity_sovereignty'}
required={'id','title','locale','problem_family','problem_family_label','scenario_type','hook','failure_mechanisms','scale','urgency','stakes','coordination_gap','domains','koali_patterns','koali_components','real_case_ids','evidence_status','koali_runtime_status'}
all_data={}
errors=[]
real_cases=json.loads((ROOT/'src/data/real-cases.json').read_text(encoding='utf-8'))
for lang in langs:
    files=sorted((ROOT/'src/content/scenarios'/lang).glob('SCN-*.md'))
    if len(files)!=36: errors.append(f'{lang}: expected 36 scenarios, found {len(files)}')
    for p in files:
        text=p.read_text(encoding='utf-8')
        m=re.match(r'^---\n(.*?)\n---\n',text,re.S)
        if not m: errors.append(f'{p}: missing frontmatter'); continue
        data=parse_frontmatter(m.group(1))
        missing=required-set(data)
        if missing: errors.append(f'{p}: missing {sorted(missing)}')
        if data.get('locale')!=lang: errors.append(f'{p}: locale mismatch')
        if data.get('id')!=p.stem: errors.append(f'{p}: id/filename mismatch')
        if data.get('problem_family') not in expected_families: errors.append(f'{p}: unknown family {data.get("problem_family")}')
        if '→' not in str(data.get('scale','')) and not data.get('scale'): errors.append(f'{p}: invalid scale')
        for field in ['failure_mechanisms','stakes','domains','koali_patterns','koali_components','real_case_ids']:
            if not isinstance(data.get(field),list) or not data[field]: errors.append(f'{p}: {field} must be non-empty list')
        for case_id in data.get('real_case_ids',[]):
            if case_id not in real_cases: errors.append(f'{p}: unknown real case {case_id}')
            elif not real_cases[case_id].get('en') or not real_cases[case_id].get('fr'): errors.append(f'{p}: incomplete real-case localization {case_id}')
        if data.get('koali_runtime_status')!='COMPOSED · runtime UNVERIFIED': errors.append(f'{p}: runtime status must remain explicit/unverified')
        if ('## Real-world parallels' if lang=='en' else '## Cas réels semblables') not in text: errors.append(f'{p}: missing real-world parallels section')
        if len(re.findall(r'https?://',text))<1: errors.append(f'{p}: no real-world source URL')
        all_data[(lang,p.stem)]=data

# V2 public-language and image contract checks
for family in expected_families:
    fallback=ROOT/'public/scenarios/fallback'/f'{family}.svg'
    if not fallback.exists(): errors.append(f'missing family image fallback: {fallback}')
for p in sorted((ROOT/'src/content/scenarios/fr').glob('SCN-*.md')):
    text=p.read_text(encoding='utf-8')
    section=re.search(r'## Ce qui casse\n\n([\s\S]*?)(?=\n## )',text)
    if section and re.search(r'\b[a-z]+_[a-z_]+\b',section.group(1)): errors.append(f'{p}: internal mechanism id exposed in French body')
    fm=re.match(r'^---\n(.*?)\n---\n',text,re.S)
    if fm:
        data=parse_frontmatter(fm.group(1)); block=re.search(r'## Cas réels semblables\n\n([\s\S]*?)(?=\n## Limites)',text)
        headings=re.findall(r'^###\s+(.+)$',block.group(1),re.M) if block else []
        expected=[real_cases[c]['fr'] for c in data.get('real_case_ids',[]) if c in real_cases]
        if headings!=expected: errors.append(f'{p}: real-case display titles differ from registry')



# V2.2 interaction/layout regression contract (restored from V1)
css=(ROOT/'src/styles/mosaic.css').read_text(encoding='utf-8')
mosaic_js=(ROOT/'src/scripts/mosaic.ts').read_text(encoding='utf-8')
offline_builder=(ROOT/'scripts/build-offline-preview.py').read_text(encoding='utf-8')
layout_checks={
    'V2.2 stability marker':'V2.2 preview stability + smartphone parity with V1',
    'stable desktop preview height':'height:318px',
    'stable medium preview height':'height:466px',
    'mobile content-driven rows':'grid-template-rows:auto auto auto',
    'mobile copy first':'.preview-copy{grid-column:1;grid-row:1;height:auto;overflow:visible}',
    'mobile profile second':'.preview-profile{grid-column:1;grid-row:2;height:auto;min-height:0;max-height:none;overflow:visible}',
    'mobile image last':'.preview-image-shell{grid-column:1;grid-row:3;width:min(176px,52vw);height:auto;max-height:none}',
}
for label,needle in layout_checks.items():
    if needle not in css: errors.append(f'layout regression contract missing: {label}')
if '140' not in mosaic_js or 'pointerenter' not in mosaic_js: errors.append('source Mosaic lost V1 hover-intent delay')
if 'touchcancel' not in mosaic_js or 'scrollIntoView' not in mosaic_js: errors.append('source Mosaic lost V1 touch/swipe handling')
if 'data-preview-swipe="true"' not in offline_builder: errors.append('offline preview lost touch/swipe marker')
if 'schedulePreview' not in offline_builder or '140' not in offline_builder or 'pointerenter' not in offline_builder: errors.append('offline preview lost V1 hover-intent delay')
if 'touchcancel' not in offline_builder or 'scrollIntoView' not in offline_builder: errors.append('offline preview lost V1 touch/swipe handling')

for i in range(1,37):
    sid=f'SCN-{i:03d}'
    if ('en',sid) not in all_data or ('fr',sid) not in all_data: errors.append(f'{sid}: bilingual pair incomplete')
    elif all_data[('en',sid)]['problem_family']!=all_data[('fr',sid)]['problem_family']: errors.append(f'{sid}: family mismatch EN/FR')
if errors:
    print('V2 validation failed:')
    for e in errors: print(' -',e)
    sys.exit(1)
print('V2 validation OK: 36 canonical scenarios, 72 localized files, 8 problem families.')
