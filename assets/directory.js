/* Timeline directory: filters only hide rows; the generated date order never changes. */
(() => {
 const rows=[...document.querySelectorAll('.program-row')], groups=[...document.querySelectorAll('.deadline-group')], form=document.querySelector('#filters');
 if(!form)return;
 const search=document.getElementById('search'), solo=document.getElementById('solo'), chips=document.getElementById('chips'), whens=[...document.querySelectorAll('[data-when]')], views=[...document.querySelectorAll('.view')];
 const sets=[...new Set([...form.querySelectorAll('fieldset.menu input[type=checkbox]')].map(i=>i.name))];
 const pad=n=>String(n).padStart(2,'0'), now=new Date(), today=`${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}`;
 const params=new URLSearchParams(location.search), showAll=params.get('view')==='records';
 let when='upcoming';
 const label=input=>input.closest('label').textContent.trim();
 const checked=name=>[...form.querySelectorAll(`input[name="${name}"]:checked`)].map(i=>i.value);
 rows.forEach(r=>{
  const d=r.dataset.deadline, closes=r.querySelector('.closes');
  if(!d||!closes||d<today||r.dataset.precision!=='day'&&r.dataset.precision!=='month')return;
  if(r.dataset.precision==='month'){closes.textContent='Closes during '+new Date(d+'T00:00:00').toLocaleString('en',{month:'long',year:'numeric'});return;}
  const days=Math.round((Date.parse(d+'T00:00:00')-Date.parse(today+'T00:00:00'))/864e5);
  closes.textContent=days===0?'Closes today':days===1?'Closes tomorrow':days<14?`Closes in ${days} days`:days<60?`Closes in ${Math.round(days/7)} weeks`:`Closes in ${Math.round(days/30)} months`;
  closes.classList.toggle('urgent',days<=14);
 });
 const viewOf=r=>r.closest('.view').dataset.view;
 function matches(r){
  const ds=r.dataset, terms=search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if(!showAll&&!GrantCatalogue.matchesView(ds,'all'))return false;
  if(solo.checked&&!GrantCatalogue.matchesTeam(ds,'solo'))return false;
  for(const name of sets){const values=checked(name);if(values.length&&!(ds[name]||'').split(' ').some(v=>values.includes(v)))return false;}
  return terms.every(t=>ds.search.toLocaleLowerCase().includes(t));
 }
 function chip(text,remove){const b=document.createElement('button');b.type='button';b.className='chip';b.innerHTML='<span aria-hidden="true">×</span>';b.prepend(text+' ');b.setAttribute('aria-label','Remove filter: '+text);b.addEventListener('click',()=>{remove();update();});return b;}
 function update(save=true){
  const matching=rows.filter(matches), visible=new Set(matching.filter(r=>viewOf(r)===when));
  views.forEach(v=>{v.hidden=v.dataset.view!==when;});
  rows.forEach(r=>{r.hidden=!visible.has(r);});
  groups.forEach(g=>{const n=[...g.querySelectorAll('.program-row')].filter(r=>visible.has(r)).length;g.hidden=n===0;g.querySelector('.group-count').textContent=n===1?'1 programme':`${n} programmes`;});
  whens.forEach(t=>{t.setAttribute('aria-pressed',String(t.dataset.when===when));t.querySelector('.n').textContent=matching.filter(r=>viewOf(r)===t.dataset.when).length;});
  document.getElementById('result-count').textContent=`${visible.size} ${visible.size===1?'programme':'programmes'}`;
  document.getElementById('empty').hidden=visible.size>0;document.querySelector('.column-guide').hidden=visible.size===0;
  form.querySelectorAll('.pill[data-label]').forEach(p=>{const n=form.querySelectorAll(`#${p.getAttribute('aria-controls')} input:checked`).length;p.firstChild.textContent=n?`${p.dataset.label} · ${n}`:p.dataset.label;p.classList.toggle('on',n>0);});
  chips.replaceChildren();
  sets.forEach(name=>form.querySelectorAll(`input[name="${name}"]:checked`).forEach(i=>chips.append(chip(label(i),()=>{i.checked=false;}))));
  if(solo.checked)chips.append(chip('Solo founders OK',()=>{solo.checked=false;}));
  if(search.value.trim())chips.append(chip(`“${search.value.trim()}”`,()=>{search.value='';}));
  if(chips.children.length){const clear=document.createElement('button');clear.type='button';clear.className='link-button';clear.textContent='Clear all';clear.addEventListener('click',reset);chips.append(clear);}
  chips.hidden=!chips.children.length;
  if(save){const p=new URLSearchParams();if(showAll)p.set('view','records');if(search.value.trim())p.set('q',search.value.trim());sets.forEach(n=>{const v=checked(n);if(v.length)p.set(n,v.join(','));});if(solo.checked)p.set('solo','1');if(when!=='upcoming')p.set('when',when);history.replaceState(null,'',location.pathname+(p.size?'?'+p:'')+location.hash);}
 }
 function restore(){
  const p=new URLSearchParams(location.search);search.value=p.get('q')||'';solo.checked=p.get('solo')==='1'||p.get('team')==='solo';when=['past','nodate'].includes(p.get('when'))?p.get('when'):'upcoming';
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
 whens.forEach(t=>t.addEventListener('click',()=>{when=t.dataset.when;update();window.scrollTo({top:document.querySelector('.controls').offsetTop});}));
 document.getElementById('empty-reset').addEventListener('click',reset);window.addEventListener('popstate',restore);
 form.hidden=false;restore();
})();
