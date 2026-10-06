/* No deadline horizon. Only an explicit intake filter narrows the catalogue. */
(function(root){
 function matchesView(event,view='all'){
  if(view==='excluded')return event.fit==='skip';
  if(event.fit!=='want')return false;
  if(view==='available')return ['open','upcoming','rolling'].includes(event.status);
  if(view==='planning'||view==='closed')return ['planning','closed'].includes(event.status);
  return true;
 }
 const api={matchesView};
 if(typeof module==='object'&&module.exports)module.exports=api;
 else root.GrantCatalogue=api;
})(typeof globalThis==='object'?globalThis:this);
