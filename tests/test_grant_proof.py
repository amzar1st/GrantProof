import sys, pathlib, unittest, json, types
sys.path.insert(0,str(pathlib.Path(__file__).parent))
import fake_genlayer as fake
sys.modules['genlayer']=fake
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'contracts'))
from grant_proof import GrantProof, validate_decision, evidence_url
F='0x'+'1'*40; B='0x'+'2'*40; O='0x'+'3'*40
class GrantTests(unittest.TestCase):
 def setUp(self):
  self.now=1000
  fake.gl.message.sender_address=fake.Address(F);fake.gl.message.value=0
  fake.VM.next_decision=None; fake.Web.responses={};fake.transfers.clear()
  self.c=GrantProof(60,60,120,600);self.c.grants={};self.c.ids=[];self.c.credits={};self.c._now=lambda:self.now
  self.terms=[{'title':'Public beta','amount_wei':'101','due_at':1500,'criteria':[{'text':'Public app','weight_bps':6000},{'text':'Docs','weight_bps':4000}]}]
  self.c.create_grant('g','Grant',B,json.dumps(self.terms),'["example.org"]',1100)
 def sender(self,a):fake.gl.message.sender_address=fake.Address(a)
 def state(self):return json.loads(self.c.get_grant('g'))
 def fund(self):fake.gl.message.value=101;self.c.fund_grant('g')
 def accept(self):self.fund();self.sender(B);self.c.accept_grant('g')
 def evidence(self):
  self.accept();self.c.submit_milestone('g','Delivered');self.c.submit_evidence('g','https://example.org/beta','','Public beta')
 def decision(self,v='MILESTONE_COMPLETED',done=None):
  return {'verdict':v,'completed':done if done is not None else [0,1],'citations':['https://example.org/beta'] if v in ('MILESTONE_COMPLETED','PARTIALLY_COMPLETED') else [],'reason':'Independent evidence review','checks':[{'url':'https://example.org/beta','side':'builder','status':'OK'}]}
 def review(self,v='MILESTONE_COMPLETED',done=None):
  self.evidence();self.now=1060;fake.VM.next_decision=self.decision(v,done);self.c.validator_review('g')
 def invariant(self):self.assertEqual(int(self.c.total_escrow)+int(self.c.total_credits)+sum(x[1] for x in fake.transfers),101)
 def test_full_payment_and_no_double_withdrawal(self):
  self.review();self.now=1120;self.c.finalize('g');self.assertEqual(self.state()['status'],'COMPLETED');self.assertEqual(self.c.get_credit(B),'101');self.c.withdraw();self.invariant()
  with self.assertRaises(fake.UserError):self.c.withdraw()
 def test_partial_weight_and_rounding(self):
  self.review('PARTIALLY_COMPLETED',[0]);self.now=1120;self.c.finalize('g');self.assertEqual(self.c.get_credit(B),'60');self.assertEqual(self.c.get_credit(F),'41');self.invariant()
 def test_early_review_rejected(self):
  self.evidence()
  with self.assertRaises(fake.UserError):self.c.validator_review('g')
 def test_early_finalize_rejected(self):
  self.review()
  with self.assertRaises(fake.UserError):self.c.finalize('g')
 def test_nonparty_submission_rejected(self):
  self.accept();self.sender(O)
  with self.assertRaises(fake.UserError):self.c.submit_milestone('g','hack')
 def test_wrong_funding_rejected(self):
  fake.gl.message.value=100
  with self.assertRaises(fake.UserError):self.c.fund_grant('g')
 def test_wrong_builder_rejected(self):
  self.fund();self.sender(O)
  with self.assertRaises(fake.UserError):self.c.accept_grant('g')
 def test_unaccepted_timeout(self):
  self.fund();self.now=1100;self.sender(O);self.c.resolve_timeout('g');self.assertEqual(self.c.get_credit(F),'101');self.invariant()
 def test_missing_submission_timeout(self):
  self.accept();self.now=1500;self.c.resolve_timeout('g');self.assertEqual(self.state()['status'],'REFUNDED');self.invariant()
 def test_revision_deadline(self):
  self.review('REVISION_REQUIRED',[]);self.now=1120;self.c.finalize('g');self.assertEqual(self.state()['status'],'REVISION')
  with self.assertRaises(fake.UserError):self.c.resolve_timeout('g')
  self.now=1240;self.c.resolve_timeout('g');self.assertEqual(self.c.get_credit(F),'101');self.invariant()
 def test_one_revision_only(self):
  self.review('INSUFFICIENT_EVIDENCE',[]);self.now=1120;self.c.finalize('g');self.c.submit_milestone('g','Repair');self.now=1180;fake.VM.next_decision=self.decision('INSUFFICIENT_EVIDENCE',[]);self.c.validator_review('g');self.now=1240;self.c.finalize('g');self.assertEqual(self.state()['status'],'REFUNDED');self.invariant()
 def test_failed_refunds_entire_grant(self):
  self.review('MILESTONE_FAILED',[]);self.now=1120;self.c.finalize('g');self.assertEqual(self.c.get_credit(F),'101');self.invariant()
 def test_stalled_review_absolute_timeout(self):
  self.evidence();self.now=2100;self.c.resolve_timeout('g');self.assertEqual(self.c.get_credit(F),'101');self.invariant()
 def test_timeout_cannot_erase_valid_pending_result(self):
  self.review();self.now=1500
  with self.assertRaises(fake.UserError):self.c.resolve_timeout('g')
 def test_reserved_capacity(self):
  self.evidence()
  for i in range(3):self.c.submit_evidence('g',f'https://example.org/{i}','','')
  with self.assertRaises(fake.UserError):self.c.submit_evidence('g','https://example.org/overflow','','')
  self.sender(F)
  for i in range(4):self.c.submit_evidence('g',f'https://example.org/f{i}','','')
  self.assertEqual(len(self.state()['evidence']),8)
 def test_challenge_reopens_review_once(self):
  self.review();self.sender(F);self.c.challenge('g','https://example.org/counter','','Counterproof');self.now=1120;fake.VM.next_decision=self.decision('MILESTONE_FAILED',[]);self.c.validator_review('g')
  with self.assertRaises(fake.UserError):self.c.challenge('g','https://example.org/counter','','Again')
  self.now=1180;self.c.finalize('g');self.invariant()
 def test_late_challenge_rejected(self):
  self.review();self.now=1120
  with self.assertRaises(fake.UserError):self.c.challenge('g','https://example.org/counter','','Late')
 def test_bad_hosts(self):
  for u in ['http://example.org/a','https://example.org.evil.com/a','https://example.org@evil.com/a','https://example.org:8080/a','https://example.org/a#f']:
   with self.assertRaises(fake.UserError):evidence_url(u,['example.org'])
 def test_citation_must_be_fetched(self):
  d=self.decision();d['citations']=['https://evil.com']
  with self.assertRaises(fake.UserError):validate_decision(d,self.terms[0]['criteria'],['https://example.org/beta'])
 def test_completion_must_cover_every_criterion(self):
  with self.assertRaises(fake.UserError):validate_decision(self.decision(done=[0]),self.terms[0]['criteria'],['https://example.org/beta'])
 def test_unknown_and_duplicate_criteria(self):
  for done in [[0,2],[0,0]]:
   with self.assertRaises(fake.UserError):validate_decision(self.decision(done=done),self.terms[0]['criteria'],['https://example.org/beta'])
 def test_fetch_failure_no_builder_payment(self):
  self.evidence();self.now=1060;self.c.validator_review('g');self.assertEqual(self.state()['decision']['verdict'],'INSUFFICIENT_EVIDENCE');self.assertEqual(self.c.get_credit(B),'0')
 def test_hash_mismatch_no_builder_payment(self):
  self.accept();self.c.submit_milestone('g','Delivered');self.c.submit_evidence('g','https://example.org/beta','0'*64,'Mismatch');fake.Web.responses['https://example.org/beta']=types.SimpleNamespace(body=b'real bytes',status_code=200);self.now=1060;self.c.validator_review('g');self.assertEqual(self.state()['decision']['checks'][0]['status'],'HASH_MISMATCH');self.assertEqual(self.c.get_credit(B),'0')
 def test_funder_fetch_failure_does_not_veto_builder(self):
  self.evidence();self.sender(F);self.c.submit_evidence('g','https://example.org/fail','','');fake.Web.responses['https://example.org/beta']=types.SimpleNamespace(body=b'working beta and documentation',status_code=200);fake.Nondet.output=self.decision();self.now=1060;self.c.validator_review('g');self.now=1120;self.c.finalize('g');self.assertEqual(self.c.get_credit(B),'101');self.invariant()
 def test_invalid_weights_rejected(self):
  self.terms[0]['criteria'][0]['weight_bps']=5000
  with self.assertRaises(fake.UserError):self.c.create_grant('bad','Title',B,json.dumps(self.terms),'["example.org"]',1100)
 def test_cancel_only_draft(self):
  self.c.cancel_grant('g');self.assertEqual(self.state()['status'],'CANCELLED')
 def test_two_milestones_conserve_funds(self):
  self.terms.append(dict(self.terms[0],title='Second',due_at=2000,amount_wei='99'))
  self.c.create_grant('multi','Two',B,json.dumps(self.terms),'["example.org"]',1100);fake.gl.message.value=200;self.c.fund_grant('multi');self.sender(B);self.c.accept_grant('multi')
  for at in [1000,1200]:
   self.now=at;self.c.submit_milestone('multi','Done');self.now+=60;fake.VM.next_decision=self.decision();self.c.validator_review('multi');self.now+=60;self.c.finalize('multi')
  self.assertEqual(self.c.get_credit(B),'200');self.assertEqual(self.c.total_escrow,0)
if __name__=='__main__':unittest.main()
