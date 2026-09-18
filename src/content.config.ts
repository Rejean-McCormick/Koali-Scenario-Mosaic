import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const scenarioText=defineCollection({
  loader:glob({pattern:'**/SCN-*.md',base:'./src/content/scenarios',generateId:({entry})=>entry.replace(/\.md$/,'')}),
  schema:z.object({
    id:z.string().regex(/^SCN-\d{3}$/),title:z.string(),locale:z.enum(['en','fr']),
    problem_family:z.string(),problem_family_label:z.string(),scenario_type:z.string(),hook:z.string(),
    failure_mechanisms:z.array(z.string()).min(1),scale:z.string(),urgency:z.string(),stakes:z.array(z.string()).min(1),
    coordination_gap:z.string(),domains:z.array(z.string()).min(1),koali_patterns:z.array(z.string()).min(1),
    koali_components:z.array(z.string()).min(1),real_case_ids:z.array(z.string()).min(1),evidence_status:z.string(),koali_runtime_status:z.string(),
  }),
});
export const collections={scenarioText};
