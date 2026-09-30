import {createClient,createAccount} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionStatus,TransactionHashVariant} from 'genlayer-js/types';
import fs from 'node:fs/promises';
const config=JSON.parse(await fs.readFile('public/deployment.json','utf8'));
const address=config.address;
const c=createClient({chain:studionet});
const funder='0xE7Aa7B783f27081cc3aAe3Fa8d9Fc3112048D4E6';
let record;
try {record=JSON.parse(await fs.readFile('docs/live-demo.json','utf8'));} catch {record={grantId:'grantproof-live-'+Date.now(),funder,builder:createAccount().address,transactions:[],network:config.network,contract:address};}
await fs.writeFile('docs/live-demo.json',JSON.stringify(record,null,2));
const step=process.argv[2];
const read=async n=>c.readContract({address,functionName:n,args:n==='get_grant'?[record.grantId]:[],transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
const state=async()=>JSON.parse(await read('get_grant'));
const brief=r=>({hash:r.hash,status:r.statusName||r.status,execution:r.txExecutionResultName||r.consensus_data?.leader_receipt?.[0]?.execution_result,result:r.resultName||r.result});
const success=r=>r.txExecutionResultName==='FINISHED_WITH_RETURN'||r.consensus_data?.leader_receipt?.[0]?.execution_result==='SUCCESS';
async function tx(name,args,who=funder,value=0n){
 const hash=await c.writeContract({account:{address:who,type:'json-rpc'},address,functionName:name,args,value});
 record.transactions.push({method:name,hash,account:who,value:value.toString(),status:'SUBMITTED'});await fs.writeFile('docs/live-demo.json',JSON.stringify(record,null,2));
 console.log('submitted',name,hash);
 const receipt=await c.waitForTransactionReceipt({hash,status:TransactionStatus.FINALIZED,retries:200,interval:3000});
 const summary=brief(receipt);Object.assign(record.transactions.at(-1),summary);await fs.writeFile('docs/live-demo.json',JSON.stringify(record,null,2));
 console.log('finalized',name,JSON.stringify(summary));
 if(!success(receipt)) {await fs.writeFile('/tmp/grantproof-failed.json',JSON.stringify(receipt,(_,v)=>typeof v==='bigint'?v.toString():v,null,2));throw Error('Execution failed; inspect /tmp/grantproof-failed.json');}
 return receipt;
}
if(step==='start'){
 await c.request({method:'sim_fundAccount',params:[record.builder,10000000000000000000]});
 const now=Math.floor(Date.now()/1000);
 record.milestones=[{title:'Publish the GrantProof funding guide',amount_wei:'10000000000000000',due_at:now+14400,criteria:[{text:'Publish a public Markdown documentation page in amzar1st/GrantProof that explicitly lists all five GrantProof verdict names.',weight_bps:5000},{text:'That same page explains immutable weighted escrow payout and the resolve_timeout deadline refund action.',weight_bps:5000}]}];
 await tx('create_grant',[record.grantId,'GrantProof public documentation proof',record.builder,JSON.stringify(record.milestones),'["raw.githubusercontent.com","github.com"]',now+7200]);
 await tx('fund_grant',[record.grantId],funder,10000000000000000n);
 await tx('accept_grant',[record.grantId],record.builder);
 await tx('submit_milestone',[record.grantId,'Published the public documentation guide. Only the documentation criteria are claimed, not a production beta or user count.'],record.builder);
 await tx('submit_evidence',[record.grantId,'https://raw.githubusercontent.com/amzar1st/GrantProof/main/docs/demo-deliverable.md','','Public repository documentation guide'],record.builder);
 record.state=await state();await fs.writeFile('docs/live-demo.json',JSON.stringify(record,null,2));console.log('responseDeadline',record.state.response_deadline);
}else if(step==='review'){
 await tx('validator_review',[record.grantId]);record.state=await state();await fs.writeFile('docs/live-demo.json',JSON.stringify(record,null,2));console.log(JSON.stringify(record.state.decision));
}else if(step==='finalize'){
 await tx('finalize',[record.grantId]);record.state=await state();record.builderCredit=await c.readContract({address,functionName:'get_credit',args:[record.builder],transactionHashVariant:TransactionHashVariant.LATEST_FINAL});
 await tx('withdraw',[],record.builder);record.builderBalance=String(await c.getBalance({address:record.builder}));record.accounting=JSON.parse(await read('get_accounting'));
 await fs.writeFile('docs/live-demo.json',JSON.stringify(record,null,2));console.log('settlement',record.state.status,record.builderCredit,record.builderBalance,record.accounting);
}else if(step==='read'){console.log(JSON.stringify(await state()));}
