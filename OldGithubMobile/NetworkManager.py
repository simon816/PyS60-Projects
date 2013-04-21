import httplib
from simon816 import json
host='api.github.com'
con=httplib.HTTPSConnection(host)
headers={}
def connect():
 try:
  con.connect()
 except httplib.socket.gaierror,e:
  appuifw.note(u'Could not connect to %s\n%s'%(host,e[1]),'error')
def close():
 con.close()
def syncronous(method,url,data):
  try:
   con.request(method,url,data,headers)
   resp=con.getresponse()
  except httplib.socket.gaierror:
   appuifw.note(u"Could not send request for %s"%url)
   return
  return ResponsePackage([method,url],resp)
def GET(url):
  return syncronous('GET',url,None)
def POST(self,url,data):
  return syncronous('POST',url,json.encode(data))
class ResponsePackage:
  class RespError(Exception):
   def __init__(self,code,msg,resp):
    self.code,self.msg,self.json=code,msg,json.decode(resp)
   def __str__(self):
    return '%d %s.'%(self.code,self.msg)
  class ClientError(RespError):pass
  class ServerError(RespError):pass
  def __init__(self,requestinfo,resp):
   self.method,self.url=requestinfo
   self.data=resp.read()
   self.date=''
   self.response=resp
  def __repr__(self):
   return '<GithubResponse from url \'%s\' method: %s>'%(self.url,self.method)
  def getData(self):
   status=self.response.status
   reason=self.response.reason
   if status/100==4:
    raise self.ClientError(status,reason,self.data)
   if status/100==5:
    raise self.ServerError(status,reason,self.data)
   return self.data
  def getheader(self,header):
   return self.resp.getheader(header)
  def getheaders(self):
   return self.resp.getheaders()
  def parseJson(self):
   return json.decode(self.getData())