from interface import Interface
from simon816.util import util
util=util()
class config:
  def __init__(self):
    self.config={}
    self.f=None
  def open(self,file,ext='.cfg',mode='alwaysopen'):
    self.mode=mode
    file=str(file+ext)
    try:
      self.f=open(file,'r+')
    except IOError:
      self.f=open(file,'w+')
    currentkey=''
    self.config[currentkey]={}
    for line in self.f.xreadlines():
      line=line.rstrip()
      if line.startswith('[') and line.endswith(']'):
        currentkey=line[1:-1]
        self.config[currentkey]={}
      else:
        line=line.replace('\t','')
        split=line.split('=')
        key=split[0].strip()
        value='='.join(split[1:]).lstrip()
        self.config[currentkey][key]=value
    del self.config['']
    if mode=='alwaysopen':
      self.f.seek(0)
    elif mode=='passive':
      self.f.close()
  def save(self):
    if self.mode == 'passive':
      self.f=open(self.f.name, 'w')
    self.f.write(self.serialize())
    if self.mode == 'passive':
      self.f.close()
  def serialize(self):
    out=[]
    keys=self.config.keys()
    keys.sort()
    for key in keys:
      out.append('[%s]'%key)
      itemkeys=self.config[key].keys()
      itemkeys.sort()
      for itemkey in itemkeys:
        out.append('  %s = %s'%(itemkey,self.config[key][itemkey]))
    return '\n'.join(out)
  def add_key(self,key,data={}):
    self.config[key]=data
    if self.mode=='passive':
      self.save()
  def set_key_data(self,head,key,value):
    self.config[head][key]=value
    if self.mode=='passive':
      self.save()
  def get_data(self,key):
    return self.config[key]
  def get_key_data(self,head,key):
    return self.config[head][key]
  def get_keys(self):
    return self.config.keys()
  def get_all(self):
    return self.config
  def delete_key(self,key):
    del self.config[key]
    if self.mode=='passive':
      self.save()
  def close(self):
    if self.f:
      self.f.close()
      self.f=None
  def __repr__(self):
    if self.f:state='open config file at %r'%self.f.name
    elif not self.config:state='new config instance'
    else:state='closed config file'
    return '<%s>'%state
  def __del__(self):
    self.close()
class UserManager:
 def __init__(self,dir):
   self.cfgfile=config()
   self.cfgfile.open(dir+'users',mode='passive')
 def forgetAll(self):
   for user in self.cfgfile.get_all():
     self.cfgfile.delete_key(user)
 def addUser(self,username,**properties):
  if username not in self.cfgfile.get_all():
    self.cfgfile.add_key(username,properties)
  else:
   raise Exception('User already exists')
 def updateUser(self,username,**properties):
    self.cfgfile.add_key(username,properties)
 def getUser(self,username):
  return self.cfgfile.get_data(username)
 def deleteUser(self,username):
   self.cfgfile.delete_key(username)
 def listUsers(self):
  return self.cfgfile.get_all()
 def finish(self):
   self.cfgfile.save()
   self.cfgfile.close()

class ConfigMgr:
  def __init__(self,dir):
    self.dir=dir
    self.cfg=config()
    self.cfg.open(dir+'config',mode='passive')
    if 'recent repositories' not in self.cfg.get_all():
      self.cfg.add_key('recent repositories')
    self.global_user_set='global user' in self.cfg.get_all()
    self.max_recent=5
  def set_global_user(self, user):
    self.cfg.add_key('global user',user)
  def recent_repos(self):
    reps=[]
    for n,l in self.cfg.get_data('recent repositories').iteritems():
      reps.append((n[3:],l))
    return reps
  def add_recent(self,name,location):
    repos={}
    index=0
    for n,l in self.cfg.get_data('recent repositories').iteritems():
      index=eval(n[:3])+1
      if index <=self.max_recent:
        repos['(%d)%s'%(index,n[3:])]=l
    repos['(1)'+name]=location
    self.cfg.delete_key('recent repositories')
    self.cfg.add_key('recent repositories',repos)
  def global_user(self):
    return self.cfg.get_data('global user')

