'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../dist'),base='https://chems.test';
(async()=>{const browser=await chromium.launch({headless:true});let checks=0;
for(const lang of ['ja','en'])for(const width of [320,390,1280]){
 const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
 await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==base)return r.abort();let f=path.join(root,u.pathname);if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f=path.join(f,'index.html');return fs.existsSync(f)?r.fulfill({path:f}):r.fulfill({status:404,body:'missing'});});
 const prefix=lang==='ja'?'':'en/';await page.goto(base+'/'+prefix+'index.html');
 assert.equal(await page.locator('.archive-route').count(),3);assert.equal(await page.locator('.archive-albums .el').count(),10);checks+=2;
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks++;
 assert.equal(await page.locator('.gh nav a').count(),5);assert.equal(await page.locator('.nowlist').count(),0);checks+=2;
 fs.mkdirSync(path.resolve(root,'../test-artifacts'),{recursive:true});await page.screenshot({path:path.resolve(root,'../test-artifacts',`archive-${lang}-${width}.png`),fullPage:true});
 await page.locator('.archive-route .more').first().click();assert(await page.locator('h1').innerText());await page.goBack();assert.equal(await page.locator('.archive-route').count(),3);checks+=2;
 await page.goto(base+'/'+prefix+'now/index.html');assert.equal(await page.locator('.nowlist').count(),0);assert.equal(await page.locator('main li a').count(),5);checks+=2;
 await page.locator('main li a').first().click();assert.equal(await page.locator('.filters').count(),1);await page.locator('.filters button[data-k="album"]').click();assert.equal(await page.locator('.filters button[data-k="album"]').getAttribute('aria-pressed'),'true');checks+=2;
 await page.locator('.gf time').scrollIntoViewIfNeeded();assert(await page.locator('.gf time').isVisible());checks++;
 await page.close();
}await browser.close();console.log(JSON.stringify({pass:true,checks,network:'all external requests blocked',playback:'not tested'}));})().catch(e=>{console.error(e);process.exit(1)});
