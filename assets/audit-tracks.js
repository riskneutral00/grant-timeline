"use strict";
document.addEventListener('change',event=>{if(!event.target.matches('.audit-track-filter'))return;const section=event.target.closest('.audit-tracks');section.querySelectorAll('[data-audit-track]').forEach(track=>{track.hidden=event.target.value!=='all'&&track.dataset.defaultExcluded==='true'});});
