import re
class jsparser:
 def __init__(self):
  self.fn=re.compile('(.+\s*)\((.*)\)')
  # parses function calls, group 1 is function, group 2 is function arguments. 
  self.f_if=re.compile('[if\(\s+\)]')
  self.eq=re.compile('.+\s*=')
  #matches atleast 1 character with = * amount of spaces infront and no spaces behind
  self.terminator=re.compile('(?!["\'])(\n|;|$|\})')#(?!.*["\'])
  # finds the end of a syntax line, either \n or ; or end of string
  # ignores any character in quotes ("or ')
  # group 1 contains what terminated the line
  self.raw="";self.o=''
  self.all_parsers=['if','eq']
  self.quote=re.compile('([\',"])')
  self.obj=re.compile('\{(.*)\}')
 def feed(self,raw):
  self.raw+=raw
  self.parse()
 def parse(self):
  raw=self.raw
  i=0
  n=len(raw)
  while i<n:
   t=self.terminator.search(raw,i)
   nt=t.start()
   q=self.quote.search(raw[i:nt])
   if q:
    if raw[i+q.end():nt].find(q.group())==-1:
     nt+=raw[i+q.end():].find(q.group())
   tc=t.group()
   #print 'current index',i,'next terminator',nt,raw[i:nt]
   o=self.obj.search(raw[i:nt+1])
   if o:
    i=nt
    print o
    tc=None
   m=self.eq.search(raw[i:nt])
   if m:
    j=m.start()+i
    i=self.parse_eq(i,nt)+len(tc)
   else:
    fn=self.fn.search(raw[i:nt])
    if fn:
     self.handle_fn(fn.groups())
    else:self.handle_data(raw[i:nt])
    i=t.end()
   if tc:self.handle_data(tc)
 def parse_eq(self,i,t):
  to_search=self.raw[t:]
  eq_string=self.raw[i:t]
  kv=eq_string.split("=")
  self.handle_eq(kv)
  return i+len(eq_string)
 def handle_eq(self,l):
  print 'eq:','='.join(l)
 def handle_data(self,data):
  print 'data:',data
 def handle_fn(self,f):
  print 'fn:',f

j=jsparser() 
j.feed("function x(y){alert('hello');window.y=y}g='h'\nwindow.onload=x()")