import frTags from './fr-tags.json';

export const locales = ['en','fr'] as const;
export type Locale = (typeof locales)[number];

export const ui = {
  en: {
    languageName:'English', alternateLanguageName:'Français', brandTagline:'the Sociotechnical Operating System',
    scenarioMosaic:'Scenario Mosaic', scenarios:'scenarios', examples:'canonical problems', allScenarios:'All scenarios',
    exploreWays:(count:number)=>`Explore ${count} real-world problem patterns`,
    hoverIntro:'Select a problem to see its scale, urgency, failure mechanisms, real-world parallels, and the Koali response path.',
    openExample:'Open the full scenario', insideKoali:'Inside Koali', systemPath:'System path', selectSystemHint:'Select a problem to see the Koali systems involved.',
    scale:'Scale', urgency:'Urgency', stakes:'Stakes', coordinationGap:'Coordination gap', mechanisms:'Failure mechanisms', koaliResponse:'What Koali changes',
    searchScenarios:'Search scenarios', searchPlaceholder:'Search a problem, sector, mechanism, or system…', surprise:'Surprise me', reset:'Reset',
    familyFilter:'Problem family', scaleFilter:'Scale', urgencyFilter:'Urgency', stakesFilter:'Stakes', allFamilies:'All families', allScales:'All scales', allUrgencies:'All urgencies', allStakes:'All stakes',
    colorLegend:'Problem families', mosaicTitle:'Koali Scenario Mosaic',
    mosaicDescription:'36 canonical sociotechnical problems arranged by eight failure families. Select one to inspect scale, urgency, mechanisms, real-world parallels, and the Koali response path.',
    mosaicHint:'Each hexagon is a recurring problem pattern. Filter by family, scale, urgency or stakes, then select one to inspect it.',
    detailBack:'Back to the full Mosaic', noneHighlighted:'None highlighted', involved:'involved', notCentral:'not central',
    detailWhatBreaks:'What breaks', detailWhoKnows:'Who holds part of the picture', detailKoaliResponse:'Koali response', detailRealCases:'Real-world parallels', detailSuccess:'What success looks like',
    evidenceNote:'Documented parallels show that the failure mechanism is real; they do not claim Koali would have changed a specific outcome.',
    swipeHint:'Swipe left for next · right for previous',
  },
  fr: {
    languageName:'Français', alternateLanguageName:'English', brandTagline:'the Sociotechnical Operating System',
    scenarioMosaic:'Mosaïque de scénarios', scenarios:'scénarios', examples:'problèmes canoniques', allScenarios:'Tous les scénarios',
    exploreWays:(count:number)=>`Explorez ${count} problèmes sociotechniques récurrents`,
    hoverIntro:'Sélectionnez un problème pour voir son échelle, son urgence, ses mécanismes de défaillance, ses cas réels analogues et la réponse Koali.',
    openExample:'Ouvrir le scénario complet', insideKoali:'Dans Koali', systemPath:'Chemin système', selectSystemHint:'Sélectionnez un problème pour voir les systèmes Koali concernés.',
    scale:'Échelle', urgency:'Urgence', stakes:'Enjeux', coordinationGap:'Déficit de coordination', mechanisms:'Mécanismes de défaillance', koaliResponse:'Ce que Koali change',
    searchScenarios:'Rechercher des scénarios', searchPlaceholder:'Rechercher un problème, secteur, mécanisme ou système…', surprise:'Au hasard', reset:'Réinitialiser',
    familyFilter:'Famille de problème', scaleFilter:'Échelle', urgencyFilter:'Urgence', stakesFilter:'Enjeux', allFamilies:'Toutes les familles', allScales:'Toutes les échelles', allUrgencies:'Toutes les urgences', allStakes:'Tous les enjeux',
    colorLegend:'Familles de problèmes', mosaicTitle:'Mosaïque de scénarios Koali',
    mosaicDescription:'36 problèmes sociotechniques canoniques organisés en huit familles de défaillance. Chaque sélection révèle échelle, urgence, mécanismes, cas réels analogues et réponse Koali.',
    mosaicHint:'Chaque hexagone représente un problème récurrent. Filtrez par famille, échelle, urgence ou enjeu, puis sélectionnez-en un.',
    detailBack:'Retour à la mosaïque complète', noneHighlighted:'Aucune mise en évidence', involved:'impliqué', notCentral:'non central',
    detailWhatBreaks:'Ce qui casse', detailWhoKnows:'Qui détient une partie du savoir', detailKoaliResponse:'Réponse Koali', detailRealCases:'Cas réels semblables', detailSuccess:'À quoi ressemble le succès',
    evidenceNote:'Les cas documentés montrent que le mécanisme de défaillance existe; ils ne prétendent pas que Koali aurait changé une issue particulière.',
    swipeHint:'Balayez à gauche : suivant · à droite : précédent',
  }
} as const;

export function getUi(locale:Locale){ return ui[locale]; }
export function humanizeTag(locale:Locale,value:string){
  if(locale==='fr') return (frTags as Record<string,string>)[value] ?? value.replace(/[-_]+/g,' ').replace(/^./,c=>c.toUpperCase());
  return value.replace(/[-_]+/g,' ').replace(/\b\w/g,c=>c.toUpperCase());
}
