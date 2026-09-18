import fs from 'node:fs';

const layout = JSON.parse(fs.readFileSync('src/data/mosaic-layout.json','utf8'));
const ui = fs.readFileSync('src/i18n/ui.ts','utf8');
const component = fs.readFileSync('src/components/MosaicTerritoryLabels.astro','utf8');
const mosaic = fs.readFileSync('src/components/ScenarioMosaic.astro','utf8');
const script = fs.readFileSync('src/scripts/territory-repulsion.ts','utf8');
const css = fs.readFileSync('src/styles/mosaic.css','utf8');
const globalCss = fs.readFileSync('src/styles/global.css','utf8');
const scenarioCss = fs.readFileSync('src/styles/scenario.css','utf8');
const pkg = JSON.parse(fs.readFileSync('package.json','utf8'));
const errors = [];

const anchors = layout.territoryLabels ?? {};
const expected = Array.from({length:8},(_,i)=>`CAT-${String(i+1).padStart(2,'0')}`);
if (Object.keys(anchors).length !== 8) errors.push('expected exactly 8 territory label anchors');
for (const id of expected) {
  const a = anchors[id];
  if (!a) { errors.push(`missing anchor ${id}`); continue; }
  for (const key of ['x','y','width']) {
    if (typeof a[key] !== 'number' || a[key] <= 0 || a[key] >= 1) errors.push(`${id} invalid normalized ${key}`);
  }
  if (a.anchor !== 'center') errors.push(`${id} anchor must be center`);
  const re = new RegExp(`'${id}'\\s*:\\s*\\[`,'g');
  if ((ui.match(re) ?? []).length !== 2) errors.push(`${id} must have EN and FR map label text`);
}
if (!component.includes('aria-hidden="true"') || !component.includes('data-territory-label-layer')) errors.push('territory label overlay accessibility contract');
if (!component.includes('data-territory-id') || !component.includes('data-territory-line')) errors.push('territory label data hooks');
if (!mosaic.includes('MosaicTerritoryLabels') || !mosaic.includes('data-mosaic-canvas')) errors.push('mosaic integration');
if (!mosaic.includes("../scripts/territory-repulsion.ts")) errors.push('magnetic script not loaded');
if (!script.includes("from 'gsap'") || !script.includes("from 'gsap/SplitText'")) errors.push('GSAP/SplitText dependency contract');
if (!script.includes('(hover: hover) and (pointer: fine)') || !script.includes('prefers-reduced-motion: reduce')) errors.push('pointer/motion eligibility contract');
if (!script.includes('ResizeObserver') || !script.includes('IntersectionObserver')) errors.push('observer lifecycle contract');
if (!script.includes('gsap.ticker.remove') || !script.includes('settleVelocity')) errors.push('ticker sleep/spring contract');
if (!css.includes('pointer-events:none') || !css.includes('.territory-label__char')) errors.push('non-intercepting character layer contract');
if (!css.includes('@media(prefers-reduced-motion:reduce)')) errors.push('reduced motion CSS fallback');
if (!globalCss.includes('--territory-tone-a:#1e6864') || !globalCss.includes('--territory-tone-b:#4a9690')) errors.push('two-tone Koali territory palette variables');
const toneA = ['cat-01','cat-03','cat-06','cat-08'];
const toneB = ['cat-02','cat-04','cat-05','cat-07'];
if (!toneA.every(id => css.includes(`.${id}`)) || !css.includes('--cell:var(--territory-tone-a)')) errors.push('checker tone A cell mapping');
if (!toneB.every(id => css.includes(`.${id}`)) || !css.includes('--cell:var(--territory-tone-b)')) errors.push('checker tone B cell mapping');
for (const id of ['01','03','06','08']) if (!scenarioCss.includes(`CAT-${id}"]{--detail-accent:var(--territory-tone-a)}`)) errors.push(`scenario detail tone A mapping CAT-${id}`);
for (const id of ['02','04','05','07']) if (!scenarioCss.includes(`CAT-${id}"]{--detail-accent:var(--territory-tone-b)}`)) errors.push(`scenario detail tone B mapping CAT-${id}`);
if (pkg.dependencies?.gsap !== '3.13.0') errors.push('GSAP must be pinned to 3.13.0');

if (errors.length) {
  console.error('Territory label validation failed:');
  for (const error of [...new Set(errors)]) console.error(`- ${error}`);
  process.exit(1);
}
console.log('✓ 8 versioned territory anchors');
console.log('✓ EN/FR territory map labels');
console.log('✓ GSAP/SplitText magnetic progressive enhancement');
console.log('✓ fine-pointer, reduced-motion, observer, and sleep/wake contracts');
console.log('✓ two-tone Koali checker palette A/B/A/B · B/A/B/A');
