from GithubGlobals import *
class RepositoryManager:
 def __init__(self, con):
  self.con=con
  self.repos={}
  self.db=util.db(DIRECTORY+'repos','c')
 def loadRepos(self,allrepos):
  for repo in allrepos:
   name=repo['name']
   try:dir=self.db.get(name)
   except KeyError:dir=os.getcwd()+'\\'+name
   self.db.mod(name,dir)
   self.repos[name]=Repository(repo,self.con,self.db)
 def listrepos(self):
  repos=[]
  for name,repo in self.repos.iteritems():
   repos.append((unicode(name), unicode(repo.description)))
  return repos
 def getRepo(self,name):
  return self.repos[name]
 def closeAll(self):
  self.repos={}

class Repository:
 def __init__(self,info,con,_db):
  self.info=info
  self.con=con
  self._db=_db
  # some common attributes:
  self.name=info['name']
  self.id=info['id']
  self.description=info['description']
  self.branch=info['default_branch']
  self.author=info['owner']['login']
  self.baseurl='/repos/%s/%s'%(self.author,self.name)
  self.dir=self._db.get(self.name)
  self.cache=cache.createCache(self.dir+'\\.git')
  self.cache.bindToRepo(self)
 def __str__(self):
  return '<%s Repository from %s>'%(self.name,self.author)
 def TakeControl(self,exitfunction):
  self.close=exitfunction
  appuifw.app.exit_key_handler=self.close
  appuifw.app.title=unicode(self.name)
  appuifw.app.menu=[]
  self.mainmenu()
  self.refs=self.con.GET(self.baseurl+'/git/refs').parseJson()
  ref=self.getBranch(self.branch)
  if ref:
   if ref['object']['type']=='commit':
    self.LATEST_COMMIT=ref['object']['sha']
 def getBranch(self,branch):
  if type(branch)==int:
   return self.refs[branch]
  for ref in self.refs:
   if ref['ref']=='refs/heads/'+branch:
    return ref
 def mainmenu(self):
  items=[
   (u'Browse Remote Files',u''),
   (u'Switch branch',u'current: %s'%self.branch),
   (u'Pull to local directory',unicode('...'+self.dir[-30:])),
   (u'Repo info',u''),
   (u'Change local path',u''),
   (u'Switch Repo',u'')
  ]
  appuifw.app.body=appuifw.Listbox(items,self.doaction)
 def doaction(self):
  c=appuifw.app.body.current()
  if c==0:
   self.fileBrowser()
  if c==1:
   self.switchBranch()
  if c==2:
   self.pull()
  if c==3:
   self.displayInfo()
  if c==4:
   self.changePath()
  if c==5:
   self.close()

 def fileBrowser(self):
  pass
 def switchBranch(self):
  refs=[ref['ref'].split('/')[-1] for ref in self.refs]
  sel=appuifw.popup_menu([unicode(r) for r in refs],u'Select Branch')
  if sel is None:return
  self.branch=refs[sel]
  self.mainmenu()
 def pull(self):
  pass
 def displayInfo(self):
  pass
 def changePath(self):
  path=util.select('dir',self.dir)
  if not path:return
  self._db.mod(self.name,path)
  self.dir=path
  self.mainmenu()
