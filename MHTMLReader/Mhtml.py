import re
class MHMLReader:
 MNormal=1 # reads all the file, auto parses data
 MInfo=2       # reads just the declaration header
 MHeaders=3# same as MNormal but only parses file headers
 MManual=4 #same as MNormal but doesn't auto parse, useful for debugging
 def __init__(self,file=None):
  if file:self.open(file)
  self._fhead=[]
  self._fcont=[]
  self.mode=None
  self._inf=None
  """def __getattr__(self,attr):
 allowed=self._alwdattr()
 if attr in allowed.keys():
  return self.__dict__['_'+allowed[attr]]
 else:
  return self.__dict__[attr]
 """
 def open(self,filename,mode=MNormal):
  fh=open(filename)
  self.mode=mode
  if mode==self.MNormal or mode==self.MManual:
   self.mhtml=fh.read()
   pieces=self.mhtml.split('\r\n\r\n')
   head=pieces[0].split('\r\n')
   body='\r\n\r\n'.join(pieces[1:])
   if mode==self.MNormal:
    self.parse_head_decl(head)
    self.parse_body(body)
   else:
    fh.close()
    return head,body
  elif mode==self.MInfo:
   self.parse_head_decl(fh.xreadlines())
  fh.close()
 def parse_head_decl(self,iterable):
  header={}
  for line in iterable:
   if line[-2:]=='\r\n':line=line[:-2]
   if not line:break
   for kv in line.split('; '):
    kv=kv.split(': ')
    if len(kv)!=2:
     kv=kv[0].split('=')
    header[kv[0]]=kv[1]
  self._inf=header
  self.correct_subject()
 def correct_subject(self):
  try:
    subject=self._inf['Subject'][2:-2].split('?')
  except KeyError:
    self._inf['Subject']=''
    return
  enc=re.compile('=[0-9][0-9]')
  t=subject[2]
  n=len(t)
  i=0
  while i<n:
   m=enc.search(t,i)
   if not m:break
   s=m.start()
   e=m.end()
   i=e-1
   c=chr(int(t[s+1:e],16))
   t=t[:s]+c+t[e:]
  self._inf['Subject']=t.decode(subject[0])
 def parse_headers(self,headers):
  fileheaders={}
  for header in headers.split('\r\n'):
   s=header.split(':')
   if len(s)>=2:fileheaders[s[0]]=':'.join(s[1:])
  self._fhead.append(fileheaders)
 def parse_body(self,body):
  files=body.split('--'+self._inf['boundary'])
  for file in files:
   if len(file)>4:
    file=file.split('\r\n\r\n')
    self.parse_headers(file[0])
    if self.mode!=self.MHeaders:
     self._fcont.append('\r\n\r\n'.join(file[1:]))
 def _alwdattr(self):
  at={'info':'inf','open':'open'}
  return at
if __name__=='__main__':
  m=MHMLReader()
  import simon816.util
  m.open(simon816.util.util().select('file', 'e:\\system\\data\\OperaMobile\\OperaSavedPages\\',extwhitelist=['mhtml']))
  import appuifw,e32, simon816.text,base64
  def s(c):
    fi=open('e:\\#testarea\\f.txt','w')
    if m._fhead[l.current()]['Content-Type'].find('base64')>-1:
      fi.write(base64.decodestring(c.read()))
    else:
      fi.write(c.read())
    fi.close()
  t=simon816.text.text()
  t.bind('save',s)
  t.display()
  def c():
    t.loadText(m._fcont[l.current()])
    
  l=appuifw.Listbox([unicode(i['Content-Type'][i['Content-Type'].find('name')+5:]) for i in m._fhead],c)
  lk=e32.Ao_lock()
  appuifw.app.exit_key_handler=lk.signal
  appuifw.app.body=l
  lk.wait()