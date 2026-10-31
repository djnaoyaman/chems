'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../dist'),base='https://djnaoyaman.github.io/chems/';
const full=fs.readFileSync(path.join(root,'llms-full.txt'),'utf8');assert.equal((full.match(/^## https:/gm)||[]).length,218);assert(full.includes('Facts and personal views'));assert(full.includes('このサイトで取り上げる'));assert(!full.includes('dataLayer.push'));
const recovery=fs.readFileSync(path.join(root,'404.html'),'utf8');assert(recovery.includes('noindex,follow'));assert(!recovery.includes('rel="canonical"'));assert(!fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').includes('404.html'));for(const p of ['','works/','timeline/','en/','en/works/'])assert(recovery.includes('href="'+base+p+'"'));
console.log('PASS full-text 218 pages; bilingual nonindexable recovery; no sitemap entry');
