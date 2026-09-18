import { existsSync } from 'node:fs';
import { join } from 'node:path';

const PNG_DIR = join(process.cwd(), 'public', 'scenarios', 'images');
export const RESPONSIVE_WIDTHS = [418, 627] as const;
export const SCENARIO_IMAGE_SIZES = '(min-width: 901px) 292px, (min-width: 721px) 220px, (min-width: 363px) 210px, 58vw';

export function scenarioPngFilename(id: string) {
  const match = id.match(/^SCN-(\d{3})$/);
  if (!match) return null;
  const number = Number(match[1]);
  return number >= 1 && number <= 36 ? `SCN-${match[1]}.png` : null;
}

export function responsiveScenarioPngFilename(id: string, width: number) {
  const base = scenarioPngFilename(id);
  if (!base) return null;
  return width === 627 ? base : base.replace(/\.png$/i, `-${width}.png`);
}

export function familyFallback(family: string) {
  return `/scenarios/fallback/${family}.svg`;
}

export function resolveScenarioPreviewImageSet(id: string, family: string) {
  const file = scenarioPngFilename(id);
  if (!file || !existsSync(join(PNG_DIR, file))) {
    return { src: familyFallback(family), srcset: undefined, sizes: undefined, isFallback: true };
  }

  const variants = RESPONSIVE_WIDTHS
    .map((width) => ({ width, file: responsiveScenarioPngFilename(id, width)! }))
    .filter((variant) => existsSync(join(PNG_DIR, variant.file)));
  const srcset = variants.length > 1
    ? variants.map((variant) => `/scenarios/images/${variant.file} ${variant.width}w`).join(', ')
    : undefined;

  return {
    src: `/scenarios/images/${file}`,
    srcset,
    sizes: srcset ? SCENARIO_IMAGE_SIZES : undefined,
    isFallback: false,
  };
}
