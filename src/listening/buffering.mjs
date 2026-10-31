// One informational notice per uninterrupted buffering episode. Never retries playback.
export function createBufferingNotice({schedule=setTimeout,cancel=clearTimeout,delay=15000,onSlow}) {
 let timer=null, key=null, slow=false, revision=0;
 function clear(){revision++;if(timer!==null)cancel(timer);timer=null;key=null;slow=false;}
 function event(e){
  const next=JSON.stringify([e.entryId,e.generation]);
  if(e.type!=='buffering'){clear();return false;}
  if(key===next)return slow;
  clear();key=next;const token=revision;
  timer=schedule(()=>{if(token!==revision||key!==next)return;timer=null;slow=true;onSlow(e);},delay);
  return false;
 }
 return {event,clear};
}
