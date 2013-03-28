class text:
 class BinaryError(Exception):pass
 def __init__(self):
  self.t=ui.Text()
  app.menu=[]
  self.onsave=lambda f:None
  self.onsaveas=lambda n,f:None
  self.onexit=lambda a:None
  self.onerror=lambda e:None
 def loadText(self,t,ignore=False):
  orig=self.orig=self.toUnicode(t,ignore)
  self.t.set(orig)
  return self.t
 def toUnicode(self,string,ignore=False):
  try:uni=u(string);self.type="plain"
  except UnicodeError:
   try:uni=string.decode("utf-8");self.type="utf8"
   except UnicodeError:
    try:uni=string.decode("utf-16");self.type="utf16"
    except UnicodeError:
     if not ignore:raise self.BinaryError(1,"String is in binary")
     else:uni=string.decode("utf-8",'ignore');self.type="ignore utf8"
  return uni
 def getText(self):
  return self.t.get().replace(u"\u2029", u'\r\n')
 def saveText(self,callopenfile=None):
  newFile=StringIO.StringIO()
  text=self.getText()
  if self.type=="utf16":
   text=text.encode("utf-16")
  else:
   text=text.encode("utf-8")
  newFile.write(text)
  newFile.seek(0)
  if callopenfile:
   callopenfile(newFile)
   newFile.close()
  return newFile
 def chunks(self,fh,n):
   fh.seek(0)
   self.loadText(fh.read(450))
   fh.close()
   self.name=n
   self.display()
  
 def readFile(self,fh,n=''):
  try:
   self.loadText(fh.read())
   fh.close()
   self.name=n
   self.display()
  except Exception, e:
   if e.errno==-4:
    self.chunks(fh,n)
   else:
    self.onerror(e)
    self.onexit()
  fh.close()
 def toTop(self):self.t.set_pos(0)
 def toBottom(self):self.t.set_pos(len(self.t.get()))
 def toLine(self,num=0):
  lines=self.getText().split('\r\n')
  num=num or ui.query(u'Goto line (1-%s)'%(len(lines)),'number',1)
  if not num:return [None]
  line=lines[num-1:]
  if not line:ui.note(u'Line number not in range','error');return [None]
  remaining_str=u'\u2029'.join(line)
  index=self.t.get().index(remaining_str)
  self.t.set_pos(index)
  return line
 def linecol(self):
  line,col=ui.multi_query(u'Line',u'Column') or (None,None)
  try:
   line=int(line)
   col=int(col)
  except:
   if line:ui.note(u'Line & column must be integers','error')
   return False
  line=self.toLine(line)[0]
  if not line:return False
  index=line[col:]
  if index:
   self.t.set_pos(self.t.get_pos()+col)
 def build_search(self,arr,s,key):
  try:ind=s.index(key,arr[len(arr)-1]+1)
  except ValueError:return arr[1:] or None
  arr.append(ind)
  return self.build_search(arr,s,key)
 def find(self,pretext='',string=''):
  if 'f' in dir(self) and not pretext:pretext=self.f
  if not string:string=ui.query(u'Find text','text',pretext)
  if not string:return
  self.f=string
  self.f_ind=self.build_search([0],self.t.get(),string)
  if self.f_ind:
   self.f_curr=0
   self.t.set_pos(self.f_ind[self.f_curr])
  else:
   if ui.query(u'Not found. Retry?','query'):
    self.find(string)
 def nav_find(self,d,onEnd):
  if not 'f_ind' in dir(self):self.find();return  
  if not self.f_ind:self.find();return
  if d=='next':self.f_curr+=1
  if d=='prev':self.f_curr=self.f_curr-1
  try:pos=self.f_ind[self.f_curr]
  except:
   onEnd()
   return
  self.t.set_pos(pos)
 def next(self):
  def ask():
   if ui.query(u'Reached the end, restart search?','query'):
    self.f_curr=-1
    self.next()
    return
  self.nav_find('next',ask)
 def prev(self):
  def ask():
   if ui.query(u'Reached the beginning, return to last occurence?','query'):
    self.f_curr=len(self.f_ind)
    self.prev()
  self.nav_find('prev',ask)
 def replace(self,limit=1,rep=None):
  if not rep:rep=ui.multi_query(u'Replace',u'With')
  if not rep:return
  self.r=rep
  t=self.t.get()
  t=t.replace(rep[0],rep[1],limit)
  self.t.set(t)
  self.r_ind=self.build_search([0],t,rep[1])
  if self.r_ind:
   self.t.set_pos(self.r_ind[-1])
 def replace_next(self):
  if 'r' in dir(self):self.replace(1,self.r)
  else:self.replace()
 def display(self):
  app.body=self.t
  app.menu=[
   (u'Save',self.saveFile),
   (u'Save As...',self.saveAs),
   (u'Goto',(
    (u'Top',self.toTop),
    (u'Bottom',self.toBottom),
    (u'Line...',self.toLine),
    (u'Line/Col...',self.linecol)
   )),
   (u'Find',(
    (u'Text...',self.find),
    (u'Next',self.next),
    (u'Previous',self.prev),
   )),
   (u'Replace',(
    (u'Text...',self.replace),
    (u'Next',self.replace_next),
    (u'All...',lambda:self.replace(-1))
   ))
   ]
  app.exit_key_handler=self.askSave
 def saveFile(self):
  self.saveText(self.onsave)
  self.orig=self.getText()
 def askSave(self):
  if self.orig !=self.getText():
   if ui.query(u'Save?','query'):self.saveFile()
  self.onexit()
 def saveAs(self):
  fields=[(u'File Name','text',u(self.name)),(u'Encoding','combo',([u'UTF-8',u'UTF-16'],0))]
  form=ui.Form(fields,17)
  form.execute()
  namefield=form[0]
  if not len(namefield)==3:return
  encoding=form[1][2][0][form[1][2][1]]
  self.type=encoding.replace('-','').lower()
  self.onsaveas(namefield[2],self.saveText())
  self.orig=self.getText()
  self.nf.close()