import os
from repository import RepositoryInterface,RemoteRepo
class repoMgr:
  def __init__(self,iface):
    self._iface=iface
  def is_repo(self, dir):
    return os.path.exists(dir+'.git\\config')
  def openRepo(self,dir,conf):
    RepositoryInterface(self._iface,conf,dir)
  def openRemote(self,username):
    rr=RemoteRepo(self._iface,username)
    repo=rr.select_repo()
    dir = util.select('dir','E:/Python/apps/simon816/GithubMobile')
    if not dir:return
    conf=self.create_repository(dir, **repo)
    self.openRepo(dir,conf)
  def create_repository(self,dir, **allinfo):
    conf=config()
    util.mkdir([dir+'.git'])
    conf.open(dir+'.git\\config','')
    conf.add_key('info')
    conf.set_key_data('info','name',allinfo['name'])
    conf.set_key_data('info','description',allinfo['description'])
    conf.set_key_data('info','branch',allinfo['master_branch'])
    conf.set_key_data('info','owner',allinfo['owner']['login'])
    #raise AttributeError('Missing requirement')
    conf.save()
    conf.close()
    conf.open(dir+'.git\\config','',mode='passive')
    return conf


class GithubMobile:
  def __init__(self):
    self.homedir='E:\\Python\\apps\\simon816\\GithubMobile\\'
    self._iface=Interface()
    self._config=ConfigMgr(self.homedir)
    self._users=UserManager(self.homedir)
    self._repoMgr=repoMgr(self._iface)
    if self._config.global_user_set:
      lb=self._iface.listbox([
        (u'Recent Repos',self.recent_repos),
        (u'New Repo',self.new_repo),
        (u'Open Repo',self.click_open_repo),
        (u'Change Global Settings',self.change_settings)
      ])
    else:
      lb=self._iface.listbox([(u'Create Account',self.set_account)])
    s=self._iface.create_screen(body=lb,title=u'Github Mobile',name='Into screen')
    self._iface.set_screen(s)
  def set_account(self,data=[u'']*3):
    f=self._iface.form([
      (u'Display Name','text',data[0]),
      (u'Username','text',data[1]),
      (u'Email','text',data[2])
    ],flags=17)
    try:data=[i[2] for i in f]
    except IndexError:return #not all form was filled in
    user={'displayname':data[0],'username':data[1],'email':data[2]}
    self._config.set_global_user(user)
    name=user['username']
    del user['username']
    self._users.updateUser(name,**user)
  def recent_repos(self):
    items=[]
    locs=[]
    for repoinfo in self._config.recent_repos():
      items.append(unicode(repoinfo[0]))
      locs.append(repoinfo[1])
    if not len(items):return
    ind=self._iface.over_list(items)
    if ind is not None:
      self.open_repo(loc=locs[ind])
  def change_settings(self):
    user=self._config.global_user()
    user=[unicode(user[k]) for k in ['displayname','username','email']]
    self.set_account(user)
  def click_open_repo(self):
    choice=self._iface.over_list([u'Open Local',u'Open Remote'])
    if choice==0:
      self.open_repo()
    elif choice==1:
      self._repoMgr.openRemote(self._config.global_user()['username'])
  def open_repo(self,loc=None):
    if not loc:loc=util.select('dir',self.homedir+'REPOS')
    if not loc:return
    if self._repoMgr.is_repo(loc):
      conf=config()
      conf.open(loc+'.git\\config','')
      self._config.add_recent(conf.get_key_data('info','name'),loc)
      self._repoMgr.openRepo(loc,conf)
      conf.close()
    else:
      self._iface.error('Not a valid repositiory')
  def new_repo(self):
    name=self._iface.prompt('Name for repository')
    dir=util.select('dir',self.homedir)
    conf=self._repoMgr.create_repository(dir,name=name)
    self._config.add_recent(name,dir)
    self._repoMgr.openRepo(dir,conf)

GithubMobile()
