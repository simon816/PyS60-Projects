import httplib
urlsplit=httplib.urlsplit
socket=httplib.socket
import os,time
from simon816.console import Console,ArgumentParser
from base64 import encodestring as b64e,decodestring as b64d

def connect_http(self,timeout=None):
    # copy of the original connect function but with option to
    # set timeout and grab some ip info
    """Connect to the host and port specified in __init__."""
    msg = "getaddrinfo returns an empty list"
    allinfo=[]
    for res in socket.getaddrinfo(self.host, self.port, 0,
                                  socket.SOCK_STREAM):
        allinfo.append(res)
        af, socktype, proto, canonname, sa = res
        try:
            self.sock = socket.socket(af, socktype, proto)
            if self.debuglevel > 0:
                print "connect: (%s, %s)" % (self.host, self.port)
            self.sock.connect(sa)
            if timeout is not None:
             self.sock.settimeout(timeout)
        except socket.error, msg:
            if self.debuglevel > 0:
               print 'connect fail:', (self.host, self.port)
            if self.sock:
                self.sock.close()
            self.sock = None
            continue
        break
    if not self.sock:
        raise socket.error, msg
    return allinfo
def connect_https(self,timeout=None):
    "Connect to a host on a given (SSL) port."
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((self.host, self.port))
    if timeout is not None:
     sock.settimeout(timeout)
    ssl = socket.ssl(sock, self.key_file, self.cert_file)
    self.sock = httplib.FakeSocket(sock, ssl)
    return socket.getaddrinfo(self.host,self.port,0,socket.SOCK_STREAM)
httplib.HTTPConnection.connect=connect_http
httplib.HTTPSConnection.connect=connect_https

class Meter:
 def __init__(self,screeninstance,cols):
  #screeninstance is an instance of simon816.console.Console
  self.cols=list(cols)
  self.tab='    '
  self.si=screeninstance
  self.index=None
  self.len=0
 def __repr__(self):
  s=self.join()
  self.len=len(s)
  return s
 def join(self):
  return self.tab.join([str(c) for c in self.cols])
 def update_col(self,col, val):
  if self.index is not None:
   pos=self.si.t.get_pos()
   oldlen=len(self.join())
   self.si.t.delete(self.index,oldlen)
   self.si.t.set_pos(self.index)
   self.cols[col]=val
   new=self.join()
   self.si.t.add(self.si.toUnicode(new))
   self.si.t.set_pos(pos+(len(new)-oldlen))
 def add(self,col):
  self.cols.append(col)
  self.update_col(len(self.cols)-1,col)
 def _print(self):
  if self.index is None:
   self.index=self.si.t.get_pos()
   self.si.output(str(self))
  else:
   raise Warning('Progress meter already exists')
 def finish(self):self.index=None;self.cols=[];del self.si


