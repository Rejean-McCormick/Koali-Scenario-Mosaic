import { getCollection, type CollectionEntry } from 'astro:content';
import type { Locale } from '../i18n/ui';

export type ScenarioTextEntry = CollectionEntry<'scenarioText'>;
export type LocalizedScenario = { entry: ScenarioTextEntry; data: ScenarioTextEntry['data'] };

export async function getLocalizedScenarios(locale: Locale): Promise<LocalizedScenario[]> {
  const entries = await getCollection('scenarioText', ({ data }) => data.locale === locale);
  return entries
    .map((entry) => ({ entry, data: entry.data }))
    .sort((a,b) => a.data.id.localeCompare(b.data.id, undefined, { numeric: true }));
}

export async function getLocalizedScenario(locale: Locale, id: string) {
  return (await getLocalizedScenarios(locale)).find((scenario) => scenario.data.id === id) ?? null;
}
