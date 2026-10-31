import WordExtractor from 'word-extractor';
import fs from 'node:fs/promises';
const sources=JSON.parse(await fs.readFile('data/platform_sources.json','utf8'));
await fs.mkdir('data/staging',{recursive:true});
for(const source of sources.filter(s=>s.kind==='academic'&&s.file.endsWith('.doc'))){
 const result=await new WordExtractor().extract(source.file);
 await fs.writeFile(`data/staging/${source.id}.txt`,result.getBody(),'utf8');
 console.log(source.year,'DOC extracted');
}
