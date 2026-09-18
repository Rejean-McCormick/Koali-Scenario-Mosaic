import { existsSync } from 'node:fs';
import { join } from 'node:path';

const PNG_DIR=join(process.cwd(),'public','scenarios','images');
const WIDTHS=[418,627] as const;
export const SCENARIO_IMAGE_SIZES='(min-width: 901px) 292px, (min-width: 721px) 220px, (min-width: 363px) 210px, 58vw';

export function scenarioPngFilename(id:string){
  const m=id.match(/^SCN-(\d{3})$/); return m?`SCN-${m[1]}.png`:null;
}
export function familyFallback(family:string){ return `/scenarios/fallback/${family}.svg`; }
export function resolveScenarioPreviewImageSet(id:string,family:string){
  const file=scenarioPngFilename(id);
  if(!file || !existsSync(join(PNG_DIR,file))) return {src:familyFallback(family),srcset:undefined,sizes:undefined,isFallback:true};
  const variants=WIDTHS.map(w=>({w,file:w===627?file:file.replace(/\.png$/i,`-${w}.png`)})).filter(x=>existsSync(join(PNG_DIR,x.file)));
  const srcset=variants.length>1?variants.map(x=>`/scenarios/images/${x.file} ${x.w}w`).join(', '):undefined;
  return {src:`/scenarios/images/${file}`,srcset,sizes:srcset?SCENARIO_IMAGE_SIZES:undefined,isFallback:false};
}
