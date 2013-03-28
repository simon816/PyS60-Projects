import appuifw as ui, e32, StringIO, os, zipfile, e32dbm, random, graphics,ftplib
from simon816 import *
app=ui.app;lk=e32.Ao_lock();
FTP=ftplib.FTP;all_errors=ftplib.all_errors;error_reply=ftplib.error_reply;error_perm=ftplib.error_perm
u=lambda s:unicode(s)
def replace_all(text, dic):
 for i, j in dic.iteritems():
  text = text.replace(i, j)
 return text
import sys
class err:
 def write(self,e):
  f=open("e:/Python/apps/simon816/ftpbrowser/err.log", "a")
  f.write(e)
  f.close()
  ui.note(u"error caught","error")
#sys.stderr=

class interface:
 def dev(self, feat):
  ui.note(u'This app is in development atm, feature "'+feat+'" has not yet been implemented', 'error')
 
 def __init__(self,db):
  self.appname=u"FTP Browser"
  self.author=u"Simon816"
  self.url=u'http://simon816.hostzi.com'
  self.db=db
  self.dd=self.db.dir
  self.root=self.db.home
  try: s=self.db.get('status')
  except:self.reset()
  self.exit(self.quit)

 def form(self, args):
  return [(u'Connection Name', 'text', args[0]), (u'Host', 'text',args[1]),(u'Port', 'number', args[2]), (u'Username', 'text', args[3]), (u'Password', 'text', args[4]), (u'Initial Directory', 'text', args[5]), (u'Passive Mode', 'combo', ([u'True', u'False'], args[6]))]

 def decodestring(self,s,a):return decode(str(s[int(float(s[:1]))+1:]),int(float(a.find(s[1:2])+1)),self.db.get('a'))
 def encodestring(self,s, a):K=random.randint(1,len(a)-1);k=encode(str(K), K,self.db.get('a'),'', 'a');return encode(s, K,self.db.get('a'), str(len(k))+k)

 def reset(self):
  try:
   for entry in self.db.items():
    if entry[0].find('acc_')==-1: self.db.delete(entry[0])
   self.db.mod('settings_dir', 'e:\\python\\apps\\simon816\\ftpbrowser')
   self.db.mod('account_dir', self.db.get('settings_dir')+'\\accounts')
   self.db.mod('cashe_dir', self.db.get('settings_dir')+'\\cashe')
   self.db.mod('version', '0.8.0')
   self.db.mod('defaultdir', 'e:\\')
   self.db.mod('color', (0,0,0))
   self.db.mod('font', (u"nokia hindi s60",14,16))
   self.db.mod('blocksize', '8192')
   self.db.mod('icons', "e:\\mbm.mbm")
   self.db.mod('status', 'ready')
   self.db.mod('debug', 'False')
   self.db.mod('mode', 'SQL')
   self.db.mod('a', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\t')
   self.db.mod("temp_timeout",60)
   ui.note(u'Successfully reset', 'conf')
  except:
   ui.note(u'error', 'error')

 def quit(self):
  try:self.db.sync();self.db.close()
  except:pass
  lk.signal();tab.hide_tabs()
 def exit(self, action):app.exit_key_handler=action
 def disp(self, cback):return ui.Listbox(self.interface, cback)
 def dummy(self):pass

 def about(self):
  ui.note(u'A FREE '+self.appname+' by '+self.author+'\nFor more info, please visit:'+self.url+'\nCurrent version: '+self.db.get('version'))

 def run(self):
  util.mkdir([self.db.get('settings_dir'), self.db.get('account_dir'), self.db.get('cashe_dir')])
  self.tabs=tab
  self.tabs.new_tab(u'Home',self.mainscr)
  self.mainscr()

 def mainscr(self):
  self.exit(self.quit)
  self.menu=[(u'Select', self.handle),(u'About', self.about),(u'Reset', self.reset), (u'Exit', self.quit)]
  self.interface=[u'Connect',u'File Browser', u'Settings', u'Setup']
  app.menu=self.menu
  app.body=self.disp(self.handle)
  app.title=self.appname


 def activate(self):
  c=app.body.current()
  if self.connections[c]==u'New Connection':self.newcon()
  else:
   name=self.connections[c]
   if self.db.get('mode')=='flatfile':f=open(self.db.get('account_dir')+'\\'+name+'.acc');data=f.read();f.close();opts=data.split('\n')
   else:opts=self.db.get('acc_'+name, 'list')
   ftp=ftpclass(self.db)
   ftp.connect(name,opts)
 def handle(self):
  c=app.body.current()
  if c==0:self.conscr()
  elif c==1:
   self.exit(self.mainscr)
   self.interface=[]
   sys_drives=['C:','D:','Z:']
   for d in e32.drive_list():
    if d in sys_drives:icon=ui.Icon(u(self.db.get('icons')), 397, 398)
    else:icon=ui.Icon(u(self.db.get('icons')), 395, 396)
    self.interface.append((u(d),icon))
   app.body=self.disp(self.file)
  elif c==2:self.settings()
  elif c==3:self.setup()
  else:pass

 def file(self):
  drive=self.interface[app.body.current()][0][:1]
  ftpclass(self.db).connect('File Browser > '+drive,['LocalUser','21',drive,'1a', '', ''],fileftp)

 def conscr(self):
  self.exit(self.mainscr)
  self.menu=[(u'Connect', self.activate), (u'New', self.newcon), (u'Edit', self.editcon), (u'Delete', self.delcon)]
  self.connections=[u'New Connection']
  if self.db.get('mode')=='flatfile':
   for file in os.listdir(self.db.get('account_dir')):
    if len(file.split('.acc'))==2:
     self.connections.append(u(file).split('.acc')[0])
  elif self.db.get('mode')=='SQL':
   l=[]
   for arr in self.db.items():
    if not arr[0].find('acc_')==-1:l.append(u(arr[0][4:]))
   l.sort(lambda x, y: cmp(x.lower(),y.lower()));self.connections+=l
  self.interface=self.connections
  app.body=self.disp(self.activate)
  app.menu=self.menu
  app.title=u'Connect to...'

 def settings(self):
  self.interface=[(u'Settings Directory', u(self.db.get('settings_dir'))),(u'Default Directory', u(self.db.get('defaultdir'))), (u'Account Directory', u(self.db.get('account_dir'))),(u'Cashe Directory', u(self.db.get('cashe_dir')))]
  app.body=self.disp(self.set)
  self.exit(self.mainscr)

 def set(self):
  if app.body.current()==0:
   d=ui.query(u'Settings Directory', 'text', u(self.db.get('settings_dir')))
   if not d:return
   self.db.mod('settings_dir', d)
  elif app.body.current()==1:
   d=ui.query(u'Default Directory', 'text', u(self.db.get('defaultdir')))
   if not d:return
   self.db.mod('defaultdir',d)
  elif app.body.current()==2:
   d=ui.query(u'Account Directory', 'text', u(self.db.get('account_dir')))
   if not d:return
   self.db.mod('account_dir',d)
   

 def setup(self):
  self.exit(self.mainscr)
  self.interface=[(u'Debug Mode', u(self.db.get('debug'))),
                          (u'Database Directory', u(self.dd)),
                          (u'Account storage mode', u(self.db.get('mode'))),
                          (u'Alphabet string', u(self.db.get('a')))]
  app.body=self.disp(self.chset)
 def chset(self):
  c=app.body.current()
  if c==0:self.db.mod('debug', ui.popup_menu([u'False', u'True']))
  elif c==1:q=ui.query(u'Database Directory', 'text', u(self.dd));f=open(self.root+'db.dir', 'w');f.write(q);f.close()
  elif c==2:
   opts=['SQL', 'flatfile']
   sel=ui.popup_menu([u(opts[0]), u(opts[1])])
   self.db.mod('mode', opts[sel])
  elif c==3:self.db.mod('a', ui.query(u'Alphabet string', 'text',  u(self.db.get('a'))))
  self.setup()


 def newcon(self):
  f=self.form([u'',u'',21,u'',u'', u'/', 0])
  f=ui.Form(f, 17)
  f.execute()
  self.savecon(f, 'true')

 def editcon(self):
  name=self.interface[app.body.current()]
  if self.db.get('mode')=='flatfile':f=open(self.db.get('account_dir')+'\\'+name+'.acc');data=f.read();f.close();data=data.split('\n')
  elif self.db.get('mode')=='SQL':data=self.db.get('acc_'+name, 'list')
  if data[5]=='true':p=0
  else: p=1
  form=self.form([u(name),u(data[0]),int(float(data[1])),u(data[2]),u(self.decodestring(data[3],self.db.get('a'))),u(data[4]),p])
  f=ui.Form(form, 17)
  f.execute()
  self.savecon(f)

 def savecon(self, f, dele=0):
   if f[6][2][1]==0: p='true'
   else:p='false'
   if f[0][2]==u'' or f[1][2]==u'':ui.note(u'Not enough data provided', 'error');return 0
   if self.db.get('mode')=='flatfile':fi=open(self.db.get('account_dir')+'\\'+f[0][2]+'.acc', 'w');m='ff'
   elif self.db.get('mode')=='SQL':fi=StringIO.StringIO();m='sql'
   for d in range(len(f)-1):
    if d==5:fi.write(p)
    elif d==3:fi.write(self.encodestring(f[d+1][2], self.db.get('a'))+'\n')
    else:fi.write(str(f[d+1][2])+'\n')
   if m=='ff':fi.close()
   elif m=='sql':
    fi.seek(0);d=fi.read();fi.close()
    self.db.mod('acc_'+f[0][2], d.split('\n'))
   if dele:self.delcon(1)
   ui.note(u'Saved', 'conf')
   self.conscr()

 def delcon(self,ok=0):
  name=self.interface[app.body.current()]
  if not ok:ok=ui.query(u'Are you sure you want to delete "'+name+'"', 'query')
  if ok==1:
   if self.db.get('mode')=='flatfile':os.unlink(self.db.get('account_dir')+'/'+name+'.acc')
   elif self.db.get('mode')=='SQL':self.db.delete('acc_'+name)
   self.connections.pop(app.body.current())
  self.conscr()

class ftpclass:
 def __init__(self, db):
  self.db=db
  self.connected=False
  self.t=text()
  self.t.t.font=self.db.get('font', 'tuple')
  self.t.t.color=self.db.get('color', 'tuple')
 def dummy(self,*args):pass
 def exit(self, action):app.exit_key_handler=action
 def disp(self, cback):return ui.Listbox(self.interface, cback)
 def do_action(self, action, *arguments):
  #function not ready
  self.doing=1
  action(*arguments)
 def login(self,ftpMgr,opts=None,chdir=True):
  if opts:self.opts=opts
  opts=self.opts
  self.user=str(opts[2]);self.host=str(opts[0]);
  self.handler=ftpMgr
  self.ftp=ftpMgr()
  #if ftpMgr==fileftp:return 1
  try:
   self.ftp.connect(self.host, int(float(opts[1])))
   self.ftp.set_pasv(opts[5])
   self.ftp.login(self.user, interface(self.db).decodestring(opts[3], self.db.get('a')))
   self.l=loader(graphics.Image.open('e:\\Python\\apps\\simon816\\ftpbrowser\\loading.gif'),100);self.pwd=''
   if chdir:self.chdir(str(opts[4]))
   return 1
  except all_errors[1], e:ui.note(u'could not connect\n'+u(e), 'error');self.disconnect(1);
  except all_errors[0], e:ui.note(u'could not login\n(Bad username/password)', 'error');self.disconnect(1)

 def connect(self,name,opts,ftp=FTP):
  self.tabs=tab
  self.name=name
  self.menu=[]
  if self.login(ftp,opts)==1:
   self.connected=True
   msg=self.ftp.getwelcome()
   if msg:ui.note(u(msg), 'info')
   self.tabs.new_tab(u(name),self.dispdir)
   if self.tabs.selected==0:self.tabs.select_tab(len(self.tabs.tabs)-1)
   
   self.menu=[
    (u'File...', (
        (u'Open', self.open), 
        (u'Download', self.download), 
        (u'File Info', self.fileinfo),
        (u'Rename', self.rename),
        (u'Chmod', self.chmod)
    )),
    (u'Edit...', (
        (u'Cut', self.cut),
        (u'Copy', self.copy)
    )),
    (u'View...', (
        (u'Refresh', self.refresh),
        (u'Change path', self.changepath)
     )), 
     (u'Upload', self.upload),
     (u'Delete', self.delete), 
     (u'New...', (
         (u'File', self.new), 
         (u'Folder', self.newdir)
     )), 
     (u'Timer Toggle',self.time_toggle),
     (u'Send Command', self.sendcmd),
     (u'Disconnect', self.disconnect)]
   app.menu=self.menu
   def ping(elapsed):self.ftp.pwd()
   self.timer=Timer(ping)
   self.t_on=1
   self.time_start()
 def time_start(self):
  self.timer.start(self.db.get("temp_timeout","int"))
 def time_toggle(self):
  if self.t_on:
   self.timer.stop()
  else:
   self.t_on=1
   self.time_start()

 def changepath(self):
  self.chdir(ui.query(u'Path','text', u(self.pwd)),True)

 def sendcmd(self):
  print self.ftp.sendcmd(ui.query(u'Command','text'))

 def refresh(self):self.l.start();self.dispdir()

 def dispdir(self,dontUpdate=False):
  try:
   self.tabs.update()
   if not dontUpdate:self.interface=self.getwd()
   t=self.tabs;s=t.selected;c=t.current
   if c()==self.name or s==0:app.body=self.disp(self.actions);app.title=u(self.pwd)
   self.exit(self.disconnect)
   app.menu=self.menu
   self.l.stop()
  except all_errors, e:self.disperr(str(e), [self.dispdir])

 def reconnect(self, func, *action):
  _pwd=self.pwd
  if self.login(self.handler,None,False)==1:
   self.l.addtext(u'reconnected', 1)
   self.l.addtext(u'Changing directory',1)
   self.ftp.cwd(_pwd)
   self.l.stop()
   if action==[]:func()
   else:func(*action)
  else:
   if not self.retry==1:
    ui.note(u'Connection was dropped but could not reconnect', 'error')
    ui.note(u'retrying...', 'info', 1);self.retry=1
    self.reconnect(func, *action)
   else:ui.note('Could not make a data connection, returning to menu', 'error');self.retry=0;self.disconnect(1)

 def disperr(self, e, action):
  if e[:3]=='421' or tuple(e)[0]==13:
   try:self.ftp.quit()
   except:pass
   self.reconnect(*action)
  elif e=="(13, 'Permission denied')":
   try:self.ftp.quit()
   except:pass
   self.reconnect(*action)
  elif e=="(32, 'Broken pipe')":
   ui.note(u'Unexpectly lost connection with '+self.host, 'error');reconn=ui.query(u'Reconnect?', 'query')
   if reconn==1:
    try:self.ftp.quit()
    except:pass
    self.reconnect(*action)
  else:ui.note(u(e), 'error');#print e

 def getwd(self,dirname=None):
  if not dirname:self.pwd=dr=self.ftp.pwd()
  else:dr=dirname
  self.l.addtext(u'Retrieving files', 1)
  s=StringIO.StringIO();self.ftp.retrbinary('LIST '+dr,s.write);s.seek(0);li=s.read();s.close();
  fs=[];l=[];a=li.split("\r\n");folder=ui.Icon(u(self.db.get('icons')), 115, 116);d=f=[];l.append((u'..', folder));self.amt=len(a)-1
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
     else:files.append((u(fs[I][9]),ui.Icon(u(self.db.get('icons')), 57, 58)))
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
 
 def chdir(self, dir,absolute=False):
  self.l.start()
  try:
   if dir=='..':self.ftp.cwd('..');self.l.addtext(u'Going up one', 1)
   else:
    if absolute:self.pwd=""
    self.l.addtext(u'changing directory to '+u(dir), 1);self.ftp.cwd(self.pwd+'/'+dir)
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
  self.l.start()
  self.submenu('d', 1, 2)
  if self.cbd[0]=='-':
   fh=StringIO.StringIO()
   self.ftp.retrbinary('RETR '+self.cbd[1]+self.cbd[2], fh.write)
   if self.cbd[3]=='cut':self.l.addtext(u'Deleting... '+u(self.cbd[1]+self.cbd[2]),1);self.ftp.delete(self.cbd[1]+self.cbd[2])
   fh.seek(0);self.l.addtext(u'Pasting '+u(self.cbd[2]),1)
   self.ftp.storbinary('STOR '+self.cbd[2],fh)
   fh.close()
  else:
   self.dirdict={}
   self.loopdir(self.cbd[1]+self.cbd[2])
   for dir in self.dirdict['dirlist']:
    try:
     self.l.addtext(u'Make directory '+u(dir),1)
     self.ftp.mkd(dir[len(self.cbd[1]):])
    except:pass
    for file in self.dirdict[dir]:
     self.l.addtext(u(dir+'/'+file),1)
     fh=StringIO.StringIO()
     self.ftp.retrbinary('RETR '+dir+'/'+file, fh.write);fh.seek(0)
     if self.cbd[3]=='cut':self.l.addtext(u'Deleting... '+u(dir+'/'+file),1);self.ftp.delete(dir+'/'+file)
     self.ftp.storbinary('STOR '+dir[len(self.cbd[1]):]+'/'+file,fh)
     fh.close()
   self.dirdict['dirlist'].reverse()
   if self.cbd[3]=='cut':
    for dir in self.dirdict['dirlist']:
     self.l.addtext(u'Deleting Directory... '+u(dir),1)
     self.ftp.rmd(dir)
  self.dispdir()

 def newdir(self):
  name=ui.query(u"New Folder", 'text')
  if not name==u'':self.l.addtext(u'Making Directory "'+name+'"',1);self.ftp.mkd(name);self.dispdir()

 def mkcache(self, pwd):
  try:
   cd='\\'+self.user+'@'+self.host
   cd=cd.strip()
   util.mkdir([self.db.get('cashe_dir')+cd])
   dir=self.db.get('cashe_dir')+cd+pwd
   util.mkdir([dir])
  except:ui.note(u'could not create cashe, downloading to save directory (set in settings)', 'error');dir=self.db.get('defaultdir')
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
   self.l.start()
   self.l.addtext(u'Downloading '+u(self.sel[9]), 1)
   self.mkcache(self.pwd)
   if self.sel[1][0]=='-':
    self.ftp.retrbinary('RETR '+self.sel[9], self.savelocal, self.db.get('blocksize', 'int'))
   else:self.downloaddir()
   if self.dcomp==1:ui.note(u'Download complete', 'conf');self.dcomp=0;del self.cache;self.l.stop()
  except all_errors, e:self.disperr(str(e), self.download)

 def downloaddir(self):
  self.dirdict={}
  self.loopdir(self.pwd+'/'+self.sel[9])
  del self.dirdict['dirlist']
  self._sel=self.sel
  for dir in self.dirdict:
   self.l.addtext(u'Make Directory '+u(dir),1)
   self.mkcache(dir)
   for file in self.dirdict[dir]:
    self.sel=['','','','','','','','','',file]
    self.l.addtext('Downloading '+u(file),1)
    self.ftp.retrbinary('RETR '+dir+'/'+file, self.savelocal, self.db.get('blocksize', 'int'))
  self.dcomp=1;self.sel=self._sel;del self._sel

 def upload(self, file=None):
  if file==None:file=ui.query(u'Please specify the path to the file', 'text')
  if os.path.exists(file):
   self.l.start()
   if zipfile.is_zipfile(file):
    if ui.query(u'Zipfile detected, extract contents to current directory?', 'query'):self.up_zip(file)
   else:
     f=open(file, 'r')
     try:
      n=f.name;
      self.l.addtext(u'Uploading '+u(n),1)
      n=replace_all(n, {'/':'\\'}).split('\\')
      self.ftp.storbinary('STOR '+n[len(n)-1], f, self.db.get('blocksize', 'int'))
      ui.note(u'Uploaded', 'conf', 1)
     except all_errors, e:
      self.disperr(str(e), [self.upload,file])
     f.close()
   self.dispdir()

 def up_zip(self, file):
  z=zipfile.ZipFile(file)
  wd=self.db.get('cashe_dir')+'\\'+self.user+'@'+self.host+replace_all(self.pwd, {'/':'\\'})+'\\';
  wd=wd.strip();
 # from urllib import quote
 # wd=quote(wd)
 #  del quote
  util.mkdir([wd])
  namelist=z.namelist()
  dirdict={'list':[]}
  for f in namelist:
   if f.endswith("/"):
    self.l.addtext(u'Make Directory '+u(f),1)
    util.mkdir([wd+f])
    self.ftp.mkd(f)
   else:
    fh=open(wd+f, 'w')
    fh.write(z.read(f))
    fh.close()
    fi=open(wd+f, 'r')
    self.l.addtext(u'Uploading '+u(f), 1)
    self.ftp.storbinary('STOR '+f, fi,self.db.get('blocksize', 'int'))
    fi.close()
  self.dispdir()

 def rename(self):
  frm=self.getsel()[9]
  self.ftp.rename(frm, ui.query(u'Rename '+u(frm), 'text', u(frm)))
  self.dispdir()

 def chmod(self):
  mode=ui.query(u"Mode", 'number')
  if not mode:return
  cmd="CHMOD "+str(mode)+" "+self.getsel()[9]
  ui.note(u(self.ftp.sendcmd(cmd)))

 def delete(self):
  self.sel=self.getsel()
  conf=ui.query(u"Delete "+self.sel[9]+"?", 'query')
  if conf==1:
   self.l.start()
   try:
    if not self.sel[1][0]=='d':self.l.addtext(u'Deleting '+u(self.sel[9]),1);self.ftp.delete(self.pwd+'/'+self.sel[9])
    else:
     try:self.l.addtext(u'Removing Directory '+u(self.sel[9]), 1);self.ftp.rmd(self.sel[9])
     except all_errors, e:
      if str(e)[:3]=='550':
       if ui.query(u'Driectory is not empty, delete all sub directories and files?', 'query')==1:
        self.dirdict={}
        self.loopdir(self.pwd+'/'+self.sel[9])
        self.dirdict['dirlist'].reverse()
        for dir in self.dirdict['dirlist']:
         for file in self.dirdict[dir]:
          self.l.addtext(u(dir+'/'+file),1)
          self.ftp.delete(dir+'/'+file)
         self.ftp.rmd(dir)
      else:raise e
    self.dispdir()
   except all_errors, e:self.disperr(str(e), [self.delete])
 def loopdir(self, initdir,**kwargs):
  obj=self.dirdict
  if 'object' in kwargs:obj=kwargs['object']
  if not 'dirlist' in obj:obj['dirlist']=[]
  obj['dirlist'].append(initdir)
  obj[initdir]=[]
  fn=self.getwd
  if 'fn' in kwargs:fn=kwargs['fn']
  fn(initdir)
  filelist=self.fs
  if 'filelist' in kwargs:filelist=kwargs['filelist']
  for file in filelist:
   if not file[9]=='..' and not file[9]=='.':
    if file[1][0]=='d':self.loopdir(initdir+'/'+file[9])
    else:obj[initdir].append(file[9])

 def retr(self):
  self.sel=self.getsel()
  fh=StringIO.StringIO()
  try:
   self.ftp.retrbinary('RETR '+self.sel[9], fh.write,self.db.get('blocksize', 'int'))
   fh.seek(0)
   return fh
  except all_errors, e:self.disperr(str(e), [self.retr])

 def new(self):
  self.sel=self.getsel()
  self.sel[9]=ui.query(u'New File', 'text')
  self.open(StringIO.StringIO())

 def open(self,f=None):
  def err(e):
   print e
   if e.errno==1:
    ui.note(u'Cannot open file for editing', 'error')
    if ui.query(u'Download '+self.sel[9]+u' instead?', 'query'):self.mkcache(self.pwd);self.savelocal(self.binary)
  def saveas(name,fh):
   self.sel[9]=name
   app.title=u(name)
   self.save(fh)
  if not f:f=self.retr()
  self.t.onexit=self.dispdir
  self.t.onsave=self.save
  self.t.onerror=err
  self.t.onsaveas=saveas
  self.t.readFile(f,self.sel[9])
  del f
  self.tabs.hide_tabs() #bug with cursor
  app.title=u(self.sel[9])
  
 def save(self, f):
  try:
   self.ftp.storbinary('STOR '+self.sel[9], f, self.db.get('blocksize', 'int'))
   f.close()
   ui.note(u'Saved!', 'conf', 1)
  except all_errors, e:
   self.disperr(str(e), [self.save, f])

 def disconnect(self,silent=False):
  try:
   if not silent:
    if not ui.query(u'Disconnect?','query'):return
    ui.note(u'Disconnecting...', 'info', 1)
    self.ftp.quit()
  except all_errors, error:
   if not silent:ui.note(u(error), 'error')
  self.tabs.delete_tab(self.name)
  self.tabs.select_tab(0,1)
  if self.connected:
   self.timer.stop()
   if not self.handler==fileftp:
    inf=self.db.get('acc_'+self.name,'list')
    if len(inf)==6:inf.append("")
    inf[6]=self.pwd
    self.db.mod('acc_'+self.name,inf)
   else:
    self.db.mod('file_last',[self.pwd])
  self.connected=False

if __name__=="__main__":
 tab=tabs()
 util=util()
 interface(util.db('cf')).run()
lk.wait()