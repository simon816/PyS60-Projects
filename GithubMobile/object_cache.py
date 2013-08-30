import zlib
import os
from objectTypes import Blob,Commit,Tree
def pad0(s):
  return ('%2s'%s).replace(' ','0')
def chr2hex(chars):
  return ''.join([pad0(hex(ord(c))[2:]) for c in chars])
def hex2chr(hexstr):
  return ''.join([eval('"\\x'+hexstr[i*2:i*2+2]+'"') for i in range(len(hexstr)/2)])

class objectCache:
  
  def __init__(self,dir):
    self.dir=dir
    self.cache={}

  def makefile(self,sha):
    d=sha[:2]
    if not os.path.exists(self.dir+d):
      os.makedirs(self.dir+d)
    return open(self.dir+d+'\\'+sha[2:],'w+')

  def load(self,sha,force=0):
    if sha in self.cache and not force:
      return self.cache[sha]
    d=sha[:2]
    if not os.path.exists(self.dir+d):
      return None
    if not os.path.exists(self.dir+d+'\\'+sha[2:]):
      return None
    fh=open(self.dir+d+'\\'+sha[2:])
    text=zlib.decompress(fh.read())
    fh.close()
    head=text[:text.find('\x00')]
    type,size=head.split(' ')
    size=int(size)
    main=text[len(head)+1:]
    body,foot=main[:size],main[size:]
    if type=='blob':
      obj=Blob(sha)
      obj.set_content(body)
    elif type=='commit':
      parts=body.split('\n')
      d={}
      format=['_tree','_parent','_author','_committer']
      for i in range(len(format)):
        d[format[i]]=' '.join(parts[i].split(' ')[1:])
      d['_message']=parts[-2]
      obj=Commit(sha)
      obj.__dict__.update(d)
    elif type=='tree':
      obj=Tree(sha)
      while len(body):
        mode=body[:body.index(' ')]
        body=body[len(mode)+1:]
        filename=body[:body.index('\x00')]
        body=body[len(filename)+1:]
        rawsha=body[:20]
        body=body[20:]
        hexsha=chr2hex(rawsha)
        obj.append({'mode':mode,'path':filename,'sha':hexsha})
    obj._etag=foot
    self.cache[sha]=obj
    return obj
        
  def serialize(self,obj):
    type=obj.type.lower()
    body=''
    if obj.type=='Blob':
      body=obj.get_content()
    elif obj.type=='Tree':
      for el in obj.get_entrys():
        entry=el.mode+' '+el.path+'\x00'+hex2chr(el.sha)
        body+=entry
    elif obj.type=='Commit':
      d=[]
      add=lambda k,v:d.append('%s %s'%(k,v))
      add('tree',obj.get_tree())
      add('parent',obj.get_parent())
      add('author',obj.get_fauthor())
      add('committer',obj.get_fcommitter())
      d.append('\n'+obj.get_message())
      body+='\n'.join(d)+'\n'
    return '%s %d\x00%s'%(type,len(body),body)

  def store(self,obj):
    fh=self.makefile(obj.get_sha())
    body=self.serialize(obj)
    if obj.get_etag() is None:obj.set_etag('')
    comp=zlib.compress(body+obj.get_etag())
    fh.write(comp)
    fh.close()
    self.cache[obj.get_sha()]=obj

  def listall(self):
    l=[]
    for d in os.listdir(self.dir):
      l.extend([d+f for f in os.listdir(self.dir+d)])
    return l

