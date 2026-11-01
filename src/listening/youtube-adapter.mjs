import { admission } from './model.mjs';

// Documented onError codes; no alternate transport or automatic retry.
export function classifyPlayerError(code) {
  return ({2:'invalid-request',5:'playback-error',100:'unavailable',101:'embedding-disabled',150:'embedding-disabled',153:'client-identity-missing'})[code] || 'player-error';
}

// Network opt-in is deliberately false for this local prototype.
export function createApiLoader({ window, document, allowNetwork = false, timeoutMs = 15000, timers = globalThis }) {
  let pending;
  return () => {
    if (!allowNetwork) return Promise.reject(Error('External API loading disabled'));
    if (window.YT?.Player) return Promise.resolve(window.YT);
    if (pending) return pending;
    pending = new Promise((resolve, reject) => {
      const previous = window.onYouTubeIframeAPIReady;
      let settled = false, timer;
      const script = document.createElement('script');
      const restore = () => { if (window.onYouTubeIframeAPIReady === ready) window.onYouTubeIframeAPIReady = previous; };
      const ready = () => {
        if (settled) return;
        settled = true; timers.clearTimeout(timer);
        restore();
        try { if (typeof previous === 'function') previous(); } catch { /* Preserve our independent readiness. */ }
        if (window.YT?.Player) resolve(window.YT); else reject(Error('YouTube API did not initialize'));
      };
      window.onYouTubeIframeAPIReady = ready;
      script.src = 'https://www.youtube.com/iframe_api';
      script.async = true;
      script.referrerPolicy = 'strict-origin-when-cross-origin';
      const fail = () => {
        if (settled) return;
        settled = true; timers.clearTimeout(timer); restore(); script.remove();
        reject(Error('YouTube API unavailable'));
      };
      script.onerror = fail;
      timer = timers.setTimeout(fail, timeoutMs);
      document.head.append(script);
    }).catch(error => { pending = undefined; throw error; });
    return pending;
  };
}

export function createVisiblePlayerAdapter({ document, loadApi, origin, unavailableText = 'YouTube unavailable. This track remains selected.', timers = globalThis, readyTimeoutMs = 15000 }) {
  let generation = 0, host, frame, player, readyPlayer, blocked = false, readyTimer;
  function dispose() {
    generation++;
    timers.clearTimeout(readyTimer);
    // Detaching the visible iframe terminates that document; no undocumented player commands.
    try { player?.destroy?.(); } catch {}
    frame?.remove(); frame = undefined; player=readyPlayer=undefined; host = undefined; blocked = false;
  }
  async function mount({ container, video, recording, edition, entry, selectionGeneration, onState, userRequested = false, continuePlayback = false, requestPlay = false }) {
    dispose();
    const token = generation;
    const notify = (type, detail) => { if (token === generation) onState({ type, generation: selectionGeneration, entryId: entry.id, ...(detail ? { detail } : {}) }); };
    const status = admission(video, recording, edition, entry);
    if (!userRequested || !status.allowed) return { mounted: false, reason: userRequested ? status.reason : 'Explicit user request required' };
    let site;
    try { site = new URL(origin); if (!['http:','https:'].includes(site.protocol) || site.origin !== origin) throw Error(); }
    catch { return { mounted: false, reason: 'Valid embedding origin required' }; }
    host = container;
    const fail = detail => {
      if (token !== generation || blocked) return;
      timers.clearTimeout(readyTimer);
      blocked = true; try { player?.destroy?.(); } catch {} readyPlayer=undefined; frame?.remove(); frame = undefined;
      host.replaceChildren(document.createTextNode(unavailableText));
      notify('error', detail);
    };
    try {
      const YT = await loadApi();
      if (token !== generation) return { mounted: false, reason: 'Selection changed' };
      // Re-check mutable inputs after an asynchronous load.
      if (!admission(video, recording, edition, entry).allowed) { fail(); return { mounted:false, reason:'Evidence changed' }; }
      // Let the official API create its standard visible iframe and permission attributes.
      frame = document.createElement('div');
      const activeFrame = frame;
      host.replaceChildren(frame);
      readyTimer=timers.setTimeout(()=>fail('player-ready-timeout'),readyTimeoutMs);
      readyTimer?.unref?.();
      player = new YT.Player(activeFrame, { host:'https://www.youtube.com', width:'100%',height:'100%',videoId:video.id,
       playerVars:{origin:site.origin,playsinline:1},events: {
        onReady(event) {
          if (token !== generation || blocked || frame !== activeFrame) return;
          timers.clearTimeout(readyTimer);
          try {
            readyPlayer=event.target;notify('ready');
            if (continuePlayback || requestPlay) event.target.loadVideoById({ videoId: video.id, startSeconds: 0 });
            else event.target.cueVideoById({ videoId: video.id, startSeconds: 0 });
          }
          catch { fail(); }
        },
        onAutoplayBlocked() { if (token === generation && !blocked && frame === activeFrame) notify('autoplay-blocked'); },
        onError(event) { fail(classifyPlayerError(event?.data)); },
        onStateChange(event) {
          if (token !== generation || blocked || frame !== activeFrame) return;
          // Report actual states; the separately opted-in release controller decides advancement.
          if (event.data === 1) notify('playing');
          else if (event.data === 0) notify('ended');
          else if (event.data === 2) notify('paused');
          else if (event.data === 3) notify('buffering');
          else if (event.data === -1) notify('unstarted');
          else if (event.data === 5) notify('cued');
        }
      }});
      return { mounted: !blocked, reason: blocked ? 'Player unavailable' : 'Visible iframe mounted; await native controls' };
    } catch { fail(); return { mounted: false, reason: 'Player unavailable' }; }
  }
  function play(){if(!blocked&&readyPlayer){readyPlayer.playVideo();return true;}return false;}
  function pause(){if(!blocked&&readyPlayer){readyPlayer.pauseVideo();return true;}return false;}
  return { mount, dispose, play, pause };
}
