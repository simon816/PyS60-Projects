class UserManager:
 def __init__(self,dir):
  self.db=util.util.db(dir+'users','c')
  self.users={}
  for k in self.db.items():
   self.users[k[0]]=self.db.get(k[0],'tuple')
 def forgetAll(self):
  self.users={}
 def addUser(self,displayname,username,password):
  if displayname not in self.users:
   up=(username,password)
   self.users[displayname]=up
   self.db.mod(displayname,up)
  else:
   raise Exception('User already exists')
 def getUser(self,displayname):
  return self.users[displayname]
 def deleteUser(self,user):
  del self.users[user]
  self.db.delete(user)
 def HTTPBasicUser(self,displayname):
  return 'Basic %s'%base64.encodestring(':'.join(self.getUser(displayname)))
 def listUsers(self):
  return [unicode(user) for user in self.users]ss UserManager:
 def __init__(self,dir):
  self.db=util.util.db(dir+'users','c')
  self.users={}
  for k in self.db.items():
   self.users[k[0]]=self.db.get(k[0],'tuple')
 def forgetAll(self):
  self.users={}
 def addUser(self,displayname,username,password):
  if displayname not in self.users:
   up=(username,password)
   self.users[displayname]=up
   self.db.mod(displayname,up)
  else:
   raise Exception('User already exists')
 def getUser(self,displayname):
  return self.users[displayname]
 def deleteUser(self,user):
  del self.users[user]
  self.db.delete(user)
 def HTTPBasicUser(self,displayname):
  return 'Basic %s'%base64.encodestring(':'.join(self.getUser(displayname)))
 def listUsers(self):
  return [unicode(user) for user in self.users]
