
class GithubObject(object):
  def __init__(self,sha=None):
    self._sha=sha
    self.type=self.__class__.__name__
    self._etag=None
  def __str__(self):
    return '[%s] SHA-1:%s'%(self.type,self._sha)
  def __repr__(self):
    return self.__str__()
  def __getattr__(self,attr):
    if attr in self.__dict__:
      return self.__dict__[attr]
    else:
      return None
  def get_etag(self):
    return self._etag
  def set_etag(self,etag):
    self._etag=etag
  def get_sha(self):
    return self._sha
  def set_sha(self,sha):
    self._sha=sha
  def read_json(self,json):
    #overrideable
    self._sha=json['sha']