import { mkdir, readdir, readFile, rename, rm } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import sharp from 'sharp';

const ROOT = process.cwd();
const SOURCE_DIR = path.join(ROOT, 'src', 'assets', 'scenario-images');
const OUTPUT_DIR = path.join(ROOT, 'public', 'scenarios', 'images');
const SOURCE_SIZE = 1254;
const DEFAULT_SIZE = 627;
const RESPONSIVE_SIZES = [418, 627];
const STALE_RESPONSIVE_SIZES = [836, 1254];
const FILE_RE = /^SCN-(\d{3})\.png$/;

await mkdir(SOURCE_DIR, { recursive: true });
await mkdir(OUTPUT_DIR, { recursive: true });

function scenarioNumber(name) {
  const match = name.match(FILE_RE);
  if (!match) return null;
  const number = Number(match[1]);
  return number >= 1 && number <= 120 ? number : null;
}

function outputFilename(name, size) {
  if (size === DEFAULT_SIZE) return name;
  return name.replace(/\.png$/i, `-${size}.png`);
}

async function pngMeta(file) {
  return sharp(file, { failOn: 'error' }).metadata();
}

const sourceEntries = (await readdir(SOURCE_DIR, { withFileTypes: true }))
  .filter((entry) => entry.isFile() && entry.name.toLowerCase().endsWith('.png'))
  .map((entry) => entry.name)
  .sort();

const errors = [];
const sourceFiles = new Map();

for (const name of sourceEntries) {
  const number = scenarioNumber(name);
  if (number === null) {
    errors.push(`${name}: expected SCN-001.png … SCN-120.png`);
    continue;
  }

  const input = path.join(SOURCE_DIR, name);
  try {
    const meta = await pngMeta(input);
    if (meta.format !== 'png') {
      errors.push(`${name}: source must be PNG`);
      continue;
    }
    if (meta.width !== SOURCE_SIZE || meta.height !== SOURCE_SIZE) {
      errors.push(`${name}: source must be exactly ${SOURCE_SIZE}×${SOURCE_SIZE}, got ${meta.width}×${meta.height}`);
      continue;
    }
    sourceFiles.set(number, input);
  } catch (error) {
    errors.push(`${name}: cannot read PNG (${error.message})`);
  }
}

if (errors.length) {
  console.error('SCENARIO IMAGE PREPARATION FAILED');
  for (const error of errors) console.error(` - ${error}`);
  process.exit(1);
}

const publicEntries = (await readdir(OUTPUT_DIR, { withFileTypes: true }))
  .filter((entry) => entry.isFile() && /^SCN-\d{3}(?:-(?:418|627|836|1254))?\.png$/i.test(entry.name))
  .map((entry) => entry.name);

const publicByScenario = new Map();
for (const name of publicEntries) {
  const match = name.match(/^SCN-(\d{3})(?:-(418|627|836|1254))?\.png$/i);
  if (!match) continue;
  const number = Number(match[1]);
  if (number < 1 || number > 120) continue;
  const declaredSize = match[2] ? Number(match[2]) : null;
  const candidates = publicByScenario.get(number) ?? [];
  candidates.push({ name, declaredSize, path: path.join(OUTPUT_DIR, name) });
  publicByScenario.set(number, candidates);
}

async function choosePublicFallback(number) {
  const candidates = publicByScenario.get(number) ?? [];
  const ranked = [];

  for (const candidate of candidates) {
    try {
      const meta = await pngMeta(candidate.path);
      if (meta.format !== 'png' || !meta.width || !meta.height || meta.width !== meta.height) continue;
      ranked.push({ ...candidate, actualSize: meta.width });
    } catch {
      // Validation below will report unreadable output files if they remain relevant.
    }
  }

  // Prefer the largest real public PNG. This makes production builds robust when
  // source masters are intentionally not committed but an older 1254/836 set is.
  ranked.sort((a, b) => b.actualSize - a.actualSize);
  return ranked.find((candidate) => candidate.actualSize >= DEFAULT_SIZE) ?? null;
}

async function buildVariant(inputBuffer, name, size) {
  const output = path.join(OUTPUT_DIR, outputFilename(name, size));
  const temp = `${output}.tmp.png`;

  try {
    await sharp(inputBuffer, { failOn: 'error' })
      .resize(size, size, {
        fit: 'fill',
        kernel: sharp.kernel.lanczos3,
        withoutEnlargement: true,
      })
      .png({
        compressionLevel: 9,
        adaptiveFiltering: true,
      })
      .toFile(temp);

    const meta = await pngMeta(temp);
    if (meta.width !== size || meta.height !== size) {
      throw new Error(`generated ${meta.width}×${meta.height}, expected ${size}×${size}`);
    }

    await rename(temp, output);
  } catch (error) {
    await rm(temp, { force: true });
    throw new Error(`${name} @ ${size}px: ${error.message}`);
  }
}

const jobs = [];
let sourceCount = 0;
let fallbackCount = 0;

for (let number = 1; number <= 120; number += 1) {
  const name = `SCN-${String(number).padStart(3, '0')}.png`;
  let inputPath = sourceFiles.get(number);

  if (inputPath) {
    sourceCount += 1;
  } else {
    const fallback = await choosePublicFallback(number);
    if (!fallback) continue;
    inputPath = fallback.path;
    fallbackCount += 1;
  }

  jobs.push({ name, inputPath });
}

async function buildOne({ name, inputPath }) {
  // Read first so the default output may safely overwrite the same public file
  // when it is also being used as the fallback input on Netlify.
  const inputBuffer = await readFile(inputPath);
  await Promise.all(RESPONSIVE_SIZES.map((size) => buildVariant(inputBuffer, name, size)));
  await Promise.all(
    STALE_RESPONSIVE_SIZES.map((size) => rm(path.join(OUTPUT_DIR, outputFilename(name, size)), { force: true })),
  );
}

const CONCURRENCY = 2;
for (let i = 0; i < jobs.length; i += CONCURRENCY) {
  await Promise.all(jobs.slice(i, i + CONCURRENCY).map(buildOne));
}

if (jobs.length === 0) {
  console.log('No scenario PNG sources or usable public fallbacks found; leaving image directory unchanged.');
} else {
  console.log(`✓ ${jobs.length} scenario image(s): responsive PNG set ${RESPONSIVE_SIZES.join(' / ')} px`);
  console.log(`✓ default src is physically ${DEFAULT_SIZE}×${DEFAULT_SIZE}`);
  if (sourceCount) console.log(`✓ ${sourceCount} image(s) rebuilt from ${path.relative(ROOT, SOURCE_DIR)}`);
  if (fallbackCount) console.log(`✓ ${fallbackCount} image(s) rebuilt from existing public PNGs (production fallback)`);
  console.log(`✓ removed stale ${STALE_RESPONSIVE_SIZES.join(' / ')} px variants from ${path.relative(ROOT, OUTPUT_DIR)}`);
}
