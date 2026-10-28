(function(){'use strict';if(window.NaoyamanAnalytics)return;var schemas={creator_site_visit:['target_site'],quiz_start:['quiz_mode'],quiz_answer:[],quiz_timeout:[],quiz_complete:[],quiz_restart:[],encyclopedia_expand:[],reading_mode_select:['reading_mode'],encyclopedia_navigate:['content_group'],walk_filter:['filter_group'],video_open:[],video_seek_request:['position_seconds'],catalog_filter:['filter_group'],music_play:['item_id'],music_pause:['item_id'],music_complete:['item_id'],music_filter:['filter_group'],art_display_open:[],share:['method','content_type']};window.NaoyamanAnalytics={track:function(name,values){try{if(location.hostname!=='djnaoyaman.github.io'||typeof window.gtag!=='function'||!schemas[name])return;var p={send_to:'G-GKZHN40P02',transport_type:'beacon',page_location:location.origin+location.pathname,page_referrer:document.referrer.split(/[?#]/)[0]};schemas[name].forEach(function(k){var v=(values||{})[k];if(typeof v==='number'&&Number.isFinite(v))p[k]=v;else if(typeof v==='string'&&/^[a-zA-Z0-9_-]{1,80}$/.test(v))p[k]=v;});window.gtag('event',name,p);}catch(_){}}};document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-creator-site]');if(a)window.NaoyamanAnalytics.track('creator_site_visit',{target_site:a.dataset.creatorSite});});})();
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
if(!window.__chemsRz){window.__chemsRz=1;var rz;window.addEventListener('resize',function(){clearTimeout(rz);rz=setTimeout(fit,120)})}

/* YouTube：タップで読み込み、秒数リンクで再生点へ */
var premiumHost=document.querySelector('.player[data-yt]');
var premiumHint=premiumHost?window.PremiumPlaybackHint.create({host:premiumHost,key:'chems-premium-hint-v1',english:L==='en',get storage(){return window.sessionStorage;}}):null;
function load(sec){var f=document.querySelector('.facade[data-yt]');var box=document.querySelector('.player');if(!box)return false;
  var id=(f&&f.dataset.yt)||box.dataset.yt;if(!id)return false;
window.NaoyamanAnalytics&&window.NaoyamanAnalytics.track('video_open',{});
  if(premiumHint)premiumHint.show();
  /* ファイルを直接開いた場合は参照元が送れず、YouTubeが再生を拒否する（エラー153）。その時はYouTubeで開く */
  if(!/^https?:$/.test(location.protocol)){window.open('https://www.youtube.com/watch?v='+id+(sec?'&t='+sec+'s':''),'_blank','noopener');return true}
  var ifr=document.createElement('iframe');
  ifr.referrerPolicy='strict-origin-when-cross-origin';ifr.setAttribute('referrerpolicy','strict-origin-when-cross-origin');
  ifr.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&rel=0&playsinline=1&origin='+encodeURIComponent(location.origin)+(sec?'&start='+sec:'');
  ifr.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';ifr.allowFullscreen=true;ifr.title=box.dataset.title||'YouTube';
  window.NaoyamanAnalytics&&window.NaoyamanAnalytics.track('video_seek_request',{position_seconds:sec});
  box.dataset.yt=id;var old=box.querySelector('.facade,iframe');if(old)old.replaceWith(ifr);else box.prepend(ifr);return true}
if(!window.__chemsDoc){window.__chemsDoc=1;document.addEventListener('click',function(e){
  var f=e.target.closest('.facade[data-yt]');if(f){e.preventDefault();load(0);return}
  var t=e.target.closest('a.ts[data-t]');if(t){if(load(parseInt(t.dataset.t,10))){e.preventDefault();document.querySelector('.player').scrollIntoView({behavior:reduce.matches?'auto':'smooth',block:'center'})}}
});}

/* 絞り込み（年表・周期表） */
document.querySelectorAll('.filters').forEach(function(fl){
  var target=document.getElementById(fl.dataset.target);if(!target)return;
  fl.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var k=b.dataset.k;
    window.NaoyamanAnalytics&&window.NaoyamanAnalytics.track('catalog_filter',{filter_group:fl.dataset.target});
    fl.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
    target.querySelectorAll('[data-kind]').forEach(function(li){li.hidden=!(k==='all'||li.dataset.kind===k)});
  });
});
})();

