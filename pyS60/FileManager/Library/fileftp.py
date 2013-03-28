from StringIO import StringIO as tmpfile
from time import localtime, time
from stat import *
class fileftp:
 host=""
 wd=""
 def __init__(self, host=''):
  mode='a'
  if not os.path.exists('e:\\Python\\apps\\simon816\\ftpbrowser\\logs\\'+str(localtime().tm_yday)+'.log'):mode='w'
  self._log=open('e:\\Python\\apps\\simon816\\ftpbrowser\\logs\\'+str(localtime().tm_yday)+'.log', mode)
  if host:self.connect(host)
  self.host=None
 def logWrite(self,s):
  try:self._log.write(str(localtime().tm_hour)+':'+str(localtime().tm_min)+':'+str(localtime().tm_sec)+'\t'+s+'\r\n')
  except:self.__init__()
 def connect(self, host,*args):
  if host in ['localhost', '127.0.0.1','LocalUser']:
   self.host=host;self.logWrite('Connect: '+host);return None
 def set_debuglevel(self, *args):pass
 def set_pasv(self, *args):pass
 def abort(self, *args):pass
 def sendcmd(self, cmd):
  if not self.host:self._log.close();raise 'error';return 0
  resp=''
  self.logWrite(cmd)
  allcmds=['RETR', 'STOR', 'LIST', 'NLST', 'RNFR', 'RNTO', 'DELE', 'CDUP', 'CWD', 'SIZE', 'MKD', 'RMD', 'PWD', 'QUIT', 'HELP', 'USER']
  if cmd[:3] in allcmds:
   if cmd[:3]=='CWD':
    os.chdir(cmd[4:]);self.wd=replace_all(os.getcwd(), {'\\':'/'})
   if cmd[:3]=='PWD':
    self.wd=replace_all(os.getcwd(), {'\\':'/'})
    return self.wd
   if cmd[:3]=='MKD':os.mkdir(cmd[4:])
   if cmd[:3]=='RMD':
    try:os.rmdir(cmd[4:])
    except OSError, e:
     if e.errno==17:raise error_reply, '550 Directory not empty.'
  elif cmd[:4] in allcmds:
   if cmd[:4]=='DELE':os.unlink(cmd[5:])
   if cmd[:4]=='CDUP':os.chdir('..');self.wd=replace_all(os.getcwd(), {'\\':'/'})
   if cmd[:4]=='RNFR':self.tmp=cmd[5:]
   if cmd[:4]=='RNTO':
    if self.tmp:os.rename(self.tmp, cmd[5:])
   if cmd[:4]=='SIZE':resp=os.path.getsize(self.pwd()+cmd[4:])
   if cmd[:4]=='NLST':
    fp=tmpfile();s=''
    for l in os.listdir(cmd[5:]):s+=l+'\n'
    fp.write(s);fp.seek(0)
    resp= fp
   if cmd[:4]=='RETR':
    try:resp=open(cmd[5:], 'r')
    except IOError, e:
     if e.errno==13: raise error_perm, '550 No such file or directory.'
   if cmd[:4]=='STOR':resp=open(self.wd+'/'+cmd[5:], 'w')
   if cmd[:4]=='LIST':
    f=tmpfile()
    if len(cmd)<6:dir=self.wd
    else:dir=self.drive+cmd[5:]+'\\'
    if dir:files=os.listdir(dir)
    else:files=e32.drive_list();self.wd=""
    for file in files:
     st=os.stat(dir+file);d='-'
     time=localtime(st.st_mtime)
     mon=('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
     r=oct(S_IMODE(st[0]))
     if len(r)==4:r=r[1:]
     if S_ISDIR(st[0]):p='d'
     else:p='-'
     for i in range(len(r)):
      if r[i]=='0':p+='---'
      elif r[i]=='1': p+='--x'
      elif r[i]=='2': p+= '-w-'
      elif r[i]=='3': p+='-wx'
      elif r[i]=='4': p+='r--'
      elif r[i]=='5': p+='r-x'
      elif r[i]=='6': p+='rw-'
      elif r[i]=='7': p+= 'rwx'
     f.write(p+'    2 '+str(st.st_uid)+'   '+str(st.st_gid)+'         '+str(st.st_size)+' '+mon[time[1]-1]+' '+str(time.tm_mday)+' '+str(time.tm_hour)+':'+str(time.tm_min)+' '+file+'\r\n')
    f.seek(0);resp=f
   if cmd[:4]=='QUIT':resp='Goodbye';self._log.write("\r\n");self._log.close()
   if cmd[:4]=='HELP':resp=allcmds
   if cmd[:4]=="USER":self.drive=cmd[5:];os.chdir(self.drive+"/")
  return resp
 def retrbinary(self,cmd,callback,blocksize=8192,rest=None):
  resp=self.sendcmd(cmd)
  while 1:
   data=resp.read(blocksize)
   if not data:
    break
   callback(data)
  resp.close()
 def sendport(self, *args):pass
 def login(self,  *args):
  self.sendcmd('USER '+args[0]+":")
 def retrlines(self,cmd,callback=None):
  if not callback:callback=print_line
  resp=self.sendcmd(cmd)
  while 1:
   line=resp.readline()
   if not line:
    break
   if line[-1:]=='\n':
    line=line[:-1]
   callback(line)
  resp.close()
 def storbinary(self,cmd,fp,blocksize=8192):
  resp=self.sendcmd(cmd)
  while 1:
   buf=fp.read(blocksize)
   if not buf:break
   resp.write(buf)
  resp.close()
 def storlines(self,cmd,fp):
  resp=self.sendcmd(cmd)
  while 1:
   buf=fp.readline()
   if not buf:break
   resp.write(buf)
  resp.close()
 def nlst(self, dir=None):
  if dir==None:dir=self.pwd()
  files=[]
  self.retrlines('NLST '+dir, files.append)
  return files
 def dir(self, dir='', cback=None):
  self.retrlines('LIST '+dir, cback)
 def rename(self, fromname, toname):
  self.sendcmd('RNFR '+fromname)
  self.sendcmd('RNTO '+toname)
 def delete(self, filename):
  self.sendcmd('DELE '+filename)
 def cwd(self,dirname):
  if dirname == '..':
   try:
    return self.sendcmd('CDUP')
   except error_perm, msg:
    if msg[:3] != '500':
     raise error_perm, msg
  elif dirname == '':
   dirname = '.' 
  cmd = 'CWD ' + dirname
  return self.sendcmd(cmd)
 def size(self, filename):
  self.sendcmd('SIZE '+filename)
 def mkd(self, dirname):
  self.sendcmd('MKD '+dirname)
 def rmd(self, dirname):
  self.sendcmd('RMD '+dirname)
 def pwd(self):
  return self.sendcmd('PWD')[2:]
 def getwelcome(self):return None
 def quit(self):
  self.sendcmd('QUIT')
 def print_line(line):print line
