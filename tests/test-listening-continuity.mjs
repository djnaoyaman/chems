import test from 'node:test';import assert from 'node:assert/strict';import {session,event} from '../src/listening/continuity.mjs';
const ev=(type,extra={})=>({type,entryId:'a',generation:1,...extra}),next={entryId:'b',admitted:true};
function playing(opt=true){return event(session('a',1,opt),ev('playing')).state;}
test('manual default never auto-advances',()=>assert.equal(event(playing(false),ev('ended'),next).effect,null));
test('ready is not playback',()=>{const s=event(session('a',1,true),ev('ready')).state;assert.equal(event(s,ev('ended'),next).effect,null);});
test('opted-in played then ended requests visible next once',()=>{const r=event(playing(),ev('ended'),next);assert.equal(r.effect.type,'request-visible-next');assert.equal(event(r.state,ev('ended'),next).effect,null);});
test('gap stops at immediate entry, never scans or skips',()=>assert.deepEqual(event(playing(),ev('ended'),{entryId:'b',admitted:false}).effect,{type:'stop-at-gap',entryId:'b'}));
test('stale callback cannot advance',()=>assert.equal(event(playing(),ev('ended',{generation:0}),next).effect,null));
test('wrong entry cannot advance',()=>assert.equal(event(playing(),ev('ended',{entryId:'other'}),next).effect,null));
test('error cancels continuation',()=>{const s=event(playing(),ev('error')).state;assert.equal(event(s,ev('ended'),next).effect,null);});
test('autoplay block prompts manual action once, no retry',()=>{const r=event(playing(),ev('autoplay-blocked'));assert.equal(r.effect.type,'manual-play-prompt');assert.equal(event(r.state,ev('autoplay-blocked')).effect,null);});
test('last entry does not wrap',()=>assert.equal(event(playing(),ev('ended'),null).effect.type,'release-ended'));
test('off or selection-change new session discards old playback',()=>assert.equal(event(session('b',2,false),ev('ended'),next).effect,null));
