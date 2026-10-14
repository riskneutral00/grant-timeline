/* Timeline directory: filters only hide rows; the generated date order never changes. */
(() => {
 const rows=[...document.querySelectorAll('.program-row')], groups=[...document.querySelectorAll('.deadline-group')], form=document.querySelector('#filters');
 if(!form)return;
 const search=document.getElementById('search'), solo=document.getElementById('solo'), chips=document.getElementById('chips'), times=[...document.querySelectorAll('[data-time]')];
 const sets=[...new Set([...form.querySelectorAll('fieldset.menu input[type=checkbox]')].map(i=>i.name))];
 const pad=n=>String(n).padStart(2,'0'), now=new Date(), today=`${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`, month=today.slice(0,7);
 const params=new URLSearchParams(location.search), showAll=params.get('view')==='records';
 let time='all';
 const label=input=>input.closest('label').textContent.trim();
 const checked=name=>[...form.querySelectorAll(`input[name="${name}"]:checked`)].map(i=>i.value);
 const isPast=r=>Boolean(r.dataset.deadline)&&r.dataset.deadline<today;

 rows.forEach(r=>{
  const d=r.dataset.deadline, closes=r.querySelector('.closes');
  if(isPast(r)){r.classList.add('is-past');return;}
  if(!d||!closes)return;
  if(r.dataset.precision==='month'){closes.textContent='Closes during '+new Date(d+'T00:00:00').toLocaleString('en',{month:'long',year:'numeric'});return;}
  const days=Math.round((Date.parse(d+'T00:00:00')-Date.parse(today+'T00:00:00'))/864e5);
  closes.textContent=days===0?'Closes today':days===1?'Closes tomorrow':days<14?`Closes in ${days} days`:days<60?`Closes in ${Math.round(days/7)} weeks`:`Closes in ${Math.round(days/30)} months`;
  closes.classList.toggle('urgent',days<=14);
 });
 groups.forEach(g=>{if(/^\d{4}-\d{2}$/.test(g.dataset.month)&&g.dataset.month<month)g.classList.add('is-past');});
 const marker=document.createElement('p');marker.className='today-marker';marker.id='today';marker.textContent='Today';
 const next=groups.find(g=>!/^\d{4}-\d{2}$/.test(g.dataset.month)||g.dataset.month>=month);
 next?next.before(marker):document.getElementById('programs').append(marker);

 function matches(r){
  const ds=r.dataset, terms=search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if(!showAll&&!GrantCatalogue.matchesView(ds,'all'))return false;
  if(solo.checked&&!GrantCatalogue.matchesTeam(ds,'solo'))return false;
  for(const name of sets){const values=checked(name);if(values.length&&!(ds[name]||'').split(' ').some(v=>values.includes(v)))return false;}
  return terms.every(t=>ds.search.toLocaleLowerCase().includes(t));
 }
 function chip(text,remove){const b=document.createElement('button');b.type='button';b.className='chip';b.innerHTML='<span aria-hidden="true">×</span>';b.prepend(text+' ');b.setAttribute('aria-label','Remove filter: '+text);b.addEventListener('click',()=>{remove();update();});return b;}
 function update(save=true){
  const matching=rows.filter(matches), visible=new Set(matching.filter(r=>time==='all'||!isPast(r)));
  rows.forEach(r=>{r.hidden=!visible.has(r);});
  groups.forEach(g=>{const n=[...g.querySelectorAll('.program-row')].filter(r=>visible.has(r)).length;g.hidden=n===0;g.querySelector('.group-count').textContent=n===1?'1 programme':`${n} programmes`;});
  times.forEach(t=>{t.setAttribute('aria-pressed',String(t.dataset.time===time));t.querySelector('.n').textContent=t.dataset.time==='all'?matching.length:matching.filter(r=>!isPast(r)).length;});
  document.getElementById('result-count').textContent=`${visible.size} ${visible.size===1?'programme':'programmes'}`;
  document.getElementById('empty').hidden=visible.size>0;document.querySelector('.column-guide').hidden=visible.size===0;
  form.querySelectorAll('.pill[data-label]').forEach(p=>{const n=form.querySelectorAll(`#${p.getAttribute('aria-controls')} input:checked`).length;p.firstChild.textContent=n?`${p.dataset.label} · ${n}`:p.dataset.label;p.classList.toggle('on',n>0);});
  chips.replaceChildren();
  sets.forEach(name=>form.querySelectorAll(`input[name="${name}"]:checked`).forEach(i=>chips.append(chip(label(i),()=>{i.checked=false;}))));
  if(solo.checked)chips.append(chip('Solo founders OK',()=>{solo.checked=false;}));
  if(search.value.trim())chips.append(chip(`“${search.value.trim()}”`,()=>{search.value='';}));
  if(chips.children.length){const clear=document.createElement('button');clear.type='button';clear.className='link-button';clear.textContent='Clear all';clear.addEventListener('click',reset);chips.append(clear);}
  chips.hidden=!chips.children.length;
  if(save){const p=new URLSearchParams();if(showAll)p.set('view','records');if(search.value.trim())p.set('q',search.value.trim());sets.forEach(n=>{const v=checked(n);if(v.length)p.set(n,v.join(','));});if(solo.checked)p.set('solo','1');if(time!=='all')p.set('time',time);history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);}
 }
 function restore(){
  const p=new URLSearchParams(location.search);search.value=p.get('q')||'';solo.checked=p.get('solo')==='1'||p.get('team')==='solo';time=p.get('time')==='ahead'?'ahead':'all';
  sets.forEach(n=>{const v=(p.get(n)||'').split(',');form.querySelectorAll(`input[name="${n}"]`).forEach(i=>{i.checked=v.includes(i.value);});});
  update(false);
 }
 function reset(){search.value='';solo.checked=false;form.querySelectorAll('input[type=checkbox]').forEach(i=>{i.checked=false;});update();}
 function closeMenus(except){form.querySelectorAll('.pill[aria-controls]').forEach(p=>{if(p===except)return;p.setAttribute('aria-expanded','false');document.getElementById(p.getAttribute('aria-controls')).hidden=true;});}
 form.querySelectorAll('.pill[aria-controls]').forEach(p=>p.addEventListener('click',()=>{const open=p.getAttribute('aria-expanded')!=='true';closeMenus(p);p.setAttribute('aria-expanded',String(open));document.getElementById(p.getAttribute('aria-controls')).hidden=!open;}));
 document.addEventListener('click',e=>{if(!e.target.closest('.menu-wrap'))closeMenus();});
 form.addEventListener('keydown',e=>{if(e.key==='Escape'){const p=e.target.closest('.menu-wrap')?.querySelector('.pill');closeMenus();p?.focus();}});
 document.querySelectorAll('.more').forEach(b=>b.addEventListener('click',()=>{const open=b.getAttribute('aria-expanded')!=='true';b.setAttribute('aria-expanded',String(open));document.getElementById(b.getAttribute('aria-controls')).hidden=!open;}));
 form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('input',()=>update());form.addEventListener('change',()=>update());
 times.forEach(t=>t.addEventListener('click',()=>{time=t.dataset.time;update();}));
 document.getElementById('empty-reset').addEventListener('click',reset);window.addEventListener('popstate',restore);
 form.hidden=false;restore();
})();
