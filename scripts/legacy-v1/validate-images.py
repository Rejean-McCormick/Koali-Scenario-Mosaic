from pathlib import Path
import json, re, struct, sys

R=Path(__file__).resolve().parents[1]
SOURCE_DIR=R/'src/assets/scenario-images'
PNG_DIR=R/'public/scenarios/images'
SOURCE_SIZE=1254
DEFAULT_SIZE=627
RESPONSIVE_SIZES=(418,627)
STALE_SIZES=(836,1254)
errors=[]

def png_size(path):
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
    if not 1<=n<=120:
        errors.append(f'Source PNG outside SCN-001..120: {p.name}')
        continue
    source_ids.add(n)
    try:
        w,h=png_size(p)
        if (w,h)!=(SOURCE_SIZE,SOURCE_SIZE):
            errors.append(f'Source PNG must be {SOURCE_SIZE}x{SOURCE_SIZE}: {p.name} ({w}x{h})')
    except ValueError as e:
        errors.append(f'{p.name}: {e}')

# Any public default PNG must physically be 627x627, even when source masters
# are absent in CI/Netlify. This prevents a 1254 file from being mislabeled 627w.
public_ids=set()
for p in sorted(PNG_DIR.glob('SCN-*.png')) if PNG_DIR.exists() else []:
    m=re.fullmatch(r'SCN-(\d{3})\.png',p.name)
    if not m:
        continue
    n=int(m.group(1))
    public_ids.add(n)
    try:
        w,h=png_size(p)
        if (w,h)!=(DEFAULT_SIZE,DEFAULT_SIZE):
            errors.append(f'Public default PNG must be {DEFAULT_SIZE}x{DEFAULT_SIZE}: {p.name} ({w}x{h})')
    except ValueError as e:
        errors.append(f'{p.name}: {e}')

for n in sorted(public_ids | source_ids):
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
        if stale.exists():
            errors.append(f'Stale oversized responsive PNG must be removed: {stale.name}')

# Offline preview may still use its SVG fallback until regenerated.
for locale in ('en','fr'):
    preview=R/'preview'/locale/'index.html'
    if not preview.exists():
        errors.append(f'preview/{locale}/index.html missing; run npm run preview:offline')
        continue
    text=preview.read_text(encoding='utf-8')
    m=re.search(r'<script type="application/json" data-mosaic-data>(.*?)</script>',text,re.S)
    if not m:
        errors.append(f'Offline {locale} preview scenario JSON missing')
        continue
    data=json.loads(m.group(1))
    if len(data)!=120:
        errors.append(f'Offline {locale} preview has {len(data)} scenarios')
    for i in range(1,121):
        sid=f'SCN-{i:03d}'
        item=data.get(sid)
        if not item:
            errors.append(f'Offline {locale} preview missing {sid}')
            continue
        png_ref=f'../../public/scenarios/images/{sid}.png'
        svg_ref=f'../assets/scenarios/{sid}.svg'
        image=item.get('image','')
        if image not in (png_ref,svg_ref):
            errors.append(f'{locale}/{sid}: unsupported image reference {image!r}')
            continue
        resolved=(preview.parent/image).resolve()
        if not resolved.exists():
            errors.append(f'{locale}/{sid}: resolved preview image missing: {resolved}')
        srcset=item.get('imageSrcSet','')
        if image==png_ref and i in public_ids:
            for size in RESPONSIVE_SIZES:
                ref=f'../../public/scenarios/images/{variant_name(sid,size)} {size}w'
                if ref not in srcset:
                    errors.append(f'{locale}/{sid}: srcset missing {size}w candidate')
            for size in STALE_SIZES:
                if f' {size}w' in srcset:
                    errors.append(f'{locale}/{sid}: srcset still exposes stale {size}w candidate')

helper=R/'src/lib/scenario-image.ts'
component=R/'src/components/ScenarioMosaic.astro'
preview_component=R/'src/components/ScenarioPreview.astro'
if not helper.exists() or 'resolveScenarioPreviewImageSet' not in helper.read_text(encoding='utf-8'):
    errors.append('Astro responsive PNG resolver helper missing')
else:
    helper_text=helper.read_text(encoding='utf-8')
    if 'const RESPONSIVE_WIDTHS = [418, 627]' not in helper_text:
        errors.append('Astro responsive PNG resolver must expose only 418 / 627 widths')
if not component.exists() or 'imageSrcSet' not in component.read_text(encoding='utf-8'):
    errors.append('Astro Mosaic does not expose responsive image srcset')
if not preview_component.exists() or 'srcset=' not in preview_component.read_text(encoding='utf-8'):
    errors.append('Astro preview image does not render srcset')

print(f'Source originals: {len(sources)} / 120 at {SOURCE_SIZE}x{SOURCE_SIZE}')
print(f'Public default images: {len(public_ids)} at required {DEFAULT_SIZE}x{DEFAULT_SIZE}')
print(f'Responsive widths: {" / ".join(map(str,RESPONSIVE_SIZES))} px')
if errors:
    print('\nIMAGE VALIDATION FAILED')
    for e in errors:
        print(' -',e)
    sys.exit(1)
print('Bilingual responsive scenario image validation passed.')
