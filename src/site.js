(function(){
var reduce=window.matchMedia('(prefers-reduced-motion: reduce)');
var L=document.documentElement.lang==='en'?'en':'ja';
var T={ja:{stop:'動きを止める',go:'動かす',os:'OSの設定で停止中'},en:{stop:'Stop motion',go:'Start motion',os:'Stopped by your system setting'}}[L];

/* 2色刷りの版 */
document.querySelectorAll('.print').forEach(function(el){
  if(el.querySelector('.plate'))return;
  var s=document.createElement('span');s.className='plate';s.setAttribute('aria-hidden','true');s.textContent=el.textContent;el.appendChild(s);
});

/* 動きの停止 */
var still=false;
function bind(){document.querySelectorAll('button.motion').forEach(function(b){
  if(reduce.matches){b.textContent=T.os;b.disabled=true;return}
  b.textContent=still?T.go:T.stop;b.setAttribute('aria-pressed',still?'true':'false');
  b.onclick=function(){still=!still;document.body.classList.toggle('still',still);bind()};
})}
bind();

/* 作品名の自動縮小（1語が枠に収まらない場合だけ） */
function fit(){var t=document.querySelector('.wtitle');if(!t)return;var pl=t.querySelector('.plate');if(pl)pl.style.display='none';t.style.fontSize='';
  var fs=parseFloat(getComputedStyle(t).fontSize),n=0;while(t.scrollWidth>t.clientWidth+1&&fs>24&&n<40){fs*=.95;t.style.fontSize=fs+'px';n++}if(pl)pl.style.display=''}
fit();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fit);
var rz;window.addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(fit,120)});

/* YouTube：タップで読み込み、秒数リンクで再生点へ */
function load(sec){var f=document.querySelector('.facade[data-yt]');var box=document.querySelector('.player');if(!box)return false;
  var id=(f&&f.dataset.yt)||box.dataset.yt;if(!id)return false;
  var ifr=document.createElement('iframe');
  ifr.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&rel=0'+(sec?'&start='+sec:'');
  ifr.allow='autoplay; encrypted-media; picture-in-picture';ifr.allowFullscreen=true;ifr.title=box.dataset.title||'YouTube';
  box.dataset.yt=id;var old=box.querySelector('.facade,iframe');if(old)old.replaceWith(ifr);else box.prepend(ifr);return true}
document.addEventListener('click',function(e){
  var f=e.target.closest('.facade[data-yt]');if(f){e.preventDefault();load(0);return}
  var t=e.target.closest('a.ts[data-t]');if(t){if(load(parseInt(t.dataset.t,10))){e.preventDefault();document.querySelector('.player').scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'center'})}}
});

/* 絞り込み（年表・周期表） */
document.querySelectorAll('.filters').forEach(function(fl){
  var target=document.getElementById(fl.dataset.target);if(!target)return;
  fl.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var k=b.dataset.k;
    fl.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
    target.querySelectorAll('[data-kind]').forEach(function(li){li.hidden=!(k==='all'||li.dataset.kind===k)});
  });
});
})();
