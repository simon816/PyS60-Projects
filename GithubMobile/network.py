from httplib import (HTTPSConnection,
                                  HTTPException)
from simon816 import json
from base64 import encodestring
class Connection:
  con=HTTPSConnection('api.github.com')
  def __init__(self,username=None,password=None):
    self.auth=''
    #self.con.set_debuglevel(1)
    self.con.connect()
    self.login(username,password)
  def login(self,username,password):
    if username and password:
      self.user=str(username)
      self.auth='Basic '+encodestring(username+':'+str(password)).rstrip('\n')
  def sendrequest(self,verb,url,data=None,header={}):
    headers={'Accept':'*/*','User-Agent':'GitHubSymbian/0.1'}
    headers.update(header)
    if self.auth:
      headers['Authorization']=self.auth
    self.con.request(verb,url,data,headers)
  def do_request(self,*args):
    self.sendrequest(*args)
    try:
      resp=self.con.getresponse()
    except HTTPException,e:
      for a in dir(e):
        z=getattr(e,a)
        if not hasattr(z,'__call__'):
          print a,z
      raise
    return Response(resp)
  def json_encode(self,dict):
    return json.encode(dict)
  def postJSON(self,url,jsondict):
    return self.do_request('POST',url,self.json_encode(jsondict))
  def close(self):
    self.con.close()
  def __del__(self):
    self.close()

class Response:
  class ClientError(Exception):
    pass
  class ServerError(Exception):
    pass
  def __init__(self,response):
    self.status=response.status
    self.reason=response.reason
    self.headers=dict(response.getheaders())
    self.data=self.rawdata=response.read()
    ctype=response.getheader('content-type')
    try:self.etag=eval(response.getheader('etag'))
    except TypeError:self.etag=None
    self.ratelimit=response.getheader('x-ratelimit-limit')
    self.ratelimit_rem=response.getheader('x-ratelimit-remaining')
    if ctype is not None:
      ctype=ctype.split(';')[0]
      if ctype=='application/json':
        self.data=json.decode(self.data)
    self.content_type=ctype
    self.check_errors()
  def check_errors(self):
    s=self.status/100
    if s==4 or s==5:
      if self.is_json():
        msg=self.data['message']
      else:
        msg=self.reason
      if s==4:
        raise self.ClientError(msg)
      else:
        raise self.ServerError(msg)
  def get_remaining_rate_limit(self):
    if self.ratelimit and self.ratelimit_rem:
      return int(self.ratelimit)-int(self.ratelimit_rem)
  def hasdata(self):
    return len(self.rawdata)>0
  def is_json(self):
    return self.content_type=='application/json'