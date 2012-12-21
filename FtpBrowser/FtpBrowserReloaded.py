import appuifw, e32, StringIO, os,ftplib
FTP=ftplib.FTP
lk=e32.Ao_lock()
class ftpbrowser:
 def dev(self, feat):
  self.ui.note(u'This app is in development atm, feature "'+feat+'" has not yet been implemented', 'error')
 def __init__(self):
  self.name="FTP Browser"
  self.author="Simon816"
  self.version='0.0.1'
  self.settings_dir='e:\\python\\apps\\simon816\\ftpbrowser'
  self.account_dir=self.settings_dir+'\\accounts'
  self.cashe_dir=self.settings_dir+'\\cashe'
  if not os.path.exists(self.account_dir):
   os.makedirs(self.account_dir);os.makedirs(self.cashe_dir)
  self.ui=appuifw
  self.app=self.ui.app
  self.connections=[u'New Connection']
  for file in os.listdir(self.account_dir):
   self.connections.append(unicode(file).split('.')[0])
  self.exit(self.quit)
  self.menu=[(u'Select', self.handle)]
  self.color=0x000000 
  self.font=(u"nokia hindi s60",14,16)
  self.maxtrans=1048576

 def quit(self):
  lk.signal()
 def exit(self, action):self.app.exit_key_handler=action
 def disp(self, cback):
  return self.ui.Listbox(self.interface, cback)

 #begin callbacks#
 def dummy(self):pass

 def actions(self):
  self.sel=self.interface[self.app.body.current()]
  if self.sel.find('>')==0:self.chdir(self.sel[self.sel.find(">")+1:])
  else:self.open()

 def activate(self):
  c=self.app.body.current()
  if self.connections[c]==u'New Connection':self.addnew()
  else:self.connect(self.connections[c])

 def handle(self):
  c=self.app.body.current()
  if c==0:self.conscr()
  elif c==1:self.settings()
  elif c==2:self.setup()
  else:pass
 #end callbacks#

 def run(self):
  self.exit(self.quit)
  self.interface=[u'Connect', u'Settings', u'Setup']
  self.app.body=self.disp(self.handle)
  self.app.menu=self.menu

 def conscr(self):
  self.exit(self.run)
  self.interface=self.connections
  self.app.body=self.disp(self.activate)
  self.app.menu=[(u'Connect', self.activate), (u'New', self.addnew), (u'Edit', self.edit), (u'Delete', self.delcon)]

 def getwd(self):
  self.list=self.ftp.nlst()
  l=[]
  l.append(u'> <UP>')
  for opt in self.list:
   if "." in opt:
    if opt.find(".")==0:l.append(unicode(">"+opt))
    else:l.append(unicode(opt))
   else:l.append(unicode(">"+opt))
  l.sort()
  return l

 def connect(self, name):
  f=open(self.account_dir+'\\'+name+'.txt');data=f.read();f.close();opts=data.split('\n')
  self.user=str(opts[2])
  self.host=str(opts[0])
  self.ftp=FTP(self.host)
  self.ftp.set_pasv(opts[5])
  self.ftp.login(self.user, str(opts[3]))
  self.ui.note(unicode(self.ftp.getwelcome()))
  self.ftp.cwd(str(opts[4]))
  self.app.title=unicode(self.ftp.pwd())
  self.interface=self.getwd()
  self.app.body=self.disp(self.actions)
  self.exit(self.disconnect)
  self.app.menu=self.browsing_menu=[(u'Open', self.open),(u'Download', self.download), (u'Disconnect', self.disconnect)]


 def chdir(self, dir):
  if dir==' <UP>':
   self.ftp.cwd('..');
   self.ui.note(u'Going up one')
  else:
   appuifw.note(u'chaning directory to '+dir)
   self.ftp.cwd(self.ftp.pwd()+'/'+dir)
  self.app.title=unicode(self.ftp.pwd())
  self.interface=self.getwd()
  self.app.body=self.disp(self.actions)

 def back(self):
  self.app.body=None
  self.app.body=self.disp(self.actions)
  self.exit(self.disconnect)
  self.app.menu=self.browsing_menu

 def savelocal(self, binary):
  cd='\\'+self.user+'\r@'+self.host
  os.makedirs(self.cashe_dir+cd)
  os.chdir(self.cashe_dir+cd)
  os.makedirs(os.getcwd()+self.pwd)
  os.chdir(os.getcwd()+self.pwd)
  self.ui.note(u'saving to '+unicode(os.getcwd()))
  f=open(os.getcwd()+self.sel, 'w')
  f.write(binary)
  f.close()
  self.ftp.sendcmd('type a')

 def download(self):
  self.pwd=self.ftp.pwd()
  self.ftp.sendcmd('type i')
  self.sel=self.interface[self.app.body.current()]
  #try:
  self.ftp.retrbinary('RETR '+self.sel, self.savelocal, self.maxtrans)
  #except ftplib.all_errors, msg: self.ui.note(unicode(msg), 'error')

 def retr(self):
  self.sel=self.interface[self.app.body.current()]
  try:self.ftp.retrbinary('RETR '+self.sel, self.getbin, self.maxtrans)
  except ftplib.all_errors, msg: self.ui.note(unicode(msg), 'error')
 def getbin(self, bin):
  try:
   self.t=self.ui.Text()
   self.t.color=self.color
   self.t.font=self.font
   self.t.set(unicode(bin))
  except UnicodeError:
   self.t=None

 def open(self):
  self.retr()
  if not self.t==None:
   self.app.body=self.t
   self.app.title=unicode(self.sel)
   self.exit(self.back)
   self.app.menu=[(u'Save', self.save)]
  else:
   self.ui.note(u'Cannot open file for editing', 'error')
   dld=self.ui.query(u'Download '+self.sel+u' instead?', 'query')
   if dld==1:self.download()
  
 def save(self):
  s = lambda s: s.encode('utf-8')
  st=self.t.get()
  output = StringIO.StringIO()
  output.write(s(st.replace(u"\u2029", u'\r\n')))
  output.seek(0)
  try:
   self.ftp.storbinary('STOR '+self.sel, output, self.maxtrans)
   self.ui.note(u'Saved!')
  except ftplib.all_errors, msg: self.ui.note(unicode(msg), 'error')
  output.close()

 def disconnect(self):
  try:
   self.ui.note(u'Disconnecting...')
   self.ftp.quit()
  except ftplib.all_errors, error:
   self.ui.note(unicode(error), 'error')
  self.conscr()

 def settings(self):
  self.dev(u'settings')

 def setup(self):
  self.dev(u'setup')

 def addnew(self):
  form=[(u'Conn. name', 'text'), (u'Host', 'text'),(u'Port', 'number', 21), (u'User nm.', 'text'), (u'Password', 'text'), (u'Initial Dir', 'text', u'/'), (u'Passive mode', 'combo', ([u'true', u'false'],0))]
  flags=appuifw.FFormEditModeOnly
  f=self.ui.Form(form, flags)
  f.execute()
  try:
   if f[6][2][1]==0: p=u'true'
   else:p=u'false'
   fi=open(self.account_dir+'\\'+f[0][2]+'.txt', 'w')
   fi.write(f[1][2]+"\n"+str(f[2][2])+"\n"+f[3][2]+"\n"+f[4][2]+"\n"+f[5][2]+"\n"+p)
   fi.close()
   self.connections.append(unicode(f[0][2]))
  except:
   self.ui.note(u'Did not save')
  self.conscr()
 def edit(self):
  name=self.interface[self.app.body.current()]
  flags=appuifw.FFormEditModeOnly
  f=open(self.account_dir+'\\'+name+'.txt');data=f.read();f.close();data=data.split('\n');
  if data[5]=='true':p=0
  else: p=1
  form=[(u'Conn. name', 'text', unicode(name)), (u'Host', 'text', unicode(data[0])),(u'Port', 'number', int(float(data[1]))), (u'User nm.', 'text', unicode(data[2])), (u'Password', 'text', unicode(data[3])), (u'Initial Dir', 'text', unicode(data[4])), (u'Passive mode', 'combo', ([u'true', u'false'], p))]
  f=self.ui.Form(form, flags)
  f.execute()
  try:
   if f[6][2][1]==0: p=u'true'
   else:p=u'false'
   fi=open(self.accont_dir+'\\'+f[0][2]+'.txt', 'w')
   fi.write(f[1][2]+"\n"+str(f[2][2])+"\n"+f[3][2]+"\n"+f[4][2]+"\n"+f[5][2]+"\n"+p)
   fi.close()
   self.ui.note(u'Saved', 'conf')
  except:
   self.ui.note(u'Did not save')
  self.conscr()
 def delcon(self):
  name=self.interface[self.app.body.current()]
  ok=self.ui.query(u'Are you sure you want to delete "'+name+'"', 'query')
  if ok==1:
   os.unlink(self.account_dir+'/'+name+'.txt')
   self.connections.pop(self.app.body.current())
  self.conscr()
if __name__=="__main__":
 ftpbrowser().run()
lk.wait()