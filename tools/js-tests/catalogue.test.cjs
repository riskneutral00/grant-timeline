const test=require('node:test');const assert=require('node:assert/strict');
const {matchesView}=require('../../assets/catalogue.js');
test('default catalogue includes old rounds, planning and far-future dates',()=>{
 const year=new Date().getUTCFullYear();
 for(const e of [{fit:'want',status:'planning',deadline:null},{fit:'want',status:'closed',deadline:`${year-1}-01-01`},{fit:'want',status:'open',deadline:`${year+5}-12-31`},{fit:'want',status:'rolling',deadline:null}])assert.equal(matchesView(e),true);
 assert.equal(matchesView({fit:'skip',status:'open'}),false);
});
test('active intake filter is explicit and does not claim planned rounds are open',()=>{
 assert.equal(matchesView({fit:'want',status:'planning'},'available'),false);
 assert.equal(matchesView({fit:'want',status:'open'},'available'),true);
 assert.equal(matchesView({fit:'want',status:'planning'},'planning'),true);
});
