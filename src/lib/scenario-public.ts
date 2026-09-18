import type { Locale } from '../i18n/ui';

function sectionRaw(body:string, heading:string) {
  const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const source = `${body.trimEnd()}\n## __END__\n`;
  const match = source.match(new RegExp(`^## ${escaped}\\s*$([\\s\\S]*?)(?=^## )`, 'm'));
  return match ? match[1].trim() : '';
}
function cleanInline(value:string) {
  return value.replace(/`([^`]+)`/g,'$1').replace(/\*\*([^*]+)\*\*/g,'$1').replace(/\*([^*]+)\*/g,'$1').replace(/\[([^\]]+)\]\([^\)]+\)/g,'$1').replace(/\s+/g,' ').trim();
}
function bullets(raw:string) {
  return raw.split('\n').map(x=>x.trim()).filter(x=>x.startsWith('- ')).map(x=>cleanInline(x.slice(2)));
}
function realCaseTitles(raw:string) {
  return [...raw.matchAll(/^###\s+(.+)$/gm)].map(m=>cleanInline(m[1]));
}
export function extractScenarioPublicDetails(body:string, locale:Locale) {
  const h = locale === 'fr' ? {
    problem:'Le problème', why:'Pourquoi c’est important', holders:'Qui détient une partie du savoir', koali:'Avec Koali', human:'Autorité humaine', success:'À quoi ressemble le succès', cases:'Cas réels semblables', limits:'Limites'
  } : {
    problem:'The problem', why:'Why it matters', holders:'Who holds part of the picture', koali:'With Koali', human:'Human authority', success:'What success looks like', cases:'Real-world parallels', limits:'Boundary'
  };
  const raw = Object.fromEntries(Object.entries(h).map(([k,v])=>[k,sectionRaw(body,v)]));
  return {
    problem: cleanInline(raw.problem), why:cleanInline(raw.why), koali:cleanInline(raw.koali), human:cleanInline(raw.human), limits:cleanInline(raw.limits),
    holders: bullets(raw.holders), success: bullets(raw.success), realCases: realCaseTitles(raw.cases), casesRaw: raw.cases,
  };
}
