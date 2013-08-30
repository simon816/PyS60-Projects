from network import Connection
from datafile import DataFile
from objectHandler import objectHandler
try:
  CONNECTION=Connection()
except:
  CONNECTION=None
class Repository:
  def __init__(self,info, dir):
    self.con=CONNECTION
    self.dir=dir
    self.__dict__.update(info)
    self.objectHandler=objectHandler(dir+'.git\\')
  def mkurl(self,thing):
    return '/repos/%s/%s/%s'%(self.owner,self.name,thing)

  def get(self,thing,etag=None,headers={}):
    url=self.mkurl(thing)
    if etag is not None:
      headers['If-None-Match']='"%s"'%etag
    resp=self.con.do_request('GET',url,None,headers)
    return resp
  def post(self,thing,json):
    url=self.mkurl(thing)
    resp=self.con.postJSON(url,json)
    return resp
  def patch(self,thing,json):
    url=self.mkurl(thing)
    jstr=self.con.json_encode(json)
    return self.con.do_request('PATCH',url,jstr)
    
    
  def latest_commit(self):
    commit=DataFile(self.dir+'.git\\LatestCommit')
    if not commit['commit']:
      commit['commit']={'sha':'','etag':''}
    etag=commit['commit']['etag']
    sha=commit['commit']['sha']
    resp=self.get('git/refs/heads/'+self.branch,etag)
    if resp.hasdata():
      if not resp.is_json():
        raise TypeError('Response not in JSON')
      sha=resp.data['object']['sha']
    commit.merge('commit',{'etag':resp.etag,'sha':sha})
    return sha
  def pull_object(self,type,url):
    #forces fresh object pull from server
    o=self.objectHandler.new_object(type)
    resp=self.get(url,None)
    if not resp.is_json():
      raise TypeError('Object not in JSON for pull %s %s'%(type,url))
    o.read_json(resp.data)
    self.objectHandler.save_object(o)
    return o
  def load_object(self,sha):
    return self.objectHandler.load_object(sha)
  def make_object(self,sha,arg2=None,arg3=None):
    obj=self.load_object(sha)
    if obj is None:
      if not arg2 or not arg3:raise ValueError('missing vals')
      obj=self.pull_object(arg2,arg3+'/'+sha)
    return obj
  def get_commit(self,sha):
    return self.make_object(sha,'commit','git/commits')
  def get_tree(self,sha):
    return self.make_object(sha,'tree','git/trees')

  def walk_tree(self,treesha,loc,callback):
    tree=self.get_tree(treesha)
    for entry in tree.get_entrys():
      if entry.mode=='040000':
        path=loc+entry.path+'/'
        #temp
        import os
        os.makedirs(self.dir+path)
        self.objectHandler.add_tree(self.dir,path,entry.sha)
        self.walk_tree(entry.sha,path,callback)
      elif entry.mode=='100644':
        blob=self.make_object(entry.sha,'blob','git/blobs')
        callback(loc,blob,entry.path)
      else:
        print 'unknown',entry
          
  def lookup(self,filename):
    return self.objectHandler.filename2sha(filename)
  def get_changes(self):
    import sha
    import difflib
    import os
    changes=[]
    allfiles=[]
    alltrees=[]
    def loop(b,d):
      alltrees.append(d)
      tree=self.objectHandler.directory2sha(d)
      for file in os.listdir(b+d):
        name=(d+file).replace('\\','/')
        if file == '.git':continue
        if os.path.isdir(b+d+file):
          loop(b,d+file+'\\')
        else:
          allfiles.append(name)
          oldsha=self.lookup(name)
          f=open(b+name)
          content=f.read()
          serial='blob %d\x00%s'%(len(content),content)
          newsha=sha.new(serial).hexdigest()
          f.close()
          if newsha==oldsha:
            continue #no changes
          else:
            blob=self.load_object(oldsha)
            if blob is not None:
              oldcontent=blob.get_content()
              tracked=1
              #file exists in object handler
            else:
              tracked=0
              oldcontent=''
            oldlines=oldcontent.splitlines()
            newlines=content.splitlines()
            diff=difflib.unified_diff(oldlines,newlines)
            x=[l for l in diff]
            changes.append((name,x[2:],tracked,newsha,content,tree))
    loop(self.dir,'')
    for file,inf in self.objectHandler.get_files().iteritems():
      if file not in allfiles:
        oldlines=self.load_object(inf['sha']).get_content().splitlines()
        diff=difflib.unified_diff(oldlines,[])
        x=[l for l in diff]
        changes.append((file,x[2:],1,None,''))
    return changes
  def create_blob(self,content):
    import base64
    resp=self.post('git/blobs',{'content':base64.encodestring(content).rstrip('\n'),'encoding':'base64'}).data
    blob=self.objectHandler.new_object('blob')
    blob.set_sha(resp['sha'])
    blob.set_content(content)
    self.objectHandler.save_object(blob)
    return blob
  def create_tree(self,data):
    resp=self.post('git/trees',data).data
    tree=self.objectHandler.new_object('tree')
    tree.read_json(resp)    
    self.objectHandler.save_object(tree)
    return tree
  def create_commit(self,data):
    resp=self.post('git/commits',data).data
    commit=self.objectHandler.new_object('commit')
    commit.read_json(resp)
    self.objectHandler.save_object(commit)
    return commit
  def update_ref(self,obj):
    resp=self.patch('git/refs/heads/'+self.branch,{'sha':obj.get_sha(),'force':True})
    print resp.data
  def commit_diff(self,sha):
    return self.get('commits/'+sha,None,{'Accept':'application/vnd.github.v3.diff'}).data