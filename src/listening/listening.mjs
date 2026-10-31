import { session, event as continuityEvent } from './continuity.mjs';
import { admission, chronological, createQueue, move, receive, queueCoverage } from './model.mjs';
import { createApiLoader, createVisiblePlayerAdapter } from './youtube-adapter.mjs';
const host = document.getElementById('listening');
if (host) {
 const ja = document.documentElement.lang === 'ja';
 const t = ja ? {choose:'作品を選ぶ', unknown:'日付未確認', unavailable:'公式音源・録音版の照合待ち', unchecked:'公式配信・曲と版を照合済み／実再生は未確認', ready:'YouTubeの準備ができました。表示中の再生ボタンを押してください。', playing:'YouTubeで再生中です。', paused:'一時停止しています。', buffering:'動画を読み込んでいます。', ended:'曲が終了しました。次の曲はご自身で選べます。', error:'この環境では再生できません。曲は飛ばさず残しています。', empty:'曲目の確認待ちです。', loadError:'音源一覧を読み込めませんでした。作品の記事と既存の埋込は引き続き利用できます。', source:'出所：YouTubeの公式配信', albumSource:'曲目：アーティスト公式サイト', detail:'作品の記事を読む', select:'曲を選んでください。再生は自動で始まりません。', before:'動画はまだ読み込んでいません。', reviewed:'曲で公式音源・版を照合', played:'曲に再生確認記録あり', missing:'未照合の曲は曲順に残しています。', full:'全収録曲を照合済み。再生可否は地域や時期で変わります。', load:'選んだ公式動画を読み込む'} : {choose:'Choose a release',unknown:'exact date unconfirmed',unavailable:'Official source / recording match pending',unchecked:'Official source and recording matched; playback untested',ready:'YouTube is ready. Use its visible play button.',playing:'Playing in YouTube.',paused:'Paused.',buffering:'Buffering.',ended:'Track ended. Choose the next track when ready.',error:'Playback is unavailable here. The track remains in sequence.',empty:'Tracklist not yet confirmed.',loadError:'The listening catalog could not be loaded. Articles and existing embeds remain available.',source:'Source: official distribution on YouTube',albumSource:'Tracklist: official artist site',detail:'Read about this release',select:'Choose a track. Playback never starts automatically.',before:'No video loaded.',reviewed:'tracks with official source / recording matches',played:'tracks with a playback-check record',missing:'Unmatched tracks remain in sequence.',full:'All listed tracks matched; availability may vary by region or time.',load:'Load selected official video'};
 const $ = key => host.querySelector('[data-listening="'+key+'"]');
 const adapter = createVisiblePlayerAdapter({document, origin:location.origin, unavailableText:t.error, loadApi:createApiLoader({window,document,allowNetwork:true})});
 let data, release, edition, queue, continuity = null, pendingAuto = false;
 const ct = ja ? {gap:"次の曲は未照合または再生不可のため、ここで停止しました。曲は飛ばしていません。", end:"この作品の最後の曲が終了しました。", blocked:"連続再生がブラウザに止められました。表示中のYouTube再生ボタンを押してください。"} : {gap:"Stopped at the next unmatched or unavailable track. No track was skipped.",end:"The last track in this release has ended.",blocked:"Your browser blocked continuous playback. Use the visible YouTube play button."};
 const sessionFailures = new Map();
 function dateLabel(d) { if(d.label)return d.label[ja?'ja':'en']; return d.precision === 'day' ? d.value : `${d.year} (${t.unknown})`; }
 function status(text) { $('status').textContent = text; }
 function link(url,label) { const a=document.createElement('a'); a.href=url; a.textContent=label; a.target='_blank'; a.rel='noopener'; return a; }
 function listReleases() {
  const selected=$('release').value; $('release').replaceChildren();
  const first=document.createElement('option');first.value='';first.textContent=t.choose;$('release').append(first);
  for(const r of chronological(data.releases)) {
   if ($('type').value !== 'all' && r.type !== $('type').value) continue;
   const option=document.createElement('option');option.value=r.id;option.textContent=`${dateLabel(r.date)} — ${r.title}`;$('release').append(option);
  }
  if ([...$('release').options].some(o=>o.value===selected)) $('release').value=selected;
 }
 function chooseRelease(id) {
  continuity=null;pendingAuto=false;adapter.dispose(); release=data.releases.find(r=>r.id===id);
  $('tracks').replaceChildren();$('sources').replaceChildren();$('visual').replaceChildren(document.createTextNode(t.before));
  $('previous').disabled=$('next').disabled=$('load').disabled=true;
  if(!release){edition=queue=null;$('heading').textContent=t.choose;$('edition').textContent='';$('coverage').textContent='';status(t.select);return;}
  edition=data.editions[release.editionIds[0]];queue=createQueue(edition);
  $('heading').textContent=release.title;$('edition').textContent=edition.label[ja?'ja':'en'];
  renderQueue();
 }
 function renderQueue(focusIndex = null) {
  continuity=null;pendingAuto=false;
  adapter.dispose();$('visual').replaceChildren(document.createTextNode(t.before));$('tracks').replaceChildren();$('sources').replaceChildren();
  const coverage=queueCoverage(edition,data.recordings,data.videos);
  $('coverage').textContent=`${coverage.allowed}/${coverage.total} ${t.reviewed} · ${coverage.playbackChecked} ${t.played}。 ${coverage.complete?t.full:t.missing}`;
  edition.entries.forEach((entry,index)=>{
   const recording=data.recordings[entry.recordingId], video=data.videos[entry.videoKey], state=admission(video,recording,edition,entry);
   const li=document.createElement('li'),button=document.createElement('button'),small=document.createElement('span');
   button.type='button';button.textContent=`${entry.positionLabel||entry.position}. ${recording.title}`;button.setAttribute('aria-current',String(index===queue.index));
   small.className='listening-meta';small.textContent=sessionFailures.has(entry.id)?t.error:(state.allowed?t.unchecked:t.unavailable);button.append(small);
   button.addEventListener('click',()=>{const keepFocus=document.activeElement===button;queue=move(queue,index-queue.index);renderQueue(keepFocus?index:null);});li.append(button);$('tracks').append(li);
  });
  const entry=edition.entries[queue.index];
  $('previous').disabled=!entry||queue.index<=0;$('next').disabled=!entry||queue.index>=edition.entries.length-1;
  if(!entry){$('load').disabled=true;status(t.empty);return;}
  const video=data.videos[entry.videoKey],recording=data.recordings[entry.recordingId],state=admission(video,recording,edition,entry);
  $('load').disabled=!state.allowed||sessionFailures.has(entry.id);status(`${entry.positionLabel||entry.position}. ${recording.title} — ${sessionFailures.has(entry.id)?t.error:(state.allowed?t.unchecked:t.unavailable)}`);
  if(video) $('sources').append(link(video.officialEvidence.sourceUrl,t.source),document.createTextNode(' · '));
  if(edition.source) $('sources').append(link(edition.source,t.albumSource),document.createTextNode(' · '));
  const detail=document.createElement('a');detail.textContent=t.detail;
  // Actual editorial route is supplied by the catalog, not guessed from a video title.
  detail.href=release.articlePath[ja?'ja':'en'];$('sources').append(detail);
  if(focusIndex!==null)$('tracks').querySelectorAll('button')[focusIndex]?.focus({preventScroll:true});
 }
 $('type').addEventListener('change',()=>{listReleases();chooseRelease($('release').value);});
 $('release').addEventListener('change',()=>chooseRelease($('release').value));
 $('previous').addEventListener('click',()=>{queue=move(queue,-1);renderQueue();});
 $('next').addEventListener('click',()=>{queue=move(queue,1);renderQueue();});
 async function loadSelected(continuePlayback = false) {
  if(!queue)return;const entry=edition.entries[queue.index];$('load').disabled=true;
  pendingAuto=continuePlayback;continuity=session(entry.id,queue.generation,$('continuous').checked);
  const mounted = await adapter.mount({container:$('visual'),video:data.videos[entry.videoKey],recording:data.recordings[entry.recordingId],edition,entry,selectionGeneration:queue.generation,userRequested:true,continuePlayback,onState:event=>{
   if(!queue)return;const next=receive(queue,event);if(next===queue)return;queue=next;
   if(event.type==='playing'||event.type==='autoplay-blocked'||event.type==='error')pendingAuto=false;
   const following=edition.entries[queue.index+1];
   const candidate=following?{entryId:following.id,admitted:!sessionFailures.has(following.id)&&admission(data.videos[following.videoKey],data.recordings[following.recordingId],edition,following).allowed}:null;
   const transition=continuity?continuityEvent(continuity,event,candidate):{state:null,effect:null};continuity=transition.state;
   if(event.type==='error'){
    sessionFailures.set(entry.id,{reason:event.detail||'session-player-error',observedAt:new Date().toISOString()});
    const label=$('tracks').querySelector('button[aria-current=true] .listening-meta');if(label)label.textContent=t.error;
    $('load').disabled=true;
   }
   status(({ready:t.ready,playing:t.playing,paused:t.paused,buffering:t.buffering,ended:t.ended,'autoplay-blocked':ct.blocked})[event.type]||t.error);
   const effect=transition.effect;
   if(effect?.type==='request-visible-next'){queue=move(queue,1);renderQueue();void loadSelected(true);}
   else if(effect?.type==='stop-at-gap'){queue=move(queue,1);renderQueue();status(ct.gap);}
   else if(effect?.type==='release-ended')status(ct.end);
  }});
  // Explicit load should leave the native player visible below the fixed site header.
  if(mounted.mounted)$('visual').scrollIntoView({block:'center',behavior:'auto'});
 }
 $('load').addEventListener('click',()=>loadSelected(false));
 $('continuous').addEventListener('change',()=>{if(pendingAuto&&!$('continuous').checked){renderQueue();return;}if(continuity)continuity={...continuity,optedIn:$('continuous').checked};});
 window.addEventListener('pagehide',()=>{continuity=null;pendingAuto=false;adapter.dispose();});
 window.addEventListener('pageshow',event=>{if(event.persisted&&data&&edition&&queue)renderQueue();});
 try {const response=await fetch(new URL('catalog.json',import.meta.url));if(!response.ok)throw Error();data=await response.json();listReleases();status(t.select);}
 catch {status(t.loadError);}
}
