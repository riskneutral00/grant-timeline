/* Visibility changes preserve the generated deadline order. */
(() => {
 const rows=[...document.querySelectorAll('.program-row')], groups=[...document.querySelectorAll('.deadline-group')], form=document.querySelector('#filters'), tabs=[...document.querySelectorAll('[data-view]')], controls=['search','country','type','team','funding','fees'].map(id=>document.getElementById(id));
 let view='all';
 const matchesView=(r,v)=>GrantCatalogue.matchesView(r.dataset,v);
 function update(save=true){
  const [search,country,type,team,funding,fees]=controls.map(c=>c.value), terms=search.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  const matching=rows.filter(r=>(!country||r.dataset.country===country)&&(!type||r.dataset.type===type)&&(!team||r.dataset.solo==='true')&&(!funding||r.dataset.funding===funding)&&(!fees||r.dataset.fees===fees)&&terms.every(t=>r.dataset.search.toLocaleLowerCase().includes(t))), visible=new Set(matching.filter(r=>matchesView(r,view)));
  rows.forEach(r=>r.hidden=!visible.has(r));
  groups.forEach(g=>{const n=[...g.querySelectorAll('.program-row')].filter(r=>visible.has(r)).length;g.hidden=n===0;g.querySelector('.group-count').textContent=`(${n})`;});
  tabs.forEach(t=>{t.setAttribute('aria-pressed',String(t.dataset.view===view));t.querySelector('span').textContent=matching.filter(r=>matchesView(r,t.dataset.view)).length;});
  document.querySelector('#empty').hidden=visible.size>0;document.querySelector('.column-guide').hidden=visible.size===0;
  document.querySelector('#result-count').textContent=`${visible.size} ${visible.size===1?'program':'programs'} · ${tabs.find(t=>t.dataset.view===view).firstChild.textContent.trim()}`;
  if(save){const p=new URLSearchParams();if(view!=='all')p.set('view',view);controls.forEach(c=>{if(c.value)p.set(c.name,c.value);});history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);}
 }
 function restore(){const p=new URLSearchParams(location.search);view=tabs.some(t=>t.dataset.view===p.get('view'))?p.get('view'):'all';controls.forEach(c=>c.value=p.get(c.name)||'');update(false);}
 function reset(){controls.forEach(c=>c.value='');view='all';update();}
 form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('input',()=>update());form.addEventListener('change',()=>update());tabs.forEach(t=>t.addEventListener('click',()=>{view=t.dataset.view;update();}));document.querySelector('#reset').addEventListener('click',reset);document.querySelector('#empty-reset').addEventListener('click',reset);window.addEventListener('popstate',restore);form.hidden=false;document.querySelector('.list-toolbar').hidden=false;restore();
})();
