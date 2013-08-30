from repobackend import Repository, CONNECTION
import os
from simon816.DiffReader import DifferenceReader
class RepositoryInterface:
  def __init__(self,iface,conf,dir):
    self._iface=iface
    self._config=conf
    self.homedir=dir
    inf=conf.get_data('info')
    self._repo=Repository(inf,dir)
    self._repo.con.login(self._repo.owner,self._iface.password('Enter Password'))
    self.latest_com=self._repo.latest_commit()
    menuitems=[
      (u'Pull Remote Files',u'Update local repository',
        self.pull),
      (u'See Changes',u'Working Directory: %s'%dir,
        self.local_changes),
      (u'Browse Commits',u'latest: %s'%self.latest_com,
        self.browse_commits),
      (u'Switch Branch',u'Current: %s'%inf['branch'],
        self.switch_branch)
    ]
    prop={
      'title':unicode(inf['name']),
      'body':self._iface.listbox(menuitems),
      'menu':[(u'See Description',self._list_desc)],
      'exit':self.exit,
      '_lbitems':menuitems,
      '_data':self._iface._lb_data,
      '_lb':self._iface._lb
      }
    self.homescreen=self._iface.create_screen(**prop)
    self.home() 
  def exit(self):
     self._repo.con.close()
     self._iface._lock.signal()
  def home(self):
    self._iface._lb_data=self.homescreen._data
    self._iface._lb=self.homescreen._lb
    self._iface.set_screen(self.homescreen)
  def _list_desc(self):
    c=self.homescreen.body.current()
    desc=u'\n'.join(self.homescreen._lbitems[c][:2])
    self._iface.alert(desc)
  def pull(self):
    commit=self._repo.get_commit(self.latest_com)
    treesha=commit.get_tree()
    def saveblob(location,blob,name):
      relpath=location.replace('\\','/')
      fullpath=self.homedir+relpath.replace('/','\\')
      if not os.path.exists(fullpath):
        os.makedirs(fullpath)
      f=open(fullpath+name,'w')
      f.write(blob.get_content())
      f.close()
      self._repo.objectHandler.update(self.homedir,relpath+name,blob.get_sha())
    self._repo.walk_tree(treesha,'',saveblob)
    self._repo.objectHandler.index.save()
    self._iface.success('Complete!')
        
  def local_changes(self):
    def quit():
      scr.destroy()
      self.home()
    changes=self._repo.get_changes()
    if not changes:
      self._iface.error('No changes')
      return
    changes.reverse()
    fs=[]
    for c in changes:
      path=unicode(c[0])
      name=os.path.basename(c[0])
      if c[2]:mode='M'
      else:mode='N'
      info=unicode('[U][%s] %s'%(mode,name))
      fs.append((path,info))
    def chview():
      ind=scr.body.current()
      self.view_diff(changes[ind][1],fs[ind][0])
    lb=self._iface.listbox(fs,chview)
    staged={}
    def tog_stag():
      c=lb.current()
      f=list(fs[c])
      dta=changes[c]
      if f[0] not in staged:
        f[1]=u'[S]'+f[1][3:]
        staged[str(f[0])]={'sha':dta[3],'content':dta[4],'tree':dta[5]}
      else:
        f[1]=u'[U]'+f[1][3:]
        del staged[str(f[0])]
      fs[lb.current()]=tuple(f)
      lb.set_list(fs,lb.current())
    def createcommit():
      self.create_commit(staged)
    menu=[
      (u'Rescan',self.local_changes),
      (u'Toggle Staged',tog_stag),
      (u'Create Commit',createcommit)
    ]
    scr=self._iface.create_screen(body=lb,title=u'View changes',exit=quit,menu=menu)
    self._iface.set_screen(scr)

  def view_diff(self,difflines,filename=''):
    def quit():
      p=diff_screen.parent_window()
      diff_screen.destroy()
      self._iface.set_screen(p)
    dr=DifferenceReader()
    dr.changeSetting('lineno',1)
    text=dr._createTextObj()
    diff=dr.parseDifference(difflines)
    dr.setTextToDiff(diff,text)
    diff_screen=self._iface.create_screen(body=text.t,menu=text.menu,name="diff screen for %r"%filename,exit=quit,title=filename)
    text.toLine(1)
    self._iface.set_screen(diff_screen)

  def create_commit(self,files):
    if not self._repo.con.auth:
      #user=self._iface.prompt2('Username','Password')
      un=self._iface.prompt('Username')
      if un is None:return
      pw=self._iface.password('Password')
      if pw is None:return
      user=[un,pw]
      #if user is None:return
      self._repo.con.login(*user)
    tree=[]
    parentcommit=self._repo.get_commit(self.latest_com)
    basetree=parentcommit.get_tree()
    entrys=self._repo.get_tree(basetree).get_entrys()
    cfiles=[e.path for e in entrys]
    for file,info in files.iteritems():
      try:
        idx=cfiles.index(file)
        del entrys[idx],cfiles[idx]
      except ValueError:
        print 'newfile',file,info
      if not os.path.exists(os.path.join(self.homedir,file.replace('/','\\'))):
        del self._repo.objectHandler.index.files[file]
      else:
        blob=self._repo.create_blob(info['content'])
        if blob.get_sha()!=info['sha']:
          print 'sha error',blob.get_sha(),info['sha']
        self._repo.objectHandler.update(self.homedir,
          file,blob.get_sha())
        tree.append(
          {'path':file,
            'mode':'100644',
            'type':'blob',
            'sha':blob.get_sha()})
    for entry in entrys:
      tree.append(entry.dictify())
    treeobj=self._repo.create_tree({'tree':tree})
    self._repo.objectHandler.add_tree(self.homedir,'',treeobj.get_sha())
    self._repo.objectHandler.index.save()
    
    msg=self._iface.prompt('Commit message')
    
    commit=self._repo.create_commit({'message':msg,'tree':treeobj.get_sha(),'parents':[parentcommit.get_sha()]})
    self.view_commit(commit,True)
  
  def view_commit(self,commit,pushable=False):
    menu=None
    if pushable:
      menu=[(u'Push Commit',lambda:self.push(commit))]
    items=[
      (u'Parent Commit','text',unicode(commit.get_parent())),
      (u'Tree','text',unicode(commit.get_tree())),
      (u'Author','text',unicode(commit.get_fauthor())),
      (u'Committer','text',unicode(commit.get_fcommitter())),
      (u'Message','text',unicode(commit.get_message()))
    ]
    s=self._iface.get_screen()
    s.title=u'Commit %s'%commit.get_sha()
    s.override()
    #self._iface.set_screen(s)
    self._iface.form(items,16,menu=menu)

  def push(self,commit):
    self._repo.update_ref(commit)
    self._iface.success('Updated branch %r to commit %s'%(self._repo.branch,commit.get_sha()))
    self.latest_com=self._repo.latest_commit()
    self.home()
  def browse_commits(self):
    latest=self._repo.get_commit(self.latest_com)
    prev=self._repo.get_commit(latest.get_parent())
    items=[(unicode(c.get_sha()),unicode(c.get_message())) for c in [latest,prev]]
    def view(entry):
      c=self._repo.commit_diff(entry[0])
      dr=DifferenceReader()
      dr.changeSetting('lineno',1)
      dr.displayDifference(c.replace('\n\\ No newline at end of file',''))
      self._iface.set_screen(screen)
    lb=self._iface.listbox(items,view)
    screen=self._iface.create_screen(body=lb,exit=self.home)
    self._iface.set_screen(screen)
  def switch_branch(self):
    pass

class RemoteRepo:
  def __init__(self,iface,username):
    self._iface=iface
    self.username=username
    self.con=CONNECTION
    self.repos={}
  def select_repo(self):
    l=[]
    resp=self.con.do_request('GET','/users/%s/repos'%self.username)
    for repo in resp.data:
      name=repo['name']
      self.repos[name]=repo
      l.append(name)
    repo=self._iface.over_list([unicode(r) for r in l])
    if repo is None:return
    name=l[repo]
    data=self.repos[name]
    return data