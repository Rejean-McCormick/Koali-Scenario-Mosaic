import type { Locale } from './ui';

const fr = {
  scale: {
    individual:'Individu', team:'Équipe', organization:'Organisation', community:'Communauté', city:'Ville', regional:'Région', national:'Pays', global:'Monde', institution:'Institution', sector:'Secteur', network:'Réseau'
  },
  urgency: {
    low:'Faible', moderate:'Modérée', significant:'Importante', high:'Élevée', critical:'Critique', immediate:'Immédiate'
  },
  coordinationGap: {
    low:'Faible', medium:'Modéré', high:'Élevé', extreme:'Extrême'
  },
  stakes: {
    access:'Accès', continuity:'Continuité', culture:'Culture', dignity:'Dignité', education:'Éducation', environment:'Environnement', equity:'Équité', essential_service:'Services essentiels', health:'Santé', identity:'Identité', innovation:'Innovation', knowledge:'Savoir', life:'Vie humaine', money:'Coûts financiers', privacy:'Vie privée', public_policy:'Politiques publiques', public_safety:'Sécurité publique', public_value:'Intérêt public', research:'Recherche', rights:'Droits', safety:'Sécurité', security:'Sécurité', service_quality:'Qualité des services', sovereignty:'Souveraineté', trust:'Confiance'
  },
  mechanisms: {
    aggregation_bias:'Biais d’agrégation', anecdote_overweight:'Surpondération de l’anecdote', blame_distortion:'Distorsion du blâme', central_dependency:'Dépendance à un système central', citizen_signal_ignored:'Signal citoyen ignoré', conflict_of_interest:'Conflit d’intérêts', connectivity_failure:'Rupture de connectivité', content_silo:'Silo de contenu', context_loss:'Perte de contexte', continuity_gap:'Rupture de continuité', criterion_ambiguity:'Ambiguïté des critères', expertise_asymmetry:'Asymétrie d’expertise', expertise_isolation:'Isolement des expertises', expertise_mismatch:'Expertise inadaptée', false_balance:'Fausse équivalence', false_certainty:'Fausse certitude', fragmentation:'Fragmentation', handoff_failure:'Échec de transmission', hidden_tradeoff:'Compromis caché', hindsight_bias:'Biais rétrospectif', institutional_amnesia:'Amnésie institutionnelle', institutional_dependency:'Dépendance institutionnelle', interoperability_failure:'Défaillance d’interopérabilité', knowledge_attrition:'Érosion du savoir', legacy_dependency:'Dépendance aux systèmes patrimoniaux', legitimacy_gap:'Déficit de légitimité', lock_in:'Verrouillage', memory_failure:'Défaillance de mémoire institutionnelle', metric_fixation:'Fixation sur les indicateurs', missing_escalation:'Absence d’escalade', noise_amplification:'Amplification du bruit', opacity:'Opacité', opaque_decision:'Décision opaque', opaque_weighting:'Pondération opaque', organizational_silo:'Silo organisationnel', participation_without_power:'Participation sans pouvoir d’action', pattern_detection_failure:'Défaillance de détection des tendances', power_asymmetry:'Asymétrie de pouvoir', premature_conclusion:'Conclusion prématurée', provenance_loss:'Perte de provenance', publication_bias:'Biais de publication', recommendation_decay:'Déperdition des recommandations', resource_orchestration_failure:'Défaillance d’orchestration des ressources', reuse_failure:'Échec de réutilisation', rights_detachment:'Dissociation des droits', risk_distortion:'Distorsion du risque', routing_failure:'Échec d’orientation', scale_confusion:'Confusion d’échelle', semantic_mismatch:'Incompatibilité sémantique', signal_dilution:'Dilution du signal', single_point_of_failure:'Point de défaillance unique', tacit_knowledge_loss:'Perte de savoir tacite', training_gap:'Déficit de formation', unclosed_loop:'Boucle non bouclée', vendor_dependency:'Dépendance au fournisseur', visibility_failure:'Défaillance de visibilité'
  }
} as const;

const enOverrides: Record<string,string> = {
  essential_service:'Essential service', public_safety:'Public safety', public_value:'Public value', service_quality:'Service quality',
  context_loss:'Context loss', signal_dilution:'Signal dilution', missing_escalation:'Missing escalation', false_certainty:'False certainty',
};
function enLabel(value:string){
  return enOverrides[value] ?? value.replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
}
function lookup(locale:Locale, group:keyof typeof fr, value:string){
  if(locale==='en') return enLabel(value);
  return (fr[group] as Record<string,string>)[value] ?? value.replace(/[-_]+/g,' ').replace(/^./,c=>c.toUpperCase());
}
export const localizeScaleValue=(locale:Locale,value:string)=>lookup(locale,'scale',value);
export const localizeUrgency=(locale:Locale,value:string)=>lookup(locale,'urgency',value);
export const localizeCoordinationGap=(locale:Locale,value:string)=>lookup(locale,'coordinationGap',value);
export const localizeStake=(locale:Locale,value:string)=>lookup(locale,'stakes',value);
export const localizeMechanism=(locale:Locale,value:string)=>lookup(locale,'mechanisms',value);
