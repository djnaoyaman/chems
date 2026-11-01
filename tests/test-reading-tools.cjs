'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../dist'),base='https://djnaoyaman.github.io/chems/';
const full=fs.readFileSync(path.join(root,'llms-full.txt'),'utf8');assert.equal((full.match(/^## https:/gm)||[]).length,109);assert(full.includes('事実と私見'));assert(full.includes('このサイトで取り上げる'));assert(!full.includes('dataLayer.push'));
const recovery=fs.readFileSync(path.join(root,'404.html'),'utf8');assert(recovery.includes('noindex,follow'));assert(!recovery.includes('rel="canonical"'));assert(!fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').includes('404.html'));for(const p of ['','works/','timeline/'])assert(recovery.includes('href="'+base+p+'"'));
console.log('PASS full-text 109 pages; Japanese-only nonindexable recovery; no sitemap entry');

assert(!recovery.includes('English home'));assert(!fs.existsSync(path.join(root,'en')));assert(!full.includes('/chems/en/'));
