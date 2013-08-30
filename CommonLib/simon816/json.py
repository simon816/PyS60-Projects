from types import *
ArrayType=(ListType,TupleType)
from os import name
if name=='e32':
 class boolean(object):
  def __init__(self,l):
   if l:self.l='True'
   else:self.l='False'
  def __str__(self):return self.l
 BooleanType=type("bool",(boolean,),{})
true=BooleanType(True)
false=BooleanType(False)

def encode(obj,spaces=1):
 out=''
 sp=' '*spaces
 t=type(obj)
 if t==DictType:
  out+='{'
  for k,v in obj.iteritems():
   out+='"%s":%s%s,%s'%(k,sp,encode(v,spaces),sp)
  if len(out)>1:out=out[:-1-len(sp)]
  out+='}'
 elif t in StringTypes:
  out+='"'
  out+=obj.replace('\\"','"').replace('"','\\"').replace('\n','\\n')
  # out +=repr(obj)[1:-1]
  out+='"'
 elif type(obj)==NoneType:
  out+='null'
 elif t in ArrayType:
  out+='['
  for k in obj:
   out +=encode(k,spaces) + ',' + sp
  if len(out)>1:out=out[:-len(sp)-1]
  out+=']'
 elif t in (IntType,FloatType,BooleanType):
  out+=str(obj).lower()
 return out
   
def decode(json):
 null=None
 return eval(json.replace('\r\n',''))
