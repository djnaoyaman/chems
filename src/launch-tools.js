(function(){'use strict';
var root=document.querySelector('.reading-tools');if(!root)return;
var en=document.documentElement.lang==='en',share=root.querySelector('[data-share]'),copy=root.querySelector('[data-copy]'),status=root.querySelector('[role="status"]'),manual=root.querySelector('.manual-copy'),field=manual.querySelector('input');
var canonical=document.querySelector('link[rel="canonical"]'),url=canonical?canonical.href:location.href.split('#')[0];field.value=url;
function say(text){status.textContent=text;}
function fallback(){manual.hidden=false;field.focus();field.select();say(en?'Copy the selected address using your device’s copy command.':'選択されたURLを、お使いの端末のコピー操作でコピーしてください。');}
async function copyLink(){try{if(!navigator.clipboard||!navigator.clipboard.writeText)throw Error('unavailable');await navigator.clipboard.writeText(url);manual.hidden=true;say(en?'Link copied.':'リンクをコピーしました。');}catch(_){fallback();}}
copy.addEventListener('click',copyLink);
share.addEventListener('click',async function(){if(!navigator.share){await copyLink();return;}share.disabled=true;try{await navigator.share({title:document.title,url:url});say(en?'Share sheet closed.':'共有画面を閉じました。');}catch(error){if(error&&error.name==='AbortError'){say(en?'Sharing cancelled.':'共有をキャンセルしました。');}else{await copyLink();}}finally{share.disabled=false;}});
})();
