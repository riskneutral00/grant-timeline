/* No deadline horizon. Only an explicit intake filter narrows the catalogue. */
(function(root){
 function matchesView(event,view='all'){
  if(view==='excluded')return event.fit==='skip';
  if(event.fit!=='want')return false;
  if(view==='available')return ['open','upcoming','rolling'].includes(event.status);
  if(view==='planning'||view==='closed')return ['planning','closed'].includes(event.status);
  return true;
 }
 function matchesTeam(event,filter='under3'){
  const minimum=event.team_min??event.teamMin, known=minimum!==null&&minimum!==undefined&&minimum!=='';
  if(filter==='all')return true;
  if(filter==='solo')return known&&Number(minimum)<=1;
  return !known||Number(minimum)<3;
 }
 const api={matchesView,matchesTeam};
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.GrantCatalogue=api;
})(typeof globalThis==='object'?globalThis:this);
