# Final-system functional architecture — public presentation bridge

**Classification:** `TARGET_DESIGN`, source-aligned public metadata; **not** a claim that the 24 functional chains, 53 repositories or 26 target owner boundaries are deployed.

## Product boundary

Koali Scenario Mosaic is an editorial, bilingual discovery UI. Its **36 English and 36 French scenario source files remain separate examples**, not 36 running workflows, and neither the older 120-item pattern corpus nor the new 24-chain architecture changes this source-content classification.

`src/data/public-architecture.v1.json` is the C0-generated public metadata view. It contains only intended chain titles, owner responsibility text, source document paths and `TARGET_DESIGN` markers. The canonical source is `kOA-Digital-Ecosystem/docs/target`. No local Windows roots, private ZIP paths, student records, patient data, deployment receipts or security diagnostics are copied into the public UI.

The bilingual routes `/en/architecture/` and `/fr/architecture/` display the 24 target capabilities with explicit disclosure limits. Existing `/en/uses/`, `/fr/uses/` and all scenario detail pages retain their source model, ownership and navigation. The architecture link is optional contextual navigation, not permission for the Mosaic to call an owner API or execute an Orgo Task.

## Update and verification

After a **reviewed C0 target change**, replace only the generated public manifest. Run `npm run architecture:validate`, `npm run validate`, the existing Astro build, and regenerate the offline static preview. Compare the manifest bytes in the Homepage and Mosaic snapshots before claiming cross-site alignment.

Actual public publishing remains a separate explicit site-owner action. Source-backed marketing and scenario examples must not be represented as integrated production evidence. Do not silently migrate the older 120-item catalog into the current 36-scenario experience without a separate owner decision.
