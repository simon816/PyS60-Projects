import os
class DataFile:
  def __init__(self,filename,mode='config'):
    filename=str(filename)
    path=os.path.split(filename)[0]
    if not os.path.exists(path):
      os.makedirs(path)
    if not os.path.exists(filename):
      f=open(filename,'w+')
      f.write('')
    else:
      f=open(filename,'r+')
    self.obj={}
    if mode=='config':
      currentkey=''
      self.obj[currentkey]={}
    for line in f.xreadlines():
      line=line.rstrip()
      if line.startswith('[') and line.endswith(']') and mode=='config':
        currentkey=line[1:-1]
        self.obj[currentkey]={}
      else:
        line=line.replace('\t','')
        split=line.split('=')
        if len(split)==1:continue
        key=split[0].strip()
        value='='.join(split[1:]).lstrip()
        if mode=='config':
          self.obj[currentkey][key]=value
        elif mode=='property':
          self.obj[key]=value
    f.close()
    if mode=='config':
      del self.obj['']
    self.filename=filename
    self.mode=mode
  def write(self):
    out=[]
    keys=self.obj.keys()
    keys.sort()
    for key in keys:
      if self.mode=='config':
        out.append('[%s]'%key)
        itemkeys=self.obj[key].keys()
        itemkeys.sort()
        for itemkey in itemkeys:
          out.append('  %s = %s'%(itemkey,self.obj[key][itemkey]))
      elif self.mode=='property':
        out.append('%s = %s'%(key,self.obj[key]))
    f=open(self.filename,'w')
    f.write('\n'.join(out))
    f.close()
  def __setitem__(self,key,value):
    if type(value)==dict and self.mode=='config':
      self.obj[key]=value
    elif self.mode=='property':
      self.obj[key]=value
    else:
      raise ValueError('Can only set keys with dict. Use __getitem__ instead')
    self.write()
  def __getitem__(self,key):
    if not key in self.obj:
      self.obj[key]={}
      self.write()
    #dict=self.specialdict(self.obj[key])
    #def update(d):self[key]=d
    #dict.parent(update)
    return self.obj[key]
  def __delitem__(self,key):
    del self.obj[key]
    self.write()
  def merge(self,key,data):
    if not key in self.obj:self.obj[key]={}
    self.obj[key].update(data)
    self.write()
  def haskey(self,key):
    return key in self.obj
  def keys(self):
    return self.obj.keys()

class DataDirectory(DataFile):
  def __init__(self,basedir):
    self.obj={}
    for file in os.listdir(basedir):
      self.obj[file]=DataFile(basedir+'\\'+file).obj
  def write(self):
    pass


