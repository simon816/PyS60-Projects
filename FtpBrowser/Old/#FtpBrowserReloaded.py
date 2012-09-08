import appuifw as ui, e32, StringIO, os, zipfile, e32dbm, random
from ftplib import all_errors, FTP
app=ui.app;lk=e32.Ao_lock();
def u(u):return unicode(u)
def replace_all(text, dic):
 for i, j in dic.iteritems():
  text = text.replace(i, j)
 return text

class ftpbrowser:
 def dev(self, feat):
  ui.note(u'This app is in development atm, feature "'+feat+'" has not yet been implemented', 'error')
 def mkdir(self, list):
  for dir in list:
   if not os.path.exists(dir):os.makedirs(dir);return 1
   else:return 0;

 def __init__(self):
  self.appname=u"FTP Browser"
  self.author=u"Simon816"
  self.url=u'http://simon816.hostzi.com'
  d='e:\\python\\apps\\simon816\\ftpbrowser\\'
  try:f=open(d+'db.dir', 'r+');dbDIR=f.read()
  except:f=open(d+'db.dir', 'w');f.write(d);dbDIR=d
  f.close()
  if not dbDIR.endswith('\\'):dbDIR+='\\'
  self.db=e32dbm.open(dbDIR+'db', 'cf')
  self.dd=dbDIR
  self.root=d
  try: s=self.db['status']
  except:self.reset()
  self.exit(self.quit)

 def form(self, args):
  return [(u'Conn. name', 'text', args[0]), (u'Host', 'text',args[1]),(u'Port', 'number', args[2]), (u'User nm.', 'text', args[3]), (u'Password', 'text', args[4]), (u'Initial Dir', 'text', args[5]), (u'Passive', 'combo', ([u'True', u'False'], args[6]))]

 def mod_db(self, key, value):
  s=''
  if value==tuple(value):
   for v in value:
    try:v=int(v);s+=str(v)+'\x01'
    except:s+=str(v)+'\x00'
   s=s[:len(s)-1]
  elif value==list(value):
   for v in value:s+=str(v)+'\x01'
  else:s=value
  self.db[str(key)]=str(s)
 def get_db(self, key, mode='str'):
  try:
   v=self.db[str(key)]
   if mode=='str':return v
   elif mode=='int':return int(float(v))
   elif mode=='tuple':
                                 t=v.split('\x00');
                                 for v in range(t):
                                  if t[v][len(t[v])-1:]=='\x01':
                                   t[v]=int(float(t[v][:len(t[v])-1]))
                                 return tuple(t)
   elif mode=='list':return tuple(v.split('\x01'))
  except:return None

 def decodestring(self,s,a):return decode(str(s[int(float(s[:1]))+1:]),int(float(a.find(s[1:2])+1)))
 def encodestring(self,s, a):K=random.randint(1,len(a)-1);k=encode(str(K), K, '', 'a');return encode(s, K, str(len(k))+k)

 def reset(self):
  try:
   for entry in self.db.items():
    if entry[0].find('acc_')==-1:del self.db[entry[0]]
   self.mod_db('settings_dir', 'e:\\python\\apps\\simon816\\ftpbrowser')
   self.mod_db('account_dir', self.db['settings_dir']+'\\accounts')
   self.mod_db('cashe_dir', self.db['settings_dir']+'\\cashe')
   self.mod_db('version', '0.0.1')
   self.mod_db('defaultdir', 'e:\\')
   self.mod_db('color', '0x000000')
   self.mod_db('font', (u"nokia hindi s60",14,16))
   self.mod_db('blocksize', '8192')
   self.mod_db('icons', "e:\\mbm.mbm")
   self.mod_db('status', 'ready')
   self.mod_db('debug', 'False')
   self.mod_db('mode', 'SQL')
   self.mod_db('a', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\t')
   ui.note(u'Successfully reset', 'conf')
  except:
   ui.note(u'error', 'error')

 def quit(self):self.db.sync();self.db.close();lk.signal()
 def exit(self, action):app.exit_key_handler=action
 def disp(self, cback):return ui.Listbox(self.interface, cback)
 def dummy(self):pass

 def about(self):
  ui.note(u'A FREE '+self.appname+' by '+self.author+'\nFor more info, please visit:'+self.url+'\nCurrent version: '+self.get_db('version'))

 def run(self):
  self.mkdir([self.get_db('settings_dir'), self.get_db('account_dir'), self.get_db('cashe_dir')])
  self.mainscr()

 def mainscr(self):
  self.exit(self.quit)
  self.menu=[(u'Select', self.handle),(u'About', self.about),(u'Reset', self.reset), (u'Exit', self.quit)]
  self.interface=[u'Connect', u'Settings', u'Setup']
  app.menu=self.menu
  app.body=self.disp(self.handle)
  app.title=self.appname


 def activate(self):
  c=app.body.current()
  if self.connections[c]==u'New Connection':self.newcon()
  else:self.connect(self.connections[c])
 def handle(self):
  c=app.body.current()
  if c==0:self.conscr()
  elif c==1:self.settings()
  elif c==2:self.setup()
  else:pass


 def conscr(self):
  self.exit(self.mainscr)
  self.menu=[(u'Connect', self.activate), (u'New', self.newcon), (u'Edit', self.editcon), (u'Delete', self.delcon)]
  self.connections=[u'New Connection']
  if self.get_db('mode')=='flatfile':
   for file in os.listdir(self.get_db('account_dir')):
    if len(file.split('.acc'))==2:
     self.connections.append(u(file).split('.acc')[0])
  elif self.get_db('mode')=='SQL':
   l=[]
   for arr in self.db.items():
    if not arr[0].find('acc_')==-1:l.append(u(arr[0][4:]))
   l.sort(lambda x, y: cmp(x.lower(),y.lower()));self.connections+=l
  self.interface=self.connections
  app.body=self.disp(self.activate)
  app.menu=self.menu
  app.title=u'Connect to...'

 def settings(self):
  self.interface=[(u'Settings Directory', u(self.db['settings_dir'])),(u'Default Directory', u(self.db['defaultdir'])), (u'Account Directory', u(self.db['account_dir'])),(u'Cashe Directory', u(self.db['cashe_dir']))]
  app.body=self.disp(self.set)
  self.exit(self.mainscr)

 def set(self):
  if app.body.current()==0:
   self.db['settings_dir']=ui.query(u'Settings Directory', 'text', u(self.db['settings_dir']))
  elif app.body.current()==1:
   self.db['defaultdir']=ui.query(u'Default Directory', 'text', u(self.db['defaultdir']))
  elif app.body.current()==2:
   self.db['account_dir']=ui.query(u'Account Directory', 'text', u(self.db['account_dir']))
   

 def setup(self):
  self.exit(self.mainscr)
  self.interface=[(u'Debug Mode', u(self.get_db('debug'))),
                          (u'Database Directory', u(self.dd)),
                          (u'Account storage mode', u(self.db['mode'])),
                          (u'Alphabet string', u(self.get_db('a')))]
  app.body=self.disp(self.chset)
 def chset(self):
  c=app.body.current()
  if c==0:self.mod_db('debug', ui.popup_menu([u'False', u'True']))
  elif c==1:q=ui.query(u'Database Directory', 'text', u(self.dd));f=open(self.root+'db.dir', 'w');f.write(q);f.close()
  elif c==2:
   opts=['SQL', 'flatfile']
   sel=ui.popup_menu([u(opts[0]), u(opts[1])])
   self.mod_db('mode', opts[sel])
  elif c==3:self.mod_db('a', ui.query(u'Alphabet string', 'text',  u(self.get_db('a'))))
  self.setup()


 def newcon(self):
  flags=ui.FFormEditModeOnly
  f=self.form([u'',u'',21,u'',u'', u'/', 0])
  f=ui.Form(f, flags)
  f.execute()
  self.savecon(f, 'true')

 def editcon(self):
  name=self.interface[app.body.current()]
  flags=ui.FFormEditModeOnly
  if self.get_db('mode')=='flatfile':f=open(self.get_db('account_dir')+'\\'+name+'.acc');data=f.read();f.close();data=data.split('\n')
  elif self.get_db('mode')=='SQL':data=self.get_db('acc_'+name, 'list')
  if data[5]=='true':p=0
  else: p=1
  form=self.form([u(name),u(data[0]),int(float(data[1])),u(data[2]),u(self.decodestring(data[3],self.get_db('a'))),u(data[4]),p])
  f=ui.Form(form, flags)
  f.execute()
  self.savecon(f)

 def savecon(self, f, append='false'):
   if f[6][2][1]==0: p='true'
   else:p='false'
  #try:
   if f[0][2]==u'' or f[1][2]==u'':raise ValueError
   if self.get_db('mode')=='flatfile':fi=open(self.get_db('account_dir')+'\\'+f[0][2]+'.acc', 'w');m='ff'
   elif self.get_db('mode')=='SQL':fi=StringIO.StringIO();m='sql'
   for d in range(len(f)-1):
    if d==5:fi.write(p)
    elif d==3:fi.write(self.encodestring(f[d+1][2], self.get_db('a'))+'\n')
    else:fi.write(str(f[d+1][2])+'\n')
   if m=='ff':fi.close()
   elif m=='sql':
    fi.seek(0);d=fi.read();fi.close()
    self.mod_db('acc_'+f[0][2], d.split('\n'))
   if append=='true':self.connections.append(u(f[0][2]))
   ui.note(u'Saved', 'conf')
   self.conscr()
  #except:
   #ui.note(u'Did not save')

 def delcon(self):
  name=self.interface[app.body.current()]
  ok=ui.query(u'Are you sure you want to delete "'+name+'"', 'query')
  if ok==1:
   if self.get_db('mode')=='flatfile':os.unlink(self.db['account_dir']+'/'+name+'.acc')
   elif self.get_db('mode')=='SQL':del self.db['acc_'+name]
   self.connections.pop(app.body.current())
  self.conscr()

 def login(self):
  if self.get_db('mode')=='flatfile':f=open(self.get_db('account_dir')+'\\'+self.name+'.acc');data=f.read();f.close();opts=data.split('\n')
  else:opts=self.get_db('acc_'+self.name, 'list')
  self.user=str(opts[2]);self.host=str(opts[0]);self.ftp=FTP()
  try:
   self.ftp.connect(self.host, int(float(opts[1])))
   self.ftp.set_pasv(opts[5])
   self.ftp.login(self.user, self.decodestring(opts[3], self.get_db('a')))
   self.ftp.cwd(str(opts[4]))
   return 1
  except all_errors[1], e:ui.note(u'could not connect\n'+u(e), 'error');self.conscr();
  except all_errors[0], e:ui.note(u'could not login\n(Bad username/password)', 'error');self.disconnect();self.conscr();

 def connect(self,name):
  self.name=name
  if self.login()==1:
   ui.note(u(self.ftp.getwelcome()), 'info', 1)
   self.menu=[
    (u'File...', (
        (u'Open', self.open), 
        (u'Download', self.download), 
        (u'File Info', self.fileinfo),
        (u'Rename', self.rename)
    )),
    (u'Edit...', (
        (u'Cut', self.cut),
        (u'Copy', self.copy)
    )),
    (u'View...', (
        (u'Refresh', self.dispdir),
        (u'Change path', self.dummy)
     )), 
     (u'Upload', self.upload),
     (u'Delete', self.delete), 
     (u'New...', (
         (u'File', self.new), 
         (u'Folder', self.newdir)
     )), 
     (u'Send Command', self.sendcmd),
     (u'Disconnect', self.disconnect)]
   self.dispdir()

 def sendcmd(self):
  print self.ftp.sendcmd(ui.query(u'Command','text'))

 def dispdir(self):
  try:
   self.interface=self.getwd()
   app.title=u(self.pwd)
   app.body=self.disp(self.actions)
   self.exit(self.disconnect)
   app.menu=self.menu
  except all_errors, e:self.disperr(str(e), [self.dispdir])

 def reconnect(self, func, *action):
  if self.login()==1:
   ui.note(u'reconnected', 'conf', 1)
   if action==[]:func()
   else:self.ftp.cwd(self.pwd);func(*action)
  else:
   if not self.rety==1:
    ui.note(u'Connection was dropped but could not reconnect', 'error')
    ui.note(u'retrying...', 'info', 1);self.retry=1
    self.reconnect(func, *action)
   else:ui.note('Could not make a data connection, returning to menu', 'error');self.retry=0;self.conscr()

 def disperr(self, e, action):
  if e[:3]=='421' or tuple(e)[0]==13:self.reconnect(*action)
  elif e=="(32, 'Broken pipe')":
   ui.note(u'Unexpectly lost connection with '+self.host, 'error');reconn=ui.query(u'Reconnect?', 'query')
   if reconn==1:self.reconnect(*action)
  else:ui.note(u(e), 'error');print e

 def getwd(self,dirname=None):
  if not dirname:self.pwd=dr=self.ftp.pwd()
  else:dr=dirname
  s=StringIO.StringIO();self.ftp.retrbinary('LIST '+dr,s.write);s.seek(0);li=s.read();s.close();
  fs=[];l=[];a=li.split("\r\n");folder=ui.Icon(u(self.get_db('icons')), 115, 116);d=f=[];l.append((u'..', folder));self.amt=len(a)-1
  if li:
   dirs=[];files=[]
   for I in range(0, self.amt):
    fs.append([I]);i=a[I].split(" ")
    for p in range(len(i)):
     if not i[p]=='':
      if p==0:i[p]=list(i[p])
      fs[I].append(i[p])
    fs[I][9]=' '.join(fs[I][9:])
    if fs[I][9]=='.' or fs[I][9]=='..':pass
    else:
     if fs[I][1][0]=="d":dirs.append((u(fs[I][9]),folder))
     else:files.append((u(fs[I][9]),ui.Icon(u(self.get_db('icons')), 57, 58)))
   I=I-1;l+=dirs+files
  self.fs=fs;return l

 def getsel(self):
  for x in range(0,self.amt):
   if self.interface[app.body.current()][0]==self.fs[x][9]:return self.fs[x];break
  return ['-1', ['d'],'','','','','','','','..']

 def actions(self):
  self.sel=self.getsel()
  if self.sel[1][0]=="d":self.chdir(self.sel[9])
  else:self.open()
 
 def chdir(self, dir):
  try:
   if dir=='..':self.ftp.cwd('..');ui.note(u'Going up one', 'info', 1)
   else:
    ui.note(u'changing directory to '+dir, 'info', 1);self.ftp.cwd(self.pwd+'/'+dir)
   self.dispdir()
  except all_errors, e:self.disperr(str(e), [self.chdir, dir])

 def fileinfo(self):
  s=''
  for i in self.getsel():
   s+=str(i)+'\n'
  ui.note(u(s))
  print s

 def submenu(self, mode='r', *args):
  subindex=args[0]
  obj=list(self.menu[subindex][1])
  try:
   if mode in ['r','w']:index=[x[0].lower() for x in self.menu[subindex][1]].index(u(args[1].lower()))
  except:return 0
  if    mode=='r':return index
  elif mode=='w':obj[index]=args[1]
  elif mode=='a':obj.insert(args[1], args[2])
  elif mode=='d':del obj[args[1]]
  self.menu[subindex]=(self.menu[subindex][0], tuple(obj))

 def cut(self):
  self.sel=self.getsel()
  self.cbd=[self.sel[1][0],self.pwd+'/',self.sel[9], 'cut']
  if not self.submenu('r', 1, 'Paste'):self.submenu('a', 1, 2, (u'Paste', self.paste))

 def copy(self):
  self.sel=self.getsel()
  self.cbd=[self.sel[1][0],self.pwd+'/',self.sel[9], 'copy']
  if not self.submenu('r', 1, 'Paste'):self.submenu('a', 1, 2, (u'Paste', self.paste))

 def paste(self):
  self.submenu('d', 1, 2)
  if self.cbd[0]=='-':
   fh=StringIO.StringIO()
   self.ftp.retrbinary('RETR '+self.cbd[1]+self.cbd[2], fh.write)
   fh.seek(0)
   self.ftp.storbinary('STOR '+self.cbd[2],fh)
   fh.close()
  else:
   self.dirdict={'reverse':[]}
   self.loopdir(self.cbd[1]+self.cbd[2])
   for dir in self.dirdict['reverse']:
    self.ftp.mkd(dir[len(self.cbd[1]):])
    for file in self.dirdict[dir]:
     fh=StringIO.StringIO()
     self.ftp.retrbinary('RETR '+dir+'/'+file, fh.write);fh.seek(0);self.ftp.delete(dir+'/'+file)
     self.ftp.storbinary('STOR '+dir[len(self.cbd[1]):]+'/'+file,fh)
     fh.close()
   self.dirdict['reverse'].reverse()
   for dir in self.dirdict['reverse']:self.ftp.rmd(dir)
  self.dispdir()

 def newdir(self):
  name=ui.query(u"New Folder", 'text')
  if not name==u'':self.ftp.mkd(name);self.dispdir()

 def mkcache(self, pwd):
  try:
   cd='\\'+self.user+'@'+self.host
   cd=cd.strip()
   self.mkdir([self.get_db('cashe_dir')+cd])
   dir=self.get_db('cashe_dir')+cd+pwd
   self.mkdir([dir])
  except:ui.note(u'could not create cashe, downloading to save directory (set in settings)', 'error');dir=self.get_db('defaultdir')
  self.cache=dir

 def savelocal(self, block):
  try:
   try:f=open(self.cache+'\\'+self.sel[9], 'ab')
   except:f=open(self.cache+'\\'+self.sel[9], 'w')
   f.write(block)
   f.close()
   self.dcomp=1
  except:ui.note(u'Could not download file. read only access?\nAborting transfer', 'error');self.ftp.abort()
  #self.ftp.sendcmd('type a')

 def download(self):
  self.pwd=self.ftp.pwd()
  self.sel=self.getsel()
  try:
   ui.note(u'Downloading '+self.sel[9], 'info', 1)
   self.mkcache(self.pwd)
   if self.sel[1][0]=='-':
    self.ftp.retrbinary('RETR '+self.sel[9], self.savelocal, self.get_db('blocksize', 'int'))
   else:self.downloaddir()
   if self.dcomp==1:ui.note(u'Download complete', 'conf');self.dcomp=0;del self.cache
  except all_errors, e:self.disperr(str(e), self.download)

 def downloaddir(self):
  self.dirdict={'reverse':[]}
  self.loopdir(self.pwd+'/'+self.sel[9])
  del self.dirdict['reverse']
  self._sel=self.sel
  for dir in self.dirdict:
   self.mkcache(dir)
   for file in self.dirdict[dir]:
    self.sel=['','','','','','','','','',file]
    self.ftp.retrbinary('RETR '+dir+'\\'+file, self.savelocal, self.get_db('blocksize', 'int'))
  self.dcomp=1;self.sel=self._sel;del self._sel

 def upload(self, file=None):
   if file==None:file=ui.query(u'Please specify the path to the file', 'text')
  #try:
   if zipfile.is_zipfile(file):e=ui.query(u'Zipfile detected, extract contents to current directory?', 'query')
   if not e==1:
    f=open(file, 'r')
    try:
     n=f.name;n=replace_all(n, {'/':'\\'}).split('\\');self.ftp.storbinary('STOR '+n[len(n)-1], f, self.get_db('blocksize', 'int'));ui.note(u'Uploaded', 'conf', 1);self.dispdir()
    except all_errors, e:self.disperr(str(e), [self.upload,file])
    f.close()
   else:self.up_zip(file)
  #except IOError, e:
  # ui.note(u'file error', 'error'+u(e));retry=ui.query(u'Retry?', 'query')
   #if retry==1:self.upload()

 def up_zip(self, file):
  ui.note(u'upping zip')
  z=zipfile.ZipFile(file)
  wd=self.get_db('cashe_dir')+'\\'+self.user+'@'+self.host+replace_all(self.pwd, {'/':'\\'})+'\\';
  wd=wd.strip();
  ui.note(u(wd))
  print wd
  self.mkdir([wd])
  for f in z.namelist():
   if f.endswith('/'):
    #if not os.path.exists(wd+f):
     self.mkdir([wd+f]);self.ftp.mkd(f)
   else:
     fh=open(wd+f, 'w')
     fh.write(z.read(f))
     fh.close()
     fi=open(wd+f, 'r')
     self.ftp.storbinary('STOR '+f, fi,self.get_db('blocksize', 'int'))
     fi.close()
  self.dispdir()

 def rename(self):
  frm=self.getsel()[9]
  self.ftp.rename(frm, ui.query(u'Rename '+u(frm), 'text', u(frm)))
  self.dispdir()

 def delete(self):
  self.sel=self.getsel()
  conf=ui.query(u"Delete "+self.sel[9]+"?", 'query')
  if conf==1:
   try:
    if not self.sel[1][0]=='d':self.ftp.delete(self.pwd+'/'+self.sel[9]);ui.note(u'deleted', 'conf', 1)
    else:
     try:self.ftp.rmd(self.sel[9]);ui.note(u'deleted', 'conf', 1)
     except all_errors, e:
      if str(e)[:3]=='550':
       if ui.query(u'Driectory is not empty, delete all sub directories and files?', 'query')==1:
        self.dirdict={'reverse':[]}
        self.loopdir(self.pwd+'/'+self.sel[9])
        self.dirdict['reverse'].reverse()
        for dir in self.dirdict['reverse']:
         for file in self.dirdict[dir]:
          self.ftp.delete(dir+'\\'+file)
         self.ftp.rmd(dir)
      else:raise e
    self.dispdir()
   except all_errors, e:self.disperr(str(e), [self.delete])

 def loopdir(self, initdir):
  self.dirdict['reverse'].append(initdir)
  self.dirdict[initdir]=[]
  self.getwd(initdir)
  for file in self.fs:
   if file[1][0]=='d':
    self.loopdir(initdir+'/'+file[9])
   else:self.dirdict[initdir].append(file[9])

 def retr(self):
  self.sel=self.getsel()
  self.binary=""
  try:self.ftp.retrbinary('RETR '+self.sel[9], self.getbin,self.get_db('blocksize', 'int'));self.parcebin()
  except all_errors, e:self.disperr(str(e), [self.retr])

 def getbin(self, data):
  self.binary+=data
  try:f=open('e:\\tmp.tmp', 'ab')
  except:f=open('e:\\tmp.tmp', 'w')
  f.write(data)
  f.close()

 def parcebin(self):
  bin=self.binary
  self.t=ui.Text();self.t.color=0x000000;self.t.font=(u"nokia hindi s60",14,16)
  try:
   self.t.set(u(bin))
  except UnicodeError:
   try:
    bin.decode('ascii')
    self.t.set(bin)
   except:
    self.t=None
  except SymbianError, e:
   if e.errno==-4:
    ui.note(u'OutOfMemory, splitting file into chunks', 'error')
    app.set_tabs([u'1', u'2',u'3'],self.dummy)
    self.ftp.retrbinary('RETR '+self.sel[9], self.getbin, self.get_db('blocksize', 'int'));self.parcebin()

 def new(self):
  self.sel=self.getsel()
  self.sel[9]=ui.query(u'New File', 'text')
  self.t=ui.Text();self.t.color=0x000000;self.t.font=self.get_db('font', 'tuple')
  app.body=self.t
  app.title=u(self.sel[9])
  self.exit(self.dispdir)
  app.menu=[(u'Save', self.save)]

 def open(self):
  self.retr()
  if not self.t==None:
   app.body=self.t
   app.title=u(self.sel[9])
   self.exit(self.dispdir)
   app.menu=[(u'Save', self.save)]
  else:
   ui.note(u'Cannot open file for editing', 'error')
   dld=ui.query(u'Download '+self.sel[9]+u' instead?', 'query')
   if dld==1:self.savelocal()
  
 def save(self):
  s = lambda s: s.encode('utf-8')
  st=self.t.get()
  f=StringIO.StringIO()
  f.write(s(st.replace(u"\u2029", u'\r\n')))
  f.seek(0)
  try:
   self.ftp.storbinary('STOR '+self.sel[9], f, self.get_db('blocksize', 'int'))
   ui.note(u'Saved!', 'conf', 1)
  except all_errors, e:
   self.disperr(str(e), [self.save])
  f.close()

 def disconnect(self):
  try:ui.note(u'Disconnecting...', 'info', 1);self.ftp.quit()
  except all_errors, error:ui.note(u(error), 'error')
  self.conscr()

a=ftpbrowser().get_db('a')
def encode(s,n,o='',w='', al=a):
 for x in range(len(s)):
  n=n+1;c=s[x:x+1]
  if a.find(c)>=0 or w=='a':al+=a;o+=al[al.find(c)+n:al.find(c)+1+n]
  else:
   try:
    if int(c) in range(0,10):o+=chr(int(c)+n)
   except:
    o+=chr(ord(c)+100)
 return o
def decode(s,n,r='', al=a):
 for z in range(len(s)):
  n=n+1;c=s[z:z+1]
  if al.find(c)>=0:al+=a;r+=al[al.find(c)-n+1:al.find(c)+2-n]
  else:
   if ord(c) in range(0,10+n):r+=str(ord(c)-n+1)
   else:r+=chr(ord(s[z:z+1])-100)
 return r
if __name__=="__main__":
 ftpbrowser().run()
lk.wait()