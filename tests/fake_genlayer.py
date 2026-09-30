import types
class Address:
 def __init__(self,s):
  if not isinstance(s,str) or len(s)!=42 or not s.startswith('0x'): raise ValueError('address')
  int(s[2:],16); self.as_hex=s
class Generic:
 def __class_getitem__(cls,x): return cls
class UserError(Exception): pass
class Write:
 def __call__(self,f): return f
 payable=property(lambda s:s)
class Recipient:
 def __init__(self,address): self.address=address
 def emit_transfer(self,**kw): transfers.append((self.address.as_hex,kw['value']))
def interface(cls): return Recipient
transfers=[]
class Return:
 def __init__(self,data): self.calldata=data
class VM:
 UserError=UserError
 Return=Return
 next_decision=None
 @staticmethod
 def run_nondet_unsafe(leader,validator):
  if VM.next_decision is not None: return VM.next_decision
  r=leader()
  if not validator(Return(r)): raise UserError('Consensus disagreement')
  return r
class Web:
 responses={}
 @staticmethod
 def get(url):
  r=Web.responses.get(url)
  if isinstance(r,Exception) or r is None: raise RuntimeError('fetch failure')
  return r
class Nondet:
 web=Web
 output={}
 @staticmethod
 def exec_prompt(*a,**kw): return Nondet.output
class GL:
 Contract=object
 public=types.SimpleNamespace(write=Write(),view=lambda f:f)
 message=types.SimpleNamespace(sender_address=Address('0x'+'1'*40),value=0)
 evm=types.SimpleNamespace(contract_interface=interface)
 vm=VM
 nondet=Nondet
gl=GL()
u256=int
TreeMap=DynArray=Generic
