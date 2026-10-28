'use strict';
const assert=require('node:assert/strict');
const {create}=require('../src/premium-playback-hint.js');
let checks=0;const ok=(v,m)=>{assert(v,m);checks++};
class E{constructor(doc){this.ownerDocument=doc;this.children=[];this.events={};this.attrs={};}append(...nodes){nodes.forEach(n=>{n.parent=this;this.children.push(n)});}remove(){this.parent.children=this.parent.children.filter(n=>n!==this);}contains(e){return this===e||this.children.some(n=>n.contains(e));}setAttribute(k,v){this.attrs[k]=v;}addEventListener(k,v){this.events[k]=v;}}
function setup(storage={getItem:()=>null,setItem:()=>{}},english=false){const doc={activeElement:null,createElement:()=>new E(doc)};const host=new E(doc);let fn,clear=0;const c=create({host,key:'site-v1',storage,english,setTimeout:f=>(fn=f,1),clearTimeout:()=>clear++});return {c,doc,host,tick:()=>fn(),clears:()=>clear};}
let e=setup();ok(e.c.show(),'first show');ok(e.host.children.length===1,'normal-flow child');ok(!e.c.show(),'repeat suppressed');let node=e.host.children[0];ok(node.children[0].children[0].children[0].href.includes('support.google.com/youtube/answer/7437519'),'official details');ok(node.children[1].attrs['aria-label'],'close accessible');e.tick();ok(!e.host.children.length,'auto hide');
e=setup({getItem:()=>1});ok(!e.c.show()&&!e.host.children.length,'session already seen across route/reload');
e=setup({getItem:()=>{throw Error('denied')}});ok(e.c.show(),'storage denied works');e.c.dismiss();ok(!e.c.show(),'storage denied memory guard');
e=setup();e.c.show();node=e.host.children[0];node.children[1].events.click();ok(!e.host.children.length,'manual dismissal');
e=setup();e.c.show();node=e.host.children[0];e.doc.activeElement=node.children[1];node.events.focusin();e.tick();ok(e.host.children.length===1,'focused hint not removed');e.doc.activeElement=null;node.events.focusout();e.tick();ok(!e.host.children.length,'blur resumes timeout');
e=setup(undefined,true);e.c.show();ok(e.host.children[0].children[0].textContent.includes('ad-free'),'English copy');
console.log(JSON.stringify({pass:true,checks}));
