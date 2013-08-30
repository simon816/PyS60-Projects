import appuifw
from os import stat
class Icon:
 def __init__(self):
  self.path=None
  self.file=None
  self.keys={}
 def open(self,path):
  try:
   self.file=open(path,'rb+')
   size=stat(path).st_size
   self.file.seek(size-1)
   klen=ord(self.file.read())
   if klen:
    self.file.seek(size-klen-1)
    self.keys=eval(self.file.read()[:-1])
    self.file.seek(size-klen-1)
    self.file.write('')#remove keys
  except IOError:raise
  self.path=unicode(path)
 def get_icon(self,index,mask=None,name=False):
  if mask is None:mask=index+1 
  icon=appuifw.Icon(self.path,index,mask)
  if name==True:
   return icon,''
  return icon
 def __getitem__(self,key):
  index=self.keys[str(key)]
  return self.get_icon(index)
 def __setitem__(self,key, value):
  self.keys[str(key)]=int(value)
 def close(self):
  if self.file:
   keystr=str(self.keys)
   self.file.write(keystr)
   self.file.write(chr(len(keystr)))
   self.file.close()
   self.file=None
 def __del__(self):
  self.close()
"""
m=Icon() #initiate instance
m.open('e:\\testfile.mbm')#open icon file
icon1=m.get_icon(1) #get icon from mbm index
icon2=m['friendlyname'] # get icon from name
m['mainicon']=5 # sets icon name to mbm index
m.get_icon(5,name=True) # returns [icon, name or '']
m.get_icon(2,6) # gets icon 2 with mask 6
m.close() # finished getting and setting icons
"""