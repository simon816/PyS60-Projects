import os
import e32dbm
import appuifw
import e32
from stat import *

class util:
 def select(self,type="file",initdir="\\",drive="",**options):
  def opt(k):
   if k in options:return options[k]
  initdir=drive+initdir
  path= os.path.normpath(initdir)
  drive,path=os.path.splitdrive(path)
  if not drive or initdir==drive+"\\..\\" and not opt("limitdrive"):
   drvs=e32.drive_list()
   ind=appuifw.popup_menu(drvs,u"Select Drive")
   if not ind==None:drive=drvs[ind]
   else:return None
  if not path[0:1]=="\\":path="\\"+path
  initdir=drive+path
  dirs=[]
  files=[]
  if not initdir[-1:]=="\\":initdir+="\\"
  dirsonly=type=="dir"
  for f in os.listdir(initdir):
   f=f.decode('utf8')
   statistics=os.stat(unicode(initdir+f).encode('utf8'))
   if S_ISDIR(statistics[0]):
    dirs.append([f.lower(),f])
   else:
    files.append([f.lower(),f])
  dirs.sort()
  files.sort()
  realdirs=[]
  if dirsonly:realdirs.append(u"[This Directory]")
  realdirs.append(u"[d] ..")
  for dir in dirs:realdirs.append(unicode("[d] "+dir[1]))
  if not dirsonly:
   realfiles=[]
   for file in files:
    allowed=True
    if opt("extblacklist"):
     for black in opt("extblacklist"):
      if os.path.splitext(file[1])[1][1:]==black:allowed=False
    if opt("extwhitelist"):
     allowed=False
     for white in opt("extwhitelist"):
      if os.path.splitext(file[1])[1][1:]==white:allowed=True
    if allowed:realfiles.append(unicode("[f] "+file[1]))
   realdirs.extend(realfiles)
  if dirsonly:title="Folder"
  else:title="File"
  ind=appuifw.popup_menu(realdirs,u'Select '+title)
  if not ind and ind is not 0:return None
  selected=realdirs[ind]
  if selected[:3]=="[d]":
   if dirsonly and selected[4:]=="[This Directory]":
    return initdir+selected[4:]
   else:
    return self.select(type,initdir+selected[4:]+"\\",'',**options)
  elif selected==u"[This Directory]":
   return  initdir
  else:
   return initdir+selected[4:]
 def mkdir(self,list):
  for dir in list:
   if not os.path.exists(dir):
    os.makedirs(dir)
 class db:
  def __init__(self,file="",mode=None):
   if file and mode:
    self.open(file,mode)
  def open(self,file,mode):
   self.openDB=e32dbm.open(file,mode)
   return self
  def items(self):
   return self.openDB.items()
  def sync(self):
   return self.openDB.sync()
  def close(self):
   return self.openDB.close()
  def mod(self, key, value):
   s=''
   if type(value)==tuple:
    for v in value:
     try:v=int(v);v=str(v)+'\x01'
     except:
      if unicode(v)==v:v='\x01'+v
      else:v=str(v)
     s+=v+'\x00'
    s=s[:len(s)-1]
   elif type(value)==list:
    for v in value:s+=str(v)+'\x01'
   else:s=value
   self.openDB[str(key)]=str(s)
   print '<',key,repr(s)
  def get(self, key, mode='str'):
   try:
    v=self.openDB[str(key)]
    if mode=='str':return v
    elif mode=='int':return int(float(v))
    elif mode=='tuple':
                                  t=v.split('\x00');i=0
                                  for c in t:
                                   if c[len(c)-1:]=='\x01':
                                    t[i]=int(float(c[:len(c)-1]))
                                   if c[:1]=='\x01':
                                    t[i]=unicode(c[1:])
                                   i=i+1
                                  return tuple(t)
    elif mode=='list':return list(v.split('\x01'))
   except:raise
  def delete(self,key):
   del self.openDB[key]
 def submenu(self, mode='r', *args):
  subindex=args[0]
  if mode=="c":
   appuifw.app.menu[subindex]=(args[1],tuple(args[2:]))
   return appuifw.app.menu[subindex]
  obj=list(appuifw.app.menu[subindex][1])
  try:
   if mode in ['r','w']:index=[x[0].lower() for x in appuifw.app.menu[subindex][1]].index(unicode(args[1].lower()))
  except:return 0
  if    mode=='r':return index
  elif mode=='w':obj[index]=args[1]
  elif mode=='a':obj.insert(args[1], args[2])
  elif mode=='d':del obj[args[1]]
  appuifw.app.menu[subindex]=(appuifw.app.menu[subindex][0], tuple(obj))


"""
submenu help
definition: creates and handles appuifw.menu sub-menus
creating a submenu:
 submenu("c",index, u"Major item",(u"Sub item1",callback),(u"Sub item 2",callback) ...)
 notes: all strings in unicode, forced by appuifw. must be atleast 2 sub items, forced by appuifw. every item must have a callback, forced by appuifw. must be tuples, forced by appuifw.
reading an index of a submenu label:
 submenu("r", index, label)
 returns the position in menu[index] of label
changing the label of a sub item:
 submenu("w",index,oldlabel,(newlabel, newcallback))
appending an item to a submenu:
 submenu("a", index, position, (label,callback))
deleting an item from a submenu:
 submenu("d",index,itemindex)
"""