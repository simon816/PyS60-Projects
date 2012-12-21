import appuifw as ui, e32, StringIO, os, zipfile, e32dbm, random, graphics
from sysinfo import display_pixels as scr
from topwindow import TopWindow
from ftplib import all_errors
app=ui.app;lk=e32.Ao_lock();
def u(u):
 try:u=unicode(u)
 except:u=unicode('!error!')
 return u
def replace_all(text, dic):
 for i, j in dic.iteritems():
  text = text.replace(i, j)
 return text

class Error(Exception):pass
class error_perm(Error):pass
class error_reply(Error):pass
all_errors = (Error, IOError, EOFError)
def T():return str(localtime().tm_hour)+':'+str(localtime().tm_min)+':'+str(localtime().tm_sec)
from StringIO import StringIO as tmpfile
from time import localtime, time
from stat import *
class file:
 def __init__(self, host=''):
  mode='a'
  if not os.path.exists('e:\\Python\\apps\\simon816\\ftpbrowser\\logs\\'+str(localtime().tm_yday)+'.log'):mode='w'
  self.log=open('e:\\Python\\apps\\simon816\\ftpbrowser\\logs\\'+str(localtime().tm_yday)+'.log', mode)
  #self.log=open('e:\\Python\\apps\\simon816\\ftpbrowser\\logs\\'+str(time())[:-2]+'.log', 'w')
  self.log.write('\r\n'+str(localtime().tm_yday)+'-'+T()+'\r\n')
  if host:self.connect(host)
  self.host=None
 def connect(self, host,*args):
  if host in ['localhost', '127.0.0.1']:
   self.host=host;return 'Welcome to pyFTP emulator by Simon816'
  self.log.close()
 def set_debuglevel(self, *args):pass
 def set_pasv(self, *args):pass
 def abort(self, *args):pass
 def sendcmd(self, cmd):
  if not self.host:self.log.close();raise 'error';return 0
  resp=''
  self.log.write(T()+'  '+cmd+'\r\n')
  allcmds=['RETR', 'STOR', 'LIST', 'NLST', 'RNFR', 'RNTO', 'DELE', 'CDUP', 'CWD', 'SIZE', 'MKD', 'RMD', 'PWD', 'QUIT', 'HELP']
  if cmd[:3] in allcmds:
   if cmd[:3]=='CWD':os.chdir(cmd[4:]);self.wd=replace_all(os.getcwd(), {'\\':'/'})
   if cmd[:3]=='PWD':self.wd=replace_all(os.getcwd(), {'\\':'/'})[:-1];return self.wd
   if cmd[:3]=='MKD':os.mkdir(cmd[4:])
   if cmd[:3]=='RMD':
    try:os.rmdir(cmd[4:])
    except OSError, e:
     if e.errno==17:raise error_reply, '550 Directory not empty.'
  elif cmd[:4] in allcmds:
   if cmd[:4]=='DELE':os.unlink(cmd[5:])
   if cmd[:4]=='CDUP':os.chdir('..');self.wd=replace_all(os.getcwd(), {'\\':'/'})
   if cmd[:4]=='RNFR':self.tmp=cmd[5:]
   if cmd[:4]=='RNTO':
    if self.tmp:os.rename(self.tmp, cmd[5:])
   if cmd[:4]=='SIZE':resp=os.path.getsize(self.pwd()+cmd[4:])
   if cmd[:4]=='NLST':
    fp=tmpfile();s=''
    for l in os.listdir(cmd[5:]):s+=l+'\n'
    fp.write(s);fp.seek(0)
    resp= fp
   if cmd[:4]=='RETR':
    try:resp=open(cmd[5:], 'r')
    except IOError, e:
     if e.errno==13: raise error_perm, '550 No such file or directory.'
   if cmd[:4]=='STOR':resp=open(self.wd+'/'+cmd[5:], 'w')
   if cmd[:4]=='LIST':
    f=tmpfile()
    if len(cmd)<6:dir=self.wd
    else:dir=self.drive+':'+cmd[5:]+'\\'
    for file in os.listdir(dir):
     st=os.stat(dir+file);d='-'
     time=localtime(st.st_mtime)
     mon=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
     r=oct(S_IMODE(st[0]))
     if len(r)==4:r=r[1:]
     if S_ISDIR(st[0]):p='d'
     else:p='-'
     for i in range(len(r)):
      if r[i]=='0':p+='---'
      elif r[i]=='1': p+='--x'
      elif r[i]=='2': p+= '-w-'
      elif r[i]=='3': p+='-wx'
      elif r[i]=='4': p+='r--'
      elif r[i]=='5': p+='r-x'
      elif r[i]=='6': p+='rw-'
      elif r[i]=='7': p+= 'rwx'
     f.write(p+'    2 '+str(st.st_uid)+'   '+str(st.st_gid)+'         '+str(st.st_size)+' '+mon[time[1]-1]+' '+str(time.tm_mday)+' '+str(time.tm_hour)+':'+str(time.tm_min)+' '+file+'\r\n')
    f.seek(0);resp=f
   if cmd[:4]=='QUIT':resp='Goodbye'
   if cmd[:4]=='HELP':resp=allcmds
  #self.log.write(str(resp)+'\r\n')
  return resp
 def retrbinary(self,cmd,callback,blocksize=8192,rest=None):
  resp=self.sendcmd(cmd)
  while 1:
   data=resp.read(blocksize)
   if not data:
    break
   callback(data)
  resp.close()
 def sendport(self, *args):pass
 def login(self,  *args):self.drive=args[0];self.cwd(args[0]+':')
 def retrlines(self,cmd,callback=None):
  if not callback:callback=print_line
  resp=self.sendcmd(cmd)
  while 1:
   line=resp.readline()
   if not line:
    break
   if line[-1:]=='\n':
    line=line[:-1]
   callback(line)
  resp.close()
 def storbinary(self,cmd,fp,blocksize=8192):
  resp=self.sendcmd(cmd)
  while 1:
   buf=fp.read(blocksize)
   if not buf:break
   resp.write(buf)
  resp.close()
 def storlines(self,cmd,fp):
  resp=self.sendcmd(cmd)
  while 1:
   buf=fp.readline()
   if not buf:break
   resp.write(buf)
  resp.close()
 def nlst(self, dir=None):
  if dir==None:dir=self.pwd()
  files=[]
  self.retrlines('NLST '+dir, files.append)
  return files
 def dir(self, dir='', cback=None):
  self.retrlines('LIST '+dir, cback)
 def rename(self, fromname, toname):
  self.sendcmd('RNFR '+fromname)
  self.sendcmd('RNTO '+toname)
 def delete(self, filename):
  self.sendcmd('DELE '+filename)
 def cwd(self,dirname):
  if dirname == '..':
   try:
    return self.sendcmd('CDUP')
   except error_perm, msg:
    if msg[:3] != '500':
     raise error_perm, msg
  elif dirname == '':
   dirname = '.' 
  cmd = 'CWD ' + dirname
  return self.sendcmd(cmd)
 def size(self, filename):
  self.sendcmd('SIZE '+filename)
 def mkd(self, dirname):
  self.sendcmd('MKD '+dirname)
 def rmd(self, dirname):
  self.sendcmd('RMD '+dirname)
 def pwd(self):
  return self.sendcmd('PWD')[2:]
 def getwelcome(self):return self.connect(self.host)
 def quit(self):
  self.sendcmd('QUIT')
  self.log.close()
 def print_line(line):print line

