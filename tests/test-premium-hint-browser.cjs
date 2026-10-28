'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..','dist'),base='https://chems.test/';
function walk(d){return fs.readdirSync(d,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(d,e.name)):path.join(d,e.name));}
const pages=walk(root).filter(p=>p.endsWith('.html')&&fs.readFileSync(p,'utf8').includes('class="facade"'));
assert(pages.length>0);
for(const p of pages){const s=fs.readFileSync(p,'utf8');assert(s.includes('chems-premium-hint-v1'));assert(s.includes('www.youtube-nocookie.com/embed/'));}
(async()=>{const browser=await chromium.launch({headless:true});let checks=0;
for(const lang of ['ja','en'])for(const width of [320,390,1280])for(const blocked of [false,true]){
 const source=pages.find(p=>fs.readFileSync(p,'utf8').includes('<html lang="'+lang+'"'));
 assert(source,'page for '+lang);
 const page=await browser.newPage({viewport:{width,height:844},reducedMotion:'reduce'});
 if(blocked)await page.addInitScript(()=>Object.defineProperty(window,'sessionStorage',{get(){throw Error('blocked')}}));
 await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==base.slice(0,-1))return r.abort();const p=path.join(root,u.pathname);return fs.existsSync(p)&&fs.statSync(p).isFile()?r.fulfill({path:p}):r.fulfill({status:404,body:'missing'});});
 await page.goto(base+path.relative(root,source));await page.locator('.facade').click();
 assert.equal(await page.locator('.premium-playback-hint').count(),1);checks++;
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks++;
 const hint=await page.locator('.premium-playback-hint').boundingBox(),video=await page.locator('.player iframe').boundingBox();
 assert(hint.y>=video.y+video.height-1);checks++;
 assert((await page.locator('.player iframe').getAttribute('src')).startsWith('https://www.youtube-nocookie.com/embed/'));checks++;
 if(!blocked&&width===390){fs.mkdirSync(path.resolve(root,'..','test-artifacts'),{recursive:true});await page.locator('.player').screenshot({path:path.resolve(root,'..','test-artifacts','premium-hint-'+lang+'.png')});}
 await page.locator('.premium-playback-hint button').click();assert.equal(await page.locator('.premium-playback-hint').count(),0);checks++;
 if(!blocked){await page.reload();await page.locator('.facade').click();assert.equal(await page.locator('.premium-playback-hint').count(),0);checks++;}
 await page.close();
}
await browser.close();console.log(JSON.stringify({pass:true,checks,generatedPlayerPages:pages.length,playback:'blocked network; iframe configuration and UI only'}));})().catch(e=>{console.error(e);process.exit(1)});
