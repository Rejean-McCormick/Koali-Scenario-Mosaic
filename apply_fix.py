from pathlib import Path
import sys

ROOT = Path.cwd()
TARGET = ROOT / 'src/pages/uses/[id].astro'

content = '''---
export function getStaticPaths() {
  return Array.from({ length: 36 }, (_, index) => {
    const id = `SCN-${String(index + 1).padStart(3, '0')}`;
    return { params: { id } };
  });
}

const id = Astro.params.id ?? 'SCN-001';
const target = `/en/uses/${id}/`;
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content={`0;url=${target}`} />
    <meta name="robots" content="noindex" />
    <link rel="canonical" href={target} />
    <title>Redirecting…</title>
  </head>
  <body>
    <p><a href={target}>Continue to the English scenario</a></p>
    <script is:inline define:vars={{ target }}>
      window.location.replace(target);
    </script>
  </body>
</html>
'''

if not (ROOT / 'package.json').exists():
    raise SystemExit('Run this script from the Koali Scenario Mosaic repository root.')

TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(content, encoding='utf-8')
print(f'Patched {TARGET}')
print('Next: npm run build')
