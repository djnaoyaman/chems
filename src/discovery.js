(function(){'use strict';
const en=document.documentElement.lang==='en';
const nav=document.getElementById('site-nav'),toggle=document.querySelector('.nav-toggle');
if(nav&&toggle){
 toggle.hidden=false;document.documentElement.classList.add('nav-ready');
 const close=()=>{toggle.setAttribute('aria-expanded','false');nav.classList.remove('is-open');};
 toggle.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle.getAttribute('aria-expanded')==='true'){close();toggle.focus();}});
 document.addEventListener('click',e=>{if(!e.target.closest('.gh'))close();});
 nav.addEventListener('click',e=>{if(e.target.closest('a'))close();});
 window.addEventListener('pageshow',close);
}
const table=document.getElementById('ptable'),input=document.getElementById('work-search');
if(!table||!input)return;
const filters=document.querySelector('.filters[data-target="ptable"]'),count=document.querySelector('[data-catalog-count]');
const tiles=[...table.querySelectorAll('.el')],original=[...table.childNodes];
let kind='all',view='list';
const views=document.createElement('div');views.className='filters catalog-views';views.setAttribute('role','group');views.setAttribute('aria-label',en?'Catalog view':'作品の表示');
for(const [key,label] of [['list',en?'Chronological list':'発売順の一覧'],['table',en?'Periodic table':'周期表']]){const b=document.createElement('button');b.type='button';b.textContent=label;b.dataset.view=key;b.addEventListener('click',()=>{view=key;apply(true);});views.append(b);}filters.before(views);
function apply(save){
 const query=input.value.trim().normalize('NFKC').toLocaleLowerCase();
 const compact=view==='list'||kind!=='all'||!!query;
 views.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
 table.classList.toggle('is-filtered',compact);
 if(compact)table.replaceChildren(...tiles.slice().sort((a,b)=>Number(a.dataset.order)-Number(b.dataset.order)));
 else{table.replaceChildren(...original);for(const tile of tiles){const stack=tile.__stack;if(stack)stack.append(tile);}}
 let n=0;for(const tile of tiles){tile.hidden=!(kind==='all'||tile.dataset.kind===kind)||!tile.dataset.search.normalize('NFKC').toLocaleLowerCase().includes(query);if(!tile.hidden)n++;}
 filters.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.k===kind)));
 count.textContent=en?`${n} of ${tiles.length} works${n?'':' — try another title, year or format.'}`:`${tiles.length}作品中 ${n}作品${n?'':' — 作品名・年・種類を変えてください。'}`;
 if(save){const url=new URL(location.href);query?url.searchParams.set('q',input.value.trim()):url.searchParams.delete('q');kind!=='all'?url.searchParams.set('format',kind):url.searchParams.delete('format');view==='table'?url.searchParams.set('view',view):url.searchParams.delete('view');history.replaceState(null,'',url);}
}
tiles.forEach(t=>t.__stack=t.parentElement);
filters.addEventListener('click',e=>{const b=e.target.closest('button[data-k]');if(b){kind=b.dataset.k;apply(true);}});
input.addEventListener('input',()=>apply(true));
document.querySelector('[data-catalog-reset]').addEventListener('click',()=>{kind='all';input.value='';apply(true);input.focus();});
function restore(){const u=new URL(location.href);input.value=u.searchParams.get('q')||'';kind=['album','single','ep'].includes(u.searchParams.get('format'))?u.searchParams.get('format'):'all';view=u.searchParams.get('view')==='table'?'table':'list';apply(false);}
window.addEventListener('popstate',restore);window.addEventListener('pageshow',restore);restore();
})();
