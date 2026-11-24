<!-- kOA Doc Server · Docs IA · lot 03 · projet : Koali_Scenario_Mosaic · proposition dérivée à valider -->
# Contexte IA — Koali_Scenario_Mosaic

## Identité et périmètre observés

Interface publique de scénarios Koali avec corpus de 120 cartes, 24 familles de patterns et vues bilingues.

**Limite d'autorité :** Les données éditoriales, l’architecture d’information et la discipline des revendications gouvernent les pages générées; C0 fournit une architecture cible.

**Provenance :** `SmartDump_20261120_221507.zip` → `Koali_Scenario_Mosaic_Code_snapshot.zip` (20 novembre 2026). Les sources citées sont celles de cette capture; le propriétaire du dépôt conserve l'autorité sur les révisions présentes et futures.

## Avant toute proposition de modification

1. Déterminer si le travail demandé porte sur **un document, un contrat, une donnée, un exécutable ou un résultat dérivé**.
2. Consulter les fichiers propriétaires, dans cet ordre :
   - [`README.md`](../../README.md)
   - [`docs/00_START_HERE.md`](../../docs/00_START_HERE.md)
   - [`docs/README.md`](../../docs/README.md)
   - [`docs/61_FINAL_SYSTEM_ARCHITECTURE_BRIDGE.md`](../../docs/61_FINAL_SYSTEM_ARCHITECTURE_BRIDGE.md)
   - [`package.json`](../../package.json)

3. Vérifier les éventuels `AGENTS.md`, manifests, locks, schémas ou décisions de ce checkout; ne pas traiter cette fiche dérivée comme un substitut.
4. Cartographier producteur, consommateur, format, version et permissions pour chaque frontière franchie.

## Procédure adaptée

**Tâche type :** Identifier le scénario et sa famille, lire le corpus et le contrat de présentation, modifier la source, puis valider le build et les images.

**Éviter précisément :** Ne pas présenter les chaînes fonctionnelles C0 ni les scénarios comme des intégrations opérationnelles déjà déployées.

**Contrôles attendus avant la conclusion :** identifier les tests, validateurs et rapports réellement présents sur le système cible; exécuter uniquement ceux qui sont non destructifs et appropriés; relier chaque résultat à une révision et un environnement précis. En absence de code/test (ou si les sources sont insuffisantes), écrire « non vérifié », jamais « PASS ».

## Utilisation par kOA Doc Server

- **Lecture et export :** n'inclure que les documents explicitement sélectionnés, avec chemins relatifs, empreintes et provenance.
- **RepoSurveyor :** profils mesurés séparément à partir du code local. Ne pas fabriquer `ENGINEERING_PROFILE.md` depuis cette fiche; l'alias français est `PROFIL_INGENIERIE.md` après génération réelle.
- **Diagnostics :** observations datées, preuves historiques et états certifiés restent distincts. Aucune promotion automatique.
- **Wikis et vues :** documents dérivés, jamais propriétaires des contrats ni des permissions.
- **Confidentialité :** filtrer secrets, données personnelles, médias sous droits, caches, backups et rapports privés avant un ZIP de contexte IA.
- **Standard Kristal Framework v11 :** si pertinent, consulter le cadre comme référence possible, sans l'exiger pour naviguer ni forcer une migration du profil historique du dépôt.

## État de cette fiche

`DOCUMENTATION_REDACTIONNELLE_A_REVOIR` : elle facilite le démarrage d'un agent, mais **ne prouve aucun état d'intégration, publication, conformité ni maturité**.
