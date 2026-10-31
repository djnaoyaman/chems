const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..'),dist=path.join(root,'dist');
(async()=>{
 const {admission,queueCoverage}=await import('../src/listening/model.mjs');
 const data=JSON.parse(fs.readFileSync(path.join(dist,'listening/catalog.json')));
 assert.equal(data.releases[0].date.precision,'early');assert.equal(data.releases[1].date.precision,'late');
 assert.equal(data.editions['fcs-unresolved-edition'].entries[0].positionLabel,'A1');
 assert.equal(data.releases.length,57);assert.equal(Object.values(data.editions).reduce((n,e)=>n+e.entries.length,0),225);
 let allowed=0,checked=0;for(const e of Object.values(data.editions)){const c=queueCoverage(e,data.recordings,data.videos);allowed+=c.allowed;checked+=c.playbackChecked;}
 assert.equal(allowed,7);assert.equal(checked,0);
 const e=data.editions['epd-official-site-sequence'],entry=e.entries[1],v=data.videos[entry.videoKey];
 for(const [position,title,id] of [[2,'In Dust We Trust','YtnBsvu72kY'],[3,'Song To The Siren (Live From Sabresonic Nightclub, United Kingdom/1994)','D7R4Z0T5ViA'],[4,'Three Little Birdies Down Beats','kJqSFi0ukEY'],[7,"Chico’s Groove".replace('’',"'"),'F8smPDj7r4w'],[8,'One Too Many Mornings','wA-FVMPg49I'],[9,'Life Is Sweet','cpTTNGzTKRo'],[11,'Alive Alone','q9rrZzrgA2I']]){const item=e.entries[position-1];assert.equal(data.recordings[item.recordingId].title,title);assert.equal(data.videos[item.videoKey].id,id);}
 assert.equal(e.entries.length,11);assert.equal(v.id,'YtnBsvu72kY');assert.equal(v.officialEvidence.providerName,'Universal Music Group');assert.equal(v.availability.state,'unchecked');assert.equal(v.channelId,undefined);
 assert(admission(v,data.recordings[entry.recordingId],e,entry).allowed);
 assert(!JSON.stringify(data).includes('6iiGQmWCCyI'));assert(!JSON.stringify(data.videos).includes('4QKi8DorEpM'));
 for(const lang of ['','en/']){
  const h=fs.readFileSync(path.join(dist,lang,'works/index.html'),'utf8');assert(h.includes('id="listening"'));assert(h.includes('type="module"'));assert(h.includes('14:39:00+00:00'));
  const work=fs.readFileSync(path.join(dist,lang,'works/exit-planet-dust/index.html'),'utf8');assert(!work.includes('listening/listening.mjs'));assert(work.includes('30p2UWAegeQ'));
 }
 const protectedFiles=JSON.parse(fs.readFileSync(path.join(root,'tests/listening-protected.json')));
 for(const [file,hash] of Object.entries(protectedFiles)){assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,file))).digest('hex'),hash,file);}
 const app=fs.readFileSync(path.join(root,'src/listening/listening.mjs'),'utf8');assert(!app.includes('localStorage'));assert(!app.includes('video.availability='));assert(app.includes('sessionFailures.set'));assert(app.includes("'pageshow'"));assert(app.includes('preventScroll:true'));
 console.log(JSON.stringify({pass:true,releases:57,trackOccurrences:225,officialMatched:allowed,playbackChecked:0,protectedFiles:Object.keys(protectedFiles).length}));
})().catch(e=>{console.error(e);process.exit(1)});
