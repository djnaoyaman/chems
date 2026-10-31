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

export function createVisiblePlayerAdapter({ document, loadApi, origin, unavailableText = 'YouTube unavailable. This track remains selected.' }) {
  let generation = 0, host, frame, blocked = false;
  function dispose() {
    generation++;
    // Detaching the visible iframe terminates that document; no undocumented player commands.
    frame?.remove(); frame = undefined; host = undefined; blocked = false;
  }
  async function mount({ container, video, recording, edition, entry, selectionGeneration, onState, userRequested = false, continuePlayback = false }) {
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
      blocked = true; frame?.remove(); frame = undefined;
      host.replaceChildren(document.createTextNode(unavailableText));
      notify('error', detail);
    };
    try {
      const YT = await loadApi();
      if (token !== generation) return { mounted: false, reason: 'Selection changed' };
      // Re-check mutable inputs after an asynchronous load.
      if (!admission(video, recording, edition, entry).allowed) { fail(); return { mounted:false, reason:'Evidence changed' }; }
      frame = document.createElement('iframe');
      frame.title = `YouTube player: ${recording.title} — ${recording.version}`;
      frame.width = '480'; frame.height = '270';
      if (continuePlayback) frame.allow = 'autoplay';
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      frame.src = `https://www.youtube.com/embed/${encodeURIComponent(video.id)}?enablejsapi=1&origin=${encodeURIComponent(site.origin)}&playsinline=1`;
      const activeFrame = frame;
      host.replaceChildren(frame);
      // No autoplay, mute, branding or controls overrides. Playback uses native visible controls.
      new YT.Player(activeFrame, { events: {
        onReady(event) {
          if (token !== generation || blocked || frame !== activeFrame) return;
          try {
            notify('ready');
            if (continuePlayback) event.target.loadVideoById({ videoId: video.id, startSeconds: 0 });
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
        }
      }});
      return { mounted: !blocked, reason: blocked ? 'Player unavailable' : 'Visible iframe mounted; await native controls' };
    } catch { fail(); return { mounted: false, reason: 'Player unavailable' }; }
  }
  return { mount, dispose };
}
