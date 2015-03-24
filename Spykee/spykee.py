import socket
class Spykee:
 def __init__(self,host='',port=9000,user='',passwd=''):
  self.sock=socket.socket(
   socket.AF_INET,socket.SOCK_STREAM)
  self.debug=0
  self.speed=5
  if host and port:
   self.connect(host,port)
  if user and passwd:
   self.login(user,passwd)

 def connect(self,host,port=9000):
  if self.debug>0:print '** Connecting  **'
  if self.debug>1:print '**  host:%s  port:%d **'%(host,port)
  self.sock.connect((host,port))

 def login(self, user, passwd):
  if self.debug>0:print '** Login  **'
  if self.debug>1:print '** user:%s  pass:%s  **'%(user,passwd)
  u_len=len(user)
  p_len=len(passwd)
  auth=self._mk_code(10,0,u_len+p_len+2,u_len)+user+chr(p_len)+passwd
  self.sock.send(auth)
  resp=self.sock.recv(4096).decode("UTF-8")
  name_length=ord(resp[6])
  print repr(resp)
  #u'PK\x0b\x00.\x01\x10SPYKEE0870029691\x10SPYKEE0870029691\x00\x061.0.26\x01\x01\x02'
  botname=resp[7:7+name_length]
  return botname

 def _mk_code(self,*nums):
  return 'PK'+''.join([chr(x) for x in nums])

 def setspeed(self, speed):
  if type(speed) is not int:raise TypeError('Invalid Speed, must be an integer')
  if speed>125 or speed < 0:raise ValueError('Speed not in range')
  self.speed=speed

 def move(self,direction,speed=None):
  s=speed or self.speed
  # forward motor direction = range 1 to 125
  # backward motor rotation = range 126 to 250
  # [left motor,right motor]
  code=[5,0,2]
  if direction=='forward':code.extend([s,s])
  elif direction=='right':code.extend([s,s+125])
  elif direction=='backward':code.extend([s+125,s+125])
  elif direction=='left':code.extend([s+125,s])
  else:raise ValueError('Invalid direction')
  self.sock.send(self._mk_code(*code))

 def sound(self, fx):
  if type(fx) is not int:raise TypeError('Sound must be an integer')
  if not fx in range(6):raise ValueError('Sound not in range')
  self.sock.send(self._mk_code(7,0,1,fx))

 def quit(self):
  self.sock.close()
  self.sock=None


def run():
 import appuifw,e32
 lock=e32.Ao_lock()
 def quit():
  lock.signal()
  s.quit()
 appuifw.app.exit_key_handler=quit
 items=[u'Move Forward',u'Move Right',u'Move Backward',u'Move Left',u'Set speed',u'Play sound',u'Upload mp3']
 s=Spykee()
 def call():
  c=appuifw.app.body.current()
  if c==0:s.move('forward')
  elif c==1:s.move('right')
  elif c==2:s.move('backward')
  elif c==3:s.move('left')
  elif c==4:s.setspeed(appuifw.query(u'Set speed','number',s.speed) or s.speed)
  elif c==5:s.sound(appuifw.query(u'Play sound 0-5','number'))
  elif c==6:
   return appuifw.note(u'Not Functioning','error')
   from simon816.util import util
   f=util().select('file',extwhitelist=['mp3'])
   if f:
    f=open(f,'rb')
    while 1:
     buf=f.read(4096)
     if not buf:break
     s.sock.send(s._mk_code(6,16,2)+buf)
    s.sock.send(s._mk_code(7,0,1,6))

 lb=appuifw.Listbox(items, call)
 s.connect(appuifw.query(u'IP Address','text',u'192.168.1.104'))
 appuifw.note(u'Connected to: %s'%s.login('username','password'))
 appuifw.app.body=lb
 lock.wait()
 
run()
