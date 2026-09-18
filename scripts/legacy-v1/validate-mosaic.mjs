import fs from 'node:fs';

const layout = JSON.parse(fs.readFileSync('src/data/mosaic-layout.json', 'utf8'));
const errors = [];
const g = layout.geometry;
const eps = 0.01;

if (Object.keys(layout.assignments).length !== 120) errors.push('expected 120 assignments');
if (Object.keys(layout.slots).length !== 150) errors.push('expected 150 slots');
if (layout.reservedSlots.length !== 30) errors.push('expected 30 reserved slots');
if (g.rows !== 6 || g.columns !== 20) errors.push('active geometry must be 20 columns × 6 rows');
if (g.territories !== 8 || g.territory_columns !== 5 || g.territory_rows !== 3) errors.push('territory geometry must be eight 5 × 3 regions');
if (Math.abs(g.dx - Math.sqrt(3) * g.size) > .001) errors.push('invalid horizontal honeycomb spacing');
if (Math.abs(g.dy - 1.5 * g.size) > .001) errors.push('invalid vertical honeycomb spacing');
if (Math.abs(g.row_offset - g.dx / 2) > .001) errors.push('invalid alternating row offset');
if (g.size > 23) errors.push('panorama hexagons are too large');

const activeSlots = [];
for (let row = 0; row < 6; row++) {
  const rowSlots = [];
  for (let col = 0; col < 20; col++) {
    const slotId = `slot-${String(row * 20 + col + 1).padStart(3, '0')}`;
    const slot = layout.slots[slotId];
    if (!slot) { errors.push(`missing ${slotId}`); continue; }
    rowSlots.push(slot);
    activeSlots.push(slot);
    if (slot.row !== row || slot.column !== col) errors.push(`${slotId} row/column metadata mismatch`);
  }
  for (let i = 1; i < rowSlots.length; i++) {
    if (Math.abs((rowSlots[i].x - rowSlots[i - 1].x) - g.dx) > eps) errors.push(`row ${row + 1} horizontal drift`);
  }
}
for (let row = 1; row < 6; row++) {
  const prev = layout.slots[`slot-${String((row - 1) * 20 + 1).padStart(3, '0')}`];
  const cur = layout.slots[`slot-${String(row * 20 + 1).padStart(3, '0')}`];
  if (Math.abs((cur.y - prev.y) - g.dy) > eps) errors.push(`row ${row + 1} vertical drift`);
  const expectedOffset = row % 2 ? g.row_offset : -g.row_offset;
  if (Math.abs((cur.x - prev.x) - expectedOffset) > eps) errors.push(`row ${row + 1} alternating offset drift`);
}

// Each canonical category owns one contiguous 5 × 3 territory.
for (let categoryIndex = 0; categoryIndex < 8; categoryIndex++) {
  const expectedRowStart = categoryIndex < 4 ? 0 : 3;
  const expectedColStart = (categoryIndex % 4) * 5;
  const occupied = new Set();
  for (let k = 0; k < 15; k++) {
    const scenarioId = `SCN-${String(categoryIndex * 15 + k + 1).padStart(3, '0')}`;
    const slotId = layout.assignments[scenarioId];
    const slot = layout.slots[slotId];
    if (!slot) { errors.push(`${scenarioId} has no valid slot`); continue; }
    if (slot.row < expectedRowStart || slot.row >= expectedRowStart + 3 || slot.column < expectedColStart || slot.column >= expectedColStart + 5) {
      errors.push(`${scenarioId} escaped its category territory`);
    }
    occupied.add(`${slot.row}:${slot.column}`);
  }
  if (occupied.size !== 15) errors.push(`category ${categoryIndex + 1} does not fill exactly 15 unique cells`);
}

const ratio = layout.viewBox[2] / layout.viewBox[3];
if (ratio < 3.4) errors.push(`viewBox is not panoramic enough (${ratio.toFixed(2)}:1)`);

if (errors.length) {
  console.error('Mosaic validation failed:');
  for (const error of [...new Set(errors)]) console.error(`- ${error}`);
  process.exit(1);
}

console.log('✓ 120 assignments');
console.log('✓ 150 slots / 30 reserved');
console.log('✓ exact 20 × 6 regular honeycomb panorama');
console.log('✓ 8 contiguous 5 × 3 category territories');
console.log(`✓ panoramic viewBox ratio ${ratio.toFixed(2)}:1`);
