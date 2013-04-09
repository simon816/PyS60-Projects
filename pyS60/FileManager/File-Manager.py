import appuifw as ui
import e32
from StringIO import StringIO
import os
import random
import ftplib
import zipfile
import graphics
import sys
from simon816 import encypher
from simon816.SyntaxHighlighter import SyntaxHighlighter
from simon816 import fileftp
from simon816 import loader
from simon816.tabs import tabs
from simon816 import text
from simon816 import timer
from simon816 import util
from simon816.eventhandler import eventHandler
# aliases
app=ui.app
lk=e32.Ao_lock()
u=lambda s:unicode(s)
util=util.util()
fileftp=fileftp.fileftp
global global_tabs;
global_tabs=tabs()
global_tabs.tabs=[]
global_tabs.callback=[]
text=text.text
editor=SyntaxHighlighter
Timer=timer.Timer
loader=loader.loader
FTP=ftplib.FTP
all_errors=ftplib.all_errors
error_reply=ftplib.error_reply
error_perm=ftplib.error_perm

class interface:
 def __init__(self):
  self.appname=u"File Manager"
  self.author=u"Simon816"
  self.url=u'http://simon816.hostzi.com/pys60/ftpbrowser'
  self.root="e:\\Python\\apps\\simon816\\ftpbrowser\\"
  dirfile=self.root+"db.dir"
  if os.path.exists(dirfile):
   db_dir_f=open(dirfile,"r")
   self.db_dir=db_dir_f.read()
   db_dir_f.close()
  else:
   self.ch_db_dir(self.root)
  self.db=util.db(self.db_dir+"db.e32dbm","cf")
  try: s=self.db.get('status')
  except:self.reset()
  self.exit(self.quit)

 def ch_db_dir(self,to):
  db_dir_f=open(self.root+"db.dir","w")
  db_dir_f.write(to)
  db_dir_f.close()
  self.db_dir=to

 def form(self, args):
  return [(u'Connection Name', 'text', args[0]), (u'Host', 'text',args[1]),(u'Port', 'number', args[2]), (u'Username', 'text', args[3]), (u'Password', 'text', args[4]), (u'Initial Directory', 'text', args[5]), (u'Passive Mode', 'combo', ([u'True', u'False'], args[6]))]

 def decodestring(self,s,a):return encypher.decode(str(s[int(float(s[:1]))+1:]),int(float(a.find(s[1:2])+1)),self.db.get('a'))
 def encodestring(self,s, a):K=random.randint(1,len(a)-1);k=encypher.encode(str(K), K,self.db.get('a'),'', 'a');return  encypher.encode(s, K,self.db.get('a'), str(len(k))+k)

 def reset(self):
  try:
   for entry in self.db.items():
    if entry[0].find('acc_')==-1: self.db.delete(entry[0])
   self.db.mod('settings_dir', 'e:\\python\\apps\\simon816\\ftpbrowser')
   self.db.mod('cache_dir', self.db.get('settings_dir')+'\\cache')
   self.db.mod('version', '0.9.0')
   self.db.mod('defaultdir', 'e:\\')
   self.db.mod('color', (0,0,0))
   self.db.mod('font', (u"nokia hindi s60",14,16))
   self.db.mod('blocksize', '8192')
   self.db.mod('icons', "e:\\mbm.mbm")
   self.db.mod('status', 'ready')
   self.db.mod('debug', 'False')
   self.db.mod('a', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\t')
   self.db.mod("temp_timeout",60)
   self.db.mod('ticks','0.01')
   ui.note(u'Successfully reset', 'conf')
  except:
   ui.note(u'error', 'error')

 def quit(self):
  try:self.db.sync();self.db.close();
  except:print sys.exc_info()
  lk.signal();self.tabs.hide_tabs()
  self.exit(sys.exit)
 def exit(self, action):app.exit_key_handler=action
 def disp(self, cback):return ui.Listbox(self.interface, cback)
 def dummy(self):pass

 def about(self):
  ui.note(u'A FREE '+self.appname+' by '+self.author+'\nFor more info, please visit:'+self.url+'\nCurrent version: '+self.db.get('version'))

 def run(self):
  util.mkdir([self.db.get('settings_dir'), self.db.get('cache_dir')])
  self.tabs=global_tabs
  self.tabs.tabs=[]
  self.tabs.new_tab(u'Home',self.mainscr)
  self.mainscr()

 def mainscr(self):
  self.exit(self.quit)
  self.menu=[
   (u'Select', self.handle),
   (u'About', self.about),
   (u'Reset', self.reset),
   (u'Exit', self.quit)]
  self.interface=[
   u'FTP File Browser',u'Local File Browser', u'Settings', u'Setup'
   ]
  app.menu=self.menu
  app.body=self.disp(self.handle)
  app.title=self.appname


 def activate(self):
  c=app.body.current()
  if c==0:self.newcon()
  else:
   name=self.connections[c]
   opts=self.db.get('acc_'+name, 'list')
   ftp=ftpclass(self.db)
   ftp.connect(name,opts)
 def handle(self):
  c=app.body.current()
  if c==0:self.conscr()
  elif c==1:
   def icon(pos):#temparty solution
    return ui.Icon(u(self.db.get('icons')), pos, pos+1)
   self.exit(self.mainscr)
   self.interface=[]
   sys_drives=['C:','D:','Z:']
   for d in e32.drive_list():
    if d in sys_drives:ico=icon(397)
    else:ico=icon(395)
    self.interface.append((u(d),ico))
   #recent places
   self.interface.append((u"Recent Places:",icon(8)))
   recent=self.db.get("file_last","list")
   for place in recent:
    if place:self.interface.append((u(place),icon(115)))
   app.body=self.disp(self.file)
  elif c==2:self.settings()
  elif c==3:self.setup()
  else:pass

 def file(self, drive=None,inidir=""):
  sel=self.interface[app.body.current()][0]
  if drive:sel=drive
  if sel in e32.drive_list():
   drive=sel[:1]
   ftpclass(self.db).connect('File Browser > '+drive,['LocalUser','21',drive,'1a', inidir, 1],fileftp)
  else:
   if sel=="Recent Places:":return
   self.file(*os.path.splitdrive(sel))

 def conscr(self):
  self.exit(self.mainscr)
  self.menu=[
   (u'Connect', self.activate),
   (u'New', self.newcon),
   (u'Edit', self.editcon),
   (u'Delete', self.delcon),
   (u'Export...', self.export),
   (u'Import', self._import)
    ]
  self.connections=[u'[New Connection]']
  l=[]
  for arr in self.db.items():
   if not arr[0].find('acc_')==-1:
    l.append(u(arr[0][4:]))
  l.sort(lambda x, y: cmp(x.lower(),y.lower()));self.connections+=l
  self.interface=self.connections
  app.body=self.disp(self.activate)
  app.menu=self.menu
  app.title=u'Connect to...'

 def settings(self):
  self.interface=[
   (u'Settings Directory', u(self.db.get('settings_dir'))),
   (u'Default Directory', u(self.db.get('defaultdir'))), 
   (u'Cache Directory', u(self.db.get('cache_dir')))]
  app.body=self.disp(self.set)
  self.exit(self.mainscr)

 def set(self):
  i=app.body.current()
  setting=self.interface[i][0]
  if setting.endswith("Directory"):
   newdir=util.select("dir",self.interface[i][1])
   if newdir:
    if    i==0:self.db.mod('settings_dir',newdir)
    elif i==1:self.db.mod('defaultdir',newdir)
    elif i==2:self.db.mod('cache_dir',newdir)

 def setup(self):
  self.exit(self.mainscr)
  self.interface=[
   (u'Debug Mode', u(self.db.get('debug'))),
   (u'Database Directory', u(self.db_dir)),
   (u'Alphabet string', u(self.db.get('a'))),
   (u'Cache Directory Trees', u(self.db.get("dir_tree")))]
  app.body=self.disp(self.chset)

 def chset(self):
  c=app.body.current()
  if c==0:
   debug=ui.popup_menu([u'False', u'True'])
   if debug:
    self.db.mod('debug', debug)
  elif c==1:
   dir=util.select("dir",self.db_dir)
   if dir:
    self.ch_db_dir(dir)
  elif c==2:
   a=ui.query(u'Alphabet string', 'text',u(self.db.get('a')))
   if a:self.db.mod('a', a)
  elif c==3:
   tree=ui.popup_menu([u'False', u'True'])
   if tree is not None:
    self.db.mod('dir_tree', tree)
  self.setup()


 def newcon(self):
  f=self.form([u'',u'',21,u'',u'', u'/', 0])
  f=ui.Form(f, 17)
  f.execute()
  self.savecon(f, 'true')

 def editcon(self):
  name=self.interface[app.body.current()]
  data=self.db.get('acc_'+name, 'list')
  form=self.form([
   u(name),
   u(data[0]),
   int(float(data[1])),
   u(data[2]),
   u(self.decodestring(data[3],self.db.get('a'))),
   u(data[4]),
   int(data[5])
   ])
  f=ui.Form(form, 17)
  f.save_hook=self.savecon
  f.execute()

 def savecon(self, f, dele=0):
   if f[0][2]==u'' or f[1][2]==u'':
    ui.note(u'Not enough data provided', 'error')
    return
   account=[]
   for opt in f:
    account.append(opt[2])
    if opt[0]=="Password":
     account[-1]=self.encodestring(opt[2], self.db.get('a'))
    if opt[0]=="Passive Mode":
     account[-1]=opt[2][1]
   del account[0]
   self.db.mod('acc_'+f[0][2], account)
   if dele:self.delcon(1)
   ui.note(u'Saved', 'conf')
   self.conscr()

 def delcon(self,ok=0):
  name=self.interface[app.body.current()]
  if not ok:
   ok=ui.query(u'Are you sure you want to delete "'+name+'"?', 'query')
  if ok==1:
   self.db.delete('acc_'+name)
   self.connections.pop(app.body.current())
  self.conscr()

 def export(self):
  name=self.interface[app.body.current()]
  if name=="[New Connection]":return
  dir=util.select("dir",self.db.get("defaultdir"))
  if dir:
   f=open(dir+name+".acc","w")
   f.write("\n".join(self.db.get("acc_"+name,"list")))
   f.close()
   ui.note(u"Successfully exported as '"+u(name)+u".acc'","conf")
 def _import(self):
  acc=util.select("file",self.db.get("defaultdir"),extwhitelist=["acc"])
  if not acc:return
  name=os.path.splitext(os.path.split(acc)[1])[0]
  f=open(acc);d=f.read();f.close()
  self.db.mod("acc_"+name,d.split("\n"))
  self.conscr()

class ftpclass:
 def __init__(self, db):
  self.db=db
  self.list=ui.Listbox([u''],lambda:None)
  self.event=eventHandler()
  self.connected=False
  self.t=editor()
  self.t.highlighter()
  self.t.inherit_indent()
 def dummy(self,*args):pass
 def exit(self, action):app.exit_key_handler=action
 def disp(self, cback,index=0):
  try:
   self.list.set_list(self.interface, index)
   self.list.bind(0,cback)
  except ValueError:
   self.list=ui.Listbox(self.interface, cback)
  return self.list
 def cmd(self, action, *arguments,**control):
  function=getattr(self.ftp,action)
  opts=""
  evtid=self.event.add_event(function,opts,arguments)
  sleeptime=float("0")
  while not self.event.isready(evtid) and sleeptime<5:
   e32.ao_sleep(float(self.db.get("ticks")))
   sleeptime=float(self.db.get("ticks"))+sleeptime
  if sleeptime>=5:
   self.ftp.quit()
   self.disconnect(False,False,True)
   return
  if 'callback' in control:
   control['callback'](self.event.get_response(evtid))
  else:
   return self.event.get_response(evtid)
 def login(self,ftpMgr,opts=None,chdir=True):
  if opts:self.opts=opts
  opts=self.opts
  self.user=str(opts[2]);self.host=str(opts[0]);
  self.handler=ftpMgr
  self.ftp=ftpMgr()
  #if ftpMgr==fileftp:return 1
  if int(opts[5])==0:pasvmode=True
  else:pasvmode=False
  try:
   self.ftp.connect(self.host, int(float(opts[1])))
   self.ftp.set_pasv(pasvmode)
   self.ftp.login(self.user, i.decodestring(opts[3], self.db.get('a')))
   self.l=loader(graphics.Image.open('e:\\Python\\apps\\simon816\\ftpbrowser\\loading.gif'),100);self.pwd=''
   self.l.wait=float(self.db.get('ticks'))
   if chdir:self.chdir(str(opts[4]))
   return 1
  except all_errors[1], e:
   #print sys.exc_info()
   ui.note(u'could not connect\n'+u(e), 'error')
   self.disconnect(1,1);
  except all_errors[0], e:
   ui.note(u'could not login\n(Bad username/password)', 'error')
   self.disconnect(1)

 def connect(self,name,opts,ftp=FTP):
  self.tabs=global_tabs
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
     (u'Mark/Select',self.mark),
     (u'Timer Toggle',self.time_toggle),
     (u'Event queue',self.pr_ev),
     (u'Send Command', self.sendcmd),
     (u'Disconnect', self.disconnect)
   ]
   app.menu=self.menu
   def ping(elapsed):self.cmd("pwd")
   self.timer=Timer(ping)
   self.t_on=1
   self.time_start()
 def time_start(self):
  self.timer.start(self.db.get("temp_timeout","int"))
 def time_toggle(self):
  if self.t_on:
   self.timer.stop()
   self.t_on=0
  else:
   self.t_on=1
   self.time_start()

 def pr_ev(self):
  print self.event.queue
  print self.event.wait_queue
  print self.event.responses

 def changepath(self):
  self.chdir(ui.query(u'Path','text', u(self.pwd)),True)

 def sendcmd(self):
  print self.cmd("sendcmd",ui.query(u'Command','text'))

 def refresh(self):self.l.start();self.dispdir()

 def dispdir(self,dontUpdate=False,i=0):
  try:
   self.tabs.update()
   if not dontUpdate:self.interface=self.getwd()
   t=self.tabs;s=t.selected;c=t.current
   if c()==self.name or s==0:
    app.body=self.disp(self.actions,i)
    app.title=u(self.pwd)
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
  if not dirname:self.pwd=dr=self.cmd("pwd")
  else:dr=dirname
  self.l.addtext(u'Retrieving files', 1)
  if self.db.get("dir_tree","int"):
   if not "tree" in dir(self):self.tree=dict()
   if dr in self.tree:
    self.fs=self.tree[dr]["fs"]
    return self.tree[dr]["l"]
  s=StringIO();
  self.cmd("retrbinary",'LIST '+dr,s.write);
  s.seek(0);li=s.read();s.close();
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
  if self.db.get("dir_tree","int"):
   self.tree[dr]={}
   self.tree[dr]["fs"]=fs
   self.tree[dr]["l"]=l
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
   if dir=='..':
    self.cmd("cwd",'..')
    self.l.addtext(u'Going up one', 1)
   else:
    if absolute:self.pwd=""
    self.l.addtext(u'changing directory to '+u(dir), 1)
    self.cmd("cwd",self.pwd+'/'+dir)
   self.dispdir()
  except all_errors, e:self.disperr(str(e), [self.chdir, dir])

 def fileinfo(self):
  def apprsize(bytes):
    if bytes < 1024:return ""
    for bytename in ["K","M","G","T","P"]:#challenge: legitly return Petabytes!
     bytes=bytes/1024
     if bytes < 1024:return ' (%s%sB)'%(bytes,bytename)
  info=self.getsel()[1:11]
  dinfo={}
  info[0]="".join(info[0])
  labels=["Permissions","A number","User","Group","Size","Month","Day","Time","Name"]
  for i in range(0,9):dinfo[labels[i]]=info[i]
  dinfo["File Type"]=dinfo['Year']=''
  ex=os.path.splitext(dinfo["Name"])
  dinfo["Name"]=ex[0]
  if ex[1]:dinfo["File Type"]=ex[1][1:].upper()+" File"
  if dinfo['Time'].find(':')==-1:
   dinfo['Year']=dinfo['Time']
   dinfo['Time']=''
  form=[]
  order=["Name","File Type","Size",{'Date':["Time",'Day','Month','Year']},"User","Group","Permissions"]
  for titles in order:
   e=0
   if not type(titles)==dict:titles={titles:[titles]}
   label=titles.keys()[0]
   text=""
   for title in titles[label]:
    if dinfo[title]:text+=dinfo[title]+" ";e=1
    if title=="Size":
     text+="B"+apprsize(int(dinfo['Size']))
   if e:form.append((u(label),'text',u(text)))
  f=ui.Form(form,18)
  f.execute()

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
  if not util.submenu('r', 1, 'Paste'):self.submenu('a', 1, 2, (u'Paste', self.paste))

 def copy(self):
  self.sel=self.getsel()
  self.cbd=[self.sel[1][0],self.pwd+'/',self.sel[9], 'copy']
  if not util.submenu('r', 1, 'Paste'):self.submenu('a', 1, 2, (u'Paste', self.paste))

 def paste(self):
  abspath=self.cbd[1]+self.cbd[2]
  for f in self.fs:
   if f[9]==self.cbd[2]:
    q=ui.query(u"%s already exists, rename:"%self.cbd[2],"text",u(" (Copy)".join(os.path.splitext(self.cbd[2]))))
    if not q:return
    self.cbd[2]=q
  util.submenu('d', 1, 2)
  self.l.start()
  if self.cbd[0]=='-':
   fh=StringIO()
   self.cmd("retrbinary",'RETR '+abspath, fh.write)
   if self.cbd[3]=='cut':
    self.l.addtext(u'Deleting... '+u(abspath),1)
    self.cmd("delete",abspath)
   fh.seek(0);self.l.addtext(u'Pasting '+u(self.cbd[2]),1)
   self.cmd("storbinary",'STOR '+self.cbd[2],fh)
   fh.close()
  else:
   self.dirdict={}
   self.loopdir(abspath)
   for dir in self.dirdict['dirlist']:
    try:
     self.l.addtext(u'Make directory '+u(dir),1)
     self.cmd("mkd",self.cbd[2]+dir[len(abspath):])
    except:pass
    for file in self.dirdict[dir]:
     self.l.addtext(u(dir+'/'+file),1)
     fh=StringIO()
     self.cmd("retrbinary",'RETR '+dir+'/'+file, fh.write);fh.seek(0)
     if self.cbd[3]=='cut':
      self.l.addtext(u'Deleting... '+u(dir+'/'+file),1)
      self.cmd("delete",dir+'/'+file)
     self.cmd("storbinary",'STOR '+self.cbd[2]+dir[len(abspath):]+'/'+file,fh)
     fh.close()
   self.dirdict['dirlist'].reverse()
   if self.cbd[3]=='cut':
    for dir in self.dirdict['dirlist']:
     self.l.addtext(u'Deleting Directory... '+u(dir),1)
     self.cmd("rmd",dir)
  self.dispdir()

 def mark(self):
  files=[u(info[9]) for info in self.fs]
  sel=ui.multi_selection_list(files,search_field=1)
  if not sel:return
  choice=ui.popup_menu([
   u'Copy (N/I)!',
   u'Cut (N/I)!',
   u'Delete',
   u'Download',
   u'Rename'
  ],u'Do with selected:')
  if choice is None:self.mark()
  update=0
  if choice==2:
   if not ui.query(u'Delete %d file(s)'%len(sel),'query'):return
   update=1
   self.l.start()
   for i in sel:
    fn=files[i]
    self.l.addtext('deleting '+fn,1)
    try:self.cmd('delete', fn)
    except:pass #need to open self.delete up to allow probing like this
  if choice==3:
   pass
  if choice==4:
   pass
  self.l.stop()
  if update:
   self.dispdir()

 def newdir(self):
  name=ui.query(u"New Folder", 'text')
  if not name==u'':
   self.l.addtext(u'Making Directory "'+name+'"',1)
   self.cmd("mkd",name)
   self.dispdir()

 def mkcache(self, pwd):
  try:
   cd='\\'+self.user+'@'+self.host
   cd=cd.strip()
   util.mkdir([self.db.get('cache_dir')+cd])
   dir=self.db.get('cache_dir')+cd+pwd
   util.mkdir([dir])
  except:ui.note(u'could not create cache, downloading to save directory (set in settings)', 'error');dir=self.db.get('defaultdir')
  self.cache=dir

 def savelocal(self, block):
  try:
   try:f=open(self.cache+'\\'+self.sel[9], 'ab')
   except:f=open(self.cache+'\\'+self.sel[9], 'w')
   f.write(block)
   f.close()
   self.dcomp=1
  except:ui.note(u'Could not download file. read only access?\nAborting transfer', 'error');self.cmd("abort")
  #self.ftp.sendcmd('type a')

 def download(self):
  self.pwd=self.cmd("pwd")
  self.sel=self.getsel()
  try:
   self.l.start()
   self.l.addtext(u'Downloading '+u(self.sel[9]), 1)
   self.mkcache(self.pwd)
   if self.sel[1][0]=='-':
    self.cmd("retrbinary",'RETR '+self.sel[9], self.savelocal, self.db.get('blocksize', 'int'))
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
    self.cmd("retrbinary",'RETR '+dir+'/'+file, self.savelocal, self.db.get('blocksize', 'int'))
  self.dcomp=1;self.sel=self._sel;del self._sel

 def upload(self, file=None):
  if file==None:file=util.select()
  if file:
   self.l.start()
   if zipfile.is_zipfile(file):
    if ui.query(u'Zipfile detected, extract contents to current directory?', 'query'):
     self.up_zip(file)
   else:
     f=open(file, 'r')
     try:
      n=f.name;
      self.l.addtext(u'Uploading '+u(n),1)
      n=n.replace('/','\\').split('\\')
      self.cmd("storbinary",'STOR '+n[len(n)-1], f, self.db.get('blocksize', 'int'))
      ui.note(u'Uploaded', 'conf', 1)
     except all_errors, e:
      self.disperr(str(e), [self.upload,file])
     f.close()
   self.dispdir(0,app.body.current())

 def up_zip(self, file):
  z=zipfile.ZipFile(file)
  wd=self.db.get('cache_dir')+'\\'+self.user+'@'+self.host+self.pwd.replace('/','\\')+'\\';
  wd=wd.strip();
  util.mkdir([wd])
  namelist=z.namelist()
  dirdict={'dirlist':[]}
  #do same as loopdir
  for f in namelist:
   path,filename=os.path.split(f)
   if not path in dirdict:
    dirdict[path]=[]
    dirdict['dirlist'].append(path)
   dirdict[path].append(filename)
  dirdict['dirlist'].reverse()
  print dirdict
  for dir in dirdict['dirlist']:
   dir+="/"
   if dir is not "/":
    self.l.addtext(u'Make Directory '+u(dir),1)
    util.mkdir([wd+dir])
    self.cmd("mkd",dir)
   else:dir=""
   for f in dirdict[dir[:-1]]:
    fh=open(wd+dir+f, 'w')
    fh.write(z.read(dir+f))
    fh.close()
    fi=open(wd+dir+f, 'r')
    self.l.addtext(u'Uploading '+u(f), 1)
    self.cmd("storbinary",'STOR '+dir+f, fi,self.db.get('blocksize', 'int'))
    fi.close()
  z.close()

 def rename(self):
  frm=self.getsel()[9]
  self.cmd("rename",frm, ui.query(u'Rename '+u(frm), 'text', u(frm)))
  self.dispdir(0,app.body.current())

 def chmod(self):
  mode=ui.query(u"Mode", 'number')
  if not mode:return
  cmd="CHMOD "+str(mode)+" "+self.getsel()[9]
  ui.note(u(self.cmd("sendcmd",cmd)))

 def delete(self):
  self.sel=self.getsel()
  conf=ui.query(u"Delete "+self.sel[9]+"?", 'query')
  if conf==1:
   self.l.start()
   try:
    if not self.sel[1][0]=='d':self.l.addtext(u'Deleting '+u(self.sel[9]),1);self.cmd("delete",self.pwd+'/'+self.sel[9])
    else:
     try:self.l.addtext(u'Removing Directory '+u(self.sel[9]), 1);self.cmd("rmd",self.sel[9])
     except all_errors, e:
      if str(e)[:3]=='550':
       if ui.query(u'Driectory is not empty, delete all sub directories and files?', 'query')==1:
        self.dirdict={}
        self.loopdir(self.pwd+'/'+self.sel[9])
        self.dirdict['dirlist'].reverse()
        for dir in self.dirdict['dirlist']:
         for file in self.dirdict[dir]:
          self.l.addtext(u(dir+'/'+file),1)
          self.cmd("delete",dir+'/'+file)
         self.cmd("rmd",dir)
      else:raise e
    self.dispdir(0,app.body.current())
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
    #print file
    if file[1][0]=='d':self.loopdir(initdir+'/'+file[9])
    else:obj[initdir].append(file[9])

 def retr(self):
  self.sel=self.getsel()
  fh=StringIO()
  try:
   self.cmd("retrbinary",'RETR '+self.sel[9], fh.write,self.db.get('blocksize', 'int'))
   fh.seek(0)
   return fh
  except all_errors, e:self.disperr(str(e), [self.retr])

 def new(self):
  self.sel=self.getsel()
  self.sel[9]=ui.query(u'New File', 'text')
  self.open(StringIO())

 def text_err(self,e,f):
   if e[0]==1:
    f.seek(0)
    if ui.query(u'Binary file. Open anyway?', 'query')==1:
     self.open(f,True)
    elif ui.query(u'Download '+self.sel[9]+u' instead?', 'query')==1:
     self.mkcache(self.pwd)
     self.savelocal(f.read())
    else:
     pass

 def open(self,f=None,ig=False):
  config={
   'font':self.db.get('font', 'tuple'),
   'color':self.db.get('color', 'tuple'),
   'chunkbytes':self.db.get('blocksize', 'int')
   }
  def saveas(name,fh):
   self.sel[9]=name
   app.title=u(name)
   self.save(fh)
  def save_settings(s):
   self.db.mod('font', s['font'])
   self.db.mod('color',s['color'])
  if not f:f=self.retr()
  self.t.bind('exit',self.dispdir,[1,app.body.current()])
  self.t.bind('save',self.save)
  self.t.bind('saveas',saveas)
  self.t.bind('error',self.text_err,[f])
  self.t.bind("get_settings",lambda:config)
  self.t.bind("set_settings",save_settings)
  self.t.bind("get_css",lambda:{})
  self.t.bind("set_css",lambda c:None)
  if self.t.readFile(f,self.sel[9],ig):
   self.tabs.hide_tabs()
   app.title=u(self.sel[9])
  
 def save(self, f):
  try:
   self.cmd("storbinary",'STOR '+self.sel[9], f, self.db.get('blocksize', 'int'))
   f.close()
   ui.note(u'Saved!', 'conf', 1)
  except all_errors, e:
   self.disperr(str(e), [self.save, f])

 def disconnect(self,silent=False,noconnection=False,forced=False):
  if noconnection:i.conscr();return
  try:
   if not silent:
    if not ui.query(u'Disconnect?','query'):return
    ui.note(u'Disconnecting...', 'info', 1)
    if not forced:self.cmd("quit")
  except all_errors, error:
   if not silent:ui.note(u(error), 'error')
  if self.connected:
   self.timer.stop()
   if not self.handler==fileftp:
    inf=self.db.get('acc_'+self.name,'list')
    if len(inf)==6:inf.append("")
    inf[6]=self.pwd
    self.db.mod('acc_'+self.name,inf)
   else:
    last=self.db.get("file_last","list")
    fulldir=self.user+":"+self.pwd
    if fulldir in last:del last[last.index(fulldir)]
    last.insert(0,fulldir)
    if len(last)>5:last=last[:5]
    self.db.mod('file_last',last)
  self.connected=False
  self.tabs.delete_tab(self.name)
  self.tabs.select_tab(0,1)

i=interface()
i.run()
lk.wait()