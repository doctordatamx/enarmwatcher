import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const html=await fs.readFile('dist/index.html','utf8');
assert.match(html,/\/enarmwatcher\/assets\//);
assert.match(html,/\/enarmwatcher\/manifest\.webmanifest/);
for(const name of ['national','academic','receiving','atlas','platform-sources','research','receiving-analysis','academic-longitudinal','catalogue','specialties']){
 const data=JSON.parse(await fs.readFile(`dist/data/${name}.json`,'utf8'));assert.equal(typeof data,'object');
}
const geo=JSON.parse(await fs.readFile('dist/data/mexico-states.geojson','utf8'));assert.equal(geo.features.length,32);
const manifest=JSON.parse(await fs.readFile('dist/manifest.webmanifest','utf8'));assert.equal(manifest.scope,'/enarmwatcher/');
for(const icon of manifest.icons)await fs.access('dist/'+icon.src);
console.log('Static subpath, JSON partitions, geography and manifest verified.');
