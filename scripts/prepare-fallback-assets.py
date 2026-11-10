#!/usr/bin/env python3
"""Generate explicitly generic fallback SVGs only when snapshot assets are absent.

Never replace supplied brand/artwork. These small placeholders are NOT official Koali
brand identity; the product owner must restore reviewed media before public release.
"""
from pathlib import Path
import html
ROOT=Path(__file__).resolve().parents[1]
FAMILIES=('coordination_breakdown','signal_context_loss','knowledge_attrition','distributed_intelligence','evidence_vs_noise','decision_traceability','action_learning_loops','capacity_sovereignty')

def ensure():
    generated=[]
    for family in FAMILIES:
        path=ROOT/'public/scenarios/fallback'/f'{family}.svg'
        if path.exists():continue
        path.parent.mkdir(parents=True,exist_ok=True)
        title=html.escape(family.replace('_',' ').title())
        path.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 627 627" role="img" aria-labelledby="title description">
<title id="title">{title}</title><desc id="description">Generic fallback illustration for a missing scenario image; not a photograph or verified outcome.</desc>
<rect width="627" height="627" fill="#101a24"/>
<path d="M314 74l207 119v241L314 553 106 434V193z" fill="#193f41" stroke="#4a9690" stroke-width="12"/>
<circle cx="314" cy="314" r="87" fill="none" stroke="#8fccc4" stroke-width="10"/>
<path d="M255 314h118m-59-59v118" stroke="#8fccc4" stroke-width="10"/>
<text x="314" y="510" fill="#eff6f8" font-size="21" font-family="sans-serif" text-anchor="middle">{title}</text>
</svg>\n''',encoding='utf8')
        generated.append(str(path.relative_to(ROOT)))
    # Source ZIPs can omit static brand assets; produce only a clearly nonofficial
    # offline fallback for a usable local preview, never overwrite owner art.
    brand=ROOT/'public/brand/koali-mark.svg'
    if not brand.exists():
        brand.parent.mkdir(parents=True,exist_ok=True)
        brand.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 84 42" aria-label="Koali — temporary fallback mark"><rect width="84" height="42" rx="9" fill="#1e6864"/><text x="42" y="28" text-anchor="middle" font-size="18" fill="white" font-family="sans-serif" font-weight="bold">Koali</text></svg>\n''',encoding='utf8')
        generated.append(str(brand.relative_to(ROOT)))
    print(f'Generic missing-asset fallbacks: {len(generated)} created; existing images preserved')

if __name__=='__main__':ensure()
