from baseObject import GithubObject
import base64
import time
def date2time(date):
  print date
  raise 
  return time.mktime(time.strptime(date),'')

class Blob(GithubObject):
  def get_content(self):
    return self._content
  def set_content(self,content):
    self._content=content
  def read_json(self,json):
    self._sha=json['sha']
    encoding=json['encoding']
    if encoding =='base64':
      self._content=base64.decodestring(json['content'])
    elif encoding=='utf-8':
      self._content=json['content'].decode('utf-8')

class Tree(GithubObject):
  class Element:
    def __init__(self,d):
      self.__dict__.update(d)
    def __repr__(self):
      return '[Tree Element] mode=%s, path=%r, SHA-1:%s'%(self.mode,self.path,self.sha)
    def dictify(self):
      if self.mode=='100644':
        type='blob'
      elif self.mode=='040000':
        type='tree'
      else:
        type='Unknown'
        print 'unknown type',self.__repr__()
      return {'path':self.path,'mode':self.mode,'type':type,'sha':self.sha}

  def __init__(self,sha=None):
    super(Tree,self).__init__(sha)
    self.entrys=[]

  def append(self,entry):
    self.entrys.append(self.Element(entry))
  def read_json(self,json):
    self._sha=json['sha']
    for entry in json['tree']:
      self.append(entry)
  def get_entrys(self):
    return self.entrys

class Commit(GithubObject):
  def get_tree(self):
    return self._tree
  def get_parent(self):
    return self._parent
  def get_author(self):
    return self._author
  def get_committer(self):
    return self._committer
  def _format_user(self,d,totime=1):
    if not totime:#NOT
      time=date2time(d['date'])
    else:
      time=d['date']
    return '%s <%s> %s'%(d['name'],d['email'],time)
  def get_fcommitter(self,tt=1):
    return self._format_user(self._committer,tt)
  def get_fauthor(self,tt=1):
    return self._format_user(self._author,tt)
  def get_message(self):
    return self._message
  def read_json(self,json):
    self._sha=json['sha']
    self._tree=json['tree']['sha']
    parents=json['parents']
    if len(parents):
      self._parent=parents[0]['sha']
    else:
      self._parent='0'*40
    self._author=json['author']
    self._committer=json['committer']
    self._message=json['message']
