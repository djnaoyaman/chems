'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../dist'),out=path.resolve(__dirname,'../test-artifacts');
(async()=>{const browser=await chromium.launch();let checks=0;fs.mkdirSync(out,{recursive:true});
for(const lang of ['ja','en'])for(const width of [320,375,390,430,768,844,1280,1440]){
 const page=await browser.newPage({viewport:{width,height:width===844?390:900},reducedMotion:'reduce'});let apiRequests=0;const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>{const u=new URL(r.request().url());
  if(u.href==='https://www.youtube.com/iframe_api'){apiRequests++;return r.fulfill({contentType:'application/javascript',body:`window.YT={Player:function(node,options){window.__mounts=(window.__mounts||0)+1;const frame=document.createElement('iframe');frame.title='YouTube mock';frame.src='https://www.youtube.com/embed/'+options.videoId;frame.allow='autoplay; encrypted-media; picture-in-picture';node.replaceWith(frame);this.destroy=()=>frame.remove();const target={cueVideoById:value=>{window.__listeningCue=value;},loadVideoById:value=>{window.__listeningAuto=value;},playVideo:()=>options.events.onStateChange({data:1}),pauseVideo:()=>options.events.onStateChange({data:2})};window.__listeningMock=options.events;if(!window.__suppressReady)queueMicrotask(()=>options.events.onReady({target}));}};window.onYouTubeIframeAPIReady();`});}
  if(u.hostname==='www.youtube.com'&&u.pathname.startsWith('/embed/'))return r.fulfill({contentType:'text/html',body:'<!doctype html><title>Mock</title><body style="background:#111;color:white;font:18px sans-serif">YouTube mock - no actual audio</body>'});
  if(u.origin!=='https://djnaoyaman.github.io')return r.abort();let file=path.join(root,u.pathname.replace(/^\/chems\//,''));if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file=path.join(file,'index.html');if(!fs.existsSync(file))return r.fulfill({status:404,body:'missing'});return r.fulfill({path:file,...(file.endsWith('.mjs')?{contentType:'application/javascript'}:{})});
 });
 await page.clock.install();
 await page.goto('https://djnaoyaman.github.io/chems/'+(lang==='en'?'en/':'')+'works/');
 await page.waitForFunction(()=>document.querySelector('[data-listening=release]').options.length===58);
 const $=key=>page.locator('[data-listening='+key+']'),frame=page.locator('[data-listening=visual] iframe');
 assert.equal(apiRequests,0);assert(await $('dock').isHidden());checks++;
 await $('start').focus();await page.keyboard.press('Enter');await page.waitForFunction(()=>window.__listeningAuto?.videoId==='4QKi8DorEpM');
 assert(await $('dock').isVisible());assert.equal(await $('release').inputValue(),'epd');assert((await $('tracks').locator('button[aria-current=true]').innerText()).startsWith('1.'));assert.equal(await $('tracks').locator('li').count(),11);assert.equal(apiRequests,1);checks++;
 assert((await $('coverage').innerText()).includes('10/11'));assert.equal(await frame.count(),1);const box=await frame.boundingBox();assert(box.width>=200&&box.height>=200);checks++;
 if(width===390)for(const native of [-1,5]){
  const emit=data=>page.evaluate(data=>window.__listeningMock.onStateChange({data}),data);
  const waiting=lang==='ja'?'再生待ちです。表示中のYouTube再生ボタンで開始できます。':'Waiting to play. Use the visible YouTube play button to start.';
  const selected=await $('now').innerText(),mounts=await page.evaluate(()=>window.__mounts);
  await emit(3);await page.clock.fastForward(5000);await emit(native);await page.clock.fastForward(16000);assert.equal(await $('status').innerText(),waiting);checks++;
  await emit(3);await page.clock.fastForward(16000);assert((await $('status').innerText()).includes(lang==='ja'?'時間がかか':'longer than'));await emit(native);assert.equal(await $('status').innerText(),waiting);await page.clock.fastForward(16000);assert.equal(await $('status').innerText(),waiting);checks++;
  await $('status').evaluate(e=>e.scrollIntoView({block:'nearest'}));await page.screenshot({path:path.join(out,`native-${native===5?'cued':'unstarted'}-${lang}-390.png`)});
  await emit(3);await $('load').click();assert((await $('status').innerText()).includes(lang==='ja'?'再生中':'Playing'));await $('pause').click();const paused=await $('status').innerText();assert(paused.includes(lang==='ja'?'一時停止':'Paused'));await page.clock.fastForward(16000);assert.equal(await $('status').innerText(),paused);assert.equal(await page.evaluate(()=>window.__mounts),mounts);checks++;
  await emit(3);await page.evaluate(()=>{window.__waitingOld=window.__listeningMock;window.__listeningMock.onError({data:101});});const failed=await $('status').innerText();await page.clock.fastForward(16000);assert.equal(await $('status').innerText(),failed);assert(await $('retry').isVisible());assert.equal(await frame.count(),0);assert.equal(await page.evaluate(()=>window.__mounts),mounts);checks++;
  await $('retry').click();await page.waitForFunction(n=>window.__mounts===n+1,mounts);await page.evaluate(native=>window.__waitingOld.onStateChange({data:native}),native);await emit(native);assert.equal(await $('status').innerText(),waiting);await $('load').click();assert((await $('status').innerText()).includes(lang==='ja'?'再生中':'Playing'));assert.equal(await $('now').innerText(),selected);assert((await $('coverage').innerText()).includes('10/11'));checks++;
 }
 assert(!(await $('continuous').isChecked()));await page.evaluate(()=>window.__listeningMock.onStateChange({data:1}));assert((await $('status').innerText()).includes(lang==='ja'?'再生中':'Playing'));checks++;
 await $('pause').click();assert((await $('status').innerText()).includes(lang==='ja'?'一時停止':'Paused'));await $('load').click();assert((await $('status').innerText()).includes(lang==='ja'?'再生中':'Playing'));checks++;
 await $('full').click();assert.equal(await $('full').getAttribute('aria-expanded'),'true');await $('full').press('Escape');assert.equal(await $('full').getAttribute('aria-expanded'),'false');checks++;
 await page.screenshot({path:path.join(out,`listening-dock-${lang}-${width}.png`)});
 await $('close').click();assert(await $('dock').isHidden());assert.equal(await frame.count(),0);assert(await $('start').evaluate(e=>e===document.activeElement));checks++;
 // Single click on a matching track opens and requests playback. Missing entries stay selectable and explicit.
 await page.getByRole('button',{name:/3\. Song To The Siren/}).click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='D7R4Z0T5ViA');assert(await $('dock').isVisible());checks++;
 await page.getByRole('button',{name:/5\. Fuck Up Beats/}).click();assert(await $('load').isDisabled());assert.equal(await frame.count(),0);checks++;
 await page.getByRole('button',{name:/3\. Song To The Siren/}).click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='D7R4Z0T5ViA');await $('continuous').check();
 await page.evaluate(()=>{window.__oldPlayer=window.__listeningMock;window.__listeningMock.onStateChange({data:1});window.__listeningMock.onStateChange({data:0});});await page.waitForFunction(()=>window.__listeningAuto?.videoId==='kJqSFi0ukEY');checks++;
 await page.evaluate(()=>{window.__oldPlayer.onStateChange({data:0});window.__listeningMock.onStateChange({data:0});});assert((await $('tracks').locator('button[aria-current=true]').innerText()).startsWith('4.'));checks++;
 await page.evaluate(()=>{window.__listeningMock.onStateChange({data:1});window.__listeningMock.onStateChange({data:0});});assert((await $('tracks').locator('button[aria-current=true]').innerText()).startsWith('5.'));assert.equal(await frame.count(),0);assert((await $('status').innerText()).includes(lang==='ja'?'飛ばしていません':'No track was skipped'));checks++;
 await page.getByRole('button',{name:/3\. Song To The Siren/}).click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='D7R4Z0T5ViA');await page.evaluate(()=>window.__listeningMock.onAutoplayBlocked());assert((await $('status').innerText()).includes(lang==='ja'?'再生ボタン':'play button'));assert.equal(await frame.count(),1);checks++;
 await page.evaluate(()=>window.__listeningMock.onStateChange({data:3}));await page.clock.fastForward(14000);assert(!(await $('status').innerText()).includes(lang==='ja'?'時間がかか':'longer than'));await page.evaluate(()=>window.__listeningMock.onStateChange({data:3}));await page.clock.fastForward(1000);const slow=await $('status').innerText();assert(slow.includes(lang==='ja'?'時間がかか':'longer than'));checks++;
 await page.evaluate(()=>window.__listeningMock.onStateChange({data:3}));assert.equal(await $('status').innerText(),slow);await $('stop').click();assert.equal(await frame.count(),0);const stopped=await $('status').innerText();await page.clock.fastForward(20000);assert.equal(await $('status').innerText(),stopped);assert((await $('coverage').innerText()).includes('10/11'));checks++;
 await page.getByRole('button',{name:/3\. Song To The Siren/}).click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='D7R4Z0T5ViA');await page.evaluate(()=>window.__listeningMock.onError({data:101}));assert.equal(await frame.count(),0);assert(await $('load').isDisabled());assert((await $('coverage').innerText()).includes('10/11'));checks++;
 await page.evaluate(()=>{dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}));dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}));});assert.equal(await frame.count(),0);assert(await $('load').isDisabled());checks++;
 await $('type').selectOption('single');assert.equal(await $('release').locator('option').count(),41);assert(await $('dock').isHidden());checks++;
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);checks++;

 // Scoped discovery never jumps from an empty format to a different release.
 await $('type').selectOption('ep');await $('release').selectOption('lof');assert(await $('start').isDisabled());assert.equal(await $('tracks').locator('li').count(),4);checks++;
 await $('type').selectOption('all');await $('search').fill('DIG');assert.equal(await $('release').locator('option').count(),2);assert(await $('start').isEnabled());checks++;
 await $('search').fill('no-such-title');assert(await $('start').isDisabled());assert.equal(await $('release').locator('option').count(),1);checks++;
 await $('search').fill('');await $('release').selectOption('cwu');await $('start').click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='PtuC8byjkJk'||document.querySelector('[data-listening=heading]').textContent==='Come with Us');assert.equal(await $('release').inputValue(),'cwu');checks++;
 await $('close').click();
 // Detail-to-shelf carries a release ID but never autoplays on arrival.
 await page.goto('https://djnaoyaman.github.io/chems/'+(lang==='en'?'en/':'')+'works/exit-planet-dust/');await page.locator('.release-listen-link').click();await page.waitForFunction(()=>document.querySelector('[data-listening=tracks]').children.length===11);assert.equal(await $('release').inputValue(),'epd');assert(await $('dock').isHidden());checks++;
 // Repeating the same selection resumes without destroying/recreating its iframe.
 await page.getByRole('button',{name:/2\. In Dust We Trust/}).click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='YtnBsvu72kY');const mounts=await page.evaluate(()=>window.__mounts);await page.getByRole('button',{name:/2\. In Dust We Trust/}).click();assert.equal(await page.evaluate(()=>window.__mounts),mounts);checks++;
 await $('next').click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='D7R4Z0T5ViA');assert((await $('now').innerText()).startsWith('3.'));checks++;
 if(width===844){
  for(const key of ['previous','load','pause','stop','next','full','continuous','pin','close']){await $(key).focus();assert(await $(key).evaluate(e=>{const r=e.getBoundingClientRect(),dock=e.closest('[data-listening=dock]'),d=dock.getBoundingClientRect(),top=dock.querySelector('.listening-dock-top').getBoundingClientRect();const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.top>=(e.closest('.listening-dock-top')?d.top:top.bottom)&&r.bottom<=d.bottom&&r.top>=0&&r.bottom<=innerHeight&&(e===hit||e.contains(hit));}),`landscape keyboard reachability: ${key}`);checks++;}
  await page.locator('.listening-controls').evaluate(e=>e.scrollIntoView({block:'start'}));await page.screenshot({path:path.join(out,`landscape-dock-scrolled-${lang}.png`)});
 }
 await $('pin').click();assert.equal(await $('dock').evaluate(e=>getComputedStyle(e).position),'relative');assert.equal(await frame.count(),1);const inline=await frame.boundingBox();assert(inline.width>=200&&inline.height>=200);await $('dock').evaluate(e=>e.scrollIntoView({block:'start'}));await page.screenshot({path:path.join(out,'listening-inline-'+lang+'-'+width+'.png')});checks++;
 if(width===320){for(const button of await page.locator('.listening-controls button').all()){assert(await button.evaluate(e=>getComputedStyle(e).whiteSpace==='nowrap'&&e.scrollWidth<=e.clientWidth),'full narrow transport label');}checks++;}
 if(width>=1280){assert((await frame.boundingBox()).height<=360);for(const key of ['previous','load','pause','stop','next','full']){const r=await $(key).boundingBox();assert(r.y>=0&&r.y+r.height<=900,`desktop transport in viewport: ${key}`);}checks++;}
 await $('close').click();assert(await $('tracks').locator('button[aria-current=true]').evaluate(e=>e===document.activeElement));checks++;
 await page.getByRole('button',{name:/3\. Song To The Siren/}).click();await page.waitForFunction(()=>window.__listeningAuto?.videoId==='D7R4Z0T5ViA');await page.evaluate(()=>window.__listeningMock.onError({data:101}));assert(await $('retry').isVisible());await $('retry').click();await page.waitForFunction(()=>document.querySelector('[data-listening=visual] iframe'));assert((await $('coverage').innerText()).includes('10/11'));checks++;
 // API script readiness alone is insufficient: bound native iframe must become ready.
 await $('stop').click();await page.evaluate(()=>window.__suppressReady=true);await $('load').click();await page.clock.fastForward(15000);assert(await $('retry').isVisible());assert.equal(await frame.count(),0);checks++;
 await page.evaluate(()=>window.__suppressReady=false);await $('retry').click();await page.waitForFunction(()=>document.querySelector('[data-listening=visual] iframe'));await $('stop').click();const stoppedAgain=await $('status').innerText();await page.clock.fastForward(20000);assert.equal(await $('status').innerText(),stoppedAgain);checks++;
 await page.screenshot({path:path.join(out,`listening-improved-${lang}-${width}.png`)});
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);
 await page.close();
}await browser.close();console.log(JSON.stringify({pass:true,checks,network:'external resources mocked/blocked; no actual playback evidence',viewports:[320,375,390,430,768,844,1280,1440]}));})().catch(e=>{console.error(e);process.exit(1)});
