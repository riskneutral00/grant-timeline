/* Published-snapshot receipt, never private state or a claim of live organizer verification. */
(() => {
 const box=document.getElementById('publication-status'), revision=document.querySelector('meta[name="grant-public-revision"]')?.content;
 if(!box)return;
 fetch('data/publication.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(m=>{
  if(!revision||m.public_revision!==revision){box.textContent='A different snapshot is published. Reload this page before relying on it.';box.dataset.state='stale';return;}
  box.textContent=`Published ${new Date(m.published_at).toLocaleString()} · snapshot ${revision.slice(0,12)}. Record review and eligibility verification are separate.`;
  box.dataset.state='verified';
 }).catch(()=>{box.textContent='Publication receipt unavailable. Freshness is unverified; check the official sources.';box.dataset.state='unknown';});
})();
