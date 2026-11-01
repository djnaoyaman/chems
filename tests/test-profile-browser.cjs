const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../dist'),out=path.resolve(__dirname,'../test-artifacts');
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch();for(const width of [320,390,1280])for(const lang of ['ja']){
const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
await page.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!=='https://chems.test')return r.abort();const p=path.join(root,u.pathname);return fs.existsSync(p)&&fs.statSync(p).isFile()?r.fulfill({path:p}):r.fulfill({status:404,body:'missing'});});
await page.goto('https://chems.test/'+(lang==='en'?'en/':'')+'profile/index.html');assert(await page.locator('h1').isVisible());assert.equal(await page.locator('h1').innerText(),'DJ Naoyaman');
const author=page.locator('main a[href="https://djnaoyaman.github.io/profile.html"]');assert(await author.isVisible());assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
await page.screenshot({path:path.join(out,`profile-${lang}-${width}.png`),fullPage:true});await page.close();}await browser.close();console.log('PASS painted compact profiles at 3 widths, both languages');})().catch(e=>{console.error(e);process.exit(1)});
