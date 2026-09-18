import type { Locale } from '../i18n/ui';
import systemCatalogJson from '../data/system-catalog.json';
import { extractScenarioPublicDetails } from './scenario-public';

export type SystemRoute = { key:string; label:string; description:string };
const systemCatalog = systemCatalogJson as Record<string,{label:string;description:Record<Locale,string>}>;

const componentKey:Record<string,string> = {
  'Kristal':'kristal',
  'Konnaxion':'konnaxion',
  'Orgo':'orgo',
  'Smart Vote':'smart-vote',
  'EkoH':'ekoh',
  'SenTient':'sentient',
  'SemantiK Architect':'semantik-architect',
  'Kreative/Konservation':'kreative',
};

export function getScenarioSystemRoutes(data:any, locale:Locale):SystemRoute[] {
  return (data?.koali_components ?? []).map((label:string) => {
    const key = componentKey[label] ?? label.toLowerCase().replace(/\s+/g,'-');
    const item = systemCatalog[key];
    return item ? {key,label:item.label,description:item.description[locale]} : {key,label,description:''};
  });
}

export function getScenarioPortal(data:any, body:string, locale:Locale) {
  const details = extractScenarioPublicDetails(body, locale);
  return {
    title: data.title,
    family: data.problem_family_label,
    hook: data.hook,
    koaliHelp: details.koali || data.hook,
    systems: getScenarioSystemRoutes(data, locale),
    mechanisms: data.failure_mechanisms ?? [],
    success: details.success,
    holders: details.holders,
    realCases: details.realCases,
  };
}
