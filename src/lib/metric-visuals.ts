import { parseScale } from './scale';

const SCALE_LEVELS: Record<string, number> = {
  individual: 1,
  team: 1,
  organization: 2,
  institution: 2,
  community: 3,
  city: 3,
  network: 3,
  sector: 3,
  regional: 4,
  national: 4,
  global: 4,
};

const URGENCY_LEVELS: Record<string, number> = {
  low: 1,
  moderate: 2,
  significant: 2,
  high: 3,
  critical: 4,
  immediate: 4,
};

const COORDINATION_GAP_LEVELS: Record<string, number> = {
  low: 1,
  medium: 2,
  high: 3,
  extreme: 4,
};

function clampLevel(value: number) {
  return Math.max(1, Math.min(4, Math.round(value || 1)));
}

export function scaleVisualLevelFromKey(extent: string) {
  return clampLevel(SCALE_LEVELS[extent] ?? 2);
}

export function scaleVisualLevel(scale: string) {
  return scaleVisualLevelFromKey(parseScale(scale).extent);
}

export function urgencyVisualLevel(value: string) {
  return clampLevel(URGENCY_LEVELS[value] ?? 2);
}

export function coordinationGapVisualLevel(value: string) {
  return clampLevel(COORDINATION_GAP_LEVELS[value] ?? 2);
}