class Indexer:
  def __init__(self,fileloc):
    self.filename=fileloc
    self.files={}
    self.trees={}
    self.version=2
    if not os.path.exists(self.filename):
      open(fileloc,'w').close()
      self.save()
      return
    self.open()
    self.parse()
  def open(self):
    f=open(self.filename)
    self.rawdata=f.read()
    f.close()
  def parse(self):
    global d
    d=self.rawdata
    def pop(i):
      global d;o=d[:i];d=d[i:];return o
    if pop(4) != 'DIRC':
      raise TypeError('File not an index file')
    int32=lambda:int(chr2hex(pop(4)),16)
    self.version=int32()
    count=int32()
    for i in range(count):
      file={}
      file['ctime']=float('%d.%d'%(int32(),int32()))
      file['mtime']=float('%d.%d'%(int32(),int32()))
      file['dev']=int32()
      file['ino']=int32()
      file['mode']=int32()
      file['uid']=int32()
      file['gid']=int32()
      file['size']=int32()
      file['sha']=chr2hex(pop(20))
      file['flags']=chr2hex(pop(2))
      namelen=int(file['flags'],16)
      if self.version>=3:
        file['flags2']=pop(2)
      file['name']=pop(namelen)
      l=0
      while 1:
        c=pop(1)
        if not c=='\x00':
          d=c+d
          break
        l+=1
      self.files[file['name']]=file
    if pop(4)!='TREE':
      print 'expected TREE entries'
      return
    treelen=int32()
    currentsize=len(d)
    while currentsize!=treelen+len(d) and len(d)!=20:
      tree={}
      namelen_end=d.index('\x00')
      tree['name']=pop(namelen_end+1)[:-1]
      entrylen_end=d.index(' ')
      tree['entrylen']=int(pop(entrylen_end+1)[:-1])
      subtrees_end=d.index('\n')
      tree['subtreecount']=int(pop(subtrees_end+1)[:-1])
      tree['sha']=chr2hex(pop(20))
      self.trees[tree['name']]=tree
    self.checksum=chr2hex(pop(20))
    if d:
      print 'More data than expected!'
      print repr(d)
  def lookup(self,filename):
    if not filename in self.files:return None
    return self.files[filename]
  def update(self,file):
    if type(file) != dict:
      raise TypeError('Not the right file type')
    self.files[file['name']]=file
    """
    treenames=self.trees.items()
    treesplit=os.path.split(file['name'])[0].split('/')
    treecount=len(treesplit)
    x=0
    tree=''
    while x<treecount:
      tree=os.path.join(tree,treesplit[x])
      x+=1
      if not tree in treenames:
        self.trees[tree]={'name':tree,'entrylen':1,'subtreecount':treecount-x,'sha':'0'*40}
        print 'made tree',self.trees[tree]
    """
  def make_tree(self,root,name,sha):
    #generates a tree object
    t={}
    t['name']=name
    t['entrylen']=len(os.listdir(os.path.join(root,name)))
    t['subtreecount']=0
    t['sha']=sha
    return t
  def file_object(self,root,path,sha=None):
    #generates a file object
    if type(path)==unicode:
      path=path.encode('utf8')
    fullpath=os.path.join(root,path)
    if sha is None:
      f=open(fullpath)
      import sha as _sha
      sha=_sha.new(f.read()).hexdigest()
      f.close()
    file={}
    file['name']=path.replace('\\','/')
    file['sha']=sha
    stat=os.stat(fullpath)
    file['ctime']=stat.st_ctime
    file['mtime']=stat.st_mtime
    file['dev']=int(stat.st_dev)
    file['ino']=stat.st_ino
    file['mode']=stat.st_mode
    file['uid']=stat.st_uid
    file['gid']=stat.st_gid
    file['size']=stat.st_size
    file['flags']=('%4s'%hex(len(path))[2:]).replace(' ','0')
    return file
  def delete(self,filename):
    del self.files[filename]
  def save(self):
    int2chr32=lambda i:hex2chr(('%8s'%hex(i)[2:]).replace(' ','0'))
    d=['DIRC']
    add=lambda c:d.append(c)
    chr32=lambda i:add(int2chr32(i))
    names=self.files.keys()
    names.sort()
    chr32(self.version)
    chr32(len(names))
    for filename in names:
      file=self.files[filename]
      ctime=map(int,str(file['ctime']).split('.'))
      if len(ctime)==1:ctime.append(0)
      chr32(ctime[0])
      chr32(ctime[1])
      mtime=map(int,str(file['mtime']).split('.'))
      if len(mtime)==1:mtime.append(0)
      chr32(mtime[0])
      chr32(mtime[1])
      chr32(file['dev'])
      chr32(file['ino'])
      chr32(file['mode'])
      chr32(file['uid'])
      chr32(file['gid'])
      chr32(file['size'])
      add(hex2chr(file['sha']))
      add(hex2chr(file['flags']))
      if self.version>=3:
        add(hex2chr(file['flags2']))
      name=file['name']
      while len(name)%8 != 0:
        name+='\x00'
      if not name.endswith('\x00'):
        name+='\x00'*8
      add(name)
    add('TREE')
    treebuf=[]
    addT=lambda c:treebuf.append(c)
    treenames=self.trees.keys()
    treenames.sort()
    for treename in treenames:
      tree=self.trees[treename]
      addT(tree['name']+'\x00')
      addT(str(tree['entrylen'])+' ')
      addT(str(tree['subtreecount'])+'\n')
      addT(hex2chr(tree['sha']))
    t=''.join(treebuf)
    chr32(len(t))
    print 'len(t)=',len(t)
    add(t)
    try:data=''.join(d)
    except:
      i=0
      for e in d:
        if type(e) != str:
          print type(e),repr(e),i
        i+=1
      print 'error joining data'
      return
    import sha
    checksum=sha.new(data).digest()
    data+=checksum
    f=open(self.filename,'w')
    f.write(data)
    f.close()
    self.checksum=chr2hex(checksum)

if __name__=='__main__':
  repodir='e:\\Python\\apps\\simon816\\GithubMobile\\REPOS\\GithubAPI\\'
  o=objectCache(repodir+'.git\\objects\\')
  i=Indexer(repodir+'.git\\index')
  