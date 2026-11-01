import test from 'node:test';
import assert from 'node:assert/strict';
import { createApiLoader, createVisiblePlayerAdapter, classifyPlayerError } from '../src/listening/youtube-adapter.mjs';
import { createQueue, receive } from '../src/listening/model.mjs';
import { createBufferingNotice } from '../src/listening/buffering.mjs';
function setup() {
 const nodes=[], callbacks=[];
 const document={createTextNode:text=>({text}),createElement:tag=>({tag,remove(){this.removed=true;}}),head:{append:n=>nodes.push(n)}};
 const container={replaceChildren(...items){this.children=items;}};
 const YT={Player:function(frame,options){callbacks.push(options.events);this.frame=frame;frame.options=options;this.destroy=()=>frame.remove();}};
 const channelId='UC'+'X'.repeat(22),id='X'.repeat(11),at='2026-10-31T00:00:00Z';
 const recording={id:'r',title:'Title',version:'Album mix'},entry={id:'e',recordingId:'r'},edition={id:'edition'};
 const video={id,testOnly:false,channelId,officialEvidence:{channelId,channelType:'artist',videoId:id,sourceUrl:'https://example.invalid/proof',checkedAt:at,reviewed:true,reviewer:'synthetic-test'},match:{recordingId:'r',entryId:'e',editionId:'edition',title:'Title',version:'Album mix',sourceUrl:'https://example.invalid/edition',checkedAt:at,reviewed:true},availability:{state:'available',embeddable:true,checkedAt:at}};
 const events=[];return {nodes,document,container,YT,callbacks,events,args:{container,video,recording,entry,edition,selectionGeneration:17,userRequested:true,onState:e=>events.push(e)}};
}

for (const [native,type] of [[-1,'unstarted'],[5,'cued']]) test(`buffering to ${type} clears the notice and permits later playback/recovery`,async()=>{
 const s=setup();let now=0,id=0,slow=0;const tasks=new Map();
 const timers={setTimeout(fn,ms){tasks.set(++id,{fn,at:now+ms});return id;},clearTimeout(id){tasks.delete(id);}};
 const advance=ms=>{now+=ms;for(const [key,t] of [...tasks])if(t.at<=now){tasks.delete(key);t.fn();}};
 const notice=createBufferingNotice({schedule:timers.setTimeout,cancel:timers.clearTimeout,onSlow:()=>slow++});
 let q=createQueue({id:'edition',entries:[s.args.entry]});
 const a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT,timers});
 const mount=()=>a.mount({...s.args,selectionGeneration:q.generation,onState:e=>{const next=receive(q,e);assert.notEqual(next,q);q=next;notice.event(e);}});
 await mount();let cb=s.callbacks.at(-1);cb.onReady({target:{cueVideoById(){}}});
 cb.onStateChange({data:3});advance(5000);cb.onStateChange({data:native});assert.equal(q.status,type);advance(16000);assert.equal(slow,0);
 cb.onStateChange({data:3});advance(16000);assert.equal(slow,1);cb.onStateChange({data:native});assert.equal(q.status,type);advance(16000);assert.equal(slow,1);
 cb.onStateChange({data:3});cb.onStateChange({data:1});advance(16000);assert.equal(q.status,'playing');assert.equal(slow,1);
 cb.onStateChange({data:2});assert.equal(q.status,'paused');cb.onStateChange({data:3});cb.onError({data:101});advance(16000);assert.equal(q.status,'error');assert.equal(slow,1);
 cb.onStateChange({data:native});assert.equal(q.status,'error');assert.equal(s.callbacks.length,1);
 await mount();assert.equal(s.callbacks.length,2);cb=s.callbacks.at(-1);cb.onReady({target:{cueVideoById(){}}});cb.onStateChange({data:native});cb.onStateChange({data:1});assert.equal(q.status,'playing');
 notice.clear();a.dispose();cb.onStateChange({data:native});advance(16000);assert.equal(q.status,'playing');
});
test('native-ready watchdog fails once and stale readiness cannot revive a timed-out player',async()=>{
 const s=setup();let timeout;const timers={setTimeout(fn){timeout=fn;return 1;},clearTimeout(){}};
 const a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT,timers});
 await a.mount(s.args);timeout();timeout();s.callbacks[0].onReady({target:{cueVideoById:()=>assert.fail('late readiness')}});
 assert.equal(s.events.length,1);assert.equal(s.events[0].detail,'player-ready-timeout');a.dispose();
});
test('no network by default; mock opted-in loader only appends declared script',async()=>{
 const s=setup(),window={};await assert.rejects(createApiLoader({window,document:s.document})());assert.equal(s.nodes.length,0);
 const load=createApiLoader({window,document:s.document,allowNetwork:true}),p=load();assert.equal(load(),p);
 assert.equal(s.nodes[0].src,'https://www.youtube.com/iframe_api');assert.equal(s.nodes[0].referrerPolicy,'strict-origin-when-cross-origin');
 window.YT=s.YT;window.onYouTubeIframeAPIReady();assert.equal(await p,s.YT);
});
test('loader mock failure rejects and supports explicit retry',async()=>{
 const s=setup(),window={},load=createApiLoader({window,document:s.document,allowNetwork:true});
 const p=load();s.nodes[0].onerror();await assert.rejects(p);const p2=load();window.YT=s.YT;window.onYouTubeIframeAPIReady();await p2;assert.equal(s.nodes.length,2);
});
test('no request or evidence means no loader call or iframe',async()=>{
 const s=setup();let calls=0;const a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>{calls++;return s.YT;}});
 assert.equal((await a.mount({...s.args,userRequested:false})).mounted,false);
 s.args.video.testOnly=true;assert.equal((await a.mount(s.args)).mounted,false);assert.equal(calls,0);
});
test('visible frame, native play and documented cue only',async()=>{
 const s=setup(),a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT});
 assert.equal((await a.mount(s.args)).mounted,true);const f=s.container.children[0];
 assert.equal(f.tag,'div');assert.equal(f.options.host,'https://www.youtube.com');assert.deepEqual(f.options.playerVars,{origin:'https://example.invalid',playsinline:1});assert.equal(f.options.videoId,'X'.repeat(11));
 let cue;s.callbacks[0].onReady({target:{cueVideoById:x=>cue=x}});assert.deepEqual(cue,{videoId:'X'.repeat(11),startSeconds:0});assert.equal(s.events[0].type,'ready');
 a.dispose();assert.equal(f.removed,true);s.callbacks[0].onError();assert.equal(s.events.length,1);
});
test('dispose during loader prevents late mounting',async()=>{
 const s=setup();let resolve;const a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:()=>new Promise(r=>resolve=r)});
 const pending=a.mount(s.args);a.dispose();resolve(s.YT);assert.equal((await pending).mounted,false);assert.equal(s.callbacks.length,0);
});
test('generic error blocks current selection without advance or late ready',async()=>{
 const s=setup(),a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT});await a.mount(s.args);
 s.callbacks[0].onError({data:123});s.callbacks[0].onReady({target:{cueVideoById:()=>assert.fail('late ready')}});s.callbacks[0].onError();
 assert.deepEqual(s.events,[{type:'error',generation:17,entryId:'e',detail:'player-error'}]);assert.match(s.container.children[0].text,/remains selected/);
});
test('stale previous selection callback cannot remove newer frame',async()=>{
 const s=setup(),a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT});await a.mount(s.args);const old=s.callbacks[0];await a.mount({...s.args,selectionGeneration:18});const current=s.container.children[0];old.onError();assert.notEqual(current.removed,true);assert.equal(s.events.length,0);
});

