# Contrat de stabilité — aperçu des scénarios

## But

Ce document fixe les règles de comportement et de mise en page de l’aperçu de scénario afin d’éviter trois régressions récurrentes :

1. le changement de scénario trop immédiat au survol, qui provoque un effet de clignotement lorsque le pointeur traverse plusieurs hexagones;
2. les huit boîtes d’actions qui sont comprimées pour tenir sur une ligne, alors qu’elles doivent conserver la largeur minimale nécessaire à leur libellé;
3. le titre placé dans une zone fixe de trois lignes, qui crée du vide sur la majorité des scénarios.

Ces règles sont des invariants. Un futur refactor ne doit pas les supprimer sans remplacer explicitement le même comportement.

## Noms des trois blocs

- Bloc 1 : `.preview-image-shell` — image carrée.
- Bloc 2 : `.preview-copy` — identifiant, titre, résumé, exemple, actions et CTA.
- Bloc 3 : `.preview-profile` — systèmes Koali et contexte.

## Invariant A — activation d’un scénario

Le survol à la souris utilise une courte temporisation d’intention.

- Délai cible : **140 ms**.
- `pointerenter` ne doit pas appeler `show()` directement.
- Si le pointeur quitte la cellule avant la fin du délai, la sélection planifiée est annulée.
- Si le pointeur entre dans une autre cellule, l’ancienne sélection planifiée est remplacée.
- Le clavier (`focus`), le clic tactile, le swipe et le bouton aléatoire restent immédiats.
- Le délai n’est pas une animation; `prefers-reduced-motion` ne le désactive pas.

Raison : traverser rapidement la mosaïque ne doit pas déclencher plusieurs mises à jour successives du titre, des systèmes et de l’image.

## Invariant B — titre sur deux lignes avec auto-fit

Le titre du bloc 2 utilise sa hauteur naturelle et occupe au maximum deux lignes.

- Il commence à la taille typographique normale du breakpoint actif.
- `text-wrap: balance` répartit les mots.
- Si le titre nécessite une troisième ligne, `preview-layout.ts` réduit progressivement sa taille.
- La réduction s’arrête à une limite minimale lisible.
- Si un cas extrême déborde encore, il est clampé à deux lignes.
- Aucune hauteur fixe d’une, deux ou trois lignes n’est réservée.

Le calcul repose sur `scrollHeight` et la hauteur réelle de ligne, pas sur le nombre de caractères. Il est relancé après :

- chaque changement de scénario;
- chaque changement de largeur du bloc 2;
- le zoom du navigateur;
- le chargement des polices.

## Invariant C — largeur minimale des huit boîtes d’actions

Les huit boîtes sont toujours ancrées au bas du bloc 2.

En desktop, le système essaie d’abord une seule ligne de huit colonnes avec une largeur intrinsèque minimale :

```css
repeat(8, minmax(max-content, 1fr))
```

Le libellé complet, son padding et son contenu déterminent donc la largeur minimale réelle de chaque boîte.

Après mise en page, le navigateur compare :

```text
largeur requise = scrollWidth de la rangée à 8 colonnes
largeur disponible = clientWidth du conteneur
```

Si la largeur requise dépasse la largeur disponible, la classe `.is-two-rows` est appliquée et la grille devient exactement :

```css
repeat(4, minmax(max-content, 1fr))
```

Résultat : **4 + 4**, jamais 7 + 1 ou une rangée de huit libellés écrasés.

La mesure doit être recalculée quand :

- la largeur du bloc 2 change;
- la fenêtre est redimensionnée;
- le zoom modifie la largeur CSS disponible;
- les polices ont terminé de charger.

Un `ResizeObserver` et `document.fonts.ready` assurent cette réévaluation.

## Invariant D — ancrage bas du bloc 2

`.preview-tags.preview-backlights` reste dans la dernière rangée du bloc 2.

Le changement 1 ligne → 2 lignes peut augmenter la hauteur de la carte, mais les boîtes restent au bas du bloc. Le contenu éditorial ne doit jamais être placé après elles.