class loader:
 def __init__(self,img,ani_xy=100):
  self.ani_xy=ani_xy
  self.img=img.resize((self.ani_xy,self.ani_xy))
  self.gif=TopWindow()
  self.gif.size=(ani_xy, ani_xy)
  self.gif.position=self.get_mid((ani_xy,ani_xy))
  self.txt=TopWindow()
  self.blank=graphics.Image.new((1,1))
  self.ani_xy=ani_xy
 def get_mid(self, d):
  return ((scr()[0]-d[0])/2,(scr()[1]-d[1])/2)
 def addtext(self,text,update=0):
  size=self.img.measure_text(text)
  t_w,t_h=(size[0][2],(size[0][1]*-1)+size[0][3])
  self.text=graphics.Image.new((t_w,t_h))
  self.text.text((0,12), text)
  self.txt.size=(t_w,t_h)
  mid=self.get_mid((t_w,self.ani_xy))
  self.txt.position=(mid[0],mid[1]+self.ani_xy)
  if update:self.disp_text()
 def rotate(self):
  e32.ao_sleep(0.01)
  self.gif.remove_image(self.img, (0,0))
  self.img=self.img.transpose(graphics.ROTATE_90)
  self.gif.add_image(self.img, (0,0))
 def start(self):
  self.gif.show()
  self.txt.show()
 def stop(self):
  self.gif.hide()
  self.txt.hide()
 def disp_text(self):
  #self.txt.add_image(self.blank,(0,0))
  try:self.txt.remove_image(self.text);
  except ValueError,e:pass#print 'not removed e='+str(e)
  self.txt.images=[]
  self.txt.add_image(self.text,(0,0))
  self.gif.add_image(self.img, (0,0))
  del self.text
  self.rotate()

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
  return [(u'Connection Name', 'text', args[0]), (u'Host', 'text',args[1]),(u'Port', 'number', args[2]), (u'Username', 'text', args[3]), (u'Password', 'text', args[4]), (u'Initial Directory', 'text', args[5]), (u'Passive Mode', 'combo', ([u'True', u'False'], args[6]))]

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

 def quit(self):self.db.sync();self.db.close();lk.signal();self.tabs.hide_tabs()
 def exit(self, action):app.exit_key_handler=action
 def disp(self, cback):return ui.Listbox(self.interface, cback)
 def dummy(self):pass

 def about(self):
  ui.note(u'A FREE '+self.appname+' by '+self.author+'\nFor more info, please visit:'+self.url+'\nCurrent version: '+self.get_db('version'))

 def run(self):
  self.mkdir([self.get_db('settings_dir'), self.get_db('account_dir'), self.get_db('cashe_dir')])
  self.tabs=tabs()
  self.tabs.new_tab(u'Home',self.mainscr)
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
  f=self.form([u'',u'',21,u'',u'', u'/', 0])
  f=ui.Form(f, 17)
  f.execute()
  self.savecon(f, 'true')

 def editcon(self):
  name=self.interface[app.body.current()]
  if self.get_db('mode')=='flatfile':f=open(self.get_db('account_dir')+'\\'+name+'.acc');data=f.read();f.close();data=data.split('\n')
  elif self.get_db('mode')=='SQL':data=self.get_db('acc_'+name, 'list')
  if data[5]=='true':p=0
  else: p=1
  form=self.form([u(name),u(data[0]),int(float(data[1])),u(data[2]),u(self.decodestring(data[3],self.get_db('a'))),u(data[4]),p])
  f=ui.Form(form, 17)
  f.execute()
  self.savecon(f)

 def savecon(self, f, dele=0):
   if f[6][2][1]==0: p='true'
   else:p='false'
   if f[0][2]==u'' or f[1][2]==u'':ui.note(u'Not enough data provided', 'error');return 0
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
   if dele:self.delcon(1)
   ui.note(u'Saved', 'conf')
   self.conscr()

 def delcon(self,ok=0):
  name=self.interface[app.body.current()]
  if not ok:ok=ui.query(u'Are you sure you want to delete "'+name+'"', 'query')
  if ok==1:
   if self.get_db('mode')=='flatfile':os.unlink(self.db['account_dir']+'/'+name+'.acc')
   elif self.get_db('mode')=='SQL':del self.db['acc_'+name]
   self.connections.pop(app.body.current())
  self.conscr()

 def login(self):
  if self.get_db('mode')=='flatfile':f=open(self.get_db('account_dir')+'\\'+self.name+'.acc');data=f.read();f.close();opts=data.split('\n')
  else:opts=self.get_db('acc_'+self.name, 'list')
  self.user=str(opts[2]);self.host=str(opts[0]);self.ftp=file()
  try:
   self.ftp.connect(self.host, int(float(opts[1])))
   self.ftp.set_pasv(opts[5])
   self.ftp.login(self.user, self.decodestring(opts[3], self.get_db('a')))
   self.l=loader(graphics.Image.open('e:\\Python\\apps\\simon816\\ftpbrowser\\loading.gif'),100);self.pwd=''
   self.chdir(str(opts[4]))
   return 1
  except all_errors[1], e:ui.note(u'could not connect\n'+u(e), 'error');self.conscr();
  except all_errors[0], e:ui.note(u'could not login\n(Bad username/password)', 'error');self.disconnect();self.conscr();

 def connect(self,name):
  self.name=name
  if self.login()==1:
   ui.note(u(self.ftp.getwelcome()), 'info')
   self.tabs.new_tab(u(name),self.dispdir)
   self.tabs.select_tab(u(name))
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
        (u'Refresh', self.refresh),
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
   app.menu=self.menu

 def sendcmd(self):
  print self.ftp.sendcmd(ui.query(u'Command','text'))

 def refresh(self):self.l.start();self.dispdir()

 def dispdir(self):
  try:
   self.interface=self.getwd()
   app.title=u(self.pwd)
   app.body=self.disp(self.actions)
   self.exit(self.disconnect)
   app.menu=self.menu
   self.l.stop()
  except all_errors, e:self.disperr(str(e), [self.dispdir])

 def reconnect(self, func, *action):
  if self.login()==1:
   self.l.addtext(u'reconnected', 1)
   if action==[]:func()
   else:self.chdir('');func(*action)
  else:
   if not self.retry==1:
    ui.note(u'Connection was dropped but could not reconnect', 'error')
    ui.note(u'retrying...', 'info', 1);self.retry=1
    self.reconnect(func, *action)
   else:ui.note('Could not make a data connection, returning to menu', 'error');self.retry=0;self.conscr()

 def disperr(self, e, action):
  if e[:3]=='421' or tuple(e)[0]==13:self.reconnect(*action)
  elif e=="(13, 'Permission denied')":self.reconnect(*action)
  elif e=="(32, 'Broken pipe')":
   ui.note(u'Unexpectly lost connection with '+self.host, 'error');reconn=ui.query(u'Reconnect?', 'query')
   if reconn==1:self.reconnect(*action)
  else:ui.note(u(e), 'error');print e

 def getwd(self,dirname=None):
  if not dirname:self.pwd=dr=self.ftp.pwd()
  else:dr=dirname
  self.l.addtext(u'Retrieving files', 1)
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
  self.l.start()
  try:
   if dir=='..':self.ftp.cwd('..');self.l.addtext(u'Going up one', 1)
   else:
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
   self.dirdict={'reverse':[]}
   self.loopdir(self.cbd[1]+self.cbd[2])
   for dir in self.dirdict['reverse']:
    self.l.addtext(u'Make directory '+u(dir),1)
    self.ftp.mkd(dir[len(self.cbd[1]):])
    for file in self.dirdict[dir]:
     self.l.addtext(u(dir+'/'+file),1)
     fh=StringIO.StringIO()
     self.ftp.retrbinary('RETR '+dir+'/'+file, fh.write);fh.seek(0)
     if self.cbd[3]=='cut':self.l.addtext(u'Deleting... '+u(dir+'/'+file),1);self.ftp.delete(dir+'/'+file)
     self.ftp.storbinary('STOR '+dir[len(self.cbd[1]):]+'/'+file,fh)
     fh.close()
   self.dirdict['reverse'].reverse()
   if self.cbd[3]=='cut':
    for dir in self.dirdict['reverse']:
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
   self.l.start()
   self.l.addtext(u'Downloading '+u(self.sel[9]), 1)
   self.mkcache(self.pwd)
   if self.sel[1][0]=='-':
    self.ftp.retrbinary('RETR '+self.sel[9], self.savelocal, self.get_db('blocksize', 'int'))
   else:self.downloaddir()
   if self.dcomp==1:ui.note(u'Download complete', 'conf');self.dcomp=0;del self.cache;self.l.stop()
  except all_errors, e:self.disperr(str(e), self.download)

 def downloaddir(self):
  self.dirdict={'reverse':[]}
  self.loopdir(self.pwd+'/'+self.sel[9])
  del self.dirdict['reverse']
  self._sel=self.sel
  for dir in self.dirdict:
   self.l.addtext(u'Make Directory '+u(dir),1)
   self.mkcache(dir)
   for file in self.dirdict[dir]:
    self.sel=['','','','','','','','','',file]
    self.l.addtext('Downloading '+u(file),1)
    self.ftp.retrbinary('RETR '+dir+'\\'+file, self.savelocal, self.get_db('blocksize', 'int'))
  self.dcomp=1;self.sel=self._sel;del self._sel

 def upload(self, file=None):
   if file==None:file=ui.query(u'Please specify the path to the file', 'text')
   e=0
  #try:
   if zipfile.is_zipfile(file):
    e=ui.query(u'Zipfile detected, extract contents to current directory?', 'query')
   self.l.start()
   if not e==1:
    f=open(file, 'r')
    try:
     self.l.addtext(u'Uploading '+u(f.name),1)
     n=f.name;n=replace_all(n, {'/':'\\'}).split('\\');self.ftp.storbinary('STOR '+n[len(n)-1], f, self.get_db('blocksize', 'int'));ui.note(u'Uploaded', 'conf', 1)
    except all_errors, e:self.disperr(str(e), [self.upload,file])
    f.close()
   else:self.up_zip(file)
   self.dispdir()
  #except IOError, e:
  # ui.note(u'file error', 'error'+u(e));retry=ui.query(u'Retry?', 'query')
   #if retry==1:self.upload()

 def up_zip(self, file):
  z=zipfile.ZipFile(file)
  wd=self.get_db('cashe_dir')+'\\'+self.user+'@'+self.host+replace_all(self.pwd, {'/':'\\'})+'\\';
  wd=wd.strip();
  self.mkdir([wd])
  for f in z.namelist():
   if f.endswith('/'):
    #if not os.path.exists(wd+f):
     self.l.addtext(u'Make Directory '+u(f),1)
     self.mkdir([wd+f]);self.ftp.mkd(f)
   else:
     fh=open(wd+f, 'w')
     fh.write(z.read(f))
     fh.close()
     fi=open(wd+f, 'r')
     self.l.addtext(u'Uploading '+u(f), 1)
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
   self.l.start()
   try:
    if not self.sel[1][0]=='d':self.l.addtext(u'Deleting '+u(self.sel[9]),1);self.ftp.delete(self.pwd+'/'+self.sel[9])
    else:
     try:self.l.addtext(u'Removing Directory '+u(self.sel[9]), 1);self.ftp.rmd(self.sel[9])
     except all_errors, e:
      if str(e)[:3]=='550':
       if ui.query(u'Driectory is not empty, delete all sub directories and files?', 'query')==1:
        self.dirdict={'reverse':[]}
        self.loopdir(self.pwd+'/'+self.sel[9])
        self.dirdict['reverse'].reverse()
        for dir in self.dirdict['reverse']:
         for file in self.dirdict[dir]:
          self.l.addtext(u(dir+'/'+file),1)
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

 def parcebin(self):
  bin=self.binary
  self.t=ui.Text();self.t.color=0x000000;self.t.font=self.get_db('font', 'tuple')
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
    self.binary=bin[:1024];self.parcebin()

 def new(self):
  self.sel=self.getsel()
  self.sel[9]=ui.query(u'New File', 'text')
  self.t=ui.Text();self.t.color=0x000000;self.t.font=self.get_db('font', 'tuple')
  app.body=self.t
  app.title=u(self.sel[9])
  self.exit(self.dispdir)
  app.menu=[(u'Save', self.save),(u'Goto', ((u'Top',self.top),(u'Bottom',self.bottom)))]

 def top(self):
  self.t.set_pos(0)
 def bottom(self):
  self.t.set_pos(len(self.binary))

 def open(self):
  self.retr()
  if not self.t==None:
   app.body=self.t
   app.title=u(self.sel[9])
   self.exit(self.dispdir)
   app.menu=[(u'Save', self.save),(u'Goto', ((u'Top',self.top),(u'Bottom',self.bottom)))]
  else:
   ui.note(u'Cannot open file for editing', 'error')
   dld=ui.query(u'Download '+self.sel[9]+u' instead?', 'query')
   if dld==1:self.mkcache(self.pwd);self.savelocal(self.binary)
  
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

