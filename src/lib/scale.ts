import type { Locale } from '../i18n/ui';
import { localizeScaleValue } from '../i18n/taxonomy';
export function parseScale(value:string){
  const [origin,extent]=value.split('→').map(x=>x.trim());
  return {origin:origin||value,extent:extent||origin||value};
}
export function localizeScale(locale:Locale,value:string){
  const {origin,extent}=parseScale(value);
  return origin===extent?localizeScaleValue(locale,extent):`${localizeScaleValue(locale,origin)} → ${localizeScaleValue(locale,extent)}`;
}
