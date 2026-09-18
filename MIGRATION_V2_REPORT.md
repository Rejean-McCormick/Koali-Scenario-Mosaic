# Koali Scenario Mosaic V2 — Migration report

## Completed

- Replaced the V1 120-scenario corpus with the final 36-scenario bilingual V2 corpus (72 Markdown files).
- Made localized Markdown front matter the single scenario source of truth.
- Replaced equal 8×15 capability territories with 8 variable-size problem-family territories.
- Rebuilt Mosaic layout for 36 hexagons without filler slots.
- Added facets for problem family, scale, urgency and stakes.
- Retained search, Surprise, reset, hover/focus selection, touch preview and swipe behavior.
- Reworked selected preview around scale, urgency, coordination gap, stakes, failure mechanisms and Koali system path.
- Reworked detail hexagons around problem anatomy: what breaks, distributed knowledge, Koali response, real cases and success conditions.
- Added full sourced scenario narrative to public detail routes.
- Retained static Astro architecture and EN/FR routes.
- Retained production magnetic family labels.
- Rebuilt the zero-install offline preview for both languages and all 72 localized detail pages.
- Added V2 validation and archived V1 validators/scripts.
- Removed active V1 120-entry metadata, capability-title and system-route files.

## Verification completed in this environment

- `npm run validate` — PASS
- `npm run preview:offline` — PASS
- offline HTML count — 75 pages (chooser + 2 mosaics + 72 details)
- offline local link check — 0 broken local links
- core V2 TypeScript (`mosaic.ts`, scenario parsing/portal/scale/i18n) — PASS with global TypeScript compiler
- browser JS syntax for offline assets — PASS

## Build verification limitation

The supplied snapshot did not contain `node_modules` or a lockfile. The environment could not reach the npm registry within the available execution window, so the full `astro build` could not be run here.

The repository is configured for the normal verification sequence on a connected development machine:

```bash
npm install
npm run validate
npm run build
```

This limitation is environmental and is intentionally recorded rather than silently treating the production build as verified.

## V2.1 preview and French localization patch

- Restored the visual image slot in `ScenarioPreview`.
- Reintroduced the V1-compatible `SCN-###.png` image naming contract through `src/lib/scenario-image.ts`.
- Added eight family-level SVG fallback illustrations so every V2 scenario always has an image even before final scenario art is supplied.
- Moved Scale / Urgency / Coordination gap / Stakes into a compact metadata row below the scenario hook.
- Added context-aware French localization for scale, urgency, coordination gap, stakes, and all 56 current failure mechanisms.
- Renamed French `Écart de coordination` to `Déficit de coordination`.
- Added localized display names for all 30 real-world cases and changed detail rendering to a semantic list so titles cannot concatenate.
- Localized the visible `Ce qui casse` lists and real-case headings in the French Markdown source files.
- Updated the zero-install offline preview to match the production UI changes.

## V2.2 preview stability and smartphone regression fix

This patch restores two V1 interaction invariants that regressed during the V2 problem-first redesign.

- On fine-pointer desktop/laptop layouts, the preview now has a fixed height while scenarios change. Hovering lower hexagons therefore no longer moves the Mosaic under the pointer.
- On medium widths (721–1119 px), the two-row preview also uses a fixed total height so scenario copy cannot shift the panorama during hover.
- On smartphone widths (≤720 px), the preview returns to the V1 reading order: **copy → Koali path/context → image**.
- Smartphone preview height is content-driven again; the hook and Koali response are not line-clamped merely to satisfy a fixed card height.
- Coarse-pointer behavior retains tap-to-preview, horizontal swipe for previous/next scenario, `touchcancel`, and smooth scroll back to the preview after a cell tap.
- The zero-install preview now uses the same 140 ms hover-intent delay as the Astro source instead of immediate `mouseenter` updates.
- `scripts/validate-v2.py` now protects these layout and interaction contracts against future regressions.
