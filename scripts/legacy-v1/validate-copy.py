from pathlib import Path
import re, sys

R = Path(__file__).resolve().parents[1]
ROOT = R / 'src' / 'content' / 'scenarios'
errors=[]
checked=0
by_locale={}

def scalar(value:str):
    value=value.strip()
    if len(value)>=2 and value[0]=="'" and value[-1]=="'": return value[1:-1].replace("''", "'")
    if len(value)>=2 and value[0]=='"' and value[-1]=='"': return value[1:-1].replace('\\"','"')
    return value

def fields(path):
    text=path.read_text(encoding='utf-8')
    fm=text.split('---',2)[1] if text.startswith('---') else ''
    out={}
    for key in ('id','locale','title','preview_summary'):
        m=re.search(rf'(?m)^{key}:\s*(.+)$',fm)
        out[key]=scalar(m.group(1)) if m else None
    return out

for locale in ('en','fr'):
    files=sorted((ROOT/locale).glob('SCN-*.md'))
    by_locale[locale]={}
    if len(files)!=120: errors.append(f'{locale}: expected 120 scenario files, found {len(files)}')
    for p in files:
        d=fields(p); sid=d['id'] or p.stem
        by_locale[locale][sid]=d
        checked+=1
        if d['locale']!=locale: errors.append(f'{sid}: {locale} file declares locale {d["locale"]!r}')
        title=(d['title'] or '').strip(); summary=(d['preview_summary'] or '').strip()
        if not title or not summary: errors.append(f'{sid}/{locale}: missing title or preview_summary'); continue
        if summary.casefold().startswith(title.casefold()): errors.append(f'{sid}/{locale}: preview_summary repeats the title')
        if 'koali' not in summary.casefold(): errors.append(f'{sid}/{locale}: preview_summary must explain the Koali response, not only the problem')
        if len(summary) < 150: errors.append(f'{sid}/{locale}: preview_summary is too short for the problem + Koali response format ({len(summary)} chars)')
        nt=re.sub(r'\s+',' ',title).strip().rstrip('.!?;:')
        first=re.split(r'(?<=[.!?])\s+',summary,maxsplit=1)[0]
        nf=re.sub(r'\s+',' ',first).strip().rstrip('.!?;:')
        if nf.casefold()==nt.casefold(): errors.append(f'{sid}/{locale}: first preview sentence duplicates title')
        words=len(summary.split())
        if words < 28 or words > 72: errors.append(f'{sid}/{locale}: preview_summary length {words} words outside 28–72')
        internal_names=('Kristal','Konnaxion','Orgo','UCKK','Smart Vote','SmartVote','SemantiK','EkoH','KonnectED')
        leaked=[name for name in internal_names if re.search(r'(?<![\w-])'+re.escape(name)+r'(?![\w-])', summary, re.I)]
        if leaked: errors.append(f'{sid}/{locale}: preview_summary contains architecture brand(s): '+', '.join(leaked))

if set(by_locale.get('en',{})) != set(by_locale.get('fr',{})):
    errors.append('EN/FR scenario ID sets do not match')
else:
    identical_titles=[]; identical_summaries=[]
    for sid in sorted(by_locale['en']):
        if by_locale['en'][sid]['title']==by_locale['fr'][sid]['title']: identical_titles.append(sid)
        if by_locale['en'][sid]['preview_summary']==by_locale['fr'][sid]['preview_summary']: identical_summaries.append(sid)
    if identical_titles: errors.append('French titles still identical to English: '+', '.join(identical_titles[:10]))
    if identical_summaries: errors.append('French summaries still identical to English: '+', '.join(identical_summaries[:10]))

print(f'Preview-copy validation: {checked} localized scenario documents checked (120 EN + 120 FR)')
if errors:
    print('\nCOPY VALIDATION FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('Bilingual scenario preview-copy validation passed.')
