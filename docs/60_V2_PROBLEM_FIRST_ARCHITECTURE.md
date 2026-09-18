# Scenario Mosaic V2 — Problem-first architecture

## Product thesis

The Mosaic no longer asks visitors to understand Koali before recognizing a use case. It starts from a recurring sociotechnical failure and then shows what continuity Koali adds.

```text
real-world problem
  → problem family
  → failure mechanisms
  → distributed knowledge / responsibility
  → Koali response patterns
  → Koali systems
  → observable success conditions
  → reusable memory
```

## Eight problem families

1. Coordination breakdown
2. Signal & context loss
3. Knowledge attrition
4. Distributed intelligence fails to converge
5. Evidence loses to noise
6. Decisions lose their why
7. Action & learning loops break
8. Institutional capacity & sovereignty

The families intentionally contain different numbers of scenarios. Geometry never determines editorial coverage.

## Content contract

Localized Markdown is the single source of truth. Stable machine-facing metadata lives in front matter so a future CMS or API can ingest the same files without rewriting editorial content.

`scale` is authored as a compact path such as `individual→regional`; the interface derives the origin and extent for display/filtering rather than storing duplicate fields.

## Evidence discipline

Each canonical archetype contains documented parallels. These parallels establish that the failure mechanism occurs in the real world. They do not establish a counterfactual claim about Koali.

`koali_runtime_status` remains `COMPOSED · runtime UNVERIFIED` until a relevant implementation or pilot produces evidence.

## Static-first architecture

No server backend is required for the public Mosaic. Astro builds the content into static routes. Client JavaScript is limited to exploration state: search, facets, preview selection, touch/swipe, and magnetic labels.

A backend should only be introduced if later product scope requires authenticated editing, public contributions, live consensus data, comments, or other mutable shared state.
