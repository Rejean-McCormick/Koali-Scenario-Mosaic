from pathlib import Path
import re, struct, sys

ROOT=Path(__file__).resolve().parents[1]
SOURCE_DIR=ROOT/'src/assets/scenario-images'
PNG_DIR=ROOT/'public/scenarios/images'
SCENARIO_COUNT=36
SOURCE_SIZE=1254
DEFAULT_SIZE=627
RESPONSIVE_SIZES=(418,627)
STALE_SIZES=(836,1254)
errors=[]

def png_size(path: Path):
    b=path.read_bytes()
    if not b.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('invalid PNG signature')
    if len(b)<24 or b[12:16]!=b'IHDR':
        raise ValueError('missing PNG IHDR')
    return struct.unpack('>II',b[16:24])

def variant_name(sid,size):
    return f'{sid}.png' if size==DEFAULT_SIZE else f'{sid}-{size}.png'

sources=sorted(SOURCE_DIR.glob('*.png')) if SOURCE_DIR.exists() else []
source_ids=set()
for p in sources:
    m=re.fullmatch(r'SCN-(\d{3})\.png',p.name)
    if not m:
        errors.append(f'Invalid source PNG name: {p.name}')
        continue
    n=int(m.group(1))
    if not 1<=n<=SCENARIO_COUNT:
        errors.append(f'Source PNG outside SCN-001..SCN-{SCENARIO_COUNT:03d}: {p.name}')
        continue
    source_ids.add(n)
    try:
        w,h=png_size(p)
        if (w,h)!=(SOURCE_SIZE,SOURCE_SIZE):
            errors.append(f'Source PNG must be {SOURCE_SIZE}x{SOURCE_SIZE}: {p.name} ({w}x{h})')
    except ValueError as e:
        errors.append(f'{p.name}: {e}')

public_defaults={}
public_variants={}
if PNG_DIR.exists():
    for p in sorted(PNG_DIR.glob('SCN-*.png')):
        m=re.fullmatch(r'SCN-(\d{3})(?:-(\d+))?\.png',p.name)
        if not m:
            errors.append(f'Unsupported scenario PNG filename: {p.name}')
            continue
        n=int(m.group(1)); suffix=int(m.group(2)) if m.group(2) else None
        if not 1<=n<=SCENARIO_COUNT:
            errors.append(f'Public scenario PNG outside SCN-001..SCN-{SCENARIO_COUNT:03d}: {p.name}')
            continue
        if suffix is None:
            public_defaults[n]=p
        else:
            public_variants[(n,suffix)]=p

for n,p in sorted(public_defaults.items()):
    try:
        w,h=png_size(p)
        if (w,h)!=(DEFAULT_SIZE,DEFAULT_SIZE):
            errors.append(f'Public default PNG must be {DEFAULT_SIZE}x{DEFAULT_SIZE}: {p.name} ({w}x{h})')
    except ValueError as e:
        errors.append(f'{p.name}: {e}')

covered=set(public_defaults)|source_ids
for n in sorted(covered):
    sid=f'SCN-{n:03d}'
    for size in RESPONSIVE_SIZES:
        output=PNG_DIR/variant_name(sid,size)
        if not output.exists():
            errors.append(f'Missing generated responsive PNG: {output.name}')
            continue
        try:
            w,h=png_size(output)
            if (w,h)!=(size,size):
                errors.append(f'Generated PNG must be {size}x{size}: {output.name} ({w}x{h})')
        except ValueError as e:
            errors.append(f'{output.name}: {e}')
    for size in STALE_SIZES:
        stale=PNG_DIR/f'{sid}-{size}.png'
        if stale.exists(): errors.append(f'Stale oversized responsive PNG must be removed: {stale.name}')

# A responsive variant without its canonical 627 default is a broken public set.
for (n,size),p in sorted(public_variants.items()):
    if size not in (*RESPONSIVE_SIZES,*STALE_SIZES):
        errors.append(f'Unsupported responsive width in filename: {p.name}')
    if n not in public_defaults and n not in source_ids:
        errors.append(f'Orphan responsive PNG without source/default: {p.name}')

helper=ROOT/'src/lib/scenario-image.ts'
helper_text=helper.read_text(encoding='utf-8') if helper.exists() else ''
for needle in ('RESPONSIVE_WIDTHS = [418, 627]','SCENARIO_IMAGE_SIZES','resolveScenarioPreviewImageSet'):
    if needle not in helper_text: errors.append(f'Astro image resolver contract missing: {needle}')

component=ROOT/'src/components/ScenarioPreview.astro'
if not component.exists() or 'srcset=' not in component.read_text(encoding='utf-8') or 'sizes=' not in component.read_text(encoding='utf-8'):
    errors.append('ScenarioPreview must render srcset and sizes')

mosaic=ROOT/'src/components/ScenarioMosaic.astro'
if not mosaic.exists() or 'resolveScenarioPreviewImageSet' not in mosaic.read_text(encoding='utf-8'):
    errors.append('ScenarioMosaic must serialize responsive image data')

print(f'Source masters: {len(sources)} / {SCENARIO_COUNT} at {SOURCE_SIZE}x{SOURCE_SIZE}')
print(f'Public final images: {len(public_defaults)} / {SCENARIO_COUNT} at {DEFAULT_SIZE}x{DEFAULT_SIZE}')
print(f'Responsive widths: {" / ".join(map(str,RESPONSIVE_SIZES))} px')
print(f'Family SVG fallback remains available for {SCENARIO_COUNT-len(public_defaults)} scenario(s) without final PNGs.')
if errors:
    print('\nIMAGE VALIDATION FAILED')
    for e in errors: print(' -',e)
    sys.exit(1)
print('V2.2 responsive scenario image validation passed.')
