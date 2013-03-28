
class util:
 def mkdir(self,list):
  for dir in list:
   if not os.path.exists(dir):os.makedirs(dir);return 1
   else:return 0;
 class db:
  home='e:\\python\\apps\\simon816\\ftpbrowser\\'
  def __init__(self,mode=None):
   try:f=open(self.home+'db.dir', 'r+');self.dir=f.read()
   except:f=open(self.home+'db.dir', 'w');f.write(self.home);self.dir=self.home
   f.close()
   if not self.dir.endswith('\\'):self.dir+='\\'
   if mode:self.open(mode)
  def open(self,mode):
   self.openDB=e32dbm.open(self.dir+'db',mode)
   return self
  def items(self):
   return self.openDB.items()
  def sync(self):
   return self.openDB.sync()
  def close(self):
   return self.openDB.close()
  def mod(self, key, value):
   s=''
   if type(value)==tuple:
    for v in value:
     try:v=int(v);v=str(v)+'\x01'
     except:
      if u(v)==v:v='\x01'+v
      else:v=str(v)
     s+=v+'\x00'
    s=s[:len(s)-1]
   elif type(value)==list:
    for v in value:s+=str(v)+'\x01'
   else:s=value
   self.openDB[str(key)]=str(s)
  def get(self, key, mode='str'):
   try:
    v=self.openDB[str(key)]
    if mode=='str':return v
    elif mode=='int':return int(float(v))
    elif mode=='tuple':
                                  t=v.split('\x00');i=0
                                  for c in t:
                                   if c[len(c)-1:]=='\x01':
                                    t[i]=int(float(c[:len(c)-1]))
                                   if c[:1]=='\x01':
                                    t[i]=u(c[1:])
                                   i=i+1
                                  return tuple(t)
    elif mode=='list':return list(v.split('\x01'))
   except:raise
  def delete(self,key):
   del self.openDB[key]


def encode(s,n,al,o='',w=''):
 a=al
 for x in range(len(s)):
  n=n+1;c=s[x:x+1]
  if a.find(c)>=0 or w=='a':al+=a;o+=al[al.find(c)+n:al.find(c)+1+n]
  else:
   try:
    if int(c) in range(0,10):o+=chr(int(c)+n)
   except:
    o+=chr(ord(c)+100)
 return o
def decode(s,n,al,r=''):
 a=al
 for z in range(len(s)):
  n=n+1;c=s[z:z+1]
  if al.find(c)>=0:al+=a;r+=al[al.find(c)-n+1:al.find(c)+2-n]
  else:
   if ord(c) in range(0,10+n):r+=str(ord(c)-n+1)
   else:r+=chr(ord(s[z:z+1])-100)
 return r