class tabs:
 def __init__(self,tabs=[],callbacks=[]):
  self.tabs=tabs
  self.callback=callbacks
  self.selected=0
  self.update()
 def update(self):
  app.set_tabs(self.tabs, self.handler)
  self.select_tab(self.selected)
 def handler(self, index):
  self.selected=index
  try:self.callback[index]({'index':index,'name':self.tabs[index]})
  except:
   try:self.callback[index]()
   except:pass
 def new_tab(self,value, call,index=-1):
  if value:
   if index==-1:self.tabs.append(value);self.callback.append(call)
   else:self.tabs.insert(index,value);self.callback.insert(index,call)
   self.update()
 def _getTab(self,tab):
  try:
   i=int(tab)
   if i==len(self.tabs):raise 'OutOfRange'
   else:return i
  except:
   try:return self.tabs.index(tab)
   except:return None
 def change_tab(self,tab,new,call=None):
  i=self._getTab(tab)
  if i or i==0 and new:self.tabs[i]=new
  if call:self.callback[i]=call
  self.update()
 def select_tab(self,tab,doCall=0):
  i=self._getTab(tab)
  if i or i==0:
   app.activate_tab(i)
   self.selected=i
   if doCall:self.handler(i)
 def blank(self):pass
 def hide_tabs(self):
  app.set_tabs([],self.blank)
 def show_tabs(self):self.update()
 def reset(self):self.__init__()
if __name__=="__main__":
 ftpbrowser().run()
lk.wait()