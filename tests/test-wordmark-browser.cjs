const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../dist'),out=path.resolve(__dirname,'../test-artifacts');
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch();const report=[];
for(const width of [320,390,768,1280])for(const lang of ['ja','en']){
const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!=='https://chems.test')return r.abort();const p=path.join(root,u.pathname);return fs.existsSync(p)&&fs.statSync(p).isFile()?r.fulfill({path:p}):r.fulfill({status:404,body:'missing'});});
for(const file of ['index.html','profile/index.html']){
await page.goto('https://chems.test/'+(lang==='en'?'en/':'')+file);const mark=page.locator('.site-wordmark');await mark.waitFor();
assert(await mark.evaluate(e=>e.complete&&e.naturalWidth>0));const box=await mark.boundingBox();assert(Math.abs(box.width/box.height-1799/504)<0.01);assert(box.width>=179&&box.x>=0&&box.x+box.width<=width);
assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));const nav=await page.locator('.gh nav').boundingBox(),language=await page.locator('.gh .lang').boundingBox();
assert(box.x+box.width<=language.x+1);if(width<=640)assert(nav.y>=box.y+box.height-1);else assert(nav.x>=box.x+box.width-1);
assert(await page.locator('.gh .home').getAttribute('aria-label')==='myChems');
await page.screenshot({path:path.join(out,`brand-${lang}-${width}-${file.replaceAll('/','-')}.png`),fullPage:false});
await page.locator('.gh .home').click();assert(page.url().endsWith('index.html'));
report.push({width,lang,file,logoWidth:box.width,ratio:box.width/box.height,painted:true});
}await page.close();}await browser.close();fs.writeFileSync(path.join(out,'wordmark-report.json'),JSON.stringify(report,null,2));console.log('PASS approved wordmark painted, no collision, navigation preserved, both languages / four widths');})().catch(e=>{console.error(e);process.exit(1)});
