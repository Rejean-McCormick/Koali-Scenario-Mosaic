# Koali Scenario Mosaic V2.2 — Preview stability & smartphone parity

## Fixed

- Hovering scenarios no longer changes the preview height on desktop/laptop.
- Medium-width two-row preview is also height-stable.
- Smartphone reading order restored from V1: scenario copy → Koali path/context → image.
- Smartphone preview is content-driven again instead of using fixed 616/656 px rows.
- Long hook and Koali-response text are no longer clamped on smartphone.
- Offline preview restored to the V1 140 ms hover-intent delay.
- Offline preview restored touch tap-to-preview, horizontal swipe, touch cancel, and scroll-to-preview behavior.

## Regression protection

`scripts/validate-v2.py` now checks the V1/V2.2 preview and touch contracts.