## Invariant E — ancrage bas du bloc 3

`.profile-context` — Échelle / Contexte / Conditions particulières — reste dans la dernière rangée du bloc 3.

Le nombre de systèmes peut varier, mais ce sous-bloc reste ancré en bas. L’espace flexible est situé avant lui.

## Invariant F — image

Le bloc 1 reste carré et ne doit pas être étiré verticalement pour égaler artificiellement la hauteur des blocs 2 ou 3.

## Invariant G — géométrie responsive

La géométrie dépend de la largeur du conteneur `.mosaic-experience` :

- à partir de 1120 px : image 250–292 px, bloc 2 flexible avec un minimum de 480 px, bloc 3 limité à 300–340 px;
- de 721 à 1119 px : image et bloc 2 sur la première rangée, bloc 3 sur toute la seconde;
- jusqu’à 720 px : bloc 2, bloc 3, puis image carrée.

Le breakpoint intermédiaire ne doit pas être repoussé à 900 px, car le bloc 2 deviendrait trop étroit juste au-dessus de ce seuil.

## Règles à ne pas réintroduire

Ne pas remettre :

```js
cell.addEventListener('pointerenter', () => show(id))
```

Ne pas forcer les huit actions avec :

```css
grid-template-columns: repeat(8, minmax(0, 1fr));
```

sans test de largeur, car cela autorise les colonnes à devenir plus étroites que leurs libellés.

Ne pas déplacer les actions ou `.profile-context` hors de leur rangée d’ancrage bas.

Ne pas réintroduire une hauteur fixe de trois lignes ou une classification fondée sur la longueur du texte :

```css
height: 3.24em;
-webkit-line-clamp: 3;
```

```js
titleDensity(title)
```

## Tests d’acceptation

1. Traverser rapidement plusieurs hexagones : aucun défilement rapide de scénarios.
2. Rester environ 140 ms sur une cellule : un seul scénario est chargé.
3. Quitter une cellule avant 140 ms : aucun changement.
4. Focus clavier sur une cellule : changement immédiat.
5. Large bloc 2 : huit boîtes sur une ligne, libellés complets.
6. Bloc 2 trop étroit : deux lignes de quatre boîtes.
7. Zoom navigateur : le passage 8 → 4×2 se recalcule automatiquement.
8. Les actions restent au bas du bloc 2 dans les deux modes.
9. Échelle / Contexte / Conditions particulières restent au bas du bloc 3.
10. L’image reste carrée.
11. Un titre court conserve la taille normale et sa hauteur naturelle.
12. Un titre long est réduit jusqu’à tenir sur deux lignes.
13. Un titre extrême est clampé à deux lignes à la taille minimale.
14. Le titre est recalculé après redimensionnement, zoom et chargement des polices.
15. Entre 721 et 1119 px, le profil occupe une rangée complète sous l’image et le bloc 2.
16. Les pages de détail et l’aperçu hors ligne utilisent le même contrôleur de layout que la mosaïque.

## Addendum V2.2 — stabilité problem-first

La V2 ajoute des indicateurs, des mécanismes et un résumé de réponse Koali dans le bloc central. Ces nouvelles données **ne doivent jamais redevenir une source de variation verticale sur un appareil à pointeur fin**.

Invariants V2.2 :

- `>= 1120 px` : la carte `.scenario-preview` conserve une hauteur fixe pendant tous les changements de scénario;
- `721–1119 px` : la preview à deux rangées conserve elle aussi une hauteur totale fixe;
- `<= 720 px` : la contrainte de hauteur fixe est levée, car il n'y a pas de hover à protéger; la hauteur redevient déterminée par le contenu;
- smartphone : ordre de lecture **`.preview-copy` → `.preview-profile` → `.preview-image-shell`**;
- smartphone : le hook et le texte « Ce que Koali change » ne sont pas tronqués pour satisfaire une hauteur artificielle;
- l'aperçu offline doit conserver le même délai d'intention de 140 ms et la même logique tactile que la version Astro.

Le validateur V2 vérifie désormais explicitement ces invariants.