test('loader timeout terminates visibly through rejection with no automatic retry',async()=>{
 const s=setup(),window={};let timeout,cleared=false;
 const timers={setTimeout(fn,ms){assert.equal(ms,15000);timeout=fn;return 1;},clearTimeout(id){assert.equal(id,1);cleared=true;}};
 const load=createApiLoader({window,document:s.document,allowNetwork:true,timers});
 const p=load(),late=window.onYouTubeIframeAPIReady;timeout();
 await assert.rejects(p,/unavailable/);assert.equal(cleared,true);assert.equal(s.nodes[0].removed,true);
 window.YT=s.YT;late();assert.equal(s.nodes.length,1);assert.equal(window.onYouTubeIframeAPIReady,undefined);
});

test('documented errors distinguish embedding denial and identity failures without retry',()=>{
 assert.equal(classifyPlayerError(101),'embedding-disabled');assert.equal(classifyPlayerError(150),'embedding-disabled');
 assert.equal(classifyPlayerError(153),'client-identity-missing');assert.equal(classifyPlayerError(100),'unavailable');
 assert.equal(classifyPlayerError(2),'invalid-request');assert.equal(classifyPlayerError(5),'playback-error');
 assert.equal(classifyPlayerError(999),'player-error');
});

test('API readiness is not playback; playing and ended do not advance selection',async()=>{
 const s=setup(),a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT});await a.mount(s.args);
 s.callbacks[0].onReady({target:{cueVideoById(){}}});assert.equal(s.events[0].type,'ready');
 s.callbacks[0].onStateChange({data:1});s.callbacks[0].onStateChange({data:2});s.callbacks[0].onStateChange({data:3});s.callbacks[0].onStateChange({data:0});
 assert.deepEqual(s.events.map(e=>e.type),['ready','playing','paused','buffering','ended']);assert.ok(s.events.every(e=>e.entryId==='e'));
});

test('continuation loads only on ready, blocked playback remains visible with manual guidance',async()=>{
 const s=setup(),a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT});await a.mount({...s.args,continuePlayback:true});let load=0;
 assert.equal(s.container.children[0].options.host,'https://www.youtube.com');s.callbacks[0].onReady({target:{loadVideoById:v=>{load++;assert.equal(v.videoId,s.args.video.id);},cueVideoById:()=>assert.fail('not cue')}});assert.equal(load,1);
 s.callbacks[0].onAutoplayBlocked();assert.equal(s.events.at(-1).type,'autoplay-blocked');assert.notEqual(s.container.children[0].removed,true);a.dispose();s.callbacks[0].onAutoplayBlocked();assert.equal(s.events.length,2);
});
test('explicit track-click requests play through standard API, pause/resume are manual',async()=>{const s=setup(),a=createVisiblePlayerAdapter({document:s.document,origin:'https://example.invalid',loadApi:async()=>s.YT});await a.mount({...s.args,requestPlay:true});let loaded,played=0,paused=0;s.callbacks[0].onReady({target:{loadVideoById:v=>loaded=v,playVideo:()=>played++,pauseVideo:()=>paused++}});assert.equal(loaded.videoId,s.args.video.id);assert(a.play());assert(a.pause());assert.equal(played,1);assert.equal(paused,1);a.dispose();assert.equal(a.play(),false);});
