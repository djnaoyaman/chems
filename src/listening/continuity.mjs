// Local next-stage state model only. No network, DOM, or production import.
export function session(entryId,generation,optedIn=false){return {entryId,generation,optedIn,played:false,consumed:false,stopped:false};}
export function event(state,e,next){
 if(e.entryId!==state.entryId||e.generation!==state.generation||state.stopped)return {state,effect:null};
 if(e.type==='playing')return {state:{...state,played:true},effect:null};
 if(['error','autoplay-blocked','cancel'].includes(e.type))return {state:{...state,stopped:true},effect:e.type==='autoplay-blocked'?{type:'manual-play-prompt'}:null};
 if(e.type!=='ended'||!state.optedIn||!state.played||state.consumed)return {state,effect:null};
 const ended={...state,consumed:true,stopped:true};
 if(!next)return {state:ended,effect:{type:'release-ended'}};
 if(!next.admitted)return {state:ended,effect:{type:'stop-at-gap',entryId:next.entryId}};
 return {state:ended,effect:{type:'request-visible-next',entryId:next.entryId}};
}
