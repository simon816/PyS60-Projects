from objectTypes import *
from object_cache import objectCache, Indexer
class objectHandler:
  """Any object processing"""
  def __init__(self,gitdir):
    self.cache=objectCache(gitdir+'objects\\')
    self.index=Indexer(gitdir+'index')
  def new_object(self,type):
    if type=='blob':
      return Blob()
    elif type=='commit':
      return Commit()
    elif type=='tree':
      return Tree()
    print 'unknown',type
  def load_object(self,arg):
    if type(arg)==str:
      # sha
      return self.cache.load(arg)
    elif type==dict:
      #json
      pass
  def save_object(self,object):
    self.cache.store(object)
  def update(self,root,path,sha):
    self.index.update(self.index.file_object(root,path,sha))
  def add_tree(self,root,name,sha):
    tree=self.index.make_tree(root,name,sha)
    self.index.trees[name]=tree
  def filename2sha(self,filename):
    file = self.index.lookup(filename)
    if file:
      return file['sha']
  def set_obj_sha(self, obj):
    import sha
    data=self.cache.serialize(obj)
    s=sha.new(data).hexdigest()
    obj.set_sha(s)
    return obj
  def get_files(self):
    return self.index.files
  def get_trees(self):
    return self.index.trees
  def directory2sha(self,dir):
    if dir in self.get_trees():
      return self.index.trees[dir]['sha']