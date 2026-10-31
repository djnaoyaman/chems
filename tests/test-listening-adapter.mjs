import test from 'node:test';
import assert from 'node:assert/strict';
import { createApiLoader, createVisiblePlayerAdapter, classifyPlayerError } from '../src/listening/youtube-adapter.mjs';
function setup() {
 const nodes=[], callbacks=[];
 const document={createTextNode:text=>({text}),createElement:tag=>({tag,remove(){this.removed=true;}}),head:{append:n=>nodes.push(n)}};
 const container={replaceChildren(...items){this.children=items;}};
 const YT={Player:function(frame,options){callbacks.push(options.events);this.frame=frame;}};
 const channelId='UC'+'X'.repeat(22),id='X'.repeat(11),at='2026-10-31T00:00:00Z';
 const recording={id:'r',title:'Title',version:'Album mix'},entry={id:'e',recordingId:'r'},edition={id:'edition'};
 const video={id,testOnly:false,channelId,officialEvidence:{channelId,channelType:'artist',videoId:id,sourceUrl:'https://example.invalid/proof',checkedAt:at,reviewed:true,reviewer:'synthetic-test'},match:{recordingId:'r',entryId:'e',editionId:'edition',title:'Title',version:'Album mix',sourceUrl:'https://example.invalid/edition',checkedAt:at,reviewed:true},availability:{state:'available',embeddable:true,checkedAt:at}};
 const events=[];return {nodes,document,container,YT,callbacks,events,args:{container,video,recording,entry,edition,selectionGeneration:17,userRequested:true,onState:e=>events.push(e)}};
}
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
 assert.equal(f.width,'480');assert.equal(f.height,'270');assert.equal(f.referrerPolicy,'strict-origin-when-cross-origin');
 assert.match(f.src,/enablejsapi=1&origin=/);assert.doesNotMatch(f.src,/autoplay|mute|controls|branding/);
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
