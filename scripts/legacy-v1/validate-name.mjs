import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd(), errors=[];
const binary=new Set(['.png','.jpg','.jpeg','.webp','.gif','.ico','.zip','.pyc']);
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(['node_modules','.git','__pycache__','dist'].includes(e.name))continue;const full=path.join(dir,e.name);if(e.isDirectory())walk(full);else{if(e.name==='validate-name.mjs'||binary.has(path.extname(e.name).toLowerCase()))continue;let t;try{t=fs.readFileSync(full,'utf8')}catch{continue}if(/\bKOALI\b/.test(t))errors.push(`${path.relative(root,full)} contains all-caps Koali`);}}}
walk(root);
const required=[
 ['README.md','Koali, the Sociotechnical Operating System'],
 ['src/layouts/BaseLayout.astro','the Sociotechnical Operating System'],
 ['src/styles/global.css','--brand:#1e6864'],
 ['src/components/ScenarioPreview.astro','Koali Scenario Mosaic'],
 ['public/mosaic-cover.svg','Koali Scenario Mosaic'],
 ['public/mosaic-cover-fr.svg','Mosaïque de scénarios Koali'],
 ['public/brand/koali-mark.svg','#1e6864'],
 ['preview/en/index.html','Koali Scenario Mosaic'],
 ['preview/fr/index.html','Mosaïque de scénarios Koali'],
];
for(const [file,token] of required){const f=path.join(root,file);if(!fs.existsSync(f)||!fs.readFileSync(f,'utf8').includes(token))errors.push(`${file} missing ${token}`)}
const pkg=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
if(pkg.name!=='koali-scenario-mosaic')errors.push(`package name is ${pkg.name}`);
if(errors.length){console.error('NAMING VALIDATION FAILED');for(const e of errors)console.error(' -',e);process.exit(1)}
console.log('✓ canonical brand: Koali');
console.log('✓ positioning: Koali, the Sociotechnical Operating System');
console.log('✓ bilingual interface names: Koali Scenario Mosaic / Mosaïque de scénarios Koali');
console.log('✓ brand color: #1e6864');
