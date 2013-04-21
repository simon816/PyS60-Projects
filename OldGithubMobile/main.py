from simon816 import json,util
import appuifw,e32,httplib,base64,os

DIRECTORY='E:\\Python\\apps\\simon816\\GithubMobile\\'
mkdir=util.util().mkdir
from UserManager import UserManager
"""
Notes:
class *Manager: container for class *
class * instance of that object eg Repository 
"""
class GithubMobile:
 """ The main class and interface """
 def __init__(self):
  lock=e32.Ao_lock()
  self.directory=DIRECTORY
  if not os.path.exists(self.directory):
   os.makedirs(self.directory)
  os.chdir(self.directory)
  self.Users=UserManager(self.directory)
  self.start()
  self.RequestHost=Request()
  self.RepositoryHost=RepositoryManager(self.RequestHost)
  self.mainlock=lock
  lock.wait()
 def start(self):
  items=[u'Create User']
  items+=self.Users.listUsers()
  appuifw.app.body=appuifw.Listbox(items,self.choose)
  appuifw.app.menu=[
   (u'Login',self.choose),
   (u'Delete',lambda:self.Users.deleteUser(items[appuifw.app.body.current()])),
   (u'Exit',self.quit)]
  appuifw.app.title=u'Github Mobile'
  appuifw.app.exit_key_handler=self.quit
 def quit(self):
  self.mainlock.signal()
  self.RequestHost.close()
  self.Users.forgetAll()
  self.RepositoryHost.closeAll()
 def choose(self):
  i=appuifw.app.body.current()
  if i==0:
   n=appuifw.multi_query(u'Displayname',u'Username')
   if n is None:return
   p=appuifw.query(u'Password','code')
   if p is None:return
   self.Users.addUser(n[0],n[1],p)
   self.start()
   return
  user=self.Users.listUsers()[i-1]
  uname=self.Users.getUser(user)[0]
  self.RequestHost.headers['Authorization']=self.Users.HTTPBasicUser(user)
  resp=self.RequestHost.GET('/user/repos')
  try:json=resp.parseJson()
  except resp.ClientError,e:
   appuifw.note(unicode(e.json['message']),'error')
   return
  mkdir([uname])
  os.chdir(uname)
  self.RepositoryHost.loadRepos(json)
  self.displayRepos()
 def switchrepo(self,list):
   # difficult to decide: should repository manage itself or GithubMobile class control it
   #for now, it controls itself
   repo=self.RepositoryHost.getRepo(list[appuifw.app.body.current()][0])
   repo.TakeControl(self.displayRepos)
 def displayRepos(self):
  list=self.RepositoryHost.listrepos()
  lb=appuifw.Listbox(list,lambda:self.switchrepo(list))
  appuifw.app.body=lb
  appuifw.app.exit_key_handler=self.start
  appuifw.app.menu=[(u'Back',self.start)]
gm=GithubMobile()