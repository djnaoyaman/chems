const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const root=path.join(__dirname,'../dist');
function walk(p){return fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(p,e.name)):[path.join(p,e.name)]);}
const htmls=walk(root).filter(p=>p.endsWith('.html')&&path.basename(p)!=='404.html');
for(const file of htmls){const h=fs.readFileSync(file,'utf8');for(const tag of ['og:image:width','og:image:height','og:image:type','apple-touch-icon','site.webmanifest'])assert(h.includes(tag),file+': '+tag);for(const m of h.matchAll(/<link rel="(?:manifest|apple-touch-icon)" href="([^"]+)"/g))assert(fs.existsSync(path.resolve(path.dirname(file),m[1])),file+' '+m[1]);}
const m=JSON.parse(fs.readFileSync(path.join(root,'site.webmanifest')));assert.equal(m.scope,'/chems/');assert.equal(m.display,'browser');
for(const i of m.icons){const b=fs.readFileSync(path.join(root,i.src));assert.equal(`${b.readUInt32BE(16)}x${b.readUInt32BE(20)}`,i.sizes);}
console.log(JSON.stringify({pages:htmls.length,icons:m.icons.length,pass:true}));