class curl:
 def __init__(self):
  dir='E:\\Python\\apps\\simon816\\cURL\\'
  self.console=Console()
  self.console.console('curl >',"CURL")
  self.console.bodystyle['input']={'color':'#117711'}
  self.console.bodystyle['output']={'color':'#000088'}
  self.console.bind('exec_cmd',self.command)
  self.console.bind('get_text_css',lambda:
   {'font-antialias':'on','font-size':'15'}
  )
  self.UserPassStore={}
  self.protocols={
   'http':[80,httplib.HTTPConnection],
   'https':[443,httplib.HTTPSConnection]
  }
  if not os.path.exists(dir):os.makedirs(dir)
  os.chdir(dir)
  self.argParser=ArgumentParser()
  # arguments in order and agree with the specification at
  # http://curl.haxx.se/docs/manpage.html
  self.add_arg('-0',0,['--http1.0'],'Use HTTP/1.0')
  self.add_arg('-A',2,['--user-agent'],'Sets user-agent')
  self.add_arg('-b',2,['--cookie'],'Send cookie')
  self.add_arg('-c',2,['--cookie-jar'],'Recieve cookie')
  self.add_arg('--connect-timeout',2,d='Set timeout')
  self.add_arg('-d',2,['--data','--data-ascii'],'POST Data')
  self.add_arg('-D',2,['--dump-header'],'Send output to a file')
  self.add_arg('-e',2,['--referer'],'Set referer header')
  self.add_arg('-F',2,['--form'],'POST a form, usally file upload')
  self.add_arg('-G',0,['--get'],'Set a GET parameter')
  self.add_arg('-H',2,['--header'],'Set a header')
  self.add_arg('-i',0,['--include'],'Return headers recieved')
  self.add_arg('-I',0,['--head'],'Use the HEAD verb')
  self.add_arg('-L',0,['--location'], 'Follow Location headers when a 3XX status code is returned')
  self.add_arg('-o',2,['--output'],'Where to dump output')
  self.add_arg('-O',0,['--remote-name'])
  self.add_arg('-s',0,['--silent'])
  self.add_arg('-u',1,['--user'],'Sets the user, using Basic auth')
  self.add_arg('--url',2,d='Specify URL to connect to')
  self.add_arg('-v',0,['--verbose'],'Makes curl talk a lot')
  self.add_arg('-X',2,['--request'],'Set HTTP verb')
  self.add_arg('-h',0,['--help'],'Displays help')
  self.maxredirs=50
  self.console.shell_run()
 def add_arg(self,n,rd,al=None,d=''):
  #just a quick shortcut
  a=self.argParser.createArgument(name=n,requiresdata=rd,description=d)
  if al:a.aliases=al
  self.argParser.RegisterArgument(a)

 def command(self,cmd):
  # handles commands when enter is pressed
  try:args,argstat=self.argParser.Parse(cmd)
  except (self.argParser.ParseError, AttributeError), e:
   print e
   return
  if not args:return
  self.verbose=False
  self.silent=False
  self.redir=0
  header={'Accept':'*/*','User-Agent':'curl/7.29.0'}
  verb='GET'
  data=''
  http=11
  timeout=None

  if '-h' in args:
   print 'Available Options:'
   for arg in self.argParser.listArguments():
    print ', '.join(arg)+' : '+self.argParser.getArgument(arg[0]).description
   return

  if not '--url' in args:
   if 'UNKNOWN' in args:
    args['--url']=args['UNKNOWN']
    del args['UNKNOWN']
   else:
    print 'Please specify a url'
    return
  proto,host,path,query,frag=urlsplit(args['--url'].last())
  try:
   host,port=host.split(':')
   port=int(port)
  except:port=None
  #only uses the last url specified
  if proto in self.protocols:
   if not port:port=self.protocols[proto][0]
  else:
   print 'Unknown protocol %s'%repr(proto)
   return
  if not host:
   print 'Error: No host name'
   return
  sufx=host.split('.')
  if len(sufx)==1 or len(sufx[-1])<2 and (not sufx[0].isdigit()):
   print 'Invalid host name'
   return
  if not path:
   path='/'
  header['Host']=host
  if query:path+='?'+query
  if frag:path+='#'+frag

  if '-0' in args:
   http=10

  if '-A' in args:
   header['User-Agent']=args['-A'].last()

  if '--connect-timeout' in args:
   try:timeout=int(args['--connect-timeout'].last())
   except:
    print 'Invalid timeout'
    return

  if '-v' in args:
   self.verbose=True
   self.silent=False

  if '-s' in args:
   self.verbose=False
   self.silent=True

  if '-u' in args:
   skip=0
   try:user=args['-u'].last()
   except IndexError:
    if host in self.UserPassStore:
     userpass=self.UserPassStore[host]
     skip=1
    else:
     print args['-u'].name+' argument has no value'
     return
   def parsestr(userarg):
    userpass=userarg.split(':')
    if len(userpass)==1:
     pwd=self.console.prompt('Enter host password for user \'%s\': '%userpass[0],1)
     userpass.append(pwd)
    return b64e(':'.join(userpass))[:-1]
   if not skip:
    userpass=parsestr(user)
    if host in self.UserPassStore:action='replace'
    else:action='save'
    saveuser=raw_input('%s username and password for %s? [y/n]'%(action,host))
    if saveuser.lower()=='y':
     self.UserPassStore[host]=userpass
   header['Authorization']='Basic '+userpass

  if '-b' in args:
   i=0
   for v in args['-b'].Values():
    if v[0]=='@':
     f=open(v[1:])
     args['-b'].values[i]=f.read()
     f.close()
    i+=1
   header['Cookie']=args['-b'].join(';')

  if '-d' in args:
   verb="POST"
   header['Content-Type']='application/x-www-form-urlencoded'
   data=args['-d'].last()
   if data=='-':
    data=raw_input('Send data:')
   elif data[0]=='@':
    f=open(data[1:])
    data=f.read()
    f.close()
   header['Content-Length']=str(len(data))

  if '-e' in args:
    header['Referer']=args['-e'].last()

  if '-H' in args:
   for h in args['-H'].Values():
    try:
     s=h.split(':')
     k=s[0];v=':'.join(s[1:])
     if not v:del header[k]
     else:
      v=v[1:]
      if not v:raise ValueError
      header[k]=v
    except:
     print 'Malformed HTTP Header: %s'%repr(h)
     return


  if '-I' in args:verb='HEAD'
  if '-G' in args:verb='GET'
  if '-X' in args:verb=args['-X'].last().upper()

  sockinfo=(proto,host,port,timeout)
  httpinfo=(verb,path,http,data,header)
  if str(self.console.oldstd['out']).startswith('<ped.PythonShellWindow'):
   # just some debugging when testing in the ped IDE
   print sockinfo
   print httpinfo
   print args
   print argstat
  self.download(sockinfo,httpinfo,args)

 def if_v(self,words):
  if self.verbose:
   print words
 def init_progress(self):
  statHead=['  %',' Total','  %','Received','Dload','Upload','Time Total']
  self.console.output('    '.join(statHead)+'\n')
  zeros=['0'+' '*6]*6
  cols=zeros+['--:--:--.---']
  m=Meter(self.console,cols)
  m._print()
  self.console.output('\n')
  return m
   
 def download(self,sockinfo,httpinfo,args):
  proto,host,port,timeout=sockinfo
  method,path,httpver,data,headers=httpinfo
  requestheaders=headers
  httpVer2str=lambda v:'HTTP/%1.1f'%(v/10.0)
  httpVer2int=lambda v:int(float(v.split('/')[1])*10)
  if '-o' in args:
   m=self.init_progress()
   if args['-o'].last()=='-':
    f=self.console
   else:
    f=open(args['-o'].last(),'w')
  def secondsToStr(t):
   rediv = lambda ll,b : list(divmod(ll[0],b)) + ll[1:]
   return "%d:%02d:%02d.%03d" % tuple(reduce(rediv,[[t*1000,], 1000,60,60]))
  fn=self.protocols[proto][1]
  time_start=time.time()
  self.if_v('* About to connect() to %s port %d'%(host,port))
  connection=fn(host,port)
  connection._http_vsn_str=httpVer2str(httpver)
  connection._http_vsn=httpver
  try:
   if proto=='http':arg=[timeout]
   else:arg=[]
   info=connection.connect(*arg)
   ips=[i[4][0] for i in info]
   if self.verbose:
    for ip in ips:self.if_v('*   Trying %s...'%ip)
   self.if_v('* Connected to %s (%s) port %d'%(host,ips[-1],port))
  except socket.gaierror:
   print 'Unable to connect to %s on port %d'%(host,port)
   return
  time_connect=time.time()
  if 'Authorization' in requestheaders:
   mode,auth=requestheaders['Authorization'].split(' ')
   if mode=='Basic':user=b64d(auth).split(':')[0]
   else:user=auth
   self.if_v('* Server auth using %s with user %s'%(mode,repr(user)))
  connection.putrequest(method,path)
  self.if_v('> %s %s %s'%(method,path,httpVer2str(httpver)))
  for h,v in requestheaders.iteritems():
   connection.putheader(h,v)
   self.if_v('> %s: %s'%(h,v))
  connection.endheaders()
  self.if_v('>')
  if data:
   connection.send(data)
   self.if_v('* upload completely sent off: %d out of %d bytes'%(len(data),len(data)))
  time_upload=time.time()
  resp=connection.getresponse()
  responseheaders=[h.rstrip() for h in resp.msg.headers]
  self.if_v('< %s %d %s'%(httpVer2str(resp.version),resp.status,resp.reason))
  if self.verbose:
   for h in responseheaders:self.if_v('< %s'%h)
   self.if_v('<')
  buf=resp.read(1024)
  out=buf
  while buf:
   buf=resp.read(1024)
   out+=buf
  time_download=time.time()
  try:totalsize=int(resp.getheader('content-length'))
  except:totalsize=len(out)
  up_time=time_upload-time_connect
  dl_time=time_download-time_upload
  if '-o' in args:
   try:percentRecieve=(len(out)/float(totalsize))*100
   except ZeroDivisionError:percentRecieve=0
   try:upSpeed=float(len(data))/up_time/1024.0
   except ZeroDivisionError:upSpeed=0
   m.update_col(0,'100')
   m.update_col(1,'%dk'%(totalsize/1024))
   m.update_col(2,'%.1f'%percentRecieve)
   m.update_col(3,'%dk      '%(len(out)/1024))
   m.update_col(4,'%.0fk'%(float(len(out))/dl_time/1024.0))
   m.update_col(5,'    %.0fk      '%upSpeed)
   m.update_col(6,secondsToStr(time_download-time_start))
   m.finish()
  if '-i' in args:
   self.console.output('\n'.join(responseheaders)+'\n')
  if not '-o' in args:
   self.console.output(out+'\n')
  else:
   f.write(out)
   f.close()
  connection.close()
  if resp.getheader('location') and '-L' in args and self.redirs < self.maxredirs:
    self.redirs+=1
    nproto,nhost,npath,nquery,nfrag=urlsplit(resp.getheader('location'))
    if not nhost:
      nhost=host
    if not nproto:
      nproto=proto
    nport=port
    if self.protocols[nproto]:
      nport=self.protocols[nproto][0]
    sockinfo=(nproto,nhost,nport,timeout)
    if resp.status in [301, 302, 303]:
      nmethod='GET'
    else:
      nmethod=method
    headers={}
    if '-e' in args:
      spl=args['-e'].last().split(';')
      if spl[-1]=='auto':
        headers['Referer']=host+path
    httpinfo=(nmethod,npath,httpver,None,headers)
    self.download(sockinfo,httpinfo,args)
    return

  if resp.will_close:
   state='closed'
  else:
   state='left intact'
  self.if_v('* Connection to host %s %s'%(host,state))



c=curl()
